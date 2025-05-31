# 2021/11/10:
# "BitBank_TESTv01.py"
# BUY logic & Defの利用、local & Global variables
# SELL LC & SP

# ------- library -----------
#import python_bitbankcc
import pandas as pd
import numpy as np
import json
import datetime
#import talib as ta
from datetime import datetime
from datetime import date
from datetime import timedelta
import pandas.tseries.offsets as offsets
# ------- Library loading


#---------- Operational Constants　-----------
C_profR = 0.02 #  = Mxprof/Bp Bp;100, newP;102
C_LCr = 0.98 #    = newP  /Bp Bp;100, newP;98
C_volume = 1
C_short =60
C_long =120

C_Pr_h = 0.04 
C_Pr_m = 0.025
C_Pr_l = 0.02
C_SPr_h = 0.9
C_SPr_m = 0.7
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
#pathb = '/Users/suusan/CloudStation/☆☆K_Trade/data/'

#write_file : "ave_x5min_TBD_t.xlsx"
#write_file : "BB_statuslog_t.xlsx"

trd1 = 'up'
trd2 = 'dn'
trd3 = 'eq'


## ### ## -------------------------------- ##### ## ##
## ### ##       INPUT:FILE READING         ##### ## ##
## ### ## -------------------------------- ##### ## ##


df_status = pd.read_excel(patha +'BB_statusT.xlsx')
df_statuslog = pd.read_excel(patha +'BB_statuslogS.xlsx')
df_smma = pd.read_excel(patha +'ave_x5min_TBD.xlsx')
df_mx = pd.read_excel(patha +'df_mx_TBD.xlsx')
ln_dfsmma=len(df_smma)

# ---------- set BB_status to vars ----------2022/09/24

date = df_status.loc[0,'date']     #date of update
Bp = df_status.loc[0,'Bp']         #price of Bought
Bdate = df_status.loc[0,'Bdate']   #date of Bought
volume = df_status.loc[0,'volume'] #volume of Bought
Pdate = df_status.loc[0,'Pdate']   #date of past max profit
profP = df_status.loc[0,'profP']   #price of past max profit
LCp = df_status.loc[0,'LCp']       #Loss Cut price
LCr = df_status.loc[0,'LCr']       #Loss Cut price rate
SPr = df_status.loc[0,'SPr']       #Shrink Profit rate
prevP = df_status.loc[0,'prevP']   #every time previous price
Sdate = df_status.loc[0,'Sdate']   #date of sell
zone = df_status.loc[0,'zone']     #every time zone
Hzone = df_status.loc[0,'Hzone']   #zone at Highest 2021/07/07 Name Changed
Manu = df_status.loc[0,'Manu']     #Manual execution
Auto = df_status.loc[0,'Auto']     #Auto operation
Prof = df_status.loc[0,'Prof']     #Prof = newP - Bp -comm

def SPrate(profP,Bp):
    profR =0
    SPr =0
    if Bp > 0:
        profR = (profP - Bp)/Bp
        
    if (C_Pr_l<=profR)and(profR < C_Pr_m):
        SPr = C_SPr_l
    if (C_Pr_m<=profR)and(profR < C_Pr_h):
        SPr = C_SPr_m
    if C_Pr_h<=profR:
        SPr = C_SPr_h
    return SPr


def zone_set(newP):
    zone = 'none'
    if newP >= mx:
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
    return zone

def set_var_buy(iter):
    global date,Bp,Bdate,volume,Pdate,profP,LCp,LCr,SPr,prevP,Sdate,zone,Hzone,Manu,Auto,Prof
    date = df_smma.at[iter,'date'] 
    Bp =  df_smma.at[iter,'Close']
    Bdate = date
    volume = C_volume
    Pdate = date
    profP = Bp
    LCp = Bp * C_LCr
    LCr = C_LCr
    SPr 
    prevP = Bp
    Sdate = ''
    zone
    Hzone = zone
    Manu
    Auto# = conds
    Prof = 0

