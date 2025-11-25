import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import APIConfig

class TushareService:
    def __init__(self):
        config = APIConfig()
        ts.set_token(config.TUSHARE_TOKEN)
        self.pro = ts.pro_api()
        
    def get_stock_basic(self, exchange: str = '') -> pd.DataFrame:
        """获取股票基本信息"""
        try:
            return self.pro.stock_basic(exchange=exchange)
        except Exception as e:
            print(f"获取股票基本信息失败: {str(e)}")
            return pd.DataFrame()
            
    def get_daily_data(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据"""
        try:
            return self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        except Exception as e:
            print(f"获取日线数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_company_info(self, ts_code: str) -> Dict:
        """获取公司基本信息"""
        try:
            # 使用stock_basic获取基本信息
            basic_data = self.pro.stock_basic(ts_code=ts_code)
            # 使用stock_company获取详细信息
            company_data = self.pro.stock_company(ts_code=ts_code)
            
            info = {}
            if not basic_data.empty:
                basic_info = basic_data.iloc[0].to_dict()
                info.update({
                    'name': basic_info.get('name', ''),
                    'list_date': basic_info.get('list_date', ''),
                    'industry': basic_info.get('industry', ''),
                    'reg_capital': basic_info.get('reg_capital', 0) * 10000  # 转换为万元
                })
            
            if not company_data.empty:
                company_info = company_data.iloc[0].to_dict()
                info.update({
                    'introduction': company_info.get('introduction', ''),
                    'main_business': company_info.get('main_business', ''),
                    'business_scope': company_info.get('business_scope', ''),
                    'province': company_info.get('province', ''),
                    'city': company_info.get('city', ''),
                    'website': company_info.get('website', '')
                })
            
            return info
        except Exception as e:
            print(f"获取公司信息失败: {str(e)}")
            return {}
            
    def get_financial_data(self, ts_code: str, period: str = '20231231') -> pd.DataFrame:
        """获取财务数据"""
        try:
            return self.pro.fina_indicator(ts_code=ts_code, period=period)
        except Exception as e:
            print(f"获取财务数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_income_data(self, ts_code: str, period: str = '20231231') -> pd.DataFrame:
        """获取利润表数据"""
        try:
            return self.pro.income(ts_code=ts_code, period=period)
        except Exception as e:
            print(f"获取利润表数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_balance_data(self, ts_code: str, period: str = '20231231') -> pd.DataFrame:
        """获取资产负债表数据"""
        try:
            return self.pro.balancesheet(ts_code=ts_code, period=period)
        except Exception as e:
            print(f"获取资产负债表数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_cashflow_data(self, ts_code: str, period: str = '20231231') -> pd.DataFrame:
        """获取现金流量表数据"""
        try:
            return self.pro.cashflow(ts_code=ts_code, period=period)
        except Exception as e:
            print(f"获取现金流量表数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_index_data(self, index_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数数据"""
        try:
            return self.pro.index_daily(ts_code=index_code, start_date=start_date, end_date=end_date)
        except Exception as e:
            print(f"获取指数数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_market_data(self, trade_date: str = None) -> pd.DataFrame:
        """获取市场整体数据"""
        try:
            if trade_date is None:
                trade_date = datetime.now().strftime('%Y%m%d')
            return self.pro.daily_basic(trade_date=trade_date)
        except Exception as e:
            print(f"获取市场数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_industry_data(self, level: str = 'L1') -> pd.DataFrame:
        """获取行业分类数据"""
        try:
            return self.pro.index(level=level)
        except Exception as e:
            print(f"获取行业数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_concept_data(self) -> pd.DataFrame:
        """获取概念分类数据"""
        try:
            return self.pro.concept()
        except Exception as e:
            print(f"获取概念数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_news(self, ts_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取新闻数据"""
        try:
            return self.pro.news(ts_code=ts_code, start_date=start_date, end_date=end_date)
        except Exception as e:
            print(f"获取新闻数据失败: {str(e)}")
            return pd.DataFrame()
            
    def get_financial_indicators(self, symbol, period):
        """获取财务指标数据"""
        try:
            print(f"正在获取股票 {symbol} 在 {period} 的财务指标数据...")
            
            # 确保股票代码格式正确
            if not symbol.endswith('.SH') and not symbol.endswith('.SZ'):
                if symbol.startswith('6'):
                    symbol = f"{symbol}.SH"
                else:
                    symbol = f"{symbol}.SZ"
            
            # 获取财务指标数据
            df = self.pro.fina_indicator(ts_code=symbol, period=period)
            
            if df is None:
                print(f"获取财务指标数据失败：返回数据为None")
                return None
            
            if df.empty:
                print(f"获取财务指标数据失败：返回数据为空DataFrame")
                return None
            
            print(f"成功获取到 {len(df)} 条财务指标数据")
            
            # 将数据转换为数值类型
            numeric_columns = df.select_dtypes(include=['object']).columns
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 将百分比值转换为小数
            for col in df.columns:
                if 'ratio' in col or 'rate' in col or 'growth' in col or 'margin' in col or 'yoy' in col or 'qoq' in col:
                    df[col] = df[col] / 100
            
            # 将无效值替换为None
            df = df.replace([0, float('inf'), float('-inf')], None)
            
            # 检查数据是否包含必要的列
            required_columns = ['eps', 'roe', 'roa', 'grossprofit_margin', 'netprofit_margin']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"警告：财务数据缺少以下必要列：{missing_columns}")
            
            return df
            
        except Exception as e:
            print(f"获取财务指标数据失败：{str(e)}")
            return None

    def get_stock_daily(self, symbol, start_date, end_date):
        """
        获取股票日线数据
        
        Args:
            symbol (str): 股票代码
            start_date (str): 开始日期，格式：YYYYMMDD
            end_date (str): 结束日期，格式：YYYYMMDD
            
        Returns:
            DataFrame: 包含日线数据的DataFrame
        """
        try:
            # 确保股票代码格式正确
            if not symbol.endswith('.SH') and not symbol.endswith('.SZ'):
                if symbol.startswith('6'):
                    symbol = f"{symbol}.SH"
                else:
                    symbol = f"{symbol}.SZ"
            
            # 获取日线数据
            df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            
            if df is None or df.empty:
                return None
                
            # 按日期排序
            df = df.sort_values('trade_date')
            
            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            
            return df
            
        except Exception as e:
            print(f"获取股票日线数据失败：{str(e)}")
            return None 