# mcp-server/app/tools/auto_api_generator/main.py

from mcp.server import Server, FastMCP
import tushare as ts
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import os
TUSHARE_TOKEN = ""
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()
mcp = FastMCP("MCP-auto_api_generator")



# ================= 工具 1：技术指标计算 =================
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
    required_cols = {"close"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing 'close' column for indicator calculation.")
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA50'] = df['close'].rolling(window=50).mean()
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(window=14).mean()
    loss = (-delta.clip(upper=0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, pd.NA)
    df['RSI'] = 100 - (100 / (1 + rs))
    exp12 = df['close'].ewm(span=12, adjust=False).mean()
    exp26 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df.where(pd.notna(df), None).to_dict(orient="records")

# ================= 工具 2：获取量价数据 =================
@mcp.tool()
def get_stock_price_volume(stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    从 TuShare 获取指定股票在日期范围内的量价历史数据（按 trade_date 升序）。
    Args:
        stock_code: 股票代码, e.g., '000001.SZ' or '600519.SH'
        start_date: 开始日期, e.g., '20230101'
        end_date: 结束日期, e.g., '20240101'
    Returns:
        {"status": "success", "data": [...]} 或 {"status":"error","message":"..."}
    """
    try:
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {"status": "error", "message": f"未能获取到股票 {stock_code} 的数据。"}
        df = df.sort_values("trade_date", ascending=True)
        cols = ["trade_date", "open", "high", "low", "close", "vol"]
        clean_data = df[cols].to_dict(orient="records")
        return {"status": "success", "data": clean_data}
    except Exception as e:
        return {"status": "error", "message": f"获取数据时发生错误: {str(e)}"}

# ================= 工具 3：获取股票基本信息 =================
@mcp.tool()
def get_stock_basic_info(stock_code: str) -> Dict[str, Any]:
    """
    获取单个股票的基本信息，如名称、所属行业、上市日期等。
    Args:
        stock_code: 股票代码, e.g., '000001.SZ'
    Returns:
        {"status": "success", "data": {...}} 或 {"status":"error","message":"..."}
    """
    try:
        df = pro.stock_basic(ts_code=stock_code, fields='ts_code,symbol,name,area,industry,market,list_date')
        if df is None or df.empty:
            return {"status": "error", "message": f"未找到股票代码 {stock_code} 的基本信息。"}
        return {"status": "success", "data": df.to_dict(orient='records')[0]}
    except Exception as e:
        return {"status": "error", "message": f"查询基本信息时出错: {str(e)}"}

# ================= 工具 4：模糊搜索股票代码 =================
@mcp.tool()
def search_stock_code(keyword: str) -> Dict[str, Any]:
    """
    根据关键词（公司名称或代码）模糊搜索匹配的股票列表。
    Args:
        keyword: 搜索关键词, e.g., '平安银行' or '茅台'
    Returns:
        {"status": "success", "data": [...]} 或 {"status":"error","message":"..."}
    """
    try:
        df = pro.stock_basic(fields='ts_code,name,industry')
        if df is None or df.empty:
            return {"status": "error", "message": "无法获取股票基础列表。"}
        results = df[df['name'].str.contains(keyword, na=False)]
        if results.empty:
             return {"status": "success", "data": [], "message": f"未找到与'{keyword}'相关的股票。"}
        return {"status": "success", "data": results.to_dict(orient='records')}
    except Exception as e:
        return {"status": "error", "message": f"搜索股票时出错: {str(e)}"}

# ================= 工具 5：计算数据摘要统计 =================
@mcp.tool()
def calculate_data_summary(data: List[Dict[str, Any]], column: str) -> Dict[str, Any]:
    """
    对给定的数据列表中的某一列进行基础统计分析。
    Args:
        data: 数据列表, e.g., from get_stock_price_volume.
        column: 要分析的列名, e.g., 'close' or 'vol'.
    Returns:
        {"status": "success", "data": {"mean":..., "std":..., "min":..., "max":..., "count":...}}
    """
    if not data:
        return {"status": "error", "message": "输入数据为空。"}
    df = pd.DataFrame(data)
    if column not in df.columns:
        return {"status": "error", "message": f"列 '{column}' 不存在。"}
    
    summary = df[column].describe().to_dict()
    return {"status": "success", "data": summary}

# ================= 工具 6：获取最新交易日 =================
@mcp.tool()
def get_latest_trade_date() -> str:
    """获取A股市场最近的一个交易日，格式为 YYYYMMDD。"""
    df = pro.trade_cal(exchange='SSE', is_open='1', end_date=pd.Timestamp.now().strftime('%Y%m%d'))
    return df['cal_date'].iloc[-1]

# ================= 工具 7：获取公司主要财务指标 =================
@mcp.tool()
def get_financial_indicators(stock_code: str, period: str) -> Dict[str, Any]:
    """
    获取公司指定报告期的主要财务指标，如每股收益(EPS)、市盈率(PE)、市净率(PB)等。
    Args:
        stock_code: 股票代码, e.g., '000001.SZ'
        period: 报告期, e.g., '20231231' (年报), '20230930' (三季报)
    Returns:
        {"status": "success", "data": {...}} 或 {"status":"error","message":"..."}
    """
    try:
        df = pro.daily_basic(ts_code=stock_code, trade_date=period)
        if df is None or df.empty:
            # 如果指定日期非交易日，尝试往前找最近的交易日
            df = pro.daily_basic(ts_code=stock_code, end_date=period, limit=1)
            if df is None or df.empty:
                return {"status": "error", "message": f"未找到 {stock_code} 在 {period} 附近日期的财务指标。"}
        
        indicators = df[['ts_code', 'trade_date', 'pe_ttm', 'pb', 'dv_ratio', 'total_share', 'total_mv']].iloc[0]
        return {"status": "success", "data": indicators.to_dict()}
    except Exception as e:
        return {"status": "error", "message": f"获取财务指标时出错: {str(e)}"}

# ================= 工具 8：查找价格突破点 =================
@mcp.tool()
def find_price_breakthrough(data: List[Dict[str, Any]], price_level: float, direction: str) -> List[Dict[str, Any]]:
    """
    在价格数据中查找向上或向下突破指定价格水平的日期。
    Args:
        data: 量价数据列表。
        price_level: 目标价格水平。
        direction: 突破方向, 'up' (向上突破) or 'down' (向下突破)。
    Returns:
        突破点的记录列表。
    """
    df = pd.DataFrame(data)
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    if direction == 'up':
        breakthroughs = df[df['close'] > price_level]
    elif direction == 'down':
        breakthroughs = df[df['close'] < price_level]
    else:
        raise ValueError("Direction must be 'up' or 'down'.")
    return breakthroughs.to_dict(orient='records')

# ================= 工具 9：获取日K线形态 =================
@mcp.tool()
def get_candlestick_pattern(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    简单识别日K线的基本形态（阳线、阴线、十字星）。
    Args:
        data: 包含 open, close, high, low 的单日或多日数据列表。
    Returns:
        带有 'pattern' 字段的数据列表。
    """
    for row in data:
        o, c, h, l = row.get('open'), row.get('close'), row.get('high'), row.get('low')
        if None in [o, c, h, l]:
            row['pattern'] = 'Unknown'
            continue
        body_size = abs(o - c)
        range_size = h - l
        if body_size / range_size < 0.1 if range_size > 0 else True:
            row['pattern'] = 'Doji/Cross' # 十字星
        elif c > o:
            row['pattern'] = 'Bullish/Yang' # 阳线
        else:
            row['pattern'] = 'Bearish/Yin' # 阴线
    return data

# ================= 工具 10：计算区间涨跌幅 =================
@mcp.tool()
def calculate_period_return(data: List[Dict[str, Any]]) -> Optional[float]:
    """
    计算给定数据区间的累计涨跌幅。
    Args:
        data: 量价数据列表，至少包含两条记录。
    Returns:
        涨跌幅百分比 (e.g., 5.25 代表上涨5.25%)，或在数据不足时返回 None。
    """
    if not data or len(data) < 2:
        return None
    start_price = data[0].get('close')
    end_price = data[-1].get('close')
    if start_price is None or end_price is None or start_price == 0:
        return None
    period_return = ((end_price - start_price) / start_price) * 100
    return round(period_return, 2)

# ================= 工具 11：获取行业分类股票 =================
@mcp.tool()
def get_stocks_by_industry(industry_name: str) -> Dict[str, Any]:
    """
    获取指定申万行业分类下的所有股票列表。
    Args:
        industry_name: 行业名称, e.g., '银行', '白酒'
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        # Tushare 接口限制，这里用基础信息里的 industry 字段做近似筛选
        df = pro.stock_basic(fields='ts_code,name,industry')
        results = df[df['industry'].str.contains(industry_name, na=False)]
        if results.empty:
            return {"status": "success", "data": [], "message": f"未找到'{industry_name}'行业相关股票。"}
        return {"status": "success", "data": results.to_dict(orient='records')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================= 工具 12：比较两只股票的价格 =================
@mcp.tool()
def compare_two_stocks_price(stock_code_a: str, stock_code_b: str, date: str) -> Dict[str, Any]:
    """
    比较两只股票在指定日期的收盘价。
    Args:
        stock_code_a: 股票A代码
        stock_code_b: 股票B代码
        date: 查询日期, YYYYMMDD
    Returns:
        包含两只股票价格和差异的字典。
    """
    price_a_res = get_stock_price_volume(stock_code_a, date, date)
    price_b_res = get_stock_price_volume(stock_code_b, date, date)

    if price_a_res['status'] == 'error' or price_b_res['status'] == 'error':
        return {"status": "error", "message": "无法获取其中一只或两只股票的价格数据。"}
    
    price_a = price_a_res['data'][0]['close']
    price_b = price_b_res['data'][0]['close']
    
    return {
        "status": "success",
        "data": {
            stock_code_a: price_a,
            stock_code_b: price_b,
            "difference": round(price_a - price_b, 2)
        }
    }

# ================= 工具 13：获取公司股东信息 =================
@mcp.tool()
def get_top10_shareholders(stock_code: str, period: str) -> Dict[str, Any]:
    """
    查询公司指定报告期的前十大股东信息。
    Args:
        stock_code: 股票代码
        period: 报告期, e.g., '20231231'
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        df = pro.top10_holders(ts_code=stock_code, end_date=period)
        if df is None or df.empty:
            return {"status": "error", "message": f"未找到 {stock_code} 在 {period} 的股东信息。"}
        return {"status": "success", "data": df[['holder_name', 'hold_ratio']].to_dict('records')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================= 工具 14：查询公司公告 =================
@mcp.tool()
def get_company_news(stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    查询上市公司在指定日期范围内的公告。
    Args:
        stock_code: 股票代码
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        df = pro.anns(ts_code=stock_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {"status": "success", "data": [], "message": f"期间内未找到 {stock_code} 的公告。"}
        return {"status": "success", "data": df[['ann_date', 'title']].to_dict('records')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================= 工具 15：筛选高股息率股票 =================
@mcp.tool()
def filter_high_dividend_stocks(min_dv_ratio: float, date: Optional[str] = None) -> Dict[str, Any]:
    """
    筛选出在指定日期股息率高于某个阈值的股票列表。
    Args:
        min_dv_ratio: 最低股息率(百分比), e.g., 3.0
        date: 查询日期 (YYYYMMDD)，如果为空，则使用最新交易日。
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        if date is None:
            date = get_latest_trade_date()
        
        df = pro.daily_basic(trade_date=date, fields='ts_code,dv_ratio')
        if df is None or df.empty:
            return {"status": "error", "message": f"无法获取 {date} 的日度指标数据。"}
            
        high_dv_stocks = df[df['dv_ratio'] > min_dv_ratio]
        return {"status": "success", "data": high_dv_stocks.to_dict('records')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================= 工具 16：获取龙虎榜数据 =================
@mcp.tool()
def get_top_list_data(trade_date: str) -> Dict[str, Any]:
    """
    获取指定交易日的龙虎榜机构明细数据。
    Args:
        trade_date: 交易日期, YYYYMMDD
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        df = pro.top_inst(trade_date=trade_date)
        if df is None or df.empty:
            return {"status": "success", "data": [], "message": f"未找到 {trade_date} 的龙虎榜数据。"}
        return {"status": "success", "data": df[['ts_code', 'exalter', 'buy', 'sell']].to_dict('records')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================= 工具 17：计算布林带指标 =================
@mcp.tool()
def calculate_bollinger_bands(data: List[Dict[str, Any]], window: int = 20, num_std: int = 2) -> List[Dict[str, Any]]:
    """
    计算布林带(BOLL)指标。
    Args:
        data: 量价数据列表
        window: 移动平均线的窗口期，默认为20
        num_std: 标准差倍数，默认为2
    Returns:
        带有'boll_upper', 'boll_mid', 'boll_lower'字段的数据列表。
    """
    if not data:
        return []
    df = pd.DataFrame(data)
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['boll_mid'] = df['close'].rolling(window=window).mean()
    std_dev = df['close'].rolling(window=window).std()
    df['boll_upper'] = df['boll_mid'] + (std_dev * num_std)
    df['boll_lower'] = df['boll_mid'] - (std_dev * num_std)
    return df.where(pd.notna(df), None).to_dict(orient="records")

# ================= 工具 18：获取港股通持股 =================
@mcp.tool()
def get_hk_hold_data(stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    获取沪深港通持股明细。
    Args:
        stock_code: A股股票代码
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        df = pro.hk_hold(ts_code=stock_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {"status": "success", "data": [], "message": f"未找到 {stock_code} 的港股通持股数据。"}
        return {"status": "success", "data": df[['trade_date', 'vol', 'ratio']].to_dict('records')}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ================= 工具 19：查询是否为ST股 =================
@mcp.tool()
def check_if_st_stock(stock_code: str) -> bool:
    """
    检查一只股票当前是否为ST或*ST股。
    Args:
        stock_code: 股票代码
    Returns:
        True 如果是ST股, False 如果不是。
    """
    info_res = get_stock_basic_info(stock_code)
    if info_res['status'] == 'success':
        name = info_res['data'].get('name', '')
        return 'ST' in name
    return False

# ================= 工具 20：获取大盘指数行情 =================
@mcp.tool()
def get_index_price(index_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    获取大盘指数的行情数据。
    Args:
        index_code: 指数代码, e.g., '000001.SH' (上证指数), '399001.SZ' (深证成指)
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    Returns:
        {"status": "success", "data": [...]}
    """
    try:
        df = pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {"status": "error", "message": f"未能获取到指数 {index_code} 的数据。"}
        df = df.sort_values("trade_date", ascending=True)
        cols = ["trade_date", "open", "high", "low", "close", "vol"]
        clean_data = df[cols].to_dict(orient="records")
        return {"status": "success", "data": clean_data}
    except Exception as e:
        return {"status": "error", "message": f"获取指数数据时发生错误: {str(e)}"}

# ================= 主程序入口 (用于本地测试) =================
if __name__ == "__main__":
    # 可以添加一些测试代码
    # print(get_stock_price_volume("000001.SZ", "20240101", "20240110"))
    # print(search_stock_code("科技"))
    # print(get_financial_indicators("600519.SH", "20231231"))
    
    # 启动 MCP 服务
    mcp.run(transport='sse')