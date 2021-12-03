from bybit import bybit
from bybit.constants import INTERVAL
import pandas as pd 
from datetime import datetime,timedelta
import time


bb=bybit.Bybit()

# h1:8760
#h4:2190
#h12:730
#15m:35040
#1m:525600
m=35040
h=8760
candles=[]
# while m>0:
#     d=datetime.now()-timedelta(minutes=m*15)
#     unix_time=int(time.mktime(d.timetuple()))
#     c=bb.kline("ETHUSDT",INTERVAL.M15,_from=unix_time,limit=200)
#     for candle in c:
#         candles.append(candle)
#     m-=200
    

while h>0:
    d=datetime.now()-timedelta(hours=h)
    unix_time=int(time.mktime(d.timetuple()))
    c=bb.kline("ETHUSDT",INTERVAL.H1,_from=unix_time,limit=200)

    for candle in c:
        candles.append(candle)
    h-=200
    

for candle in candles:
    d["high"].append(candle['high'])
    d["low"].append(candle['low'])
    d["close"].append(candle['close'])
    d["volume"].append(candle['volume'])

df = pd.DataFrame(data = d)


vol_sum = ( df["volume"].rolling(window=20).sum() ) 
# df['anchor_volume'] = df.iloc[:,1].rolling(window=20).sum()

# df['h-l'] = df['high']-df['low']

# df['|h-cp|'] = abs(df['high']-df['close'].shift(1))

# df['|l-cp|'] = abs(df['low']-df['close'].shift(1))

# df['tr'] = df[['h-l','|h-cp|','|l-cp|']].values.max(1)

# df['atr'] = df['tr'].ewm(alpha = 1/10).mean()

# df['atr']= ((df['atr'].shift(1) * 95) + df['tr'])/96

 # evwma = (evma[-1] * (vol_sum - volume)/vol_sum) + (volume * price / vol_sum)
df['eVWMA']=df.iloc[:,0]

x=(vol_sum-df['volume'])/vol_sum
y=(df['volume']*df['close'])/vol_sum

evwma=[0]

for x, y in zip(x.fillna(0).iteritems(), y.iteritems()):
            if x[1] == 0 or y[1] == 0:
                evwma.append(0)
            else:
                evwma.append(evwma[-1] * x[1] + y[1])

df['eVWMA']=pd.Series(evwma[1:], index=df.index, name="{0} period EVWMA.".format(20),)

# df['uc'] = df['eVWMA'] + 3*df['eVWMA'].rolling(20).std()
# df['lc'] = df['eVWMA'] - 3*df['eVWMA'].rolling(20).std()


df['pct_change']=df['close'].pct_change()
df['state']= df['pct_change'].apply(lambda x: 'up' if (x>.001)else('down')if (x<-0.001)else('Flat'))
df['prior_state']=df['state'].shift(1)


states=df[['prior_state','state']].dropna()
states_matrix=states.groupby(['prior_state','state']).size().unstack()

transition_matrix= states_matrix.apply(lambda x:x/float(x.sum()),axis=1)
transition_matrix