def set_var_sell(iter):
    global date,Bp,Bdate,volume,Pdate,profP,LCp,LCr,SPr,prevP,Sdate,zone,Hzone,Manu,Auto,Prof    
    date = df_smma.at[iter,'date'] 
    last_Bp = Bp #2021/11/09
    Bp =  0
    Bdate = ''
    volume = 0
    Pdate = ''
    profP = 0
    LCp = 0
    LCr = 0
    SPr = 0
    prevP = newP
    Sdate = date
    zone 
    Hzone = ''
    Manu = 'go'
    Auto# = conds
    Prof = (newP*(1-0.002) - last_Bp*(1+0.002))* C_volume  #2021/11/09

def set_var_keep(iter):
    global date,Bp,Bdate,volume,Pdate,profP,LCp,LCr,SPr,prevP,Sdate,zone,Hzone,Manu,Auto,Prof
    date = df_smma.at[iter,'date'] 
    Bp 
    Bdate 
    volume
    Pdate
    profP 
    LCp
    LCr
    SPr
    prevP = df_smma.at[iter,'Close']
    Sdate = ''
    zone 
    Hzone
    Manu 
    Auto# = conds
    Prof = 0

def setVars_BB_status():
    df_status.loc[0,'date'] = date     #date of update
    df_status.loc[0,'Bp'] = Bp         #price of Bought
    df_status.loc[0,'Bdate'] = Bdate   #date of Bought
    df_status.loc[0,'volume'] = volume #volume of Bought
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

#BB_statuslog.columns
#'date'
#'Bp', 
#'Bdate', 
#'volume', 
#'Pdate', 
#'profP', 
#'LCp', 
#'LCr', 
#'SPr',
#'prevP', 
#'Sdate', 
#'zone', 
#'Hzone', 
#'Manu', 
#'Auto', 
#'Prof'],

df_smma_t= df_smma
df_smma_t['zone']="z1"
ln_smma = len(df_smma_t)



# -------　関数 * 現在zone判断 ------
###  "ln-1" is range starts from zero_0
        
# df_smmaに列zoneを追加　df_smma_t
i = 0
# ----- set figs to vars --------
ln_smma = len(df_smma)
for i in range(ln_smma-1):
    date=df_smma.at[i,'date']
    mx=df_smma.at[i,'Max']
    Zu=df_smma.at[i,'Zu']
    ave=df_smma.at[i,'Ave']
    Zd=df_smma.at[i,'Zd']
    mn=df_smma.at[i,'Min']
    
    newP = df_smma.at[i,'Close']
    df_smma_t.at[i,'zone']=zone_set(newP)

df_smma_t.to_excel('df_smma_t.xlsx')

###### --------------------------- ######
###### ----  BUY Conditions  ----- ######
###### --------------------------- ######


def fBcon1(iter):
    global date,zone,zone_0,Min0,Min1,speed_0,speed_1,waveS,waveL,rsi_chk,macd
    date = df_smma_t.at[iter,'date']
    zone = df_smma_t.at[iter,'zone']
    Min0 = df_smma_t.at[iter,'Min']
    speed_1 = df_mx.at[iter,'speed']
    waveS = df_mx.at[iter,'wave_s']
    waveL = df_mx.at[iter,'wave_l']
    rsi_chk = df_smma_t.at[iter,'rsi']
    macd = df_smma_t.at[iter,'macd']

    
    if iter >= 1:
        zone_0 = df_smma_t.at[iter-1,'zone']
        Min1 =  df_smma_t.at[iter-1,'Min']
        speed_0 = df_mx.at[iter-1,'speed']   
    else:
        zone_0 = ''
        Min1 = ''
        speed_0 = 0
     #return date0,zone,zone_0,Min0,Min1

    
def fScon1(iter):
    global aaa
    newP = df_smma.at[iter,'Close']
    profP = 0
    
# -----  ------------ ------ #
# -----  Buy and Sell ------ #
# -----  ------------ ------ #

for i in range(ln_smma-1):
    fBcon1(i)
    newP = df_smma.at[i,'Close']

# ###################################
# ##### Auto BUY Process Starts #####
# ###################################
    Bcon1 = False # z4, Min0 = Min1, Speed>0 に該当するか？
    Bcon1A = False # z4
    Bcon1B = False # Min0=Min1
    Bcon1C = False # Speed>0
    Bcon1D = False # waves>0 wavel>0

    Bcon2 = False # macd -0.4
    Bcon3 = False # 欠番：waveチェック
    Bcon4 = False # 欠番：z1に該当するか？
    Bcon5 = False # 欠番：Max0 < Max1になっているか？
    Bcon6 = False # quick buy
    BconTeck = False # Technical Check

