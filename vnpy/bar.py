from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.utility import BarGenerator
from vnpy.trader.utility import ArrayManager
from vnpy.trader.constant import Interval,Exchange
from vnpy.trader.database import get_database
from datetime import datetime
from time import perf_counter
import warnings

warnings.filterwarnings('ignore')
database=get_database()
bars=database.load_bar_data(symbol='rb2210',exchange=Exchange.SHFE,interval=Interval.MINUTE,start=datetime(2022,1,1),end=datetime(2022,9,30))
print('第一条:{}'.format(bars[0]))
print('最后一条:{}'.format(bars[-1]))

def on_bar(bar):
    '一分钟k线回调'
    pass
def on_window_bar(bar):
    '窗口k线回调'
    print(bar)

# 创建实例后,合成打印5分钟K线
bg=BarGenerator(on_bar,window=5,on_window_bar=on_window_bar)
for bar in bars:
    bg.update_bar(bar)

#合成缓存10分钟K线列表
window_bars=[]
bg=BarGenerator(on_bar,window=10,on_window_bar=window_bars.append)
for bar in bars:
    bg.update_bar(bar)

for wb in window_bars[:10]:
    print(wb)

am=ArrayManager()
for bar in bars[:10]:
    am.update_bar(bar)

am.close
am.inited
am.sma(5,array=True)

