from datetime import datetime

from vnpy.trader.optimize import OptimizationSetting
import warnings
from vnpy_ctastrategy.backtesting import BacktestingEngine
from turtle_signal import TurtleSignal

warnings.filterwarnings('ignore')
# 创建回测引擎
engine = BacktestingEngine()
# 设置回测参数
engine.set_parameters(vt_symbol='I2210.SHFE', interval='day', start='2022.1.1', end='2022.9.30', rate=0.0001,
                      slippage=0, size=100, pricetick=0.01, capital=1_000_000)
# 添加策略

setting = {"entry_window": 17, "exit_window": 14, "n_window": 10}
engine.add_strategy(TurtleSignal, {})
# 加载数据回测
engine.load_data()
engine.run_backtesting()
# 计算逐日盈亏
df = engine.calculate_result()
# 计算统计结果
engine.calculate_statistics()
# 输出图表
engine.show_chart()

# 创建优化设置
setting = OptimizationSetting()
# 目标函数为sharpe_ratio
setting.set_target("sharpe_ratio")
# 包括出入场三个参数
setting.add_parameter("entry_window", 15, 25, 1)
setting.add_parameter("exit_window", 5, 15, 1)
setting.add_parameter("n_window", 10, 30, 2)
#执行穷举优化
engine.run_bf_optimization(setting)
