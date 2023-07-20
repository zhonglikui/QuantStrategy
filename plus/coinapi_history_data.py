from typing import Optional,List,Dict
from datetime import datetime,timedelta
import requests
import json
from time import time
from peewee import chunked

from vnpy.trader.database import database_manager
from vnpy.trader.constant import Interval
from vnpy.trader.object import BarData, HistoryRequest
from vnpy.trader.utility import TZ_INFO,get_local_datetime,extract_vt_symbol

COINAPI_HOST = "https://rest.coinapi.io"
EXCHANGE_MAP = {
    "BINANCES":"BINANCE"
}
#------------------------------------------------------------------------------------
def to_ca_symbol(symbol:str, exchange:str):
    """
    将交易所代码转换为CoinAPI代码
    """
    filter_ = symbol.split("-")
    symbol = f"{filter_[0]}_{filter_[1]}"
    exchange = EXCHANGE_MAP.get(exchange.value,exchange.value)
    return f"{exchange}_PERP_{symbol}".upper()
#------------------------------------------------------------------------------------
class CoinapiData:
    """
    CoinAPI数据服务接口
    """
    #------------------------------------------------------------------------------------
    def __init__(self):
        """"""
        self.password: str = "XXX"
        self.headers = {"X-CoinAPI-Key": self.password}
    #------------------------------------------------------------------------------------
    def get_all_symbols(self,symbol:str,exchange:str):
        url = COINAPI_HOST + "/v1/symbols"
        params = {
            "filter_symbol_id":symbol,
            "filter_exchange_id": exchange,
            "filter_asset_id":"USDT",
        }
        response = requests.request(
            method="GET",
            url=url,
            params=params,
            headers=self.headers
        )

        if response.status_code != 200:
            print(f"获取合约列表出错，错误信息：{response.text}")
            return None
        data = json.loads(response.text)
        print(f"交易所合约列表：{data}")
    #------------------------------------------------------------------------------------
    def query_bar_history(self,vt_symbol:str,start:datetime,end:datetime) -> Optional[List[BarData]]:
        """
        查询k线数据
        """
        symbol,exchange,gateway_name = extract_vt_symbol(vt_symbol)

        symbol_id = to_ca_symbol(symbol, exchange)
        period_id = "1MIN"
        url = COINAPI_HOST + f"/v1/ohlcv/{symbol_id}/history?"
        history = []
        limit = 10000
        time_consuming_start = time()
        while True:
            time_start = datetime.strftime(start, "%Y-%m-%dT%H:%M:%S")
            params = {
                "period_id": period_id,
                "time_start": time_start,
                "limit": limit,
            }

            response = requests.request(
                method="GET",
                url=url,
                params=params,
                headers=self.headers
            )

            if response.status_code != 200:
                print(f"获取合约：{vt_symbol}历史数据出错，错误信息：{response.text}")
                return None

            bars: List[BarData] = []
            
            data = json.loads(response.text)
            if not data:
                print(f"未获取到合约：{vt_symbol}历史合约数据")
                return
            for d in data:
                dt = get_local_datetime(d["time_period_start"])

                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=Interval.MINUTE,
                    datetime=dt,
                    open_price=d["price_open"],
                    high_price=d["price_high"],
                    low_price=d["price_low"],
                    close_price=d["price_close"],
                    volume=d["volume_traded"],
                    gateway_name=gateway_name,
                )
                bars.append(bar)
            start = bar.datetime
            history.extend(bars)
            if (datetime.now(TZ_INFO) - start).total_seconds() < 600:
                break
        if not history:
            msg = f"未获取到合约：{vt_symbol}历史数据"
            print(msg)
            return
        for bar_data in chunked(history, 10000):               #分批保存数据
            try:
                database_manager.save_bar_data(bar_data,False)      #保存数据到数据库  
            except Exception as err:
                print(f"{err}")
                return
        time_consuming_end =time()        
        query_time = round(time_consuming_end - time_consuming_start,3)
        msg = f"载入{vt_symbol}:bar数据，开始时间：{history[0].datetime} ，结束时间： {history[-1].datetime}，数据量：{len(history)}，耗时:{query_time}秒"
        print(msg)
if __name__ == "__main__":
    end = datetime.now()
    start = end - timedelta(10)
    vt_symbols = ["APT-USDT_OKEX/OKEX"]
    data = CoinapiData()
    # 获取合约列表
    #data.get_all_symbols("APT","OKEX")
    #下载历史数据
    for vt_symbol in vt_symbols:
        data.query_bar_history(vt_symbol,start,end)