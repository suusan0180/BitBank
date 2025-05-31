## 実稼働版EXEC 版 　Checked #　BitBankVer107 + TEST　7/14
# Idea starts at 
# Edited  v1.24 Prev_Hi Lowの維持　2024/07/12 22:02
# message chainged on 25/05/24
# v1.24 Prev_Hi Lowの維持　2024/07/12 22:02
# v1.23 B_statusへの表示　2024/07/12 18:02
# v1.22 p_time supo or => and   2024/07/11 00:43
# v1.21 SELL Limitエラー処理  2024/06/21 13:02
# v1.20 C_pair = '' error exception 2024/05/29 00:50:00
# v1.19 store prevP at sta 2024/05/22 10:50:00
# v1.18 update B_status.xlsx by price & time 2024/05/22 01:25:00
# v1.17 focusR unfocusR by price & time
# v1.16 Check through Con_to control
# v1.15 reset Con_to control nan
# v1.14 reset pair:reset prev_hi prev_low at new pair
# v1.13 ;Con_toの縮小
# v1.12 ;ds vicRの確認
# v1.11 ;db momRの確認
# v1.10 ;log <> staの確認
# v1.09  ;ib,is 変更
# v1.08（変更u(d)_price,resi,supo）

################     現状　        ########
# 'go' は not coded 
# 'qb/qs', 'ib/is', 'db/ds'が実行可能
# vol_bal vol_trnに分け、vol_balはAPIから入手
# vol_trnは　SEL BUYともstatus.volに入力
# Bpは平均単価を手入力するか最後に買った金額を引き継ぐ
##########################################

# -------- extention in future ---------- 
# MA by 1h,1dが可能なようにする
# technicalの拡張性を持たせる
# ---------------------------------------

# 実行前確認
# 1. 必ずcond_TEST = True  を #TEST環境
# 2. 必ずcond_TEST = False を #EXEC環境

## ***************************************** ##
## -------    TEST MODE setting   ---------- ##
## -------    cond_TEST = True    ---------- ##
## ***************************************** ##

#cond_TEST = True # <------- Test時のみ有効
#newP_t_btc = 9550000
# <--- Test時のみ有効

## ***************************************** ##
## -------   EXECute MODE setting ---------- ##
## -------   cond_TEST = False    ---------- ##
## ***************************************** ##

cond_TEST = True # 実行モード            ###
## -------  TEST setting END   --------- ###

## ---------- Operational Constants　-----------
#psh = 0.2
#C_pair = 'btc_jpy'
#C_pair = 'eth_jpy'
#C_pair = 'xrp_jpy'

### ### ############################### ### ###
### ###   　　　PREparation area         ### ###
### ### ############################### ### ###

## ---------    library   -----------
import python_bitbankcc
import pandas as pd
import numpy as np
import math
import json
import datetime
import talib as ta
from time import sleep
from datetime import datetime
from datetime import date
from datetime import timedelta
import pandas.tseries.offsets as offsets
#         Library end              -

## --------- API public -------------
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

## ---------- API Private ------------
import key
API_KEY = key.set_API_key()
API_SECRET = key.set_Secret_key()
prv = python_bitbankcc.private(API_KEY, API_SECRET)


##------------ functions -------------
# -- DataFrame extract: new、old範囲を抽出、出力はboolean
def statics(old,new):
    j=(df_smma['date']>=old) & (df_smma['date']<=new)
    return j

# -- EXEcute  BUY & SELL
def def_active_orders(pair):       #240621
    try:
        value = prv.get_active_orders(pair)
        return value
    except Exception as e:
        print(e)
        return None
    
def def_cancel_order(pair,id):     #240621
    try:
        value = prv.cancel_order(pair,id)
        return value
    except Exception as e:
        print(e)
        return None    
    
def exe_selll_p(pair,newP,volume):    #240620
    pair
    price = str(newP)
    amount = str(volume)
    side = 'sell'
    order_type = 'limit'# market成行,limit指値
    res=prv.order(pair, price, amount, side, order_type)
    return res

