from  datetime import datetime,time,timedelta
from typing import List,Set,Tuple
from time import sleep

import rqdatac
from vnpy.trader.object import HistoryRequest, BarData
from vnpy.trader.constant import Exchange,Interval
from vnpy.trader.datafeed import get_datafeed,BaseDatafeed
from vnpy.trader.database import get_database,BaseDatabase
# 初始化
datafeed:BaseDatafeed=get_datafeed()
datafeed.init()
database:BaseDatabase=get_database()
# 定义要下载的数据
suffix_list:List[str]=['888','999']
interval:Interval=Interval.DAILY
start:datetime=datetime(2022,1,1)
end:datetime=datetime.now()

def download_data(symbol:str,exchange:Exchange,interval:Interval,start:datetime,end:datetime)->bool:
    # 下载并将数据写入数据库
    req=HistoryRequest(symbol=symbol,exchange=exchange,interval=interval,start=start,end=end)
    bars:List[BarData]=datafeed.query_bar_history(req)
    if bars:
        database.save_bar_data(bars)
        return True
    else:
        return False

def get_products()->Set[Tuple[str,Exchange]]:
    # 查询期货品种信息
    products=set()
    df=rqdatac.all_instruments(type='Future')
    for _,row in df.iterrows():
        product=(row.underlying_symbol,Exchange(row.exchange))
        products.add((product))
    return products

def run_task()->None:
    # 执行遍历下载任务
    products:set=get_products()
    success:list=[]
    fail:list=[]
    for prefix,exchange in products:
        if exchange in {Exchange.DCE,Exchange.SHFE}:
            prefix=prefix.lower()

        for suffix in suffix_list:
            symbol=prefix+suffix
        r=download_data(symbol,exchange,interval,start,end)

        if r:
            success.append(symbol)
        else:
            fail.append(symbol)

    if success:
        print('下载成功',success)
    else:
        print('下载失败',fail)

def task_time()->None:
    task_time:time=time(16,30)
    last_run:datetime=None
    while True:
        sleep(10)
        now:datetime=datetime.now()
        # 如果今日已经运行过则无需再次运行
        if last_run and last_run.date()==now.date():
            continue
            # 时间未到无需运行
        if now.time()<task_time:
            continue
            # 记录本轮运行时间
        last_run=now
        print(f'执行任务时间{now},下载范围{start}-{end},数据周期{interval}')
    # 执行下载任务
    run_task()
    # 更新下次下载开始时间
    start=now-timedelta(days=7)