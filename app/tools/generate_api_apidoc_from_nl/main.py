# mcp-server/app/tools/auto_api_generator/main.py

from mcp.server import Server, FastMCP
import tushare as ts
import json
import pandas as pd
from typing import List, Dict, Any


TUSHARE_TOKEN = ""
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()
mcp = FastMCP("MCP-auto_api_generator")


@mcp.tool()
def calculate_technical_indicators(data):
        """计算技术指标。根据量价数据计算常用的技术指标，如移动平均线、相对强弱指数（RSI）和MACD。
        Args:
            data: 输入是 Pandas DataFrame 格式的股票数据
        Return:
            一个包含技术指标的字典列表 (A list of dictionaries containing technical indicators)。
        """
        df = data.copy()
        
        # Moving averages
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # 将 NaN 值替换为 None，以便 JSON 序列化
        df = df.where(pd.notna(df), None)
        
        # 返回 JSON 友好的格式
        return df.to_dict('records')



@mcp.tool()
# 1. 确保类型注解是 dict 或者更精确的 Dict[str, Any]
def get_stock_price_volume(stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    获取股票量价数据，根据股票代码和日期范围，从 Tushare 获取简化的量价历史数据。

    Args:
        stock_code (str): 股票代码，例如 '000001.SZ'。
        start_date (str): 开始日期，格式 'YYYYMMDD'，例如 '20230101'。
        end_date (str): 结束日期，格式 'YYYYMMDD'，例如 '20240101'。

    Returns:
        dict: 一个字典，包含状态和数据。
              成功时: {'status': 'success', 'data': [{}, {}, ...]}
              失败时: {'status': 'error', 'message': '错误信息'}
    """
    
    try:
        df = pro.daily(
            ts_code=stock_code,
            start_date=start_date,
            end_date=end_date
        )

        if df.empty:
            return {
                "status": "error",
                "message": f"未能获取到股票 {stock_code} 的数据。请检查代码是否正确或日期范围内是否有交易。"
            }

        df = df.sort_values('trade_date', ascending=True)
        df_selected = df[['trade_date', 'open', 'high', 'low', 'close', 'vol']]
        
        clean_data = df_selected.to_dict('records')

        # 2. 返回一个结构清晰的 Python 字典，而不是 JSON 字符串
        return {
            "status": "success",
            "data": clean_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"获取数据时发生未知错误: {str(e)}"
        }
if __name__ == "__main__":
    # Initialize and run the server

    mcp.run(transport='sse')