def exe_buyl_p(pair,newP,volume):       #240620
    pair
    price = str(newP)
    amount = str(volume)
    side = 'buy'
    order_type ='limit'
    res=prv.order(pair, price, amount, side, order_type)
    return res

def exe_sellm_p(pair,newP,volume):
    pair
    price = str(newP)
    amount = str(volume)
    side = 'sell'
    order_type = 'market'#成行 limit,指値
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

def is_datetime(var):
    return isinstance(var, datetime)

##-------  MACRO DEF ------------------------##
def check(pair):
    id = None
    st = None
    ans=def_active_orders(pair)
    ln=len(ans['orders'])
    for i in range(ln):
        id = ans['orders'][i]['order_id']
        st = ans['orders'][i]['status']
    return id,st

def cancel(id,pair):
    pair
    id1 = id
    ans=def_cancel_order(pair,id1)

def checkNwait(count,FULFIL,countMAX): #240620
    while count <= countMAX and FULFIL:
        id,st=check(C_pair)
        if id is None or st is None:
            print("No orders found")
            break
        print(count,id,st)
        if st=='FULLY_FILLED':
            break
        else:
            sleep(slp)
            count += 1
            FULFIL = True
    return count,id
#------- functions end 

## ----------- Fixed Constants     -------------
patha = '/Users/suusan/Documents/MyPandas/'
#pathb = '/Users/suusan/CloudStation/☆☆K_Trade/DCR_data/'#2024/05/01
pathb = '/Users/suusan/SynologyDrive/Drive/☆☆K_Trade/DCR_data/'#2025/05/18


## ---------- Variables Initialization --------2024/05/17
#　 ---- Initialize : set vars ZERO ----
Bp,d_price,prevP,u_price,vol_bal,vol_trn,prev_low,prev_hi,newP = 0,0,0,0,0,0,0,0,0
resi,ent,supo = 0,0,0
focusR,unfocusR,monR,tmomR,delP,prev_Mani,vicR,tvicR = 0,0,0,0,0,'',0,0 #2024/05/21

#　 ---- Initialize : Judge parametaers ----
CX,Y_mx,X_mx,profr_mx,prof_mx,profr_mx,prof_new,RR,RK,LN = 0,0,0,0,0,0,0,0,1,0

#------------------ para for BUY completion ---------
lk = 0.001      #2406/20
volume=1.00    #2406/20
slp=10         #2406/20
count=1        #2406/20
countMAX = 5   #2406/20
FULFIL = False #2406/20
#---------------------------------------------------- 

Mani = ''
date = ''
CHK = False     #Flag:d/u price seq, %d/u price, set dif_d/u,
Con_to = False  #Flag:update "B_status.xslx"


#　 ---- initialize : SELL BUY conditions
Scon4 = False # qs; quick sell
Scon5a = False
Econ5b = False
Scon5 = False # ds; difference sell
Scon6a = False
Scon6b = False
Scon6 = False # is; indicate sell  
SELL  = False

Bcon4 = False # qb; 
Bcon5 = False # db;dynamic buy
Bcon6 = False # ib;Indicate Buy
BUY = False

#-- --- ------------------------------- --- ---
### ###   　　　PREparation END          ### ###
### ### ############################### ### ###


## ## ######################### ## ##
## ##     Input Process Zone    ## ##
## ## ######################### ## ##

##--- Read file 'B_status.XL'&'B_statuslog.XL' #20220218 -----
if cond_TEST:
    df_bstatus = pd.read_excel(patha + "B_status_.xlsx")
    df_bstatuslog = pd.read_excel(patha + "B_statuslog_.xlsx")
else:    
    df_bstatus = pd.read_excel(patha + "B_status.xlsx")
    df_bstatuslog = pd.read_excel(patha + "B_statuslog.xlsx")

##--- Read File ave_x5min.xlsx ;for future technical ANA ----

##------ Make Vacant DF -----
col = list(df_bstatus.columns)
tmp_bstatus=pd.DataFrame([],columns=col)
df = pd.DataFrame([],columns = col)

