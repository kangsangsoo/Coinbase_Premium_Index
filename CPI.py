import tkinter 
import ccxt
import time
import cbpro
import threading
from tradingview_ta import TA_Handler, Interval, Exchange



class CoinPriceUpdate(threading.Thread):

    def __init__(self, binance_price, coinbase_price):
        super().__init__()
        self.binance_price = binance_price
        self.coinbase_price = coinbase_price
        self.lock = threading.Lock()

    def run(self, ):

        while 1:
            public_client = cbpro.PublicClient()
            binance = ccxt.binance() 
            ticker = binance.fetch_ticker('BTC/USDT')
            self.lock.acquire()
            self.binance_price[0] = ticker['close']
            self.coinbase_price[0] = public_client.get_product_ticker(product_id='BTC-USD')['price']
            self.lock.release()
            time.sleep(2)

class TetherIndexUpdate(threading.Thread):

    def __init__(self, tether_index):
        super().__init__()
        self.tether_index = tether_index
        self.lock = threading.Lock()

    def run(self):
        while 1:
            handler = TA_Handler(
                    symbol="USDTUSD",
                    exchange="KRAKEN",
                    screener="crypto",
                    interval=Interval.INTERVAL_1_MINUTE
                    ) 
            self.lock.acquire()
            self.tether_index[0] = handler.get_analysis().indicators['close']
            self.lock.release()
            time.sleep(2)
             

class Application(tkinter.Frame):

    coinbase_price = ['0']
    binance_price = ['0']
    tether_index = ['0']

    def __init__(self, master):
        super().__init__(master)
        self.timer = None
        self.master = master
        self.master.title("Coinbase Premium Index")
        self.pack(fill='both', expand=True)

        now = "NONE"
        self.label = tkinter.Label(self, text=str(now))
        self.label.pack(padx=15, pady=15)

        self.lock = threading.Lock()

        self.start_button = tkinter.Button(self, text='start')
        self.start_button.pack(side='left', padx=15, pady=15)
        self.start_button.bind("<Button-1>", self.startTimer)

    def startTimer(self, *_):

        

        # run 시작
        coin_price = CoinPriceUpdate(Application.binance_price, Application.coinbase_price)
        tether_index = TetherIndexUpdate(Application.tether_index)

        coin_price.start()
        tether_index.start()

        time.sleep(1)
               
        self.tiktok()
        self.start_button.configure(state='disabled')

    def tiktok(self):
        self.lock.acquire()
        now = float(Application.coinbase_price[0]) - float(Application.binance_price[0]) * float(Application.tether_index[0])
        texts = "Tether Index : " + str(Application.tether_index[0]) +"\nBinance(btc/usdt) :  " + str(round(Application.binance_price[0])) + "\nCoinabse(btc/usd) :  " + Application.coinbase_price[0] +  "\n" + "Coinbase Premium Index :  " + str(round(now, 2))
        self.lock.release()
        self.label.config(text=texts, font= '40')
        self.timer = self.after(1000, self.tiktok)





root = tkinter.Tk()
root.geometry("400x100+100+100")
app = Application(root)
app.mainloop()

