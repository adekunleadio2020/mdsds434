import pandas as pd
import yfinance as yf
import datetime
import time
import requests
import io
import sys

def download(name):
    today = datetime.datetime.today()
    start = datetime.datetime(2020,1,1)
    end = datetime.datetime(today.year,today.month,today.day)

    Symbols = []
    Symbols.append(name)
    

    # create empty dataframe
    stock_final = pd.DataFrame()
    # iterate over each symbol
    for i in Symbols:  
    
    # print the symbol which is being downloaded
    #print(str(Symbols.index(i)) + str(' : ') + i, sep=',', end=',', flush=True)  
    
        try:
        # download the stock price 
            stock = []
            stock = yf.download(i,start=start, end=end, progress=False)
            
            # append the individual stock prices 
            if len(stock) == 0:
                None
            else:
                stock['Name']=i
                stock_final = stock_final.append(stock,sort=False)
        except Exception:
            None

    return stock_final

print("Hi")
stock_final=download(sys.argv[2])
print(stock_final.head())
stock_final.to_csv('gs://{}/data_files/stocks.csv'.format(sys.argv[1]))

#var = 1
#var = var
