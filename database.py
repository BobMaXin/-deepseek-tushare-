import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from models import InvestmentPortfolio, InvestmentGoal, InvestmentAsset
import json

class DatabaseService:
    def __init__(self, db_path: str = "investment.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建用户表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        experience TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 创建投资组合表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        risk_tolerance TEXT NOT NULL,
                        initial_capital REAL NOT NULL,
                        investment_goal TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        total_value REAL DEFAULT 0,
                        total_profit REAL DEFAULT 0,
                        total_profit_rate REAL DEFAULT 0,
                        risk_score REAL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # 创建资产表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS assets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        portfolio_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        cost_price REAL NOT NULL,
                        current_price REAL NOT NULL,
                        market_value REAL NOT NULL,
                        profit REAL NOT NULL,
                        profit_rate REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (portfolio_id) REFERENCES portfolios (id)
                    )
                """)
                
                # 创建投资分析表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS investment_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        symbol TEXT NOT NULL,
                        analysis_type TEXT NOT NULL,
                        analysis_data TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                # 创建收益分析表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS profit_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        initial_capital REAL NOT NULL,
                        investment_period INTEGER NOT NULL,
                        expected_return REAL NOT NULL,
                        monthly_investment REAL NOT NULL,
                        risk_tolerance TEXT NOT NULL,
                        total_investment REAL NOT NULL,
                        expected_profit REAL NOT NULL,
                        annualized_return REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)
                
                # 创建交易记录表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        asset_id INTEGER NOT NULL,
                        type TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL,
                        amount REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (asset_id) REFERENCES assets (id)
                    )
                """)
                
                # 创建投资目标表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS goals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        target_amount REAL NOT NULL,
                        current_amount REAL DEFAULT 0,
                        deadline DATE NOT NULL,
                        risk_tolerance TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                conn.commit()
            return True
        except Exception as e:
            print(f"初始化数据库失败：{str(e)}")
            return False
    
    def create_user(self, name: str, experience: str) -> int:
        """创建新用户"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, experience) VALUES (?, ?)",
                (name, experience)
            )
            return cursor.lastrowid
    
    def get_user(self, user_id: int) -> Dict:
        """获取用户信息"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "experience": row[2],
                    "created_at": row[3]
                }
            return {}
    
    def create_portfolio(self, user_id: int, name: str, risk_tolerance: str, investment_goal: str, total_value: float, total_profit: float, total_profit_rate: float, initial_capital: float) -> int:
        """创建投资组合"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO portfolios (user_id, name, risk_tolerance, investment_goal, total_value, total_profit, total_profit_rate, initial_capital, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (user_id, name, risk_tolerance, investment_goal, total_value, total_profit, total_profit_rate, initial_capital))
                portfolio_id = cursor.lastrowid
                conn.commit()
                return portfolio_id
        except Exception as e:
            print(f"创建投资组合失败：{str(e)}")
            return None
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Dict]:
        """获取投资组合信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM portfolios 
                    WHERE id = ?
                """, (portfolio_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            print(f"获取投资组合失败：{str(e)}")
            return None
    
    def get_portfolios(self, user_id: int) -> List[Dict]:
        """获取用户的所有投资组合"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM portfolios 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                """, (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"获取投资组合列表失败：{str(e)}")
            return []
    
    def update_portfolio(self, portfolio_id: int, portfolio: InvestmentPortfolio) -> bool:
        """更新投资组合信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE portfolios 
                    SET name = ?, risk_tolerance = ?, initial_capital = ?,
                        investment_goal = ?, total_value = ?, risk_score = ?
                    WHERE id = ?
                """, (
                    portfolio.name,
                    portfolio.risk_tolerance,
                    portfolio.initial_capital,
                    portfolio.investment_goal,
                    portfolio.total_value,
                    portfolio.risk_score,
                    portfolio_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"更新投资组合失败：{str(e)}")
            return False
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """删除投资组合"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 先删除相关的资产
                cursor.execute("DELETE FROM assets WHERE portfolio_id = ?", (portfolio_id,))
                # 删除投资组合
                cursor.execute("DELETE FROM portfolios WHERE id = ?", (portfolio_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除投资组合失败：{str(e)}")
            return False
    
    def add_asset(self, portfolio_id: int, symbol: str, name: str, quantity: int, cost_price: float, current_price: float, market_value: float, profit: float, profit_rate: float) -> int:
        """添加资产"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO assets 
                   (portfolio_id, symbol, name, quantity, cost_price, current_price, market_value, profit, profit_rate, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (portfolio_id, symbol, name, quantity, cost_price, current_price, market_value, profit, profit_rate)
            )
            return cursor.lastrowid
    
    def get_assets(self, portfolio_id: int) -> List[Dict]:
        """获取投资组合的资产列表"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assets WHERE portfolio_id = ?", (portfolio_id,))
            return [{
                "id": row[0],
                "portfolio_id": row[1],
                "symbol": row[2],
                "name": row[3],
                "quantity": row[4],
                "cost_price": row[5],
                "current_price": row[6],
                "market_value": row[7],
                "profit": row[8],
                "profit_rate": row[9]
            } for row in cursor.fetchall()]
    
    def create_goal(self, user_id: int, goal: InvestmentGoal) -> int:
        """创建投资目标"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO goals 
                   (user_id, name, target_amount, deadline, risk_tolerance)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, goal.name, goal.target_amount, 
                 goal.deadline, goal.risk_tolerance)
            )
            return cursor.lastrowid
    
    def get_goals(self, user_id: int) -> List[Dict]:
        """获取用户的所有投资目标"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, target_amount, current_amount, deadline, 
                           risk_tolerance, created_at, progress
                    FROM goals
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                """, (user_id,))
                goals = cursor.fetchall()
                return [{
                    'id': g[0],
                    'name': g[1],
                    'target_amount': g[2],
                    'current_amount': g[3],
                    'deadline': g[4],
                    'risk_tolerance': g[5],
                    'created_at': g[6],
                    'progress': g[7]
                } for g in goals]
        except Exception as e:
            print(f"获取投资目标失败：{str(e)}")
            return []
    
    def add_goal(self, user_id: int, goal: InvestmentGoal) -> int:
        """添加新的投资目标"""
        try:
            progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO goals (
                        user_id, name, target_amount, current_amount, 
                        deadline, risk_tolerance, created_at, progress
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    goal.name,
                    goal.target_amount,
                    goal.current_amount,
                    goal.deadline,
                    goal.risk_tolerance,
                    datetime.now(),
                    progress
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"添加投资目标失败：{str(e)}")
            return None
    
    def update_goal(self, goal_id: int, goal: InvestmentGoal) -> bool:
        """更新投资目标"""
        try:
            progress = (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE goals
                    SET name = ?, target_amount = ?, current_amount = ?, 
                        deadline = ?, risk_tolerance = ?, progress = ?
                    WHERE id = ?
                """, (
                    goal.name,
                    goal.target_amount,
                    goal.current_amount,
                    goal.deadline,
                    goal.risk_tolerance,
                    progress,
                    goal_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"更新投资目标失败：{str(e)}")
            return False
    
    def delete_goal(self, goal_id: int) -> bool:
        """删除投资目标"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"删除投资目标失败：{str(e)}")
            return False
    
    def update_goal_progress(self, goal_id: int, current_amount: float) -> bool:
        """更新投资目标进度"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE goals
                    SET current_amount = ?,
                        progress = (current_amount / target_amount * 100)
                    WHERE id = ?
                """, (current_amount, goal_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"更新目标进度失败：{str(e)}")
            return False
    
    def add_transaction(self, user_id: int, asset_id: int, 
                       transaction_type: str, quantity: int, 
                       price: float, amount: float):
        """添加交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO transactions 
                   (user_id, asset_id, type, quantity, price, amount)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, asset_id, transaction_type, quantity, price, amount)
            )
    
    def get_transactions(self, user_id: int, asset_id: Optional[int] = None) -> List[Dict]:
        """获取交易记录"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if asset_id:
                cursor.execute(
                    "SELECT * FROM transactions WHERE user_id = ? AND asset_id = ?",
                    (user_id, asset_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM transactions WHERE user_id = ?",
                    (user_id,)
                )
            return [{
                "id": row[0],
                "user_id": row[1],
                "asset_id": row[2],
                "type": row[3],
                "quantity": row[4],
                "price": row[5],
                "amount": row[6],
                "transaction_date": row[7]
            } for row in cursor.fetchall()]
    
    def get_recent_user(self) -> Optional[Dict]:
        """获取最近创建的用户"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, experience, created_at
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                user = cursor.fetchone()
                if user:
                    return {
                        "id": user[0],
                        "name": user[1],
                        "experience": user[2],
                        "created_at": user[3]
                    }
                return None
        except Exception as e:
            print(f"获取最近用户失败：{str(e)}")
            return None
    
    def get_recent_portfolio(self, user_id: int) -> Optional[Dict]:
        """获取用户最近创建的投资组合"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, risk_tolerance, initial_capital, investment_goal, 
                           created_at, is_active, total_value, risk_score
                    FROM portfolios
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (user_id,))
                portfolio = cursor.fetchone()
                if portfolio:
                    return {
                        "id": portfolio[0],
                        "name": portfolio[1],
                        "risk_tolerance": portfolio[2],
                        "initial_capital": portfolio[3],
                        "investment_goal": portfolio[4],
                        "created_at": portfolio[5],
                        "is_active": portfolio[6],
                        "total_value": portfolio[7],
                        "risk_score": portfolio[8]
                    }
                return None
        except Exception as e:
            print(f"获取最近投资组合失败：{str(e)}")
            return None
    
    def clear_all_data(self):
        """清空所有数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 按顺序删除数据，避免外键约束问题
                conn.execute("DELETE FROM transactions")
                conn.execute("DELETE FROM assets")
                conn.execute("DELETE FROM goals")
                conn.execute("DELETE FROM portfolios")
                conn.execute("DELETE FROM users")
                return True
        except Exception as e:
            print(f"清空数据失败：{str(e)}")
            return False
    
    def save_investment_analysis(self, user_id: int, symbol: str, analysis_type: str, analysis_data: dict) -> int:
        """保存投资分析数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO investment_analysis (user_id, symbol, analysis_type, analysis_data)
                    VALUES (?, ?, ?, ?)
                """, (user_id, symbol, analysis_type, json.dumps(analysis_data)))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"保存投资分析数据失败：{str(e)}")
            raise
    
    def get_investment_analysis(self, user_id: int, symbol: str, analysis_type: str) -> Optional[dict]:
        """获取投资分析数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM investment_analysis
                    WHERE user_id = ? AND symbol = ? AND analysis_type = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (user_id, symbol, analysis_type))
                row = cursor.fetchone()
                return json.loads(row['analysis_data']) if row else None
        except Exception as e:
            print(f"获取投资分析数据失败：{str(e)}")
            return None
    
    def save_profit_analysis(self, user_id: int, initial_capital: float, investment_period: int,
                            expected_return: float, monthly_investment: float, risk_tolerance: str,
                            total_investment: float, expected_profit: float, annualized_return: float) -> int:
        """保存收益分析数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO profit_analysis (
                        user_id, initial_capital, investment_period, expected_return,
                        monthly_investment, risk_tolerance, total_investment,
                        expected_profit, annualized_return
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, initial_capital, investment_period, expected_return,
                     monthly_investment, risk_tolerance, total_investment,
                     expected_profit, annualized_return))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"保存收益分析数据失败：{str(e)}")
            raise
    
    def get_profit_analysis(self, user_id: int) -> Optional[dict]:
        """获取收益分析数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM profit_analysis
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"获取收益分析数据失败：{str(e)}")
            return None 