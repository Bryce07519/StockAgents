# mcp-server/app/tools/auto_api_generator/main.py

from mcp.server import Server, FastMCP
import tushare as ts
import json
import pandas as pd
from typing import List, Dict, Any


TUSHARE_TOKEN = "50565aa8b8c369cb3a9d72ff2d3e150283564f437e482425b67c9359"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()
mcp = FastMCP("MCP-auto_api_generator")




# ================= 工具 1：技术指标 =================
@mcp.tool()
def calculate_technical_indicators(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    计算技术指标：MA20/MA50、RSI(14)、MACD(12,26,9)。
    Args:
        data: 量价数据，JSON 友好的 list[dict]，例如：
              [{"trade_date":"20240102","open":..., "high":..., "low":..., "close":..., "vol":...}, ...]
    Returns:
        list[dict]: 每行附带技术指标后的记录（JSON 友好）。
    """
    if not data:
        return []

    df = pd.DataFrame(data)

    # 确保必须字段存在
    required_cols = {"close"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns for indicator calculation: {missing}")

    # 移动均线
    df["MA20"] = df["close"].rolling(window=20, min_periods=1).mean()
    df["MA50"] = df["close"].rolling(window=50, min_periods=1).mean()

    # RSI(14)
    delta = df["close"].diff()
    gain = delta.clip(lower=0).rolling(window=14, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14, min_periods=14).mean()
    rs = gain / loss.replace(0, pd.NA)
    df["RSI"] = 100 - (100 / (1 + rs))

    # MACD(12,26,9)
    exp12 = df["close"].ewm(span=12, adjust=False).mean()
    exp26 = df["close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = exp12 - exp26
    df["Signal_Line"] = df["MACD"].ewm(span=9, adjust=False).mean()

    # JSON 友好：把 NaN -> None
    out = df.where(pd.notna(df), None)

    return out.to_dict(orient="records")

# ================= 工具 2：获取量价数据 =================
@mcp.tool()
def get_stock_price_volume(stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    从 TuShare 获取简化的量价历史数据（按 trade_date 升序）。
    Returns:
        {"status": "success", "data": [...]} 或 {"status":"error","message":"..."}
    """
    try:
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {
                "status": "error",
                "message": f"未能获取到股票 {stock_code} 的数据。请检查代码是否正确或日期范围内是否有交易。"
            }

        df = df.sort_values("trade_date", ascending=True)
        cols = ["trade_date", "open", "high", "low", "close", "vol"]
        # 有些市场可能没有某些列，做个交集保护
        cols = [c for c in cols if c in df.columns]
        clean_data = df[cols].to_dict(orient="records")

        return {"status": "success", "data": clean_data}

    except Exception as e:
        return {"status": "error", "message": f"获取数据时发生未知错误: {str(e)}"}

if __name__ == "__main__":
    # SSE 传输启动（默认 127.0.0.1:3000，可按需要配置）
    # 例如：mcp.run(transport="sse", host="127.0.0.1", port=3000)
    mcp.run(transport="sse")