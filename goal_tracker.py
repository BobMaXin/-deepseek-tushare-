from typing import List, Dict
from datetime import datetime, timedelta
from models import InvestmentGoal
import pandas as pd

class GoalTracker:
    def __init__(self):
        self.goals: List[InvestmentGoal] = []

    def add_goal(self, goal: InvestmentGoal) -> None:
        """添加投资目标"""
        self.goals.append(goal)

    def update_goal_progress(self, goal_name: str, current_amount: float) -> None:
        """更新目标进度"""
        for goal in self.goals:
            if goal.name == goal_name:
                goal.current_amount = current_amount
                goal.progress = min(current_amount / goal.target_amount, 1.0)
                break

    def get_goal_progress(self, goal_name: str) -> Dict:
        """获取目标进度"""
        for goal in self.goals:
            if goal.name == goal_name:
                return {
                    "name": goal.name,
                    "target_amount": goal.target_amount,
                    "current_amount": goal.current_amount,
                    "progress": goal.progress,
                    "remaining_amount": goal.target_amount - goal.current_amount,
                    "days_remaining": (goal.deadline - datetime.now()).days
                }
        return {}

    def calculate_monthly_saving(self, goal_name: str) -> float:
        """计算每月需要储蓄的金额"""
        goal = next((g for g in self.goals if g.name == goal_name), None)
        if not goal:
            return 0.0
        
        remaining_days = (goal.deadline - datetime.now()).days
        if remaining_days <= 0:
            return 0.0
        
        remaining_months = remaining_days / 30
        remaining_amount = goal.target_amount - goal.current_amount
        
        return remaining_amount / remaining_months

    def get_all_goals_progress(self) -> List[Dict]:
        """获取所有目标的进度"""
        return [
            {
                "name": goal.name,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "progress": goal.progress,
                "remaining_amount": goal.target_amount - goal.current_amount,
                "days_remaining": (goal.deadline - datetime.now()).days,
                "monthly_saving": self.calculate_monthly_saving(goal.name)
            }
            for goal in self.goals
        ]

    def generate_progress_report(self) -> Dict:
        """生成进度报告"""
        total_target = sum(goal.target_amount for goal in self.goals)
        total_current = sum(goal.current_amount for goal in self.goals)
        total_progress = total_current / total_target if total_target > 0 else 0
        
        return {
            "total_goals": len(self.goals),
            "total_target_amount": total_target,
            "total_current_amount": total_current,
            "total_progress": total_progress,
            "goals": self.get_all_goals_progress(),
            "risk_distribution": self._calculate_risk_distribution()
        }

    def _calculate_risk_distribution(self) -> Dict[str, float]:
        """计算风险分布"""
        risk_levels = ["保守", "稳健", "激进"]
        distribution = {level: 0.0 for level in risk_levels}
        
        total_target = sum(goal.target_amount for goal in self.goals)
        if total_target == 0:
            return distribution
        
        for goal in self.goals:
            distribution[goal.risk_tolerance] += goal.target_amount / total_target
        
        return distribution

    def suggest_goal_adjustments(self) -> List[str]:
        """建议目标调整"""
        suggestions = []
        
        # 检查目标完成时间
        for goal in self.goals:
            remaining_days = (goal.deadline - datetime.now()).days
            monthly_saving = self.calculate_monthly_saving(goal.name)
            
            if remaining_days < 0:
                suggestions.append(f"目标 '{goal.name}' 已过期，建议重新设定截止日期")
            elif monthly_saving > goal.current_amount * 0.5:
                suggestions.append(f"目标 '{goal.name}' 每月储蓄金额较高，建议考虑延长完成时间或降低目标金额")
        
        # 检查风险分布
        risk_distribution = self._calculate_risk_distribution()
        if risk_distribution["激进"] > 0.5:
            suggestions.append("激进型目标占比过高，建议增加稳健型目标以平衡风险")
        elif risk_distribution["保守"] > 0.7:
            suggestions.append("保守型目标占比过高，可以考虑适当增加收益目标")
        
        return suggestions 