from datetime import datetime

from vnpy.trader.optimize import OptimizationSetting
import warnings
from vnpy_ctastrategy.backtesting import BacktestingEngine
from turtle_signal import TurtleSignal
from vnpy.trader.database import get_database
import pandas as pd
from time import perf_counter


# 批量回测
warnings.filterwarnings('ignore')

database = get_database()

overviews = database.get_bar_overview()
vt_symbols = ["{o.symbol}.{o.exchange.value}" for o in overviews if "99" in o.symbol]
vt_symbols = set(vt_symbols)
vt_symbols = list(vt_symbols)


def empty_output(msg):
    pass


# 遍历收集结果
result = []
for vt_symbol in vt_symbols:
    # 创建回测引擎
    engine = BacktestingEngine()
    engine.output = empty_output
    # 设置回测参数
    engine.set_parameters(vt_symbol=vt_symbol, interval='day', start='2022.1.1', end='2022.9.30', rate=0.0001,
                          slippage=0, size=100, pricetick=0.01, capital=1_000_000)
    engine.add_strategy(TurtleSignal, {})
    # 加载数据回测
    engine.load_data()
    engine.run_backtesting()
    # 计算逐日盈亏
    df = engine.calculate_result()
    # 计算统计结果
    d = engine.calculate_statistics()
    # 输出图表
    # engine.show_chart()
    result[vt_symbol] = d

#转为dataFrame查看
df=pd.DataFrame.from_dict(result)
df=df.T
df.sort_values(by='sharpe_ratio')

#用map执行遍历
start=perf_counter()
data=list(map(run_backtesting,vt_symbols))
end=perf_counter()
print("耗时",end-start,"毫秒")

