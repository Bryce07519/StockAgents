# 📈 StockAgent - An Enterprise-Grade AI Financial Analysis Toolkit

[**简体中文**](README_zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**StockAgent** is a comprehensive financial analysis toolkit designed specifically for Large Language Models (LLMs). It bridges the gap between powerful AI Agents and real-time, accurate financial data by providing a suite of plug-and-play APIs. This enables a seamless transition from natural language queries to deep financial insights.

## 🌟 Core Features

-   **Full-Spectrum Coverage**: The toolkit covers the entire analysis chain, from **data retrieval**, **technical analysis**, and **fundamental queries** to **information retrieval**, providing a solid foundation for building complex financial workflows.
-   **Natural Language Driven**: Designed for conversational interaction. The AI Agent can intelligently parse user intent and autonomously select, combine, and utilize any of the 20 available tools to accomplish tasks.
-   **Real-time & Accurate**: All data is sourced in real-time via the [Tushare Pro](https://tushare.pro/) API, ensuring the timeliness and accuracy of the information, primarily focused on the Chinese A-share market.
-   **Deeply Optimized for AI Agents**: All tool interfaces (inputs/outputs) are meticulously designed with a strict, JSON-serializable data structure, guaranteeing perfect compatibility with mainstream LLM frameworks and AI development platforms like Cherry Studio.
-   **Highly Extensible**: Built on `mcp-server`, its modular code structure makes it exceptionally easy to add new financial data sources or custom analysis tools.

## 📸 Functional Demo

The following demonstrates a typical workflow of StockAgent within an AI application platform. A user issues a multi-step analysis request in natural language, and the Agent autonomously plans and executes a sequence of tools (`search_stock_code`, `get_stock_price_volume`, `calculate_technical_indicators`) to generate a complete report.

![StockAgent Demo](./docs/demo.png)

---

## 🛠️ The Complete Toolkit at a Glance

StockAgent provides 20 well-designed tools, categorized as follows:

### 1. Market Data & Price Retrieval

| Tool Name | Description |
| :--- | :--- |
| **`get_stock_price_volume`** | Fetches historical price and volume data for a specified stock within a date range. |
| **`get_index_price`** | Retrieves market index data (e.g., Shanghai Composite Index). |
| **`get_latest_trade_date`** | Gets the most recent trading day for the A-share market. |

### 2. Technical Analysis & Calculation

| Tool Name | Description |
| :--- | :--- |
| **`calculate_technical_indicators`** | Calculates common technical indicators (MA, RSI, MACD). |
| **`calculate_bollinger_bands`** | Calculates Bollinger Bands (BOLL). |
| **`calculate_period_return`** | Computes the cumulative return over a given data period. |
| **`calculate_data_summary`** | Performs basic statistical analysis on a data column (mean, std, etc.). |
| **`find_price_breakthrough`** | Identifies dates when the price breaks above or below a specified level. |
| **`get_candlestick_pattern`** | Performs simple recognition of daily candlestick patterns (e.g., Bullish, Bearish, Doji). |

### 3. Corporate Fundamentals & Financials

| Tool Name | Description |
| :--- | :--- |
| **`get_stock_basic_info`** | Retrieves basic information about a single stock (name, industry, listing date). |
| **`get_financial_indicators`** | Fetches key financial indicators (PE, PB, EPS) for a specific reporting period. |
| **`get_top10_shareholders`** | Queries the top 10 shareholders for a company in a given period. |
| **`check_if_st_stock`** | Checks if a stock is currently designated as "ST" (Special Treatment). |

### 4. Information Retrieval & Screening

| Tool Name | Description |
| :--- | :--- |
| **`search_stock_code`** | Performs a fuzzy search for stocks based on keywords (company name or code). |
| **`get_stocks_by_industry`** | Retrieves a list of all stocks within a specified industry category. |
| **`get_company_news`** | Queries for company announcements within a specified date range. |
| **`filter_high_dividend_stocks`** | Screens for stocks with a dividend yield higher than a certain threshold. |

### 5. Specialized & Holdings Data

| Tool Name | Description |
| :--- | :--- |
| **`get_top_list_data`** | Fetches the "Dragon and Tiger List" (top trading seats) data for a specific day. |
| **`get_hk_hold_data`** | Retrieves detailed holdings data from the HK-Stock Connect for an A-share stock. |
| **`compare_two_stocks_price`** | Compares the closing prices of two stocks on a specific date. |

---

## 💡 Complex Workflow Examples

The true power of StockAgent lies in its ability to chain tools together. An Agent can link these functions to perform sophisticated analysis tasks:

-   **Market Scan & In-depth Analysis**:
    > "Find stocks in the 'Baijiu' industry with a P/E ratio below 30 and an RSI below 40 over the last month."
    -   **Agent's Path**: `get_stocks_by_industry` -> (Loop) `get_financial_indicators` -> (Filter) `get_stock_price_volume` -> (Filter) `calculate_technical_indicators` -> (Filter) -> **Final Report**

-   **Event-Driven Analysis**:
    > "What were the latest announcements from Kweichow Moutai, and how did its stock price and technical indicators change in the five days following the announcement?"
    -   **Agent's Path**: `get_company_news` -> (Get Date) `get_stock_price_volume` -> `calculate_period_return` + `calculate_technical_indicators` -> **Synthesized Answer**

## 📜 License

This project is licensed under the [MIT License](LICENSE).