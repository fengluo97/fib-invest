# FIB-Invest: 个人量化投资平台 — 设计规格

> 版本: v1.0 | 日期: 2026-06-19 | 状态: 待审核

---

## 1. 项目概述

面向个人的量化投资平台，支持 A 股市场（架构预留多市场扩展），提供基于技术指标、因子模型和 AI/ML 策略的自动化与半自动化交易能力。

### 1.1 核心目标

- 提供从数据 → 策略 → 回测 → 模拟交易 → (未来)实盘交易的完整链路
- 三类策略并存：经典技术指标、多因子选股、AI/ML 推理
- 按策略独立配置全自动/半自动执行模式
- 先以模拟交易闭环，通过回测和模拟盘验证策略有效性

### 1.2 关键决策记录

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 架构 | 模块化单体 | 个人项目需要简单运维，但模块边界清晰便于未来扩展 |
| 技术栈 | FastAPI + React + SQLAlchemy | Python 量化生态无可替代，React 做好用看板 |
| 数据库 | SQLite 起步，可切 PostgreSQL | 零运维起步，数据量大后一行配置切换 |
| 任务队列 | arq (async Redis Queue) | AI 推理和回测异步执行，不阻塞主进程 |
| 数据源 | AKShare 首发，可插拔 | 免费起步，架构支持商业源接入 |
| 市场 | A 股优先 | 按需扩展美股/加密货币 |
| 用户 | 单用户为主 | 架构不排斥多用户 |

---

## 2. 系统架构

### 2.1 架构总览

模块化单体：一个 FastAPI 主进程 + arq 任务队列（Redis）+ 数据库。

```
┌─────────────────────────────────────────────────────────┐
│                    React 前端 (SPA)                      │
│   看板 │ 策略管理 │ 回测 │ 交易日志 │ 账户 │ 系统设置     │
├──────────────────────────┬──────────────────────────────┤
│                     FastAPI Server                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │ 行情数据  │  │策略引擎   │  │ 回测引擎  │  │ 任务队列  ││
│  │ 模块     │  │          │  │          │  │ (arq)    ││
│  │ 适配器模式│  │ 技指/因子 │  │ 逐K回放  │  │ 异步策略  ││
│  │ 可插拔源  │  │ /AI-ML   │  │ 指标/绘图 │  │ 回测/同步  ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│  ┌──────────┐  ┌──────────┐                              │
│  │ 执行模块  │  │ 风控模块  │       ┌─────────────────┐  │
│  │ 模拟/实盘 │  │ 独立规则集│       │   SQLite / PG    │  │
│  │ 订单状态机│  │ 策略熔断  │       │                 │  │
│  └──────────┘  └──────────┘       └─────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
fib-invest/
├── backend/
│   ├── app/
│   │   ├── data/          # 数据模块
│   │   ├── strategy/      # 策略模块
│   │   ├── backtest/      # 回测模块
│   │   ├── execution/     # 执行模块
│   │   ├── risk/          # 风控模块
│   │   ├── api/           # FastAPI 路由
│   │   ├── models/        # ORM 模型
│   │   └── core/          # 配置、依赖注入
│   ├── worker/            # arq 后台任务
│   └── tests/
├── frontend/              # React + TypeScript
└── docker-compose.yml     # FastAPI + Redis + DB
```

### 2.3 核心设计原则

1. **端口-适配器** — 数据源和交易通道通过统一接口接入，换实现不影响业务逻辑
2. **策略统一接口** — `Strategy.on_bar()` 是所有策略的唯一入口，引擎不关心内部实现
3. **信号不直接下单** — 信号 → 风控 → 仓位计算 → 订单生成 → 执行，每步隔离
4. **任务队列解耦** — AI/ML 策略推理、批量回测等重任务通过 arq 异步执行
5. **配置驱动** — 每个策略一个 YAML 配置文件，包含模式、参数、风险约束

---

## 3. 模块详细设计

### 3.1 数据模块

#### 职责
行情数据的获取、清洗、存储和分发。

#### 接口

```python
class DataProvider(ABC):
    """所有数据源适配器的统一接口"""
    name: str
    supports: List[str]              # ["daily", "tick", "fundamental"]

    async def get_bars(self, symbol, start, end, freq) -> pd.DataFrame
    async def get_tick(self, symbol, date) -> pd.DataFrame
    async def list_symbols(self, market) -> List[SymbolInfo]
    async def health_check(self) -> bool
```

#### 数据模型
- 股票列表：symbol, name, market, list_date, status
- 日线数据：symbol, date, open, high, low, close, volume, amount, adj_factor
- 分时数据（预留）：symbol, datetime, price, volume, direction
- 基本面数据（预留）：财报、估值指标

