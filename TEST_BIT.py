## 実稼働版EXEC 版 　Checked #2025/05/18 16:00
# 'BitBank.py' ver 04.72

# btc 'qb qs','ib is'統合,btcもテスト対応
# TEST 'go' 'qb/qs' 'ib/is' ok 'db/ds'詳細にチェックすべし
# 内部にメモリが残るので　"BitBank.py"でやるべき
#ver 04.68 ; date = 'a',B_status.XL変更時にlog出力
#ver 04.67  ;　vol_balを次のplanに追加line:1058
#ver 04.66 go では残高あるときは買わない  を追加
# XRP: Manu ; go, stop, qb, qs, ib, is , 
# BTC: Manu ; q(b,s), i(b,s) 今回　　db,dsおよび連続処理
# db date='a', u/d_price(実額または%), prevP 現在水準, vol_trn, dsはvol_bal
# db,ds 修正入れるときはdateに'a'を入れる
# pathb変更

###########      現 状　     ############
# vol_bal vol_trnに分け、　vol_balはAPIから入手
# vol_trnはSEL BUYともstatus.volに入力
# Bpは平均単価を手入力するか最後に買った金額を引き継ぐ
########### vol_bal vol_trn ############


# 実行前確認
# 1. 必ずcond_TEST = True を #Off
# 2. 必ずcond_TEST = False を #ON

PrRange = 92 #2022/01/21 12:10from iPad
C_LCr = 0.95 #2022/01/21

## ***************************************** ##
## ---------   　  TEST MODE      ---------- ##
## ---------   cond_TEST = True   ---------- ##
## ***************************************** ##
cond_TEST = True# <------- Test時のみ有効
newP_t_xrp = 89.25 # <------- Test時のみ有効
newP_t_btc = 4600500 # <--- Test時のみ有効

## ****************************************** ##
## -------    　EXECUTIVE MODE　   ---------- ##
## -------   　cond_TEST = False   ---------- ##
## ****************************************** ##
#cond_TEST = False # Exec時はFalse        ###
## -------  TEST setting END   --------- ###

### ### ------------------------------- ### ###
### ###   　　　PREparation area         ### ###
### ### ------------------------------- ### ###

# ---------    library   -----------
import python_bitbankcc
import pandas as pd
import numpy as np
import json
import datetime
import talib as ta
from datetime import datetime
from datetime import date
from datetime import timedelta
import pandas.tseries.offsets as offsets
#           Library End


# --------- API public -------------
class BitBankPubAPI:
    def __init__(self):
        self.pub = python_bitbankcc.public()
        
    def get_ticker(self, pair):
        try:
            value = self.pub.get_ticker(pair)
            return value
        except Exception as e:
            print(e)
            return None

# ---------- API Private ------------
import key
API_KEY = key.set_API_key()
API_SECRET = key.set_Secret_key()
prv = python_bitbankcc.private(API_KEY, API_SECRET)

#------------ functions -------------
#-- SELL process -----
def exe_sell_l(newP,volume):
    pair ='xrp_jpy'
    price = str(newP)
    amount = str(volume)
    side = 'sell'
    order_type = 'limit'#指値
    prv.order(pair, price, amount, side, order_type)
    return

def exe_sellm(newP,volume):
    pair ='xrp_jpy'
    price = str(newP)
    amount = str(volume)
    side = 'sell'
    order_type = 'market'#成行
    prv.order(pair, price, amount, side, order_type)
    return

#-- BUY process -----
def exe_buyl(newP,volume):
    pair ='xrp_jpy'
    price = str(newP)
    amount = str(volume)
    side = 'buy'
    order_type ='limit'
    prv.order(pair, price, amount, side, order_type)
    return

def exe_buym(newP,volume):
    pair ='xrp_jpy'
    price = str(newP)
    amount = str(volume)
    side = 'buy'
    order_type ='market'
    prv.order(pair, price, amount, side, order_type)
    return

# -- DataFrame extract ----         
# new、old範囲を抽出、出力はboolean
def statics(old,new):
    j=(df_smma['date']>=old) & (df_smma['date']<=new)
    return j
#         functions end 


#---------- Operational Constants　-----------
C_profR = 0.02 #  = Mxprof/Bp
#C_LCr = 0.90 #2021/12/30
C_volume = 1
C_short =60
C_long =120

C_Pr_h = 0.05 #Edit2021/11/22
C_Pr_m = 0.025
C_Pr_l = 0.02
C_SPr_h = 0.9
C_SPr_m = 0.5
C_SPr_l = 0.5

past_term =72#     =12*6=6時間 ：移動平均
fivemin= 5
nshort = 12#  1 hour
nlong = 72#   6 hour
rsi_ln = 14

macd_fp = 12
macd_sp = 26
macd_sgnl = 9

# ----------- Fixed Constants -------------
patha = '/Users/suusan/Documents/MyPandas/'
pathb = '/Users/suusan/SynologyDrive/Drive/☆☆K_Trade/DCR_data/'


## ---------- Initialize -----------------2022/03/13
# ---- Initialize : set var ZERO ----
Bp,d_price,prevP,u_price,vol_bal,vol_trn,prev_low,prev_hi,newP = 0,0,0,0,0,0,0,0,0
Manu = ''
date = ''
CHK = False     #Flag: d/u price seq, %d/u price, set dif_d/u,
Con_to = False  #Flag:update "B_status.xslx"

# ---- initialize : Set SELL BUY to False
Scon5 = False # ds;difference sell
Scon6 = False # qs;quick sell, is;indicate sell  
SELL  = False
Bcon5 = False # db;difference buy
Bcon6 = False # qb;Quick Buy, ib;Indicate Buy
BUY = False



## ------  変更　2022/03/13 -------------

## ### ## -------------------------------- ##### ## ##
## ### ##       INPUT:FILE READING         ##### ## ##
## ### ## -------------------------------- ##### ## ##

##------ Read 'ave_x5min.xl'file
df_smma = pd.read_excel(patha + "ave_x5min.xlsx")
ln_smma=len(df_smma)

##------ Read 'BitBank.XL'file
DF = pd.read_excel(patha +'BitBank.xlsx')

##------ Read 'BB_status.XL'　& 'BB_statuslog.XL'file
if cond_TEST:
    df_status = pd.read_excel(patha + "BB_status_.xlsx")
    df_statuslog = pd.read_excel(patha + "BB_statuslog_.xlsx")
else:    
    df_status = pd.read_excel(patha + "BB_status.xlsx")
    df_statuslog = pd.read_excel(patha + "BB_statuslog.xlsx")

