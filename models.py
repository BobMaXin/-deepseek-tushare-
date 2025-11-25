from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class InvestmentAsset(BaseModel):
    """投资资产模型"""
    symbol: str
    name: str
    category: str  # 资产类别（股票、基金、债券等）
    quantity: int
    cost_price: float
    current_price: float
    purchase_price: float  # 购买价格
    purchase_date: datetime
    last_updated: datetime = Field(default_factory=datetime.now)

class InvestmentPortfolio:
    def __init__(self, name: str, risk_tolerance: str, initial_capital: float, investment_goal: str,
                 assets: List[InvestmentAsset] = None, total_value: float = 0, risk_score: float = 0):
        self.name = name
        self.risk_tolerance = risk_tolerance
        self.initial_capital = initial_capital
        self.investment_goal = investment_goal
        self.assets = assets or []
        self.total_value = total_value
        self.risk_score = risk_score
        self.created_at = datetime.now()
        self.is_active = True
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'name': self.name,
            'risk_tolerance': self.risk_tolerance,
            'initial_capital': self.initial_capital,
            'investment_goal': self.investment_goal,
            'total_value': self.total_value,
            'risk_score': self.risk_score,
            'created_at': self.created_at,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InvestmentPortfolio':
        """从字典创建对象"""
        return cls(
            name=data.get('name', ''),
            risk_tolerance=data.get('risk_tolerance', '稳健'),
            initial_capital=data.get('initial_capital', 0),
            investment_goal=data.get('investment_goal', '长期财富增值'),
            total_value=data.get('total_value', 0),
            risk_score=data.get('risk_score', 0)
        )
    
    def calculate_total_value(self) -> float:
        """计算投资组合总价值"""
        return sum(asset.quantity * asset.current_price for asset in self.assets)
    
    def calculate_risk_score(self) -> float:
        """计算投资组合风险评分"""
        if not self.assets:
            return 0
        
        # 根据风险承受能力设置基础风险系数
        risk_coefficient = {
            '保守': 0.5,
            '稳健': 1.0,
            '激进': 1.5
        }.get(self.risk_tolerance, 1.0)
        
        # 计算资产波动率加权平均
        total_value = self.calculate_total_value()
        if total_value == 0:
            return 0
        
        weighted_volatility = sum(
            (asset.quantity * asset.current_price / total_value) * 
            (abs(asset.current_price - asset.cost_price) / asset.cost_price)
            for asset in self.assets
        )
        
        return weighted_volatility * risk_coefficient

class InvestmentGoal(BaseModel):
    """投资目标模型"""
    name: str
    target_amount: float
    current_amount: float = 0.0
    deadline: datetime
    risk_tolerance: str  # 保守、稳健、激进
    progress: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)

class RiskAssessment(BaseModel):
    """风险评估模型"""
    risk_score: float
    risk_level: str  # 低风险、中风险、高风险
    risk_factors: List[str]
    suggestions: List[str]
    assessment_date: datetime = Field(default_factory=datetime.now)

class InvestmentStrategy(BaseModel):
    """投资策略模型"""
    strategy_type: str  # 保守型、平衡型、进取型
    strategy_points: List[str]
    suitability_score: float
    expected_return: float
    risk_level: str
    created_at: datetime = Field(default_factory=datetime.now) 