## --------------- zone == z4,z3 -----------------
    if (zone == 'z3')or(zone == 'z4')or(zone_0=='z4')or(zone_0=='mn'):
        Bcon1A = True       
## ---------------- Min0 == Min1 --------------
#ln = len(df_smma)
    if Min0==Min1:
        Bcon1B = True
## ------------ Price going up  ---------------
    if speed_1>0 :
        Bcon1C = True   

## ------------ Wave Check Down not buy -------
    if (waveS<0) and (waveL<0):
        Bcon1D = False
    else:
        Bcon1D = True

## ------------ Technical Check -----------------#

    if rsi_chk <= 30:# rsi < 30 to Buy
        BconTeck = True #Buy
    else:
        BconTeck = False #Not Buy

    Bcon1 = Bcon1A and Bcon1B and Bcon1C and Bcon1D

## ------------ macd check ---------------
    if (macd <-0.4) and Bcon1A and Bcon1C:
        Bcon2 = True

# BUYの条件記録をするが、すでにhold_1=1の場合は0も1も代入しない
    log_volume = df_statuslog.at[i,'volume']#2021/11/09
    if (Bcon1 or Bcon2) and (log_volume ==0 ):#2021/11/09
        BUY = True
        df_smma_t.at[i,'hold']=1
    else:
        BUY = False
        df_smma_t.at[i,'hold']=0


## ######################################################
## ########### Auto Selling Process Starts ##############
## ######################################################
    if df_smma_t.at[i,'hold']==0:
        None
    else:
        fScon1(i)
# ------- ------------------------ ----
# ------- check selling conditions ----
# -------------------------------------
    Scon1 = False # Shrink Profit
    Scon2 = False # Loss Cutting
    Scon3 = False # No Use :z1 to z2
    Scon4 = False # No Use :Max1 = Max2
    Scon5 = False # No Use :time nomonate
    Scon6 = False # quick sell    

    SPr = SPrate(profP,Bp)

# ------- check price increase
# ------- 'volume > 0' check 
    if (newP > profP) and (volume > 0):
        profP = newP
        Hzone = zone
        Pdate = df_smma.at[i,'date']

## ------- Loss Cut & Shrink Profit check ------
    if Bp == 0: #2021/09/21
        Bp = newP
    preprof = newP - Bp
    preprofR = preprof/Bp
    Maxprof = profP - Bp
    profR = Maxprof/Bp
    permitP = Mxprof*SPr + Bp
    
    if i>1 :
        prevMin = df_smma.loc[i-1,'Min']
    else:
        prevMin = df_smma.loc[i,'Min']

    thisMin = df_smma.loc[i,'Min']


    if profR > C_profR:
## ------- Proft Shrink --------                            
        if preprof <= Maxprof*SPr:
            Scon1 = True
    else:
## ------- Loss Cutting --------               
        if newP/Bp <= LCr:
            Scon2 = True
            



## ------- Loss Cutting2 :Floor down --------
#    if thisMin < prevMin:
#        Scon2 = True

        
    
## ------- Max1 == Max2 --------
#    ln = len(df_smma)
#    Max0 =df_smma.loc[ln_smma-2,'Max']
#    Max1 =df_smma.loc[ln_smma-1,'Max']

    if log_volume > 0:
        SELL = Scon1 or Scon2
    else:
        Bp = 0
        SELL = False 

    if BUY:
        set_var_buy(i)
    elif SELL:
        set_var_sell(i)
    else:
        set_var_keep(i)
    
    setVars_BB_status()
    df_statuslog = pd.concat([df_statuslog,df_status],ignore_index = True)


    
    
df_statuslog.to_excel('BB_statuslogT.xlsx')    
df_smma_t.to_excel('df_smma_t.xlsx')
    
    
    ## ------- z1 down to z2 ----------
#if (zone == 'z2') and ((Hzone =='z1')or(Hzone == 'mx')):
#    Scon3 = True



# "BitBank_TESTvxx.py"