import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from config import APIConfig

class MarketDataService:
    def __init__(self):
        self.config = APIConfig()
        self.base_url = "http://hq.sinajs.cn/list="
        self.headers = {
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _get_stock_code(self, symbol: str) -> str:
        """将股票代码转换为新浪财经格式"""
        if symbol.startswith('6'):
            return f"sh{symbol}"
        elif symbol.startswith('0') or symbol.startswith('3'):
            return f"sz{symbol}"
        else:
            raise ValueError(f"不支持的股票代码格式: {symbol}")

    def get_stock_price(self, symbol: str) -> Dict:
        """获取股票实时价格"""
        try:
            code = self._get_stock_code(symbol)
            url = f"{self.base_url}{code}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.text.split('="')[1].split(',')
                return {
                    "symbol": symbol,
                    "name": data[0],
                    "open": float(data[1]),
                    "close": float(data[2]),
                    "current": float(data[3]),
                    "high": float(data[4]),
                    "low": float(data[5]),
                    "volume": int(data[8]),
                    "amount": float(data[9]),
                    "change": float(data[3]) - float(data[2]),
                    "change_percent": (float(data[3]) - float(data[2])) / float(data[2]) * 100
                }
            else:
                return {"error": f"获取数据失败: {response.status_code}"}
        except Exception as e:
            return {"error": f"获取股票价格时出错: {str(e)}"}

    def get_market_index(self, index: str) -> Dict:
        """获取市场指数数据"""
        index_codes = {
            "sh000001": "上证指数",
            "sz399001": "深证成指",
            "sz399006": "创业板指",
            "sh000300": "沪深300"
        }
        
        try:
            url = f"{self.base_url}{index}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.text.split('="')[1].split(',')
                return {
                    "name": index_codes.get(index, index),
                    "current": float(data[3]),
                    "change": float(data[3]) - float(data[2]),
                    "change_percent": (float(data[3]) - float(data[2])) / float(data[2]) * 100,
                    "volume": int(data[8]),
                    "amount": float(data[9])
                }
            else:
                return {"error": f"获取数据失败: {response.status_code}"}
        except Exception as e:
            return {"error": f"获取指数数据时出错: {str(e)}"}

    def get_stock_list(self, market: str = "A") -> List[Dict]:
        """获取股票列表"""
        try:
            if market == "A":
                url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
                params = {
                    "page": 1,
                    "num": 100,
                    "sort": "symbol",
                    "asc": 1,
                    "node": "hs_a"
                }
                response = requests.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = json.loads(response.text)
                    return [{
                        "symbol": item["symbol"],
                        "name": item["name"],
                        "price": float(item["trade"]),
                        "change_percent": float(item["changepercent"])
                    } for item in data]
            return []
        except Exception as e:
            return []

    def get_stock_news(self, symbol: str, count: int = 10) -> List[Dict]:
        """获取股票相关新闻"""
        try:
            code = self._get_stock_code(symbol)
            url = f"http://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php"
            params = {
                "symbol": code,
                "Page": 1,
                "PageSize": count
            }
            response = requests.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                # 这里需要解析HTML页面获取新闻内容
                # 实际实现可能需要使用BeautifulSoup等库
                return []
            return []
        except Exception as e:
            return []

    def get_stock_financial(self, symbol: str) -> Dict:
        """获取股票财务数据"""
        try:
            code = self._get_stock_code(symbol)
            url = f"http://vip.stock.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/{code}/ctrl/2019/displaytype/4.phtml"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                # 这里需要解析HTML页面获取财务数据
                # 实际实现可能需要使用BeautifulSoup等库
                return {}
            return {}
        except Exception as e:
            return {}

    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        try:
            # 获取上证指数
            sh_data = self.get_market_index("sh000001")
            sh_index = f"{sh_data.get('current', 'N/A')} ({sh_data.get('change_percent', 0):.2f}%)" if sh_data and 'error' not in sh_data else "N/A"
            
            # 获取深证成指
            sz_data = self.get_market_index("sz399001")
            sz_index = f"{sz_data.get('current', 'N/A')} ({sz_data.get('change_percent', 0):.2f}%)" if sz_data and 'error' not in sz_data else "N/A"
            
            # 获取创业板指
            cyb_data = self.get_market_index("sz399006")
            cyb_index = f"{cyb_data.get('current', 'N/A')} ({cyb_data.get('change_percent', 0):.2f}%)" if cyb_data and 'error' not in cyb_data else "N/A"
            
            # 计算市场情绪
            market_sentiment = "中性"
            if sh_data and sz_data and cyb_data and 'error' not in sh_data and 'error' not in sz_data and 'error' not in cyb_data:
                changes = [
                    float(sh_data.get('change_percent', 0)),
                    float(sz_data.get('change_percent', 0)),
                    float(cyb_data.get('change_percent', 0))
                ]
                avg_change = sum(changes) / len(changes)
                if avg_change > 1:
                    market_sentiment = "乐观"
                elif avg_change < -1:
                    market_sentiment = "悲观"
            
            return {
                'sh_index': sh_index,
                'sz_index': sz_index,
                'cyb_index': cyb_index,
                'market_sentiment': market_sentiment
            }
        except Exception as e:
            print(f"获取市场概览失败：{str(e)}")
            return {
                'sh_index': 'N/A',
                'sz_index': 'N/A',
                'cyb_index': 'N/A',
                'market_sentiment': 'N/A'
            } 