from typing import List, Dict
from datetime import datetime
from models import InvestmentPortfolio, RiskAssessment, InvestmentStrategy
import numpy as np
import pandas as pd

class InvestmentAnalysis:
    def __init__(self, portfolio: InvestmentPortfolio):
        self.portfolio = portfolio

    def calculate_portfolio_metrics(self) -> Dict:
        """计算投资组合指标"""
        total_value = sum(asset.quantity * asset.current_price for asset in self.portfolio.assets)
        total_cost = sum(asset.quantity * asset.purchase_price for asset in self.portfolio.assets)
        total_return = (total_value - total_cost) / total_cost if total_cost > 0 else 0.0
        
        asset_allocation = self._calculate_asset_allocation()
        risk_score = self._calculate_risk_score()
        
        return {
            "total_value": total_value,
            "total_cost": total_cost,
            "total_return": total_return,
            "asset_allocation": asset_allocation,
            "risk_score": risk_score
        }

    def _calculate_asset_allocation(self) -> Dict[str, float]:
        """计算资产配置比例"""
        total_value = sum(asset.quantity * asset.current_price for asset in self.portfolio.assets)
        if total_value == 0:
            return {}
            
        allocation = {}
        for asset in self.portfolio.assets:
            category = asset.category
            value = asset.quantity * asset.current_price
            allocation[category] = allocation.get(category, 0) + value / total_value
            
        return allocation

    def _calculate_risk_score(self) -> float:
        """计算风险评分"""
        if not self.portfolio.assets:
            return 0.0
            
        # 基于资产类别的风险权重
        risk_weights = {
            "股票": 0.8,
            "基金": 0.6,
            "债券": 0.3,
            "现金": 0.1
        }
        
        # 计算加权风险得分
        total_value = sum(asset.quantity * asset.current_price for asset in self.portfolio.assets)
        if total_value == 0:
            return 0.0
            
        weighted_risk = 0.0
        for asset in self.portfolio.assets:
            weight = (asset.quantity * asset.current_price) / total_value
            risk_weight = risk_weights.get(asset.category, 0.5)
            weighted_risk += weight * risk_weight
            
        return weighted_risk

    def assess_risk(self) -> RiskAssessment:
        """评估投资组合风险"""
        try:
            # 计算总价值
            total_value = sum(asset.quantity * asset.current_price for asset in self.portfolio.assets)
            if total_value == 0:
                return RiskAssessment(
                    risk_score=0.0,
                    risk_level="低",
                    risk_factors=["投资组合为空"],
                    suggestions=["添加资产以开始投资"],
                    assessment_date=datetime.now()
                )
            
            # 计算各类资产占比
            asset_categories = {}
            for asset in self.portfolio.assets:
                category = asset.category
                value = asset.quantity * asset.current_price
                asset_categories[category] = asset_categories.get(category, 0) + value
            
            # 计算风险分数
            risk_score = 0.0
            risk_factors = []
            
            # 1. 资产集中度风险
            if len(asset_categories) < 3:
                risk_score += 0.3
                risk_factors.append("资产类别过于集中")
            
            # 2. 单一资产风险
            for category, value in asset_categories.items():
                if value / total_value > 0.5:
                    risk_score += 0.2
                    risk_factors.append(f"{category}占比过高")
            
            # 3. 波动性风险
            for asset in self.portfolio.assets:
                if asset.cost_price == 0:  # 添加成本价为零的检查
                    continue
                if asset.current_price / asset.cost_price > 1.5:
                    risk_score += 0.1
                    risk_factors.append(f"{asset.name}涨幅过大")
                elif asset.current_price / asset.cost_price < 0.8:
                    risk_score += 0.2
                    risk_factors.append(f"{asset.name}跌幅较大")
            
            # 确定风险等级
            if risk_score < 0.3:
                risk_level = "低"
            elif risk_score < 0.6:
                risk_level = "中"
            else:
                risk_level = "高"
            
            # 生成建议
            suggestions = []
            if "资产类别过于集中" in risk_factors:
                suggestions.append("建议增加资产类别，实现多元化投资")
            if any("占比过高" in factor for factor in risk_factors):
                suggestions.append("建议调整资产配置，降低单一资产占比")
            if any("涨幅过大" in factor for factor in risk_factors):
                suggestions.append("建议考虑部分获利了结")
            if any("跌幅较大" in factor for factor in risk_factors):
                suggestions.append("建议评估是否需要止损")
            
            return RiskAssessment(
                risk_score=risk_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                suggestions=suggestions,
                assessment_date=datetime.now()
            )
        except Exception as e:
            print(f"风险评估失败：{str(e)}")
            return RiskAssessment(
                risk_score=0.0,
                risk_level="未知",
                risk_factors=["风险评估过程出错"],
                suggestions=["请检查投资组合数据是否正确"],
                assessment_date=datetime.now()
            )

    def recommend_strategy(self) -> InvestmentStrategy:
        """推荐投资策略"""
        risk_score = self._calculate_risk_score()
        
        if risk_score < 0.3:
            strategy_type = "保守型"
            expected_return = 0.05
            risk_level = "低风险"
            strategy_points = [
                "以保本为主要目标",
                "配置高比例固定收益类资产",
                "少量配置权益类资产",
                "保持较高流动性"
            ]
        elif risk_score < 0.7:
            strategy_type = "平衡型"
            expected_return = 0.08
            risk_level = "中风险"
            strategy_points = [
                "平衡收益与风险",
                "均衡配置各类资产",
                "适当配置权益类资产",
                "保持适度流动性"
            ]
        else:
            strategy_type = "进取型"
            expected_return = 0.12
            risk_level = "高风险"
            strategy_points = [
                "追求较高收益",
                "重点配置权益类资产",
                "适当配置另类资产",
                "保持必要流动性"
            ]
            
        # 计算策略适合度
        suitability_score = 1.0 - abs(risk_score - 0.5)  # 越接近0.5分越高
            
        return InvestmentStrategy(
            strategy_type=strategy_type,
            strategy_points=strategy_points,
            suitability_score=suitability_score,
            expected_return=expected_return,
            risk_level=risk_level
        ) 