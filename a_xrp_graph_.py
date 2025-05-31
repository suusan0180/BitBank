# EXEC Version
# file:a_xrp_graph.py ver 1.06 Tested 2021/09/26 15:45
# 
#-------完成実行版 -----

## ############################ ##
## -------- PREparation ------- ##
## ############################ ##

## --------- TEST setting --------- ##
#cond_TEST = True
## file write 
## -------------------------------- ##
cond_TEST = False
## -------- End TEST setting ------ ##

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
pathb = '/Users/suusan/CloudStation/☆☆K_Trade/DCR_data/' #2022/05/10

# file name
#main = "a_xrp5min.xlsx"
#test = "a_xrp5min_.xlsx"
#ANA  = "ave_x5min.xlsx"
#test = "ave_x5min_.xlsx"


# set reading  # fig to str #
start = (date.today()-timedelta(days=1)).strftime('%Y%m%d')
end = date.today().strftime('%Y%m%d')

pair="xrp_jpy"
candle_type= "5min"
past_term =72#     =12*6=6時間 ：移動平均
fivemin= 5
nshort = 12#  1 hour
nlong =  72#  6 hour
rsi_ln = 14
#---------- end constants  

## ############################## ##
## -------- Input Section ------- ##
## ############################## ##

# ---------- file reading  -------------
# 過去の蓄積データ :
df_o =pd.read_excel(pathb + "a_xrp5min.xlsx")

# ------- get API candlestick ----------
# 新規　過去一時間(start, end)
df_n = get_bitdata(start,end,pair,candle_type)


### #################################### ####
### ------------ process starts -------- ####
### #################################### ####


# ---------- file record 抽出　----------
# 過去分の最新date(最後のrec)チェック
prv_date =df_o.loc[len(df_o)-1,'date']

# API dataのうち、過去分に含まれるものを除外
df_append=df_n[df_n['date']>prv_date]

 #df_outに df_appendを追加する 2021/07/04
df_out = pd.concat([df_o,df_append],ignore_index=True)

if cond_TEST: # File 出力　FileSave secでは内容が変わる
    df_out.to_excel(pathb + "a_xrp5min_.xlsx" ,index=False)
else:
    df_out.to_excel(pathb + "a_xrp5min.xlsx", index=False)


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


    # *** judge ***     
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


    df_t.loc[ii,'Ave'],df_t.loc[ii,'Std'],df_t.loc[ii,'Max'],df_t.loc[ii,'Min']=av,st,mx,mn
    new=next_day


## -------- SMMA の作成 -----------

# ------------- create columns -----------
df_t['SMMA_S']  = df_t['Close'].rolling(2).mean()
df_t['SMMA_L']  = df_t['Close'].rolling(4).mean()
df_t['Zu']  = df_t['Close'].rolling(5).mean()
df_t['Zd']  = df_t['Close'].rolling(5).mean()



df_t = df_t.reset_index()
for index, row in df_t.iterrows():
    
    df_t.at[index, 'Zu'] = (df_t.at[index, 'Max'] - df_t.at[index, 'Ave'])/2 + df_t.at[index, 'Ave']
    df_t.at[index, 'Zd'] = (df_t.at[index, 'Ave'] - df_t.at[index, 'Min'])/2 + df_t.at[index, 'Min']
   
    if index > nshort:
        df_t.at[index, 'SMMA_S'] = (( nshort - 1 ) * df_t.at[index-1, 'SMMA_S'] + df_t.at[index, 'Close'])/nshort
    if index > nlong:
        df_t.at[index, 'SMMA_L'] = (( nlong - 1 ) * df_t.at[index-1, 'SMMA_L'] + df_t.at[index, 'Close'])/nlong

df_t=df_t.drop(columns=['index'])

##  ------- RSI ---------
#df_rsi=df_t
diff=df_t['Close'].diff()
diff_data = diff[1:]
#diff_data
up,down = diff_data.copy(),diff_data.copy()
up[up<0],down[down>0]=0,0

up_sma=up.rolling(window=rsi_ln,center=False).mean()
down_sma=down.abs().rolling(window=rsi_ln,center=False).mean()

RS =up_sma/down_sma
RSI = 100.0 - (100.0/(1.0+RS))
df_t['rsi']= RSI
#df_t



### ### ----------------------------- ### ###
### ###       SAVE FILE ZONE 1/1      ### ###
### ### ----------------------------- ### ###


# TEST 2021/09/25
if cond_TEST:
    df_t.to_excel(patha + 'ave_x5min_.xlsx',index=False)
else:
    df_t.to_excel(patha + 'ave_x5min.xlsx',index=False)


    
### ### ----------------------------- ### ###
### ###         Genarate Graph        ### ###
### ### ----------------------------- ### ###

length = len(df_t)
df_t = df_t.reset_index()
limitNo = length - 12*24*1    
df_t=df_t[df_t['index']>=limitNo]


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

