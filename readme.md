# 📈 StockAgent - 股票分析 AI 代理工具集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**StockAgent** 是一个专为大语言模型（LLM）设计的强大金融工具集。它通过提供一系列即插即用的 API，使 AI 代理（Agent）能够无缝接入实时股票数据和进行复杂的技术分析，将自然语言查询转化为精准的金融数据洞察。

## 🌟 核心特点

-   **自然语言驱动**: 设计初衷是让用户通过对话式交互获取金融信息。AI 代理可以智能地解析用户意图，并调用本工具集中的相应功能。
-   **实时数据接入**: 集成了业界知名的 [Tushare Pro](https://tushare.pro/) 数据接口，确保提供准确、及时的中国 A 股市场行情数据。
-   **强大的分析能力**: 不仅仅是数据查询。内置了核心技术指标的计算引擎，能够处理复杂的时序数据，为量化分析和投资决策提供支持。
-   **为 AI Agent 深度优化**: 所有工具的接口（输入/输出）都经过精心设计，遵循严格的、可被 JSON 序列化的数据结构，确保与主流 LLM 框架（如 LangChain, LlamaIndex）和 AI 开发平台（如 Cherry Studio）完美兼容。
-   **轻量且可扩展**: 基于高性能的 `mcp-server` 构建，资源占用小，响应迅速。模块化的代码结构使得添加新的金融数据源或自定义分析工具变得异常简单。

## 📸 功能演示

下图展示了 StockAgent 在 AI 应用平台中的实际工作流程：用户用自然语言提出需求，Agent 自动调用 `get_stock_price_volume` 工具获取数据，并以结构化格式返回。


![StockAgent 演示](./docs/demo.png)


---

## 🛠️ 内置工具集一览

### 1. 实时行情查询 (`get_stock_price_volume`)

-   **功能**: 根据指定的股票代码和日期范围，精确获取历史日线行情。
-   **输出**: 返回包含交易日期、开盘价、收盘价、最高价、最低价和成交量的结构化数据。
-   **应用场景**: “查询贵州茅台（600519.SH）上周的股价表现。”

### 2. 技术指标计算 (`calculate_technical_indicators`)

-   **功能**: 基于输入的行情数据，动态计算多种关键技术指标。
-   **支持指标**:
    -   **移动平均线 (Moving Averages)**: MA20, MA50
    -   **相对强弱指数 (Relative Strength Index)**: RSI (14)
    -   **平滑异同移动平均线 (MACD)**: MACD Line, Signal Line
-   **应用场景**: “获取平安银行（000001.SZ）最近一个月的行情数据，并计算其 RSI 和 MACD 指标。”

---

## 💡 设计理念

StockAgent 的核心理念是**“为智能体赋能”**。我们相信，未来的人机交互将更多地依赖于能够理解上下文并自主调用工具的 AI 代理。StockAgent 正是这一理念在金融领域的实践，它扮演着连接自然语言和复杂金融数据世界的桥梁角色。

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源。