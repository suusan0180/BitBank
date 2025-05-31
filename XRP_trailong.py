
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
# ------- Library loading ----------

cond_TEST = True# <------- Test時のみ有効
newP_t_xrp = 91 # <------- Test時のみ有効
newP_t_btc = 4600500 # <--- Test時のみ有効

# ---- Initialize : set var ZERO ----
Bp,d_price,prevP,u_price,vol_bal,vol_trn,prev_low,prev_hi,newP = 0,0,0,0,0,0,0,0,0
Manu = ''
date = ''
CHK = False     #Flag: d/u price seq, %d/u price, set dif_d/u,
Con_to = False  #Flag:update "B_status.xslx"

# ---- initialize : SELL BUY 
Scon5 = False # ds;difference sell
Scon6 = False # qs;quick sell, is;indicate sell  
SELL  = False
Bcon5 = False # db;difference buy
Bcon6 = False # qb;Quick Buy, ib;Indicate Buy
BUY = False

##------ Read 'BB_status.XL'　& 'BB_statuslog.XL'file
patha = '/Users/suusan/Documents/MyPandas/'
pathb = '/Users/suusan/CloudStation/☆☆K_Trade/data/'

if cond_TEST:
    df_status = pd.read_excel(patha + "BB_status_.xlsx")
    df_statuslog = pd.read_excel(patha + "BB_statuslog_.xlsx")
else:    
    df_status = pd.read_excel(patha + "BB_status.xlsx")
    df_statuslog = pd.read_excel(patha + "BB_statuslog.xlsx")

    
newP = newP_t_xrp
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

## ######################################################
## ############# Trailing System Starts #################
## ######################################################

# ------ d_price : pct conversion by df_status -------
if (d_price <1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    d_pct = d_price
elif (d_price >1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    d_pct = (prevP - d_price)/prevP 
else:
    d_pct = (prevP - d_price)/prevP

# ------ u_price : pct conversion by df_status -------
if (u_price < 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    u_pct = u_price
elif (u_price > 1) and (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    u_pct = (u_price - prevP)/prevP
else:
    u_pct = (u_price - prevP)/prevP

# ------ pct to Number :d/u_price -------
d_price = prevP * (1 - d_pct)
u_price = prevP * (1 + u_pct)

# ------ First Parameters check ---------
if (date == 'a') and ((Manu == 'db') or (Manu == 'ds')):
    CHK = (d_price < prevP) and (u_price > prevP)
    if not CHK:
        print('d/u_price seq error')

# ------       Initialize      -----------
if (prev_low == 0) and (Manu == 'db'):
    prev_low = prevP
if (prev_hi == 0) and (Manu == 'ds'):
    prev_hi = prevP

# -----        set dif         -----------
#dif_d = prevP - d_price
#dif_u = u_price - prevP

# -----   trailing down -- Buying process
if (Manu == 'db') and (prev_low > newP):
    prev_low = newP
    prevP = newP
    d_price = prevP * (1 - d_pct)
    u_price = prevP * (1 + u_pct)


# -----   trailing high -- Selling process
if (Manu == 'ds') and (prev_hi < newP):
    prev_hi = newP
    prevp = newP
    d_price = prevP * (1 - d_pct)
    u_price = prevP * (1 + u_pct)


## ----- db BUY :ds SELL Judgement

Bcon5 = (Manu == 'db') and (( d_price > newP) or ( u_price < newP))
Scon5 = (Manu == 'ds') and (( d_price > newP) or ( u_price < newP))
prevP = newP
today = datetime.today().strftime('%Y-%m-%d-%H-%M')
date = today


## ################# trailing #############
## ################# ## end # #############

df_status.loc[0,'d_price'] = d_price
df_status.loc[0,'u_price'] = u_price
df_status.loc[0,'prev_low'] = prev_low
df_status.loc[0,'prev_hi'] = prev_hi
df_status.loc[0,'prevP'] = prevP   #every time previous price

if cond_TEST:
    df_status.to_excel(patha + "BB_status_.xlsx",index=False)
#    df_statuslog.to_excel(patha + "BB_statuslog_.xlsx")
else:    
    df_status.to_excel(patha + "BB_status.xlsx",index=False)
#    df_statuslog.to_excel(patha + "BB_statuslog.xlsx")



print(prev_low,d_price,prevP,u_price,u_pct,d_pct)