col = list(df_status.columns)
df = pd.DataFrame([],columns = col)# use SELL BUY to delete line from BB_status.xlsx


# ---------- set BB_status to vars ----------2022/03/13
df_status["vol_bal"]=df_status["vol_bal"].astype(float) #20220220 type指定

date = df_status.loc[0,'date']     #1:date of update
Bp = df_status.loc[0,'Bp']         #2:price of Bought
Bdate = df_status.loc[0,'Bdate']   #3:date of Bought
#volume = df_status.loc[0,'volume'] #4:volume of Bought 20220127
Pdate = df_status.loc[0,'Pdate']   #5:date of past max profit
profP = df_status.loc[0,'profP']   #6:price of past max profit
LCp = df_status.loc[0,'LCp']       #7:Loss Cut price
LCr = df_status.loc[0,'LCr']       #8:Loss Cut price rate
SPr = df_status.loc[0,'SPr']       #9:Shrink Profit rate
prevP = df_status.loc[0,'prevP']   #10:every time previous price
old_prevP = prevP # 'db'で使う
Sdate = df_status.loc[0,'Sdate']   #11:date of sell
zone = df_status.loc[0,'zone']     #12:every time zone
Hzone = df_status.loc[0,'Hzone']   #13:zone at Highest 2021/07/07 Name Changed
Manu = df_status.loc[0,'Manu']     #14:Manual execution
Auto = df_status.loc[0,'Auto']     #15:Auto operation
Prof = df_status.loc[0,'Prof']     #16:Prof = newP - Bp - comm
d_price = df_status.loc[0,'d_price'].astype(float)   #17:price indication
u_price = df_status.loc[0,'u_price'].astype(float)   #18:price indication
Date = df_status.loc[0,'Date']     #19:price indication
rsi = df_status.loc[0,'rsi']       #20:price indication
macd = df_status.loc[0,'macd']     #21:macd
macdsignal = df_status.loc[0,'macdsignal']   #22:macdsignal
macdhist = df_status.loc[0,'macdhist']   #23:macdhistry
vol_bal = df_status.loc[0,'vol_bal']#24:volume_balance
if Manu == 'go':
    vol_trn = C_volume
else:
    vol_trn =  df_status.loc[0,'vol_trn']#25:volume transaction
prev_low = df_status.loc[0,'prev_low']#26:lowest_price
prev_hi = df_status.loc[0,'prev_hi']#27:highest_price

# 27 pieces 2022/03/13



## ### ## -------------------------------- ##### ## ##
## ### ##       INPUT:API READING          ##### ## ##
## ### ## -------------------------------- ##### ## ##

#------ get ticker_API to df_thistime
pub = BitBankPubAPI()
ticker = pub.get_ticker('xrp_jpy')
df_thistime= pd.DataFrame([ticker])

colist=['sell', 'buy', 'open', 'high', 'low', 'last', 'vol']
for i in colist:
    df_thistime.loc[0,i] =float(df_thistime.loc[0,i])



#------ set var from API <new price>
# ----- TEST environment Process ----
if cond_TEST:
    newP = newP_t_xrp
    df_thistime.loc[0,'last']=newP_t_xrp
else:
    newP = df_thistime.loc[0,'last']
    
# ----- alternative
##########################################
### ####                          #### ###        
### ####  BitBank Process Starts  #### ###
### ####                          #### ### 
##########################################
today = datetime.today().strftime('%Y-%m-%d-%H-%M')

## -------- edit to time_val ;str
time_val = df_thistime.loc[0,'timestamp']#fig
time_val = datetime.fromtimestamp(time_val/1000)#fig
time_val = datetime.strftime(time_val,'%Y-%m-%d-%H-%M')#str

## -------- round 5min process
## BitBank の保存するdataは実時間、5分足のロウソク足データは
## きっかり５分刻み、datetime_indexで使うために５分で丸める

## --------- DataFrame  準備 -----
df_t01 = pd.DataFrame([],columns=['date','date_t','chk'])
df_date= pd.DataFrame([],columns=['date'])

## -------- import data --------   
date01=time_val#str

tonow = datetime.strptime(date01,'%Y-%m-%d-%H-%M')#str>Fig
tonow_t = datetime(tonow.year,tonow.month,tonow.day,tonow.hour,0)#Fig
    
    # --- 5分刻み基本時間登録(0,5,10,,,50,55)
for ia in range(14):
    if ia > 0:
        tonow_t = tonow_t+timedelta(minutes=5)#Fig
    df_date.loc[ia,'date']=tonow_t#Fig

    # --- 丸め行為
for ib in range(13):
    jikan = df_date.loc[ib,'date']#Fig
    before = jikan -timedelta(minutes=3)#Fig
    after = jikan +timedelta(minutes=2)#Fig
    if (before < tonow) & (tonow <= after):
        df_t01.loc[0,'date'] = tonow#Fig
        df_t01.loc[0,'date_t'] = df_date.loc[ib,'date']#Fig
        time_val = df_date.loc[ib,'date']

time_val = time_val.strftime('%Y-%m-%d-%H-%M')#Fig > Str
# ------ end round 5min

df_thistime['date']=time_val#Str


# ------ Concat DF & df_thistime
DF = pd.concat([DF,df_thistime],ignore_index=True)# 2021/07/06edit 
DF = DF.loc[:,'sell':'date']

### ### ----------------------------- ### ###
### ###       SAVE FILE ZONE 1/3      ### ###
### ### ----------------------------- ### ###

# ------ Save updated record
if cond_TEST:
    DF.to_excel(patha + 'BitBank_.xlsx',index=False)
else:
    DF.to_excel(patha + 'BitBank.xlsx',index=False)


#############################################
######### RealTime ANA process stars ########
#############################################


#------ last date of BitBank.XL ---
prv_date1 = DF.loc[len(DF)-1,'date']

#------ last date of ave_x5min.XL ---
prv_date2 = df_smma.loc[len(df_smma)-1,'date']

#------ prepare vacant 'df_smma_t1' --- 
col_sm=list(df_smma.columns)
df_smma_t1 = pd.DataFrame([],columns=col_sm)

#   -- DF抽出時　NumberIndex残存問題OK
DF = DF[DF['date'] > prv_date2]

DF = DF.reset_index()
DF = DF.loc[:,'sell':'date']#

ln=len(DF)#  date1 date2 の差分
for i in range(ln):
    df_smma_t1.loc[i,'date']=DF.loc[i,'date']
    df_smma_t1.loc[i,'Close']=DF.loc[i,'last']
    
#-------- BitBank 追加分をdf_smmaに加える    
df_smma = pd.concat([df_smma,df_smma_t1],ignore_index = True)
# 2021/09/26
df_smma = df_smma.loc[:,'Open':'rsi']# DEL unnamed col


