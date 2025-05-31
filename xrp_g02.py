#!/usr/bin/env python
# coding: utf-8


# file:a_xrp_graph.py
# hourly チャートを出力し
# a_xrp5min.xl# file:a_xrp_graph.py
#print('Start here')
# はじめに　hourly made の修正
# 次はrealtime の修正
#-------完成実行版 -----

###### 準備 ######
#-------- library　-----------
import python_bitbankcc
import pandas as pd
import json
import numpy as np
import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import pandas.tseries.offsets as offsets
import matplotlib.pyplot as plt
#%matplotlib inline

#---------- function -----------
# new、oldを一定時間進めて、出力はboolean
def statics(old,new):
    j=(df_t['date']>=old) & (df_t['date']<=new)
    return j

# get CandleStick return DF
def get_bitdata(start,end,pair,candle_type):
    #ライブラリ
    import python_bitbankcc
    import datetime
    import pandas as pd
    
    #パブリックAPIのオブジェクトを取得
    pub = python_bitbankcc.public()
    
    #引数を日付データに変換
    start_date = datetime.datetime.strptime(start,"%Y%m%d")
    end_date = datetime.datetime.strptime(end,"%Y%m%d")
    
    #日付の引き算
    span = end_date - start_date
    
    #データフレームの定義
    col = ["Open","High","Low","Close","Volume","Unix Time"]
    df_sum = pd.DataFrame(columns = col)
    
    
    #1日ごとに時間足データを取得し、結合していく
    for counter in range(span.days + 1):
        #日付の計算
        the_day = start_date + datetime.timedelta(days = counter)
        

        try:
            #パブリックAPIのインスタンス化
            value = pub.get_candlestick(pair, candle_type, the_day.strftime("%Y%m%d"))
            
            #データ部分の抽出
            ohlcv = value["candlestick"][0]['ohlcv']
            
                 
            #データの長さを取得
            length = len(value["candlestick"][0]['ohlcv'])

            #カラムの設定
            col = ["Open","High","Low","Close","Volume","Unix Time"]

            #データフレームに変換
            df = pd.DataFrame(ohlcv, columns = col)
                     
            for i in col:
                for j in range(length):
                    df.loc[j,i] =float(df.loc[j,i])
            
                     
            #df_sumに結合
            df_sum = pd.concat([df_sum, df])
            
        except:
            pass
        

    # No. index の解除
    df_sum = df_sum.reset_index()
    df = df_sum.drop(columns = "index")
    
    #UnixTimeから日付を計算
    date_and_time = []
    length = len(df)
    for counter in range(length):
        unix_time = df.at[counter,"Unix Time"]
        time_date = datetime.datetime.fromtimestamp(unix_time/1000)
        time = time_date.strftime("%Y-%m-%d-%H-%M")
        date_and_time.append(time)
        
    #日付の列を追加
    df["date"] = date_and_time
        
    return(df)
# ------- end function



# ------- Constant -------------
# Constant
patha = '/Users/suusan/Documents/MyPandas/'
pathb = '/Users/suusan/CloudStation/☆☆K_Trade/data/'

# 書出file
read_f = "a_xrp5min.xlsx"
write_f = "a_xrp5min.xlsx"
read_t = "a_x5min_test.xlsx"
write_f1 = "a_x5min_test.xlsx"

#read_of =
#write_f = "a_xrp5min.xlsx"
#write_f = "ave_xpr5min.xlsx"

# set reading  # fig to str #
start = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
end = date.today().strftime('%Y%m%d')

pair="xrp_jpy"
candle_type= "5min"
past_term =72#     =12*3=1.5時間 ：移動平均
fivemin= 5
nshort = 12#  1 hour
nlong = 72# 3 hour
#---------- end constants  

# ---------- create vacant df ---------
col=['Ave','Std','Max','Min','date']
df_record=pd.DataFrame(columns=col)
#---------- end vacant df 



###########################################
############### process starts ############
###########################################

# ---------- file reading  -------------
# 過去の蓄積データ :
read_of = pathb + "a_xrp5min.xlsx"
df_o =pd.read_excel(read_of)

# ------- get API candlestick ----------
# 新規　過去一時間以内
df_n = get_bitdata(start,end,pair,candle_type)


# ---------- file record 抽出　----------
#　過去分の最新date(最後のrec)チェック
prv_date =df_o.loc[len(df_o)-1,'date']

# 最新のうち、過去分に含まれるものを除外
df_append=df_n[df_n['date']>prv_date]

#df_oに df_appendを追加する 2021/07/04
df_out = pd.concat([df_o,df_append],ignore_index=True)

#numberingが初期化される
#df_out=df_out.reset_index()

# 不要なnumbering　columnsを削除
#df_out=df_out.drop(columns=['index','Unnamed: 0'])


# New 2021/07/02 7:35
df_out.to_excel(pathb+write_f,index=False)
#--end


df_t = df_out



new =df_t.loc[0,'date']
num =len(df_t)             # RECORD 数

# ----------- process past_term ---------
old=new