LN = len(df_bstatuslog)-1  #latest record number
## ------- DataFrame_to_vars ---------------------------------
# new paras from df_bstatus
C_pair = df_bstatus.at[0,'pair']          #0:str:currency pair 'btc_jpy','eth_jpy'.'xrp_jpy'
date = df_bstatus.at[0,'date']            #1:str:date of update 
Mani = df_bstatus.at[0,'Mani']            #3:str:Manipulation Code #2022/11/14
d_price = df_bstatus.at[0,'d_price']      #4:sgl:downward price indication 
prevP = df_bstatus.at[0,'prevP']          #5:sgl:newest price in memo                 **Change
u_price = df_bstatus.at[0,'u_price']      #6:sgl:upward price indication  
vol_bal = df_bstatus.at[0,'vol_bal']      #7:sgl:volume_balance                       **Change
vol_trn = df_bstatus.at[0,'vol_trn']      #8:sgl:volume_transaction

prev_low = df_bstatuslog.at[LN,'prev_low']    #9:sgl:past lowest price   **Change 20240712
prev_hi = df_bstatuslog.at[LN,'prev_hi']      #10:sgl:past highest price **Change 20240712

ent = df_bstatus.at[0,'ent']              #13:sgl:entrance price in memo　2022/11/13
focusR = df_bstatus.at[0,'focusR']
unfocusR = df_bstatus.at[0,'unfocusR']
p_time = df_bstatus.at[0,'p_time'] 

if is_datetime(p_time):
    p_time = p_time.strftime('%Y-%m-%d-%H-%M')
else:
    p_time ='2999-12-31-00-00'

if C_pair=='':
    C_pair = df_bstatuslog.at[LN,'pair']  
if C_pair == 'xrp':
    C_pair = 'xrp_jpy'
if C_pair == 'eth':
    C_pair = 'eth_jpy'
if C_pair == 'btc':
    C_pair = 'btc_jpy'

# previous paras from df_bstatuslog
Bp = df_bstatuslog.at[LN,'Bp']            #2:sgl:price of Bought 
prev_Mani = df_bstatuslog.at[LN,'Mani']   #3:str:Manipulation Code  2024/05/17

   
# supo & resi from both df conditionally
supo = df_bstatus.at[0,'supo']           #11:sgl:support price in memo　 supo.sta <> supo.log 2024/05/17
resi = df_bstatus.at[0,'resi']           #12:sgl:resistance price in memo resi/sta <> resi.log 2024/05/17

## --------- read API ----------------------------------------
# C_pair = null ならERROR警告
pub = BitBankPubAPI()
ticker = pub.get_ticker(C_pair)
df_thistime= pd.DataFrame([ticker])

colist=['sell', 'buy', 'open', 'high', 'low', 'last', 'vol']
for i in colist:
    df_thistime.loc[0,i] =float(df_thistime.loc[0,i])

#------ set var from API <new price> ------------------------
if cond_TEST:
    newP = newP_t_btc
else:
    newP = df_thistime.loc[0,'last']
    
today = datetime.today().strftime('%Y-%m-%d-%H-%M')

# ------Check ; d_price u_price -----
dpNEW=df_bstatus.at[0,'d_price']
dpOLD=df_bstatuslog.at[LN,'d_price']
upNEW=df_bstatus.at[0,'u_price']
upOLD=df_bstatuslog.at[LN,'u_price']

CHK = (not math.isnan(dpNEW)) and (dpOLD != dpNEW)
if CHK:
    d_price = dpNEW
    Con_to = Con_to or CHK
CHK =False

CHK = (not math.isnan(upNEW)) and (upOLD != upNEW)
if CHK:
    u_price = upNEW
    Con_to = Con_to or CHK
CHK =False


# ------Check ; supo  -----
supoNEW=df_bstatus.at[0,'supo']
supoOLD=df_bstatuslog.at[LN,'supo']

CHK = (not math.isnan(supoNEW)) and supoNEW != supoOLD
if CHK:
    if not math.isnan(supoNEW):
        supo = supoNEW
Con_to = CHK or Con_to

CHK = math.isnan(supoNEW) and (not math.isnan(supoOLD))
if CHK:
    supo = supoOLD  
Con_to = CHK or Con_to
CHK = False

# ------Check ; resi  -----
resiNEW=df_bstatus.at[0,'resi']
resiOLD=df_bstatuslog.at[LN,'resi']