# ------ 過去分の計算 <av,st,mx,mn>  -----
new =prv_date2# ave_x5minの最新date
num = len(df_smma[(df_smma['date']<=prv_date1)&(df_smma['date']>prv_date2)])#最大12個

ii=0
for ii in range(num):#12
    old = datetime.strptime(new,'%Y-%m-%d-%H-%M')
    old_n = datetime(old.year,old.month,old.day,old.hour,old.minute) - timedelta(minutes=past_term*5)
    
    next_day = datetime(old.year,old.month,old.day,old.hour,old.minute) + timedelta(minutes=fivemin)
    old = datetime.strftime(old_n,'%Y-%m-%d-%H-%M')
    next_day = datetime.strftime(next_day,'%Y-%m-%d-%H-%M')


    # judge ***     
    df_tm=df_smma[statics(old,new)]
    
    if ii==0:
        av=df_tm['Close'].mean()
        st=df_tm['Close'].std()
        mx=df_tm['Close'].max()
        mn=df_tm['Close'].min()
    else:
        av=df_tm['Close'].mean()
        st=df_tm['Close'].std()
        mx=df_tm['Close'].max()
        mn=df_tm['Close'].min()
        
 
    df_smma.loc[ln_smma+ii,'Ave'],df_smma.loc[ln_smma+ii,'Std'],df_smma.loc[ln_smma+ii,'Max'],df_smma.loc[ln_smma+ii,'Min']=av,st,mx,mn
    new = next_day

    
## -------- SMMA の作成 -----------
# df_smma['date'] のprv_date2位置の件数を代入
at_new = list(df_smma.loc[:,'date']).index(prv_date2)

lnt1=len(df_smma_t1)
for i in range(lnt1):
    df_smma.at[i + at_new+1, 'Zu'] = (df_smma.at[i + at_new+1, 'Max'] - df_smma.at[i + at_new+1, 'Ave'])/2 + df_smma.at[i + at_new+1, 'Ave']
    df_smma.at[i + at_new+1, 'Zd'] = (df_smma.at[i + at_new+1, 'Ave'] - df_smma.at[i + at_new+1, 'Min'])/2 + df_smma.at[i + at_new+1, 'Min']
    
    df_smma.at[i + at_new+1, 'SMMA_S'] = (( nshort - 1 ) * df_smma.at[i + at_new -1+1, 'SMMA_S'] + df_smma.at[i + at_new+1, 'Close'])/nshort
    df_smma.at[i + at_new+1, 'SMMA_L'] = (( nlong - 1 ) * df_smma.at[i + at_new -1+1, 'SMMA_L'] + df_smma.at[i + at_new+1, 'Close'])/nlong

##  ------- RSI ---------
#df_rsi=df_t
diff=df_smma['Close'].diff()
diff_data = diff[1:]
#diff_data
up,down = diff_data.copy(),diff_data.copy()
up[up<0],down[down>0]=0,0

up_sma=up.rolling(window=rsi_ln,center=False).mean()
down_sma=down.abs().rolling(window=rsi_ln,center=False).mean()

RS =up_sma/down_sma
RSI = 100.0 - (100.0/(1.0+RS))
df_smma['rsi']= RSI
#df_t

## -------- MACD -------
close = df_smma['Close']
df_smma['macd'],df_smma['macdsignal'],df_smma['macdhist']=ta.MACD(close,fastperiod=macd_fp,slowperiod=macd_sp,signalperiod=macd_sgnl)
df_smma['ta_RSI']=ta.RSI(close,timeperiod=rsi_ln)


### ### ----------------------------- ### ###
### ###        df_smma to status      ### ###
### ### ----------------------------- ### ###
ln_smma = len(df_smma)-1
Date = df_smma.loc[ln_smma,'date']
rsi = df_smma.loc[ln_smma,'rsi']
macd = df_smma.loc[ln_smma,'macd']
macdsignal = df_smma.loc[ln_smma,'macdsignal']
macdhist = df_smma.loc[ln_smma,'macdhist']


### ### ----------------------------- ### ###
### ###       SAVE FILE ZONE 2/3      ### ###
### ###      'ave_x5min_TBD.xlsx'     ### ###
### ### ----------------------------- ### ###
if cond_TEST:
    df_smma.to_excel(patha + 'ave_x5min_TBD_.xlsx',index=False)
else:
    df_smma.to_excel(patha + 'ave_x5min_TBD.xlsx',index=False)
   
    
## ###################################################
## ########### Auto Sell Process Starts ##############
## ###################################################

  
# --------- collect data for judgment ---------- 
thisP = newP - Bp# profit price
prevP = newP#      prevP is histrical record of newP
# thisP is profit but never used

# ----- set figs to vars --------
ln_smma = len(df_smma)
date=df_smma.at[ln_smma-1,'date']
mx=df_smma.at[ln_smma-1,'Max']
Zu=df_smma.at[ln_smma-1,'Zu']
ave=df_smma.at[ln_smma-1,'Ave']
Zd=df_smma.at[ln_smma-1,'Zd']
mn=df_smma.at[ln_smma-1,'Min']
    
# ---- cycle check -------            <---- TEST
smma1 = df_smma.at[ln_smma-1,'SMMA_S']
smma2 = df_smma.at[ln_smma-2,'SMMA_S']
smma3 = df_smma.at[ln_smma-3,'SMMA_S']

if (smma1 - smma2 > 0) and (smma2 - smma3 > 0):
    smmas_cyc = True
else:
    smmas_cyc = False


# -------　現在zone判断 ------
zone = 'none'
if newP >= mx:# to be cheked !!
    zone = 'mx'
elif (Zu < newP) & (newP < mx ):
    zone = 'z1'
elif (ave < newP) & (newP <= Zu ):
    zone = 'z2'
elif (Zd < newP) & (newP <= ave ):
    zone = 'z3'
elif (mn < newP) & (newP <= Zd ):
    zone = 'z4'
elif newP <= mn:
    zone = 'mn'

# ------- check price increase
if (newP > profP) and (vol_bal > 0):#20220127
    profP = newP
    Hzone = zone
    Pdate = today


# -------　Update SPr  ------
past1=timedelta(minutes=C_short)
past2=timedelta(minutes=C_long)

date_str = df_status.loc[0,'Pdate']

# ----- measure Close speed -----
col = ['Max','Close','date','speed','wave_s','wave_l']
df_mx = pd.DataFrame([],columns = col)

df_mx['Close']=df_smma['Close']
df_mx['date']=df_smma['date']
df_mx['Max']=df_smma['Max']

