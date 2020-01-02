import ccxt
import pandas as pd
import numpy as np 
import tulipy as ti
import feather
import os
import datetime
from os import path
from flask import Flask, render_template, request, url_for, redirect
import json
from loguru import logger
from tinydb import TinyDB, Query
import hashlib

db = TinyDB('db.json')
User = Query()

app = Flask(__name__)

cur = datetime.datetime.now()
cur = cur.strftime("%d%H%M") #to generate folder name
base_path = "/Users/tharifansari/desktop/web-mini/feather_file" #base path
ohlcv_data1={}
ohlcv_data2={}
input_coin_pair=[]
exch = getattr (ccxt, 'binance') () # instantiate
exch.load_markets()# preload all symbols for this exchange
ls,ls1 = [],[]
ls_all = exch.symbols
for i in ls_all:
    #ls = re.findall("./[A-Z]*", str(exchange.symbols))
    ls.append(i.split('/')[0])
    ls1.append(i.split('/')[1])
ls=list(set(ls))
ls1=list(set(ls1))

def calculate_financial_technical_data(comparision_type,comparision_value):
    logger.debug(comparision_value)
    data_list = []
    fin_res=[]
    for i in ohlcv_data2.keys():
        data_list.append(ohlcv_data2[i][str(comparision_value)])
    logger.debug(data_list)
    if comparision_type == 'sma':
        data = ( ti.sma(np.asarray(data_list), period=10) )
        return data
    elif comparision_type is 'stddev':
        #dataaa = ( ti.stddev(np.asarray(data_list), period=5) )
        #logger.debug(dataaa)
        #data = dataaa.tolist()
        fin_res = ti.stddev(np.asarray(data_list), period=5).tolist() 
        return fin_res
    elif comparision_type is 'wma':
        data = ( ti.wma(np.asarray(data_list), period=5) )
        return data
    elif comparision_type is 'zlema':
        data = ( ti.zlema(np.asarray(data_list), period=5) )
        return data

class Featherdb:

    def __init__(self):
        """ this is the init method which takes in basepath. """
        self.base_path = base_path
        self.feather_name = "/df.feather"

    def write_into_featherfile(self, dataframe, symbol, data_type):
        """Takes dataframe, symbol and datatype , check if the file exists in the dir
         If not make the dir and write the feather file in."""
        paath = path.join(self.base_path, cur, symbol, data_type)
        if not os.path.exists(paath):
            os.makedirs(paath)
            feather.write_dataframe(dataframe, paath+self.feather_name)
        else:
            pass

    def read_from_featherfile(self, symbol, data_type):
        """Checks whether the file exists or not
        If yes, the data frame will be returned from the feather file"""
        paath = path.join(self.base_path, cur, symbol, data_type)
        if os.path.exists(paath):
            return ( pd.read_feather( paath + self.feather_name))
        else:
            pass


class Fetch:

    def __init__(self,exchange_name ,symbol, time_stamp):
        """this metthod takes exchange name, symbol and the time stamp for which the data is needed"""
        self.exchange_name = exchange_name
        self.symbol = symbol
        self.time_stamp = time_stamp
        self.exchange = getattr(ccxt, self.exchange_name)()
        self.exchange.load_markets()
        self.data_frame = pd.DataFrame(self.exchange.fetch_ohlcv(symbol, time_stamp))

    def store_data(self,data_type):
        """takes what type of data has to be stored """
        self.feather_db_object = Featherdb()
        self.feather_db_object.write_into_featherfile(self.data_frame, self.symbol, data_type)

    def read_data(self,data_type):
        """Returns the dataframe of the requested data_type"""
        return(self.feather_db_object.read_from_featherfile(self.symbol,data_type))

    def all_symbols(self):
        return self.exchange.symbols()




