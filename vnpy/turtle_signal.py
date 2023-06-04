from vnpy_ctastrategy import CtaTemplate, StopOrder, TickData, BarData, TradeData, OrderData, ArrayManager,BarGenerator
from vnpy.trader.constant import Direction, Offset


class TurtleSignal(CtaTemplate):
    '海龟信号策略'
    # 参数
    entry_window: int = 20
    exit_window: int = 10
    n_window: int = 20
    trading_size: int = 1

    # 变量
    # 入场通道
    entry_up: float = 0.0
    entry_down: float = 0.0
    # 出场通道
    exit_up: float = 0.0
    exit_down: float = 0.0
    # 波动度量
    n: float = 0.0
    # 开仓价
    long_entry: float = 0.0
    short_entry: float = 0.0

    parameters = ["entry_window", "exit_window", "n_window", "trading_size"]
    variables = ["entry_up", "entry_down", "exit_up", "exit_down", "n", "long_entry", "short_entry"]

    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(self, cta_engine, strategy_name, vt_symbol, setting)
        self.am = ArrayManager()

    def on_init(self) -> None:
        self.write_log('策略初始化')
        self.load_bar(20)

    def on_start(self) -> None:
        pass

    def on_stop(self) -> None:
        pass

    def on_tick(self, tick: TickData) -> None:

        pass

    def on_bar(self, bar: BarData) -> None:
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        # 全撤之前的委托
        self.cancel_all()

        # 基于numpy数组计算通道上下轨

        # 只有在没有仓位时,才更新入场通道位置和波动度量
        if not self.pos:
            self.entry_up, self.entry_down = self.am.donchian(self.entry_window)
            self.n = self.am.atr(self.n_window)

        self.exit_up, self.exit_down = self.am.donchian(self.exit_window)

        self.entry_up = self.am.high[-self.entry_window:].max()
        self.entry_down = self.am.low[-self.entry_window:].min()

        # 突破入场写法
        if not self.pos:
            self.send_long_orders()
            self.send_short_orders()
        elif self.pos > 0:
            # 发送加仓委托
            self.send_long_orders()
            # 计算固定止损价格
            long_stop: float = self.long_entry - 2 * self.n
            # 和离场通道比较,取更高价挂出停止单
            long_stop = max(long_stop, self.exit_down)
            self.sell(long_stop, self.pos, stop=True)
        else:
            self.send_short_orders()

            short_stop: float = self.short_entry + 2 * self.n
            short_stop = min(short_stop, self.exit_up)
            self.cover(short_stop, abs(self.pos), stop=True)

    def on_trade(self, trade: TradeData) -> None:
        # 成交推送
        # 记录开仓价格
        if trade.offset == Offset.OPEN:
            # 区分多空开仓
            if trade.direction == Direction.LONG:
                self.long_entry = trade.price
            else:
                self.short_entry = trade.price

    def on_order(self, order: OrderData) -> None:
        # 委托推送
        pass

    def send_long_orders(self):
        # 多头委托
        # 初始入场
        if self.pos < self.trading_size:
            self.buy(self.entry_up, self.trading_size, stop=True)

        # 第一次加仓
        if self.pos < self.trading_size * 2:
            self.buy(self.entry_up + self.n * 0.5, self.trading_size, stop=True)

            # 第二次加仓
        if self.pos < self.trading_size * 3:
            self.buy(self.entry_up + self.n * 1, self.trading_size, stop=True)
        # 第三次加仓

        if self.pos<self.trading_size*4:
            self.buy(self.entry_up+self.n*1.5,self.trading_size,stop=True)

    def send_short_orders(self):
        # 空头委托
        # 初始入场
        if self.pos >- self.trading_size:
            self.short(self.entry_down, self.trading_size, stop=True)

        # 第一次加仓
        if self.pos >- self.trading_size * 2:
            self.buy(self.entry_down - self.n * 0.5, self.trading_size, stop=True)

            # 第二次加仓
        if self.pos >- self.trading_size * 3:
            self.buy(self.entry_down -self.n * 1, self.trading_size, stop=True)
        # 第三次加仓

        if self.pos >- self.trading_size * 4:
            self.buy(self.entry_down - self.n * 1.5, self.trading_size, stop=True)

class TurtleFactor:
    #海龟因子
    def __init__(self,entry_window:int,exit_window:int,n_window:int,trading_size:int)->None:
        #工具
        self.am=ArrayManager()
        self.bg=BarGenerator()
        #参数
        self.entry_window=entry_window
        self.exit_window=exit_window
        self.n_window=n_window
        self.tradeing_size=trading_size
        #变量
        self.entry_up:float=0.0       #入场通道
        self.entry_down:float=0.0

        self.exit_up:float=0.0         #出场通道
        self.exit_down:float=0.0

        self.n:float=0                  #波动度量

        self.long_entry:float=0.0      #开仓价格
        self.short_entry:float=0.0
