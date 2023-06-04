from vnpy.trader.datafeed import get_datafeed
from vnpy.trader.object import HistoryRequest
from vnpy.trader.constant import Interval,Exchange
from vnpy.trader.database import get_database
from datetime import datetime
from time import perf_counter
import warnings
from vnpy.trader.setting import SETTINGS
warnings.filterwarnings('ignore')
# SETTINGS['datafeed.name']='tqsdk'
# SETTINGS['datafeed.username']='tqsdk'
# SETTINGS['datafeed.password']='tqsdk'
datafeed=get_datafeed()
datafeed.init()
# datafeed.query_bar_history()
# datafeed.query_tick_history()
req=HistoryRequest(symbol='rb2210',exchange=Exchange.SHFE,interval=Interval.MINUTE,start=datetime(2022,1,1),end=datetime(2022,9,30))
bars=datafeed.query_bar_history(req)
database=get_database()
if bars:
    database.save_bar_data(bars)
    print('下载成功',req.symbol,req.exchange,req.interval,bars[0].datetime,bars[-1].datetime)
start=perf_counter()
data=database.load_bar_data(symbol=req.symbol,exchange=req.exchange,interval=req.interval,start=req.start,end=req.end)
end=perf_counter()
print('读取耗时{}秒'.format((end-start)))