#------ mesure Close speed & MA-------
min5 = timedelta(minutes=5)
ln_mx =len(df_mx)
for i in range(ln_mx-1):
    df_mx.at[i+1,'speed'] = (df_mx.at[i+1,'Close']-df_mx.at[i,'Close'])/5
    df_mx.at[i+1,'wave_s']= df_smma.at[i+1,'SMMA_S']-df_smma.at[i,'SMMA_S']#10/10
    df_mx.at[i+1,'wave_l']= df_smma.at[i+1,'SMMA_L']-df_smma.at[i,'SMMA_L']#10/10    


# ###-------------------------------- ####
# ###     check selling conditions    ####
# ###-------------------------------- ####
profR =0
SPr =0
if Bp > 0:
    profR = (profP - Bp)/Bp

    
## -----　Set SPr  -------  
if (C_Pr_l<=profR) and (profR < C_Pr_m):
    SPr = C_SPr_l
if (C_Pr_m <=profR) and (profR < C_Pr_h):
    SPr = C_SPr_m
if C_Pr_h <=profR:
    SPr = C_SPr_h


## ------- PrePare parametors ------
Bp_tmp = 99
if Bp == 0:#2021/09/21
    Bp_tmp = 0 #2022/01/30
    Bp = newP

preprof = newP - Bp
preprofR = preprof/Bp
Maxprof = profP - Bp
profR = Maxprof/Bp
permitP = Maxprof*SPr + Bp

## ------ waveS,L ---------
prevMin = df_smma.loc[ln_smma-2,'Min']
thisMin = df_smma.loc[ln_smma-1,'Min']
iter = len(df_mx)-1
waveS = df_mx.at[iter,'wave_s']
waveL = df_mx.at[iter,'wave_l']


# initialize
Scon1 = False # Shrink Profit
Scon2 = False # Loss Cutting
Scon3 = False # No Use
Scon4 = False # No Use
Scon5 = False # ds;
Scon6 = False # qs; is;    
SELL = False

## --------- Judgement logic --------
# Stage1
Scon1 = (Manu == 'go') and (preprof <= Maxprof * SPr) and (not(waveS>0 and waveL>0)) and (preprof > 0)#21220203
Scon2 = (Manu == 'go') and (newP/Bp <= LCr)
Scon6 = (Manu == 'qs') or (Manu == 'is') and ((d_price >= newP) or (u_price <= newP))


if Bp_tmp == 0:#2022/01/30
    Bp = Bp_tmp
    


### ------------------------ ######## 
###        SEL Judgment      ########
### ------------------------ ########

# ----- volume check ------20220127
Scon1 = (vol_bal >= vol_trn) and Scon1
Scon2 = (vol_bal >= vol_trn) and Scon2
Scon6 = (vol_bal >= vol_trn) and Scon6



## ######################################################
## ###########    Auto BUY Process Starts   #############
## ######################################################

speed_1 = df_mx.at[ln_mx-1,'speed']
speed_0 = df_mx.at[ln_mx-2,'speed']
wave_s = df_mx.at[ln_mx-1,'wave_s']
wave_l = df_mx.at[ln_mx-1,'wave_l']
ln_slog = len(df_statuslog)
zone_0 = df_statuslog.at[ln_slog-1,'zone']
ln = len(df_smma)
df_smma_1=df_smma.loc[ln-1,'Min']
df_smma_2=df_smma.loc[ln-2,'Min']
rsi_chk = df_smma.loc[ln-1,'rsi']
macd_chk = df_smma.at[ln-1,'macd']

# ------- initialize ---------
Bcon1 = False # z4, Min0 = Min1, Speed>0 に該当するか？
Bcon1A = False # z4
Bcon1B = False # Min0=Min1
Bcon1C = False # Speed>0
Bcon1D = False # waves>0 wavel>0
Bcon2 = False # macd -0.4

Bcon3 = False # No use
Bcon4 = False # No use
Bcon5 = False # db;

Bcon6 = False # qb,ib
BconTeck = False # Technical Check
BUY = False



## ----------------- db OR ds ----------------- ##
old_prevP
old_d_price = d_price
old_u_price = u_price
## -------------------------------------------- ##

## ######################################################
## ############# Trailing System Starts #################
## ######################################################
    
# ------       Initialize      -----------
d_pct = 0.001
u_pct = 0.001
if old_prevP == 0: #20220315
    old_prevP = newP
if (prev_low == 0) and (Manu == 'db'):
    prev_low = old_prevP
if (prev_hi == 0) and (Manu == 'ds'):
    prev_hi = old_prevP