#### 设计要点
- **同步策略**：arq 定时任务每日 15:30 同步，仅同步关注标的
- **缓存**：内存缓存热点数据，减少对 AKShare 的请求频率
- **复权**：存储原始数据 + 复权因子，按需计算前/后复权价
- **扩展**：新数据源只需实现 `DataProvider` 并注册
- **市场隔离**：`market` 字段编码（sh/sz），新市场加枚举值

### 3.2 策略引擎

#### 职责
策略的抽象定义、实例化、运行和信号产生。

#### 接口

```python
class Strategy(ABC):
    name: str
    frequency: str                  # "daily" | "minute"
    symbols: List[str]
    mode: str                       # "auto" | "semi-auto"
    risk_profile: dict

    async def on_start(self): ...   # 初始化、加载模型
    async def on_bar(self, bar: pd.Series) -> Signal | None: ...
    async def on_stop(self): ...    # 清理
```

#### Signal 数据结构

```python
@dataclass
class Signal:
    strategy_id: str
    symbol: str
    direction: str                  # BUY | SELL | HOLD
    strength: float                 # 0~1 置信度/强度
    reason: str                     # 人类可读原因
    meta: dict                      # 策略自定义数据
```

#### 策略分类

| 类型 | 说明 | 示例 |
|------|------|------|
| 技术指标策略 | 基于经典技术分析指标 | 均线交叉、MACD、布林带、RSI |
| 因子策略 | 基于多因子模型选股 | 动量、质量、估值、成长因子 |
| AI/ML 策略 | 基于机器学习/AI 模型 | LLM 新闻分析、XGBoost 预测、强化学习 |

#### 设计要点
- **策略注册表** (`StrategyRegistry`)：维护所有可用策略类型
- **策略管理器** (`StrategyManager`)：管理运行中策略的生命周期
- **Config 化**：每个策略一个 YAML 配置，热加载配置变更
- **AI 策略异步**：AI 推理通过 arq Worker 执行，不阻塞主数据流
- **信号去重**：同一策略对同一标的的同方向信号，N 根 K 线内去重

### 3.3 回测引擎

#### 职责
在历史数据上回放策略，评估绩效。

#### 流程

```
策略实例 + 日期区间 + 初始资金 + 手续费
    → 历史数据加载
    → 数据预热（策略指标计算期）
    → 逐 K 回放（策略.on_bar() 产生信号）
    → 模拟撮合（滑点/手续费/涨跌停限制）
    → 性能统计 + 权益曲线
```

#### 核心绩效指标

| 类别 | 指标 |
|------|------|
| 收益 | 总收益率、年化收益率、超额收益 |
| 风险 | 最大回撤、年化波动率、下行波动率 |
| 风险调整 | 夏普比率、索提诺比率、卡玛比率 |
| 交易统计 | 胜率、盈亏比、最大连胜/连败、换手率 |
| 其他 | 总交易次数、日均交易、平均持仓周期 |

#### 设计要点
- **时序安全**：逐 K 回放保证策略不会"看到未来"
- **撮合规则**：可配置滑点（固定/百分比）、手续费率、最小交易单位（A 股 100 股整手）、涨跌停限制
- **预热期**：数据前 N 根 K 线用于策略初始化技术指标，不产生信号
- **结果输出**：交易记录 DataFrame + 权益曲线 + 回撤曲线 + 交易标记
- **参数扫描预留**：架构支持网格搜索，输出不同参数组合绩效对比

### 3.4 执行模块

#### 职责
信号 → 订单的转换、订单生命周期管理、与交易通道的对接。

#### 订单管线

```
Signal → 风控审批 → 仓位计算 → 订单生成 → 提交执行
```

#### 双模式控制

```python
class ExecutionPipeline:
    async def process_signal(signal, strategy_config):
        mode = strategy_config['mode']  # 'auto' | 'semi-auto'

        # 风控过滤（所有模式必经）
        if not risk_engine.approve(signal):
            return

        order = order_builder.build(signal)
        order.status = 'pending' if mode == 'semi-auto' else 'ready'

        if mode == 'auto':
            await broker.submit(order)
        # semi-auto: 前端展示 pending 订单，等人工确认
```

#### BrokerAdapter 接口

```python
class BrokerAdapter(ABC):
    name: str

    async def submit_order(self, order) -> OrderResult
    async def cancel_order(self, order_id) -> bool
    async def query_positions(self) -> List[Position]
    async def query_account(self) -> AccountInfo
    async def query_orders(self, date) -> List[Order]
```