@app.route('/financial_technical_analysis', methods=["POST","GET"])
def financial_technical_analysis():
    comparision_type = str(request.form.get('comparision'))
    comparision_value = str(request.form.get('comparision_data'))

    data_list = []

    for i in ohlcv_data2.keys():
        data_list.append(ohlcv_data2[i][str(comparision_value)])
    if comparision_type == 'sma':
        res = ( ti.sma(np.asarray(data_list), period=20) ).tolist()
        print(res[-1])
        return render_template('binance_tech_analysis_result.html', res = res[-1],comparision_type="Simple Moving Average",comparision_value=comparision_value.upper())
    elif comparision_type == 'stddev':
        res = ti.stddev(np.asarray(data_list), period=20).tolist()
        print(res[-1])
        return render_template('binance_tech_analysis_result.html', res = res[-1],comparision_type="Standard Deviation",comparision_value=comparision_value.upper())
    elif comparision_type == 'wma':
        res = ( ti.wma(np.asarray(data_list), period=20) ).tolist()
        return render_template('binance_tech_analysis_result.html', res = res[-1],comparision_type="Weighted Moving Average",comparision_value=comparision_value.upper())
    elif comparision_type == 'zlema':
        res = ( ti.zlema(np.asarray(data_list), period=20) ).tolist()
        return render_template('binance_tech_analysis_result.html', res = res[-1],comparision_type="Zero-Lag exponential moving average" ,comparision_value=comparision_value.upper())
    

@app.route('/percentage', methods=["POST","GET"])
def percentage():
    """ this is to take percentage as input and calculate the open vs close , open vs high and 
        open vs low for 2 coin pairs """
    if request.method == "GET":
        return render_template('binance_percentage.html')
    else:
        """PAIR 1"""
        open_list,close_list,high_list,low_list=[],[],[],[]
        for i in ohlcv_data1.keys():
            open_list.append({i:ohlcv_data1[i]['open']})
            close_list.append({i:ohlcv_data1[i]['close']})
            high_list.append({i:ohlcv_data1[i]['high']})
            low_list.append({i:ohlcv_data1[i]['low']})
        percentage = request.form.get('percentage')
        comp = request.form.get('comparision')
        result={ 'open_vs_high':{},'open_vs_close':{}, 'open_vs_low':{}  }
        if comp == "OH":
            for i in range(len(open_list)):
                for key in open_list[i].keys():
                    if high_list[i][key] > (open_list[i][key]*(1+(float(percentage)/100))):
                        result['open_vs_high'][key]={open_list[i][key] : high_list[i][key]}
            #return render_template('result.html',result=result,comp=comp)
        elif comp == "OC":
            for i in range(len(open_list)):
                for key in open_list[i].keys():
                    if close_list[i][key] > (open_list[i][key]*(1+(float(percentage)/100))):
                        result['open_vs_close'][key]={open_list[i][key] : close_list[i][key]}
            #return render_template('result.html',result=result,comp=comp)
        elif comp == "OL":
            for i in range(len(open_list)):
                for key in open_list[i].keys():
                    if low_list[i][key] > (open_list[i][key]*(1+(float(percentage)/100))):
                        result['open_vs_low'][key]={open_list[i][key] : low_list[i][key]}
            #return render_template('result.html',result=result,comp=comp)


        """PAIR 2"""
        open_list,close_list,high_list,low_list=[],[],[],[]
        for i in ohlcv_data2.keys():
            open_list.append({i:ohlcv_data2[i]['open']})
            close_list.append({i:ohlcv_data2[i]['close']})
            high_list.append({i:ohlcv_data2[i]['high']})
            low_list.append({i:ohlcv_data2[i]['low']})
        result1={ 'open_vs_high':{},'open_vs_close':{}, 'open_vs_low':{}  }
        if comp == "OH":
            for i in range(len(open_list)):
                for key in open_list[i].keys():
                    if high_list[i][key] > (open_list[i][key]*(1+(float(percentage)/100))):
                        result1['open_vs_high'][key]={open_list[i][key] : high_list[i][key]}
            #return render_template('result.html',result=result,comp=comp)
        elif comp == "OC":
            for i in range(len(open_list)):
                for key in open_list[i].keys():
                    if close_list[i][key] > (open_list[i][key]*(1+(float(percentage)/100))):
                        result1['open_vs_close'][key]={open_list[i][key] : close_list[i][key]}
            #return render_template('result.html',result=result,comp=comp)
        elif comp == "OL":
            for i in range(len(open_list)):
                for key in open_list[i].keys():
                    if low_list[i][key] > (open_list[i][key]*(1+(float(percentage)/100))):
                        result['open_vs_low'][key]={open_list[i][key] : low_list[i][key]}
            #return render_template('result.html',result=result,comp=comp)
        comp_dict={'OH':'open_vs_high','OC':'open_vs_close','OL':'open_vs_low'}
        return render_template('result.html',result=result,result1=result,comp_dict=comp_dict,comp=comp,input_coin_pair=input_coin_pair)