CHK = (not math.isnan(resiNEW)) and resiNEW != resiOLD
if CHK:
    if not math.isnan(resiNEW):
        resi = resiNEW

Con_to = Con_to or CHK 
CHK = False

CHK = math.isnan(resiNEW) and (not math.isnan(resiOLD))
if CHK:
    resi = resiOLD  
Con_to = CHK or Con_to
CHK = False

# ------------------------------------------------------------------
# ---------- pair変更時チェック -----
#CHK = (df_bstatuslog.at[LN,'pair']!=df_bstatus.at[0,'pair'])
CHK = (df_bstatuslog.at[LN,'pair']!=C_pair)

if CHK:
    prev_low = newP
    prev_hi  = newP
Con_to = CHK or Con_to
CHK = False

# ---------- db初回チェック ----- #240704 think how to keep right prev_xx
# suggest
#               
CHK =(prev_Mani != Mani) and (prev_Mani != 'db') and (Mani== 'ib')
#print('Old',prev_Mani,'New',Mani)
if CHK:
    prev_low = newP
    prev_hi = newP
Con_to = CHK or Con_to
CHK = False 


CHK =(prev_Mani != Mani) and (prev_Mani != 'ib') and (Mani== 'db')
#print('Old',prev_Mani,'New',Mani)
if CHK:
    prev_low = newP
    prev_hi = newP
Con_to = CHK or Con_to
CHK = False     
#----- suggestion ends --------    


#CHK =(prev_Mani != Mani) and (Mani == 'db')
#if CHK:
#    prev_low = newP
#    prev_hi  = newP


# ---------- ds初回チェック
# suggest
#               
CHK = (prev_Mani != Mani) and (prev_Mani != 'ds') and (Mani== 'is')
if CHK:
    prev_low = newP
    prev_hi = newP
Con_to = CHK or Con_to
CHK = False
    
CHK = (prev_Mani != Mani) and (prev_Mani != 'is') and (Mani== 'ds')
if CHK:
    prev_low = newP
    prev_hi = newP
Con_to = CHK or Con_to
CHK = False
    
#----- suggestion ends --------    

#CHK =(prev_Mani != Mani) and (Mani == 'ds')
#if CHK:
#    prev_low = newP
#    prev_hi  = newP

## ------------------------- ##
## ##### INPUT Zone END #### ##
## ######################### ##


## ## #################### ## ##
##      Main Processing       ## 2022/11/14
## ## #################### ## ##

## ------------------------------------ ##
##         qb qs, ib is, db ds          ##
## ------------------------------------ ##

## ############################### ##
## initilize  ib,is db,ds prev_xx  ##
## ############################### ##


# Init think what is correct ********
if (prev_low == 0) and (Bp != 0) and ((Mani == 'db') or (Mani == 'ib')):
    prev_low = newP
    CHK = True

Con_to = CHK or Con_to
CHK = False


if prev_low > newP :
    prev_low = newP
    CHK = True

Con_to = CHK or Con_to
CHK = False


if prev_hi < newP :
    prev_hi = newP
    CHK = True

Con_to = CHK or Con_to
CHK = False


if (prev_hi == 0) and ( Bp != 0) and ((Mani == 'ds') or (Mani == 'is')):
    prev_hi = newP
    prof_mx = prev_hi - Bp
    profr_mx = prof_mx/Bp
    prof_new = newP - Bp
    profr_new = prof_new/Bp
    CHK = True
    
Con_to = CHK or Con_to
CHK = False
Con_to = True # -------  Every time Con_to ------

if (prev_hi < newP) and (Bp != 0):
    prev_hi = newP
    prof_mx = prev_hi - Bp
    profr_mx = prof_mx/Bp
    prof_new = newP - Bp
    profr_new = prof_new/Bp
    CHK = True
    
Con_to = CHK or Con_to
CHK = False


# delPの計算
delP = newP - prevP


## ############## ##
## SELL Judgement ##
## ############## ##

# ------ qs -------
Scon4 = (Mani == 'qs')

# ------ is -------
##   Short term judgement   ##
Scon5 = (Mani == 'is') and ((d_price > newP) or (u_price <= newP))