ii=0
# 一定の時間幅で  past_term = new - oldを変化させる
for ii in range(num): 
    if ii<past_term:
        old = datetime.strptime(new,'%Y-%m-%d-%H-%M')           #str to fig      
        old_n = datetime(old.year,old.month,old.day,old.hour,old.minute) - timedelta(minutes=ii*5)
        next_day = datetime(old.year,old.month,old.day,old.hour,old.minute) + timedelta(minutes=fivemin)           
        old = datetime.strftime(old_n,'%Y-%m-%d-%H-%M')         #fig to str          
        next_day = datetime.strftime(next_day,'%Y-%m-%d-%H-%M') #fir to str      
        
    
    else:
        old = datetime.strptime(new,'%Y-%m-%d-%H-%M')
        old_n = datetime(old.year,old.month,old.day,old.hour,old.minute) - timedelta(minutes=past_term*5)
        next_day = datetime(old.year,old.month,old.day,old.hour,old.minute) + timedelta(minutes=fivemin)
        old = datetime.strftime(old_n,'%Y-%m-%d-%H-%M')
        next_day = datetime.strftime(next_day,'%Y-%m-%d-%H-%M')


    # judge ***     
    df_tm=df_t[statics(old,new)]
    
    if ii==0:
        av=df_tm['Close'].mean()
        st=0
        mx=df_tm['Close'].max()
        mn=df_tm['Close'].min()
    else:
        av=df_tm['Close'].mean()
        st=df_tm['Close'].std()
        mx=df_tm['Close'].max()
        mn=df_tm['Close'].min()

    
    #col=['Ave','Std','Max','Min','date']
    df_tmp = pd.DataFrame({"Ave":[av],"Std":[st],"Max":[mx],"Min":[mn],"date":[new]})
    df_record=pd.concat([df_record,df_tmp])

    new=next_day

df_record_m = pd.merge(df_record,df_t,left_on="date",right_on="date",how='outer')

    

## -------- SMMA の作成 -----------
df_t = df_record_m

# ------------- create columns -----------
df_t['SMMA_S']  = df_t['Close'].rolling(2).mean()
df_t['SMMA_L']  = df_t['Close'].rolling(4).mean()
#  追加
df_t['Zu']  = df_t['Close'].rolling(5).mean()
df_t['Zd']  = df_t['Close'].rolling(5).mean()


# ------------- Delete No index ----------
df_smma = df_t.reset_index()
for index, row in df_smma.iterrows():
    
    df_smma.at[index, 'Zu'] = (df_smma.at[index, 'Max'] - df_smma.at[index, 'Ave'])/2 + df_smma.at[index, 'Ave']
    df_smma.at[index, 'Zd'] = (df_smma.at[index, 'Ave'] - df_smma.at[index, 'Min'])/2 + df_smma.at[index, 'Min']
   
    if index > nshort:
        df_smma.at[index, 'SMMA_S'] = (( nshort - 1 ) * df_smma.at[index-1, 'SMMA_S'] + df_smma.at[index, 'Close'])/nshort
    if index > nlong:
        df_smma.at[index, 'SMMA_L'] = (( nlong - 1 ) * df_smma.at[index-1, 'SMMA_L'] + df_smma.at[index, 'Close'])/nlong

df_smma=df_smma.drop(columns=['index'])
df_smma.to_excel(patha + 'ave_x5min.xlsx',index=False)



############# Genarate Graph ##############

df_t = pd.read_excel(patha + 'ave_x5min.xlsx')
length = len(df_t)
df_t = df_t.reset_index()
limitNo = length - 12*24*1    
df_t=df_t[df_t['index']>=limitNo]
#CP
df_t4 = df_t


#追加  文字から数字日付：Xが自動で調整される
for index,row in df_t.iterrows():
    dd = df_t.at[index,'date']
    df_t.at[index,'date'] = datetime.strptime(dd,"%Y-%m-%d-%H-%M")



#x = df_t.index
x = df_t['date']
y  = df_t['Close']
y2 = df_t['Max']
y21= df_t['Zu']
y22= df_t['Ave']
y23= df_t['Zd']

y3 = df_t['Min']
y4 = df_t['SMMA_S']
y5 = df_t['SMMA_L']

plt.figure(figsize=(30,15))
plt.plot(x,y2,label='max',color='b',linewidth=3)

plt.plot(x,y21,label='Zu',color='b',linewidth=0.5)
plt.plot(x,y22,label='Ave',color='k',linewidth=1)
plt.plot(x,y23,label='Zd',color='b',linewidth=0.5)

plt.plot(x,y3,label='min',color='b',linewidth=3)
plt.plot(x,y4,label='smma_s',color='g',linewidth=5)
plt.plot(x,y5,label='smma_l',color='tan',linewidth=5)

plt.plot(x,y,label='close',color='r',linewidth=3,linestyle='solid')


plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.xlabel('Date',fontsize=30,color='r')
plt.ylabel('Price',fontsize=30,color='r')
plt.grid(axis='y')
plt.title('XRP',fontsize=30)
plt.legend('XRP',fontsize=30)

now = datetime.now()
####------- 修正--------####
filename = '/Users/suusan/Documents/Python_cron/a_xrp5mn'+ now.strftime('%m%d%H') + '.jpg'
plt.savefig(filename)
#plt.show()

today = datetime.today().strftime('%Y%m%d-%H:%M')
print(today)