@app.route('/selection', methods=["POST","GET"])
def selection():
    if request.method == "GET":
        return render_template("binance_selection.html")
    else:
        selection_value = int(request.form.get('selection'))
        if selection_value == 1:
            return render_template('binance_percentage.html')
        elif selection_value == 2:
            return render_template('binance_financial_technical_analysis.html')


@app.route('/after_login', methods=["POST","GET"])
def after_login():
    '''this method is used to get the first part of the coin pair for 2 different coins pairs'''
    if request.method == "GET":
        return render_template("binance.html",ls=ls,ls1=ls1)
    else:
        str1 = str(request.form.get('coin_1_1'))+'/'+str(request.form.get('coin_1_2'))
        str2 = str(request.form.get('coin_2_1'))+'/'+str(request.form.get('coin_2_2'))
        input_coin_pair.append(str1)
        input_coin_pair.append(str2)
        print(str1)
        print(str2)
        if str1 in ls_all and str2 in ls_all:
            fetch1 = Fetch('binance',str1,'1h')
            fetch1.store_data('ohlcv')
            data_frame1 = fetch1.read_data('ohlcv')
            data_frame1.columns=['timestamp','open','high','low','c','value']
            #print( ti.sma(data_frame1['open'].to_numpy(), period=5) )
            for i in range(data_frame1.shape[0]):
                    ohlcv_data1[str(data_frame1.loc[i,'timestamp'])]={'timestamp':str(data_frame1.loc[i,'timestamp']),'open':data_frame1.loc[i,'open'],'high':data_frame1.loc[i,'high'],'low':data_frame1.loc[i,'low'],'close':data_frame1.loc[i,'c'],'value':data_frame1.loc[i,'value']}
            """2ND PAIR"""

            fetch2 = Fetch('binance',str2,'1h')
            fetch2.store_data('ohlcv')
            data_frame2 = fetch2.read_data('ohlcv')
            data_frame2.columns=['timestamp','open','high','low','c','value']
            for i in range(data_frame2.shape[0]):
                    ohlcv_data2[str(data_frame2.loc[i,'timestamp'])]={'timestamp':str(data_frame2.loc[i,'timestamp']),'open':data_frame2.loc[i,'open'],'high':data_frame2.loc[i,'high'],'low':data_frame2.loc[i,'low'],'close':data_frame2.loc[i,'c'],'value':data_frame2.loc[i,'value']}
            return render_template('binance_selection.html')
        else:
            return "PLEASE ENTER A VALID PAIR"

def make_md5_hash(user_entered_password):
    result = hashlib.md5(user_entered_password.encode()) 
    password_hash = result.hexdigest()
    return password_hash


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/sign_up')
def sign_up():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    search_result = db.search(User.username == username)
    if len(search_result) != 0:
        return 'username already exists.'
    else:   
        password_hash = make_md5_hash(password)
        user_pass_dict = {'username':username, 'password':password_hash, 'email':email}
        db.insert(user_pass_dict)
        return redirect(url_for('home'))


@app.route('/check_login', methods=['POST'])
def check_login():
    username = request.form.get('username')
    password = request.form.get('password')
    search_result = db.search(User.username == username)
    if len(search_result) == 0:
        return 'incorrect username.'
    else:
        correct_password_hash = search_result[0]['password']
        user_entered_password_hash = make_md5_hash(password)

        if user_entered_password_hash == correct_password_hash:
            return render_template("binance.html",ls=ls,ls1=ls1)
        else:
            return 'Wrong password.'

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'GET':
        return render_template('change_password.html')
    else:
        username = request.form.get('username')
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        search_result = db.search(User.username == username)
        if len(search_result) == 0:
            return 'incorrect username.'
        else:
            old_password_hash = make_md5_hash(old_password)
            correct_password_hash = search_result[0]['password']
            if old_password_hash == correct_password_hash:
 
                result = db.update({
                    'password': make_md5_hash(new_password)}, 
                    User.username == username
                    )
                print(result)
                return redirect(url_for('home'))
            else:
                return 'wrong password.'


if __name__ == '__main__':
    app.run(debug=True)


#    8547378044