# ------ ds -------
##   Loss Cut judgement   ##
Scon6a = (Mani == 'ds') and (d_price > newP)

##   profit get judgement   ##
if (today>p_time)and(resi<newP):
    vicR = focusR
else:
    vicR = unfocusR
tvicR = abs((newP - prev_hi)/prev_hi)
Scon6b = (Mani=='ds') and (delP<0) and (tvicR>=vicR)
Scon6 = Scon6a or Scon6b
        
SELL = Scon4 or Scon5 or Scon6
SELL = SELL and (vol_bal >= vol_trn) 

## ############### ##
##  BUY Judgement  ##
## ############### ##

# ------ qb -------
Bcon4 = (Mani == 'qb')

# ------ ib -------
Bcon5 = (Mani == 'ib') and ((d_price >= newP)or(u_price <= newP))

# ------ db -------
if (today>p_time)and(supo>newP):
    momR = focusR
else:
    momR = unfocusR 
tmomR = (newP-prev_low)/prev_low
Bcon6 = (Mani=='db') and (delP>0) and (tmomR>=momR)
        
BUY = Bcon4 or Bcon5 or Bcon6

## ############################## ##
##    BUY SELL NOP StatusUpdate   ##
## ############################## ##

## ------------ ##
## 　　SELL      ##
## ------------ ##

if SELL:
    #print('befor SELL')                          ##############################################    
    price = str(newP)
    amount = str(vol_trn)#20220127
    if cond_TEST:
        print (Mani," TEST SELL",C_pair)
    else:
        exe_sellm_p(C_pair,price,amount)
        print(Mani," EXEC SELL",C_pair)
    
    vol_bal = vol_bal - vol_trn
    Bp = 0
    date = today #20221120
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'Bp'] =newP #20240712 sell price
    df_bstatus.at[0,'d_price']=d_price
    df_bstatus.at[0,'prevP']=newP #20221120
    df_bstatus.at[0,'u_price']=u_price
    df_bstatus.at[0,'vol_bal']=vol_bal
    df_bstatus.at[0,'vol_trn']=vol_trn
    df_bstatus.at[0,'prev_low']=prev_low
    df_bstatus.at[0,'prev_hi']=prev_hi
    df_bstatus.at[0,'pair']=C_pair #20240519
    df_bstatus.at[0,'supo']=0   #20240712    


    
    
## -- logへの更新 
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
        df_bstatus.at[1,'prevP'] = newP         #5:sgl:newest price in memo                   **Change
        df_bstatus.at[1,'vol_bal'] = vol_bal     #7:sgl:volume_balance                        **Change
        df_bstatus.at[1,'prev_low'] = prev_low    #9:sgl:past lowest price   reset at bal=0   **Change
        df_bstatus.at[1,'prev_hi'] = prev_hi      #10:sgl:past highest price  reset at bal=0  **Change
        df_bstatus.at[1,'pair']= C_pair


## -- save B_status.xlsx --
    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:    
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)
        
    FULFIL = False
        

## ------------ ##
## 　 　BUY      ##
## ------------ ##
        
