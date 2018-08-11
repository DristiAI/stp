"""

Gets sp500 meta data 

At time I am using just the ticker :GOOG

"""



import pandas as pd
import pandas_datareader.data as web_reader
import wikipedia as W
import os
import json
import requests
import time
import re
import numpy as np



class DataObject():


    def __init__(self,wiki_title,start_date=0,end_date=None,sp500=False):
        self.wiki_title = wiki_title
        self.start = start_date
        self.end = end_date
        self.sp500 =False


    def get_data(self,ticker='GOOG',sp500=False):

        
        if sp500:
            if os.path.exists('sp500.csv'):
                ticker = pd.read_csv('sp500.csv')['Ticker symbol']
            else:
                html = W.page(title = self.wiki_title)
                html_ = html.html().encode('utf-8') 
                table = pd.read_html(html_)[0]
                ticker = self.clean_wiki(table,save=True)
                print('Stored data in sp500.csv')
            stock_data=self.get_stocks(ticker,islist=True)
            return stock_data



        #implemented only for one ticker at time
        stock_data = self.get_stocks(ticker,islist=False)

        
        return stock_data


    def clean_wiki(self,table,columns = None,
                    save=True,sp_500=True):

        """

        cleans the wiki table &
        stores the ticker to company mapping 

        returns :a dataframe with three meta columns
        column1 : ticker(categorical)
        column2 : GICS Sector(categorical)
        column3 : founded on(year)

        if required can be tweaked for extra features

        """
        if columns is None:
            columns = [0,3,8]
        req_table = table.loc[:,columns]
        
        if self.sp500:
            tickers= table[0][1:]
            company_name = table[1][1:]

        if save:
            if tickers is not None:
                mapping = dict(zip(tickers,company_name))
                f = open('mappings','w')
                d = json.dumps(mapping)
                f.write(d)
                f.close()
        req_table.to_csv('sp500.csv',header=None,index=False)
        return req_table['Ticker symbol']


    def get_stocks(self,ticker,islist=False):

        """
        get stock data of any ticker 
        also ,if required it can be iterated 
        over sp500 tickers to get the historical data
        of sp500 tickers
        
        """

        stock_df = self.get_ticker_data(ticker)

        if islist:

            raise Exception('!!!!!!!!Not Implemented yet !!!!!!!!')

        return stock_df

        
    def get_ticker_data(self,ticker):

        """
        reference:

        https://stackoverflow.com/a/46894740/8044314


        returns: the dataframe of arguament ticker 

        """

        res = requests.get('https://finance.yahoo.com/quote/' + ticker + '/history')
        yahoo_cookie = res.cookies['B']
        yahoo_crumb = None
        pattern = re.compile(r'.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')
        for line in res.text.splitlines():
            m = pattern.match(line)
            if m is not None:
                yahoo_crumb = m.groupdict()['crumb']
        cookie_tuple = yahoo_cookie, yahoo_crumb

        url_kwargs = {'symbol': ticker, 'timestamp_end': self.end,
            'crumb': cookie_tuple[1]}
        url_price = 'https://query1.finance.yahoo.com/v7/finance/download/' \
                    '{symbol}?period1=0&period2={timestamp_end}&interval=1d&events=history' \
                    '&crumb={crumb}'.format(**url_kwargs)


        response = requests.get(url_price, cookies={'B': cookie_tuple[0]})
        with open ('history.csv', 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return pd.read_csv('history.csv')
    
    def create_dataset(self,df):
        df_ = df.shift(-1)
        target = df_['Close']
        columns = ['Open','High','Low','Volume']
        #df_r = 
        return df.loc[:,columns],target

    def preprocess_data(self,df,target):
        train,val,test= df.iloc[:2800,:],df.iloc[2800:3300,:],df.iloc[3300:,:]
        train_y,val_y,test_y = target[:2800],target[2800:3300],target[3300:]
        train_max = np.max(train,axis=0)
        train/=train_max
        val/=train_max
        test/=train_max
        train_y_max= np.max(train_y)
        train_y /=train_y_max
        val_y /= train_y_max
        test_y/= train_y_max
        args = (train_max,train_y_max)
        return (train,train_y),(val,val_y),(test,test_y) ,args
    def reshape(self,*args):
        train_x,val_x,test_x = args
        train_x = train_x.values.reshape(-1,1,4)
        val_x= val_x.values.reshape(-1,1,4)
        test_x = test_x.values.reshape(-1,1,4)
        return train_x,val_x,test_x
    



if __name__ == '__main__':

    data = DataObject('List of S&P 500 companies',end_date=int(time.time()))
    df = data.get_data()
    df.to_csv('stock_history.csv',index=False)