# ------ d_price : pct conversion by df_status -------
if (old_d_price < 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    d_pct = old_d_price
    test = old_d_price
    d_pct2b = d_pct #CP
elif (old_d_price > 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    d_pct = (old_prevP - old_d_price)/old_prevP
    

# ------ u_price : pct conversion df_status -------
if (old_u_price < 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    u_pct = old_u_price
    u_pct2b = u_pct #CP
elif (old_u_price > 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    u_pct = (old_u_price - old_prevP)/old_prevP


if (date != 'a') and (Manu == 'db'):
    d_pct = (prev_low - old_d_price)/prev_low #20220315
    u_pct = (old_u_price - prev_low)/prev_low #20220315
        
if (date != 'a') and (Manu == 'ds'):
    d_pct = (prev_hi - old_d_price)/prev_hi #20220315
    u_pct = (old_u_price - prev_hi)/prev_hi #20220315

# CP ###############
d_price2 = old_d_price


prevP2 = old_prevP
u_price2 = old_u_price
d_pct2s = d_pct
u_pct2s = u_pct
prev_low2=prev_low
prev_hi2=prev_hi
# CP ###############    
    
# ------ pct to Number :d/u_price -------
if Manu == 'db':
    d_price = prev_low * (1 - d_pct)
    u_price = prev_low * (1 + u_pct)
if Manu == 'ds':
    d_price = prev_hi * (1 - d_pct)
    u_price = prev_hi * (1 + u_pct)


# CP ###############
d_price3 = d_price
u_price3 = u_price
prevP3 = old_prevP
d_pct3 = d_pct
u_pct3 = u_pct
prev_low3=prev_low
prev_hi3=prev_hi
# CP ###############    

# ------ First Parameters check ---------
if (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    CHK = (d_price < prevP) and (u_price > prevP)
    if not CHK:
        print('d/u_price seq error')


# -----   trailing down -- Buying process
if (Manu == 'db') and (prev_low > newP):
    prev_low = newP
    prevP = newP
    d_price = prev_low * (1 - d_pct)#20220315
    u_price = prev_low * (1 + u_pct)#20220315
    
# CP ###############
d_price4 = d_price
u_price4 = u_price
prevP4 = prevP
d_pct4 = d_pct
u_pct4 = u_pct
prev_low4=prev_low
prev_hi4=prev_hi
# CP ###############    

# -----   trailing high -- Selling process
if (Manu == 'ds') and (prev_hi < newP):
    prev_hi = newP
    prevP = newP
    d_price = prev_hi * (1 - d_pct)#20220315
    u_price = prev_hi * (1 + u_pct)#20220315
    
# CP ###############
d_price5 = d_price
u_price5 = u_price
prevP5 = prevP
d_pct5 = d_pct
u_pct5 = u_pct
prev_low5=prev_low
prev_hi5=prev_hi
# CP ###############    

    
    
    
## ----- db BUY :ds SELL Judgement
Bcon5 = (Manu == 'db') and (( d_price > newP) or ( u_price < newP))
Scon5 = (Manu == 'ds') and (( d_price > newP) or ( u_price < newP))
#prevP = newP
date = today

## ############ trailing valuables #############
Manu6 = Manu
Bcon5_6 = Bcon5
Scon5_6 = Scon5
d_price6 = d_price
u_price6 = u_price
newP6 = newP
prevP6 = prevP
d_pct6 = d_pct
u_pct6 = u_pct
prev_low6=prev_low
prev_hi6=prev_hi
## ############   ##   end    ##   #############




###### --------------------------- ######
###### ----  BUY Conditions  ----- ######
###### --------------------------- ######


# Stage1
Bcon1A = (zone == 'z3') or (zone == 'z4') or (zone_0=='z4') or (zone_0=='mn')
Bcon1B = (df_smma_1==df_smma_2)
Bcon1C = (speed_1>0)
Bcon1D = not ((wave_s <0) and (wave_l<0))
BconTeck = (rsi_chk <=30)

Bcon1 = Bcon1A and Bcon1B and Bcon1C and Bcon1D and BconTeck
Bcon2 = (macd_chk <-0.4) and Bcon1A and Bcon1C
Bcon6 = (Manu == 'qb') or (Manu == 'ib') and ((d_price >= newP) or (u_price <= newP))





###### ------------------ ########    
######    BUY Judgment    ########  
###### ------------------ ########

# -------- Volume Check ---------- 20220212
if (vol_bal > 0) and (Manu == 'go'):
    Bcon1 = False
    Bcon2 = False
# Cheked

# ---- final Decision ------
SELL = (Manu == 'go') and (Scon1 or Scon2) or Scon6 or Scon5
BUY = (Manu == 'go') and ((Bcon1 or Bcon2) and (newP <= PrRange)) or Bcon6 or Bcon5

if SELL and BUY:
    SELL = False
    BUY = False

if Manu == 'stop':
    SELL = False
    BUY = False
    

# ------ set para to Conds -------
SC = ''
if Scon1:
    SC = SC+"1"
else:
    SC = SC+"0"
if Scon2:
    SC = SC+"1"
else:
    SC = SC+"0"
if Scon3:
    SC = SC+"1"
else:
    SC = SC+"0"
if Scon4:
    SC = SC+"1"
else:
    SC = SC+"0"
if Scon5:
    SC = SC+"1"
else:
    SC = SC+"0"
if Scon6:
    SC = SC+"1"
else:
    SC = SC+"0"


BC = ''
if Bcon1:
    BC = BC+"1"
else:
    BC = BC+"0"
if Bcon2:
    BC = BC+"1"
else:
    BC = BC+"0"
if Bcon3:
    BC = BC+"1"
else:
    BC = BC+"0"
if Bcon4:
    BC = BC+"1"
else:
    BC = BC+"0"
if Bcon5:
    BC = BC+"1"
else:
    BC = BC+"0"
if Bcon6:
    BC = BC+"1"
else:
    BC = BC+"0"

conds = "S"+SC+"/"+"B"+BC+"/"+Manu    
#--------- end


if Manu == "go":
    d_price = 0
    u_price = 0

    
    
    
if SELL:
    price = str(newP)
    amount = str(vol_trn)#20220127
    if cond_TEST:
        print("TEST SELL XRP")
        #None
    else:
        print("EXEC SELL XRP")
        exe_sellm(price,amount)
    date = today
    last_Bp = Bp
     # ------------ set vars  ---------
    vol_bal = vol_bal - vol_trn #20220127    
    if vol_bal == 0:
        Bp=0
    else:
        Bp
    Bdate = ''
    Pdate = ''
    profP = 0
    LCp = 0
    LCr = 0 #2021/11/07
    SPr = 0
    prevP = newP
    zone
    Hzone = ''
    Sdate = today
    Manu = 'go'
    Auto = conds #         Auto operation conditions ----> excel
    Prof = (newP*(1-0.001) - last_Bp*(1+0.001))* vol_trn  #20220127
    d_price = 0
    u_price = 0    

    
    # ---------- set vars to BB_status ----------2022/01/21
    df_status.loc[0,'date'] = date     #date of update
    df_status.loc[0,'Bp'] = Bp         #price of Bought
    df_status.loc[0,'Bdate'] = Bdate   #date of Bought
#df_status.loc[0,'volume'] = volume #volume of Bought
    df_status.loc[0,'Pdate'] = Pdate   #date of past max profit
    df_status.loc[0,'profP'] = profP   #price of past max profit
    df_status.loc[0,'LCp'] = LCp       #Loss Cut price
    df_status.loc[0,'LCr'] = LCr       #Loss Cut price rate
    df_status.loc[0,'SPr'] = SPr       #Shrink Profit rate
    df_status.loc[0,'prevP'] = prevP   #every time previous price
    df_status.loc[0,'Sdate'] = Sdate   #date of sell
    df_status.loc[0,'zone'] = zone     #every time zone
    df_status.loc[0,'Hzone'] = Hzone   #zone at Highest 2021/07/07 Name Changed
    df_status.loc[0,'Manu'] = Manu     #Manual execution
    df_status.loc[0,'Auto'] = Auto     #Auto operation
    df_status.loc[0,'Prof'] = Prof
    df_status.loc[0,'d_price'] = d_price
    df_status.loc[0,'u_price'] = u_price
    df_status.loc[0,'Date'] = Date
    df_status.loc[0,'rsi'] = rsi
    df_status.loc[0,'macd'] = macd
    df_status.loc[0,'macdsignal'] = macdsignal
    df_status.loc[0,'macdhist'] = macdhist
    # ---- 20220127 ------
    df_status.loc[0,'vol_bal'] = vol_bal
    df_status.loc[0,'vol_trn'] = vol_trn
    # ---- 20220313 -------
    df_status.loc[0,'prev_low'] = prev_low
    df_status.loc[0,'prev_hi'] = prev_hi



# # #  ---------- Check AND Use -------------
    # 現在の1行をlogに追加
    if cond_TEST:
#        df_statuslog = pd.read_excel(patha + "BB_statuslog_.xlsx")
        df_statuslog["vol_bal"]=df_statuslog["vol_bal"].astype(float)
        df_statuslog = pd.concat([df_statuslog,df_status.loc[0:0,:]],ignore_index = True)
        df_statuslog.to_excel(patha + 'BB_statuslog_.xlsx',index=False)
    else:
#        df_statuslog = pd.read_excel(patha + "BB_statuslog.xlsx")
        df_statuslog["vol_bal"]=df_statuslog["vol_bal"].astype(float)
        df_statuslog = pd.concat([df_statuslog,df_status.loc[0:0,:]],ignore_index = True)
        df_statuslog.to_excel(patha + 'BB_statuslog.xlsx',index=False)

    # １行を削除しB_status.xlsxを更新
    df = df_status.drop([0])
    df_status = df
    if len(df_status)>1:
        df_status.at[1,'Bp'] = 0
        df_status.at[1,'vol_bal'] = vol_bal #20220215追加

    if cond_TEST:
        df_status.to_excel(patha + "BB_status_.xlsx",index=False)
    else:    
        df_status.to_excel(patha + 'BB_status.xlsx',index=False)

# # # ------------------------------------------



elif BUY:
    newP_ads = newP
    price = str(newP_ads)
    amount = str(vol_trn)
    if cond_TEST:
        print("TEST BUY XRP")
        #None
    else:
        print("EXCUTE BUY XRP")
        exe_buym(price,amount)
    date = today
    
    # ------------ set vars  --------------
    Bdate = today #      date of Bought
    Bp   = newP #        price of Bought  ----> set excel
    vol_bal = vol_bal + vol_trn #20220127
    Pdate = Bdate#       date of past max profit
    profP = Bp#          Price of past max profit
    LCp = Bp * C_LCr#    Loss Cut price
    LCr = C_LCr#0.98#    Loss Cut price rate ---> set excel
    SPr   #variable #    Shrink Profit rate   ---> set constant
    prevP = Bp #         previous price
    Sdate = '' #         date of sell
    Hzone = zone #       zone at Highest 2021/07/07
    Manu  = 'go'  #      Manual execution  qb,qs,ib ----> clear
    Auto  = conds #      Auto operation conditions ----> excel
    Prof = 0
    d_price = 0
    u_price = 0

    # ---------- set vars to BB_status ----------2022/01/21
    df_status.loc[0,'date'] = date     #date of update
    df_status.loc[0,'Bp'] = Bp         #price of Bought
    df_status.loc[0,'Bdate'] = Bdate   #date of Bought
#df_status.loc[0,'volume'] = volume #volume of Bought
    df_status.loc[0,'Pdate'] = Pdate   #date of past max profit
    df_status.loc[0,'profP'] = profP   #price of past max profit
    df_status.loc[0,'LCp'] = LCp       #Loss Cut price
    df_status.loc[0,'LCr'] = LCr       #Loss Cut price rate
    df_status.loc[0,'SPr'] = SPr       #Shrink Profit rate
    df_status.loc[0,'prevP'] = prevP   #every time previous price
    df_status.loc[0,'Sdate'] = Sdate   #date of sell
    df_status.loc[0,'zone'] = zone     #every time zone
    df_status.loc[0,'Hzone'] = Hzone   #zone at Highest 2021/07/07 Name Changed
    df_status.loc[0,'Manu'] = Manu     #Manual execution
    df_status.loc[0,'Auto'] = Auto     #Auto operation
    df_status.loc[0,'Prof'] = Prof
    df_status.loc[0,'d_price'] = d_price
    df_status.loc[0,'u_price'] = u_price
    df_status.loc[0,'Date'] = Date
    df_status.loc[0,'rsi'] = rsi
    df_status.loc[0,'macd'] = macd
    df_status.loc[0,'macdsignal'] = macdsignal
    df_status.loc[0,'macdhist'] = macdhist
    # ---- 20220127 ------
    df_status.loc[0,'vol_bal'] = vol_bal
    df_status.loc[0,'vol_trn'] = vol_trn
    # ---- 20220313 -------
    df_status.loc[0,'prev_low'] = prev_low
    df_status.loc[0,'prev_hi'] = prev_hi

    
# # #  ---------- Check AND Use -------------
    
    # 現在の1行をlogに追加
    if cond_TEST:
#        df_statuslog = pd.read_excel(patha + "BB_statuslog_.xlsx")
        df_statuslog["vol_bal"]=df_statuslog["vol_bal"].astype(float) #20220220 type指定
        df_statuslog = pd.concat([df_statuslog,df_status.loc[0:0,:]],ignore_index = True)
        df_statuslog.to_excel(patha + 'BB_statuslog_.xlsx',index=False)
    else:
#        df_statuslog = pd.read_excel(patha + "BB_statuslog.xlsx")
        df_statuslog["vol_bal"]=df_statuslog["vol_bal"].astype(float) #20220220 type指定        
        df_statuslog = pd.concat([df_statuslog,df_status.loc[0:0,:]],ignore_index = True)
        df_statuslog.to_excel(patha + 'BB_statuslog.xlsx',index=False)

    # １行を削除しB_status.xlsxを更新
    df = df_status.drop([0])
    df_status = df
    if len(df_status)>1:
        df_status.at[1,'Bp'] = Bp
        df_status.at[1,'vol_bal'] = vol_bal #20220215追加
    if cond_TEST:
        df_status.to_excel(patha + "BB_status_.xlsx",index=False)
    else:    
        df_status.to_excel(patha + 'BB_status.xlsx',index=False)
    
else:
    date = today    
    Sdate = "" #         date of sell
    Auto  = conds#       Auto operation    next ----> excel    
    Prof = 0
# ---------- set vars to BB_status ----------2022/01/21
    df_status.loc[0,'date'] = date     #date of update
    df_status.loc[0,'Bp'] = Bp         #price of Bought
    df_status.loc[0,'Bdate'] = Bdate   #date of Bought
#df_status.loc[0,'volume'] = volume #volume of Bought
    df_status.loc[0,'Pdate'] = Pdate   #date of past max profit
    df_status.loc[0,'profP'] = profP   #price of past max profit
    df_status.loc[0,'LCp'] = LCp       #Loss Cut price
    df_status.loc[0,'LCr'] = LCr       #Loss Cut price rate
    df_status.loc[0,'SPr'] = SPr       #Shrink Profit rate
    df_status.loc[0,'prevP'] = prevP   #every time previous price
    df_status.loc[0,'Sdate'] = Sdate   #date of sell
    df_status.loc[0,'zone'] = zone     #every time zone
    df_status.loc[0,'Hzone'] = Hzone   #zone at Highest 2021/07/07 Name Changed
    df_status.loc[0,'Manu'] = Manu     #Manual execution
    df_status.loc[0,'Auto'] = Auto     #Auto operation
    df_status.loc[0,'Prof'] = Prof
    df_status.loc[0,'d_price'] = d_price
    df_status.loc[0,'u_price'] = u_price
    df_status.loc[0,'Date'] = Date
    df_status.loc[0,'rsi'] = rsi
    df_status.loc[0,'macd'] = macd
    df_status.loc[0,'macdsignal'] = macdsignal
    df_status.loc[0,'macdhist'] = macdhist
    # ---- 20220127 ------
    df_status.loc[0,'vol_bal'] = vol_bal
    df_status.loc[0,'vol_trn'] = vol_trn
    # ---- 20220313 -------
    df_status.loc[0,'prev_low'] = prev_low
    df_status.loc[0,'prev_hi'] = prev_hi


# # #  ---------- Check AND Use -------------

    # 現在の1行をlogに追加
    if cond_TEST:
        df_statuslog = pd.concat([df_statuslog,df_status.loc[0:0,:]],ignore_index = True)
        df_statuslog.to_excel(patha + 'BB_statuslog_.xlsx',index=False)
    else:
        df_statuslog = pd.concat([df_statuslog,df_status.loc[0:0,:]],ignore_index = True)
        df_statuslog.to_excel(patha + 'BB_statuslog.xlsx',index=False)

    df_status.at[0,'Bp'] = 0
    df_status.at[0,'vol_bal'] = vol_bal #20220215追加
    if cond_TEST:
        df_status.to_excel(patha + "BB_status_.xlsx",index=False)
    else:    
        df_status.to_excel(patha + 'BB_status.xlsx',index=False)

# # # ------------------------------------------



### ### ----------------------------- ### ###
### ###       SAVE FILE ZONE 3/3      ### ###
### ### ----------------------------- ### ###

# ----------- 非参照file 更新　--------
df_mx.to_excel(patha+'df_mx_TBD.xlsx',index=False)#

# ----------  管理file 更新   ---------
#df_statuslog = pd.concat([df_statuslog,df_status],ignore_index = True)
#if cond_TEST:
#    df_status.to_excel(patha + 'BB_status_.xlsx',index=False)
#    df_statuslog.to_excel(patha + 'BB_statuslog_.xlsx',index=False)
#else:
#    df_status.to_excel(patha + 'BB_status.xlsx',index=False)
#    df_statuslog.to_excel(patha + 'BB_statuslog.xlsx',index=False)


ln = len(df_smma)
mx=df_smma.loc[ln-1,'Max']
mn=df_smma.loc[ln-1,'Min']
cl=df_smma.loc[ln-1,'Close']

print(today,':', 'Max',mx,'Min',mn,'Close',cl,'zone',zone,'SC',SC,'BC',BC)  
## 実稼働版EXEC 版





#### ---------------------------------------------##
#### ------------ Independent Program ------------##
#### ---------------------------------------------##



## ------------------------------------ ##
##     BTC の qb qs, ib is, db ds        ##
## ------------------------------------ ##

# -------- functions ----------
def exe_sellm_p(pair,newP,volume):
    pair
    price = str(newP)
    amount = str(volume)
    side = 'sell'
    order_type = 'market'#成行
    prv.order(pair, price, amount, side, order_type)
    return
def exe_buym_p(pair,newP,volume):
    pair
    price = str(newP)
    amount = str(volume)
    side = 'buy'
    order_type ='market'
    prv.order(pair, price, amount, side, order_type)
    return

# --- Constants ----
C_pair ='btc_jpy'
patha = '/Users/suusan/Documents/MyPandas/'

# ---- Initialize : set var ZERO ----
Bp,d_price,prevP,u_price,vol_bal,vol_trn,prev_low,prev_hi,newP = 0,0,0,0,0,0,0,0,0
Manu = ''
date = ''
CHK = False     #Flag: d/u price seq, %d/u price, set dif_d/u,
Con_to = False  #Flag: update "B_status.xslx"

# ---- initialize : SELL BUY 
Scon6 = False # quick sell, indicate sell  
Scon5 = False # difference sell
SELL  = False
Bcon5 = False # difference buy
Bcon6 = False # Quick Buy,Indicate Buy
BUY = False


##------ Read file 'B_status.XL'　& 'B_status_.XL' #20220218
if cond_TEST:
    df_bstatus = pd.read_excel(patha + "B_status_.xlsx")
else:    
    df_bstatus = pd.read_excel(patha + "B_status.xlsx")

col = list(df_bstatus.columns)
df = pd.DataFrame([],columns = col)

# ------- DateFrame_to_vars --------
df_bstatus["vol_bal"]=df_bstatus["vol_bal"].astype(float) #20220220 type指定

date = df_bstatus.at[0,'date'] 
Bp = df_bstatus.at[0,'Bp'] 
Manu = df_bstatus.at[0,'Manu']
d_price = df_bstatus.at[0,'d_price']
prevP = df_bstatus.at[0,'prevP']
u_price = df_bstatus.at[0,'u_price']
vol_bal = df_bstatus.at[0,'vol_bal']
vol_trn = df_bstatus.at[0,'vol_trn']
prev_low = df_bstatus.at[0,'prev_low']
prev_hi = df_bstatus.at[0,'prev_hi']

today = datetime.today().strftime('%Y-%m-%d-%H-%M')

# --------- read API ---------
pub = BitBankPubAPI()
ticker = pub.get_ticker(C_pair)
df_thistime= pd.DataFrame([ticker])

colist=['sell', 'buy', 'open', 'high', 'low', 'last', 'vol']
for i in colist:
    df_thistime.loc[0,i] =float(df_thistime.loc[0,i])

#------ set var from API <new price> -------
if cond_TEST:
    newP = newP_t_btc
else:
    newP = df_thistime.loc[0,'last']
    

if (prevP == 0):
    print('prevP is vacant')
    Con_x = False # 処理の停止

# ------ d_price : pct conversion -------
if (d_price <1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    d_pct = d_price
    Con_to = True #20220218 
elif (d_price >1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    d_pct = (prevP - d_price)/prevP
    Con_to = True #20220218 
else:
    d_pct = (prevP - d_price)/prevP
    
# ------ u_price : pct conversion -------
if (u_price < 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    u_pct = u_price
    Con_to = True #20220218
elif (u_price > 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    u_pct = (u_price - prevP)/prevP
    Con_to = True #20220218 
else:
    u_pct = (u_price - prevP)/prevP

# pct to Number :d/u_price
d_price = prevP * (1 - d_pct)
u_price = prevP * (1 + u_pct)

# First Parameters check
if (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    CHK = (d_price < prevP) and (u_price > prevP)
    if not CHK:
        print('d/u_price seq error')

# Initialize
if (prev_low == 0) and (Manu == 'db'):
    prev_low = prevP
    Con_to = True
if (prev_hi == 0) and (Manu == 'ds'):
    prev_hi = prevP
    Con_to = True

# set dif 
dif_d = prevP - d_price
dif_u = u_price - prevP

# 以下は prevP -> prev_low -> newPの順に変動させる。
# 
# trailing down -- Buying process
if (Manu == 'db') and (prev_low > newP):
    prev_low = newP
    d_price = prev_low - dif_d
    u_price = prev_low + dif_u
    Con_to  = True

# trailing high -- Selling process
if (Manu == 'ds') and (prev_hi < newP):
    prev_hi = newP
    d_price = prev_hi - dif_d
    u_price = prev_hi + dif_u
    Con_to = True

## ----- db BUY :ds SELL Judgement

Bcon5  = (Manu == 'db') and (( d_price > newP) or ( u_price < newP))
Scon5 = (Manu == 'ds') and (( d_price > newP) or ( u_price < newP))
prevP = newP
date = today

## ------ q(b/s) i(b/s) Judgement ---------
Scon6 = (Manu == 'qs') or ((Manu == 'is') and ((d_price >= newP) or (u_price <= newP)))
Scon6 = (vol_bal >= vol_trn) and Scon6
SELL = Scon6 or Scon5

Bcon6 = (Manu == 'qb') or ((Manu == 'ib') and ((d_price >= newP) or (u_price <= newP)))
BUY = Bcon6 or Bcon5



## -------- Excute -----------
if SELL:
    print("SEL")
    price = str(newP)
    amount = str(vol_trn)#20220127
    if cond_TEST:
        print (Manu," TEST SELL BTC")
    else:
        exe_sellm_p(C_pair,price,amount)
        print(Manu," EXEC SELL BTC")
    vol_bal = vol_bal - vol_trn
    Bp = 0
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'Bp'] =Bp 
    df_bstatus.at[0,'Manu']=Manu
    df_bstatus.at[0,'d_price']=d_price
    df_bstatus.at[0,'prevP']=prevP
    df_bstatus.at[0,'u_price']=u_price
    df_bstatus.at[0,'vol_bal']=vol_bal
    df_bstatus.at[0,'vol_trn']=vol_trn
    df_bstatus.at[0,'prev_low']=prev_low
    df_bstatus.at[0,'prev_hi']=prev_hi
    
    df_bstatus = df_bstatus.sort_index()
    # 現在の1行をlogに追加
    if cond_TEST:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog_.xlsx")
        df_bstatuslog["vol_bal"]=df_bstatuslog["vol_bal"].astype(float) #20220220 type指定
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog_.xlsx',index=False)
    else:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog.xlsx")
        df_bstatuslog["vol_bal"]=df_bstatuslog["vol_bal"].astype(float) #20220220 type指定
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog.xlsx',index=False)

    # １行を削除しB_status.xlsxを更新
    df = df_bstatus.drop([0])
    df_bstatus = df
    if len(df_bstatus)>1:
        df_bstatus.at[1,'Bp'] = 0
        df_bstatus.at[1,'vol_bal'] = vol_bal #20220215追加

    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:    
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)


elif BUY:
    print("BUY")
    price = str(newP)
    amount = str(vol_trn)
    if cond_TEST:
        print(Manu," TEST BUY BTC")
    else:
        exe_buym_p(C_pair,price,amount)
        print(Manu," EXEC BUY BTC")    
    Bp = newP
    vol_bal = vol_bal + vol_trn
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'Bp'] =Bp 
    df_bstatus.at[0,'Manu']=Manu
    df_bstatus.at[0,'d_price']=d_price
    df_bstatus.at[0,'prevP']=prevP
    df_bstatus.at[0,'u_price']=u_price
    df_bstatus.at[0,'vol_bal']=vol_bal
    df_bstatus.at[0,'vol_trn']=vol_trn
    df_bstatus.at[0,'prev_low']=prev_low
    df_bstatus.at[0,'prev_hi']=prev_hi
    
    df_bstatus = df_bstatus.sort_index()
    # 現在の1行をlogに追加
    if cond_TEST:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog_.xlsx")
        df_bstatuslog["vol_bal"]=df_bstatuslog["vol_bal"].astype(float) #20220220 type指定
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog_.xlsx',index=False)
    else:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog.xlsx")
        df_bstatuslog["vol_bal"]=df_bstatuslog["vol_bal"].astype(float) #20220220 type指定        
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog.xlsx',index=False)

    # １行を削除しB_status.xlsxを更新
    df = df_bstatus.drop([0])
    df_bstatus = df
    if len(df_bstatus)>1:
        df_bstatus.at[1,'Bp'] = Bp
        df_bstatus.at[1,'vol_bal'] = vol_bal #20220215追加
    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:    
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)


    
if Con_to and (not SELL and not BUY):
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'d_price']=d_price
    df_bstatus.at[0,'prevP']=prevP
    df_bstatus.at[0,'u_price']=u_price
    df_bstatus.at[0,'vol_bal']=vol_bal
    df_bstatus.at[0,'vol_trn']=vol_trn
    df_bstatus.at[0,'prev_low']=prev_low
    df_bstatus.at[0,'prev_hi']=prev_hi


    # 現在の1行をlogに追加
    if cond_TEST:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog_.xlsx")
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog_.xlsx',index=False)
    else:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog.xlsx")
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog.xlsx',index=False)

    # １行削除を除く 20220221    
    if len(df_bstatus)>1:
        df_bstatus.at[1,'Bp'] = 0
        df_bstatus.at[1,'vol_bal'] = vol_bal #20220215追加
    else:
        df_bstatus.at[0,'Bp'] = 0
        df_bstatus.at[0,'vol_bal'] = vol_bal #20220215追加

        
        
    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:    
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)

    

Manu,d_price,prevP,u_price,prev_low,prev_hi,vol_bal,vol_trn
# BitBank.py　v4.70