elif BUY:
    #print('BUY1')                          ############################################## 
    price = newP*(1-lk)  #240621
    amount = vol_trn     #240621
    if cond_TEST:
        print(Mani," TEST BUY",C_pair)
    else:
        #exe_buyl_p(C_pair,price,amount) #240621
        exe_buym_p(C_pair,price,amount) #240621
        print(Mani," EXEC BUY",C_pair)  
    
    # ------------ begine -----    #240624
    FULFIL = True
    count = 1
    count,id = checkNwait(count,FULFIL,countMAX)
    
    if count==countMAX +1:
        cancel(id,C_pair)
        print('cancel',id)
    # ------------  end -------    
        
    Bp,prev_low,prev_hi = newP,newP,newP
    vol_bal = vol_bal + vol_trn
    date = today #20221120
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'Bp'] =Bp
    df_bstatus.at[1,'Bp'] =Bp
    df_bstatus.at[0,'Mani']=Mani
    df_bstatus.at[0,'d_price']=d_price
    df_bstatus.at[0,'prevP']=newP #20221120
    df_bstatus.at[0,'u_price']=u_price
    df_bstatus.at[0,'vol_bal']=vol_bal
    df_bstatus.at[0,'vol_trn']=vol_trn
    df_bstatus.at[0,'prev_low']=prev_low
    df_bstatus.at[0,'prev_hi']=prev_hi
    df_bstatus.at[0,'pair']=C_pair #20240519
    df_bstatus.at[0,'resi']=0    #20240712    
 

    ## -- logへの更新
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
        df_bstatus.at[1,'prevP'] = newP           #5:sgl :newest price in memo                **Change
        df_bstatus.at[1,'vol_bal'] = vol_bal      #7:sgl :volume_balance                      **Change
        df_bstatus.at[1,'prev_low'] = prev_low    #9:sgl :past lowest price   reset at bal=0  **Change
        df_bstatus.at[1,'prev_hi'] = prev_hi      #10:sgl:past highest price  reset at bal=0  **Change
        df_bstatus.at[1,'pair']= C_pair

    #print('BUY2')                          ##############################################
    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:    
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)

    #print('BUY_aft cancel')                          ############################################## 
## ------------ ##
##      NOP     ##
## ------------ ##        

elif Con_to:
    #print('Con_to')                                  ##############################################
    date = today
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'d_price']=d_price
    df_bstatus.at[0,'prevP']=newP #20221120
    df_bstatus.at[0,'u_price']=u_price
    df_bstatus.at[0,'vol_bal']=vol_bal
    df_bstatus.at[0,'vol_trn']=vol_trn
    df_bstatus.at[0,'prev_low']=prev_low
    df_bstatus.at[0,'prev_hi']=prev_hi
    
    if not((Mani=='db') or (Mani == 'ib')):#20240714
        supo = 0
        
    if not((Mani=='ds') or (Mani == 'is')):#20240714
        resi = 0
            
        
    df_bstatus.at[0,'resi']=resi #240515
    df_bstatus.at[0,'supo']=supo #240515
    df_bstatus.at[0,'pair']=C_pair #240519


    # 現在の1行をlogに追加
    if cond_TEST:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog_.xlsx")
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog_.xlsx',index=False)
    else:
        df_bstatuslog = pd.read_excel(patha + "B_statuslog.xlsx")
        df_bstatuslog = pd.concat([df_bstatuslog,df_bstatus.loc[0:0,:]],ignore_index = True)
        df_bstatuslog.to_excel(patha + 'B_statuslog.xlsx',index=False)
        
    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:    
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)
        
## ------------------------------ ##
##   Status Update without log    ##
## ------------------------------ ##   
 
else:
    #print('ELSE')                                         ############################################## 
    date = today
    df_bstatus.at[0,'date'] =date 
    df_bstatus.at[0,'prevP']=newP #20240522 
    
    if cond_TEST:
        df_bstatus.to_excel(patha + "B_status_.xlsx",index=False)
    else:
        df_bstatus.to_excel(patha + 'B_status.xlsx',index=False)        

    # ----- notBUY notSELL notCon_to -- UNFILLED 対策 ------        
    FULFIL = False    # False to no_Check/ True to check 
    if FULFIL==True:
        count = 1
        count,id = checkNwait(count,FULFIL,countMAX)
        if count==countMAX +1:
            cancel(id,C_pair)        
        
        
        
        
#-----TEST----
print(today,'v1.21-104','count FULFIL lk' ,count,FULFIL,lk)
print('/pair',C_pair,'/Ma',Mani,'/pMan',prev_Mani,'/Con_to',Con_to,'/BUY',BUY,'/SELL',SELL,'/newP',newP,'/prevP',prevP,'delP',f"{delP:.3f}")
print('/momR',momR,'/tmomR',f"{tmomR:.4f}",'vicR',vicR,'tvicR',f"{tvicR:.4f}",'/prev_low',prev_low,'/prev_hi',prev_hi,'sup',supo,'res',resi,'p_t',p_time,'\n')
# -----------
##################### コメント ##########################
# elif all OK
# SELL/BUY/Con_to/ELSE OK
# check point #off