#### 订单状态机

```
pending → ready → submitted → partial_filled → filled
                          ↘ cancelled
```

- **semi-auto** 策略：信号生成后停留在 `pending`，等人工变更到 `ready`
- **auto** 策略：风控通过直接 `ready` → `submitted`
- **模拟适配器**：不连接真实券商，本地撮合，记录到数据库
- **实盘适配器（未来）**：实现 `BrokerAdapter` 接口对接券商 API

### 3.5 风控模块

#### 职责
独立的风险控制层，所有信号必经，不可绕过。

#### 风控规则接口

```python
class RiskRule(ABC):
    name: str
    severity: str                    # "block" | "warn" | "limit"

    def evaluate(self, signal, portfolio, context) -> RiskResult: ...

@dataclass
class RiskResult:
    passed: bool
    message: str
    adjusted_quantity: int | None    # limit 场景下调后的数量
```

#### 内置规则（首批）

| 规则 | 作用 |
|------|------|
| 日亏损线 | 当日累计亏损超过阈值，熔断所有策略 |
| 单票仓位上限 | 单一股票占总仓位比例限制 |
| 日内撤单次数 | 超过 N 次撤单后暂停该策略 |
| 策略级熔断 | 策略连续亏损 N 次后自动暂停 |
| 涨跌停保护 | 触及涨跌停板的标的不生成买单/卖单 |
| 交易时间 | 只在集合竞价时段允许下单 |

#### 设计要点
- **规则可组合**：按策略配置加载不同规则集
- **severity 分级**：`block` 拒绝信号，`warn` 记录警告但不阻止，`limit` 调整交易量
- **代码强制执行**：信号必须走完整 `ExecutionPipeline`，绕过风控不可行

---

## 4. 技术规格

### 4.1 技术栈

| 层 | 技术 | 备注 |
|----|------|------|
| 后端框架 | FastAPI (Python 3.12+) | 异步原生，WebSocket 支持 |
| ORM | SQLAlchemy 2.0 + Alembic | 异步模式 |
| 数据库 | SQLite → PostgreSQL | SQLite 起步，零运维 |
| 任务队列 | arq + Redis | 异步任务、定时调度 |
| 数据分析 | pandas, numpy | 量化基石 |
| 数据源 | AKShare | 首批实现 |
| 前端框架 | React 18 + TypeScript | Vite 构建 |
| 图表库 | TradingView Lightweight Charts | K 线 + 权益曲线 |
| 部署 | Docker Compose | FastAPI + Redis + DB 一键启动 |

### 4.2 开发环境

- uv 管理 Python 依赖
- pnpm 管理前端依赖
- pytest + pytest-asyncio 后端测试
- Vitest 前端测试
- pre-commit 代码检查

---

## 5. 边界与限制

### 5.1 首批范围（v1.0 MVP）

✅ A 股日线数据（AKShare）
✅ 技术指标策略（均线交叉、MACD）
✅ 因子策略（基础多因子）
✅ AI/ML 策略（基础 XGBoost 预测）
✅ 回测引擎（完整指标 + 可视化）
✅ 模拟交易（本地撮合）
✅ 风控（所有内置规则）
✅ 半自动模式（模拟盘）
✅ Web 看板（策略状态、持仓、净值曲线）
✅ YAML 策略配置

### 5.2 明确不做（v1.0）

❌ 分钟级/Tick 级数据
❌ 实盘券商对接
❌ 美股/加密货币
❌ 多用户登录和权限
❌ 生产级部署（K8s/云原生）
❌ 移动端

### 5.3 风险与假设

- **数据质量风险**：AKShare 免费接口可能不稳定，数据需做完整性校验
- **模拟撮合保真度**：模拟交易无法 100% 模拟真实市场流动性，回测收益≠实盘收益
- **合规假设**：当前不涉及实盘交易，无监管合规问题；未来接实盘需评估
- **性能假设**：个人使用、关注 < 100 只股票，SQLite 足以支撑
- **AI 模型安全**：AI 策略的信号必须走风控管线，不能因 AI 推理拒绝就绕过

---

## 6. 后续版本规划

| 版本 | 内容 |
|------|------|
| v1.1 | 分钟级数据 + 日内策略 |
| v1.2 | 商业数据源适配（TuShare Pro） |
| v2.0 | 实盘券商对接（中泰/华泰） |
| v2.1 | 美股市场扩展 |
| v2.2 | 多用户支持 |
| v3.0 | 高级 AI 策略（LLM Agent 决策、强化学习） |
