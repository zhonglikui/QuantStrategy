import requests
from datetime import datetime
from pytz import timezone
from time import sleep

from vnpy.trader.object import BarData
from vnpy.trader.constant import Exchange, Interval

CHINA_TZ = timezone('Asia/Shanghai')
base = "https://fapi.binance.com"
endpoint = "/fapi/v1/time"
url = base + endpoint
r = requests.get(url)
print(r.json())


# endpoint="/fapi/v1/exchangeInfo"
# url=base+endpoint
# r=requests.get(url)
# print(r.json())

# endpoint = "/fapi/v1/klines"
# params = {"symbol": "ETHUSDT", "interval": "1m"}
# url = base + endpoint
# r = requests.get(url, params=params)
# data = r.json()
# print(data[0])


def download_binance_minute_data(symbol: str, start: str, end: str):
    base = "https://fapi.binance.com"
    endpoint = "/fapi/v1/klines"

    url = base + endpoint

    start_dt = datetime.strptime(start, "%Y%m%d")
    start_dt = CHINA_TZ.localize(start_dt)

    end_dt = datetime.strptime(end, "%Y%m%d")
    end_dt = CHINA_TZ.localize(end_dt)

    # 查询缓存变量
    bar_data = {}  # 使用字典对时间戳去重
    finished = False
    while True:
        params = {"symbol": symbol, "interval": "1m", "startTime": int(start_dt.timestamp() * 1000), "limit": 1000}
        r = requests.get(url, params=params)
        data = r.json()

        if data:
            for item in data:
                dt = datetime.fromtimestamp(item[0] / 1000)
                bar = BarData(symbol=symbol,
                              exchange=Exchange.BINANCE,
                              datetime=CHINA_TZ.localize(dt),
                              interval=Interval.MINUTE,
                              open_price=float(item[1]),
                              high_price=float(item[2]),
                              low_price=float(item[3]),
                              close_price=float(item[4]),
                              volume=float(item[5]),
                              gateway_name="BINANCE")
                bar_data[bar.datetime] = bar
            print(start_dt, bar.datetime)  # 打印本轮查询范围
            start_dt = bar.datetime
        else:
            finished = True

        if finished:
            break

    dts = list(bar_data.keys())
    dts.sort()


    return [bar_data[dt] for dt in dts]

data = download_binance_minute_data("ETHUSDT","20230101","20230109")
print(data[0])
print(data[-1])

endpoint = "/fapi/v1/ticker/bookTicker"
url = base + endpoint
params = {"symbol": "ETHUSDT"}
r = requests.get(url, params=params)
print(r.json())
while True:
    r = requests.get(url, params=params)
    d = r.json()
    symbol = d["symbol"]
    bp = d["bidPrice"]
    bq = d["bidQty"]
    ap = d["askPrice"]
    aq = d["askQty"]
    time = d["time"]

    msg = f"{symbol}: 买价{bp}[{bq}] 卖价{ap}[{aq}] "
    print(msg)
    sleep(30)
