import streamlit as st
import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from config import APIConfig
from market_data import MarketDataService
from tushare_service import TushareService
from database import DatabaseService
from analysis import InvestmentAnalysis
from goal_tracker import GoalTracker
from models import InvestmentPortfolio, InvestmentGoal, InvestmentAsset
import pandas as pd
import plotly.graph_objects as go

# 加载配置
config = APIConfig()

# 设置页面配置
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
    <style>
    /* 全局样式 */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 聊天消息样式 */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    /* 用户消息样式 */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        margin-left: 2rem;
    }
    
    .stChatMessage[data-testid="user-message"]::before {
        content: "👤";
        position: absolute;
        left: -2rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
    }
    
    /* AI助手消息样式 */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
        border-left: 4px solid #4caf50;
        margin-right: 2rem;
    }
    
    .stChatMessage[data-testid="assistant-message"]::before {
        content: "🤖";
        position: absolute;
        right: -2rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        border-radius: 25px;
        padding: 12px 20px;
        font-size: 16px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
        background-color: white;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2196f3;
        box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%);
        color: white;
        font-weight: bold;
        padding: 10px 20px;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* 标题样式 */
    .stMarkdown h3 {
        color: #2c3e50;
        margin-top: 1.5rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 文本样式 */
    .stMarkdown p {
        color: #34495e;
        line-height: 1.6;
        font-size: 16px;
    }
    
    /* 列表样式 */
    .stMarkdown li {
        margin-bottom: 0.8rem;
        color: #34495e;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* 卡片样式 */
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2196f3, #4caf50);
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* 加载动画 */
    .stSpinner > div {
        border-color: #2196f3;
    }
    
    /* 错误提示样式 */
    .stAlert {
        border-radius: 15px;
        padding: 1rem;
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
        border-left: 4px solid #f44336;
    }
    </style>
    """, unsafe_allow_html=True)

# 设置页面标题和描述
st.title(config.APP_TITLE)
st.markdown(config.APP_DESCRIPTION)

# 初始化服务
market_service = MarketDataService()
tushare_service = TushareService()
db_service = DatabaseService()

# 初始化数据库表
db_service._init_db()

# 初始化会话状态
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "portfolio_id" not in st.session_state:
    st.session_state.portfolio_id = None
if "portfolio_data" not in st.session_state:
    st.session_state.portfolio_data = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# 尝试从数据库加载上次的用户信息
if st.session_state.user_id is None:
    try:
        # 获取最近创建的用户
        recent_user = db_service.get_recent_user()
        if recent_user:
            st.session_state.user_id = recent_user['id']
    except Exception as e:
        st.error(f"加载用户信息失败：{str(e)}")

# 尝试从数据库加载上次的投资组合
if st.session_state.user_id is not None and st.session_state.portfolio_id is None:
    try:
        # 获取最近创建的投资组合
        recent_portfolio = db_service.get_recent_portfolio(st.session_state.user_id)
        if recent_portfolio:
            st.session_state.portfolio_id = recent_portfolio['id']
            # 保存投资组合数据到会话状态
            st.session_state.portfolio_data = recent_portfolio
    except Exception as e:
        st.error(f"加载投资组合失败：{str(e)}")

# 创建侧边栏
st.sidebar.title("💰 投资助手")
st.sidebar.markdown("---")

# 功能导航
page = st.sidebar.radio(
    "选择功能",
    ["智能对话", "市场行情", "投资分析"]
)

# 用户信息
st.sidebar.markdown("### 👤 用户信息")
if st.session_state.user_id is None:
    with st.sidebar.form("user_form"):
        name = st.text_input("您的姓名")
        experience = st.selectbox(
            "投资经验",
            ["新手", "有一定经验", "资深投资者"]
        )
        if st.form_submit_button("保存"):
            try:
                user_id = db_service.create_user(name, experience)
                st.session_state.user_id = user_id
                st.success("用户信息保存成功！")
                st.rerun()
            except Exception as e:
                st.error(f"保存用户信息失败：{str(e)}")
else:
    try:
        user_info = db_service.get_user(st.session_state.user_id)
        if user_info:
            st.sidebar.write(f"👤 {user_info['name']}")
            st.sidebar.write(f"📊 {user_info['experience']}")
            if st.sidebar.button("切换用户"):
                st.session_state.user_id = None
                st.success("已退出当前用户")
                st.rerun()
        else:
            st.session_state.user_id = None
            st.rerun()
    except Exception as e:
        st.error(f"获取用户信息失败：{str(e)}")
        st.session_state.user_id = None
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 使用说明")
st.sidebar.markdown("""
✨ 输入您的投资理财问题

💡 获取专业的分析和建议

🔄 可以持续对话，系统会记住上下文
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 示例问题")
st.sidebar.markdown("""
📈 如何开始投资股票？

💰 基金和股票有什么区别？

📊 如何制定个人理财计划？

🌟 当前市场环境下如何配置资产？
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚠️ 免责声明")
st.sidebar.markdown("""
🔒 本工具提供的建议仅供参考，不构成投资建议。

⚠️ 投资有风险，入市需谨慎。
""")

# 添加清空数据按钮
st.sidebar.markdown("---")
st.sidebar.markdown("### 🗑️ 数据管理")
if st.sidebar.button("清空所有数据"):
    if st.sidebar.checkbox("⚠️ 我确认要清空所有数据，此操作不可恢复"):
        if st.sidebar.button("确认清空"):
            if db_service.clear_all_data():
                st.sidebar.success("数据已清空")
                st.session_state.user_id = None
                st.rerun()
            else:
                st.sidebar.error("清空数据失败")

# 智能对话页面
if page == "智能对话":
    # 主界面
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 顶部横幅
        st.markdown("""
        <div class="card" style='background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); color: white;'>
            <h2 style='margin: 0; font-weight: 600; display: flex; align-items: center; gap: 0.5rem;'>
                <span>💰</span> 欢迎使用投资理财分析助手
            </h2>
            <p style='margin: 10px 0 0 0; font-size: 16px; display: flex; align-items: center; gap: 0.5rem;'>
                <span>💡</span> 专业的投资建议，助您实现财富增长
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 初始化会话状态
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # 添加欢迎消息
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"👋 您好！我是您的投资理财助手。我可以为您提供专业的投资建议和理财规划。请问您有什么投资方面的问题需要咨询？"
            })
        
        # 显示历史消息
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # 用户输入
        if prompt := st.chat_input("💬 请输入您的投资理财问题", key="chat_input"):
            # 添加用户消息到会话
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # 调用DeepSeek API
            headers = {
                "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": st.session_state.messages,
                "temperature": 0.7
            }
            
            try:
                with st.spinner("🤔 正在思考..."):
                    response = requests.post(config.DEEPSEEK_API_URL, headers=headers, json=data)
                    response.raise_for_status()
                    ai_response = response.json()["choices"][0]["message"]["content"]
                    
                    # 添加AI响应到会话
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    with st.chat_message("assistant"):
                        st.markdown(ai_response)
                        
            except Exception as e:
                st.error(f"❌ 发生错误：{str(e)}")
    
    with col2:
        # 投资小贴士卡片
        st.markdown("""
        <div class="card">
            <h3 style='color: #2196f3; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;'>
                <span>📊</span> 投资小贴士
            </h3>
            <ul style='color: #34495e;'>
                <li>✨ 分散投资降低风险</li>
                <li>💎 长期持有优质资产</li>
                <li>📈 定期评估投资组合</li>
                <li>🧘 保持理性投资心态</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 市场动态卡片
        st.markdown("""
        <div class="card">
            <h3 style='color: #2196f3; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;'>
                <span>📈</span> 市场动态
            </h3>
            <ul style='color: #34495e;'>
                <li>🌍 关注宏观经济指标</li>
                <li>📊 了解行业发展趋势</li>
                <li>💡 把握市场投资机会</li>
                <li>🔄 及时调整投资策略</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 添加一个清空对话的按钮
        if st.button("🗑️ 清空对话历史", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

# 市场行情页面
elif page == "市场行情":
    st.header("📈 市场行情")
    
    # 创建标签页
    tab1, tab2, tab3 = st.tabs(["股票查询", "市场指数", "财务数据"])
    
    with tab1:
        st.subheader("股票查询")
        
        try:
            # 获取股票列表
            stock_list = tushare_service.get_stock_basic()
            if stock_list is not None and not stock_list.empty:
                stock_options = stock_list['name'] + ' (' + stock_list['ts_code'] + ')'
                selected_stock = st.selectbox("选择股票", stock_options)
                
                if selected_stock:
                    ts_code = selected_stock.split('(')[1].strip(')')
                    
                    # 创建两列布局
                    col1, col2 = st.columns(2)
                    
                    # 左侧显示公司信息
                    with col1:
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
                            <h3 style='color: #2c3e50; margin-top: 0;'>公司基本信息</h3>
                        """, unsafe_allow_html=True)
                        
                        # 获取公司基本信息
                        company_info = tushare_service.get_company_info(ts_code)
                        if company_info:
                            st.metric("公司名称", company_info.get('name', 'N/A'))
                            st.metric("上市日期", company_info.get('list_date', 'N/A'))
                            st.metric("所属行业", company_info.get('industry', 'N/A'))
                            
                            # 显示公司简介
                            st.markdown("### 公司简介")
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                                {company_info.get('introduction', '暂无公司简介')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 显示主营业务
                            st.markdown("### 主营业务")
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                                {company_info.get('main_business', '暂无主营业务信息')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 显示经营范围
                            st.markdown("### 经营范围")
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
                                {company_info.get('business_scope', '暂无经营范围信息')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 显示其他信息
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("注册资本", f"{company_info.get('reg_capital', 0):,.2f}万元")
                                st.metric("所在省份", company_info.get('province', 'N/A'))
                            with col2:
                                st.metric("所在城市", company_info.get('city', 'N/A'))
                                st.metric("公司网站", company_info.get('website', 'N/A'))
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # 右侧显示实时行情
                    with col2:
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px;'>
                            <h3 style='color: #2c3e50; margin-top: 0;'>实时行情</h3>
                        """, unsafe_allow_html=True)
                        
                        try:
                            # 获取实时行情
                            price_data = market_service.get_stock_price(ts_code.split('.')[0])
                            if price_data and "error" not in price_data:
                                st.metric("当前价格", f"¥{price_data.get('current', 'N/A')}")
                                st.metric("涨跌幅", f"{float(price_data.get('change_percent', 0)):.2f}%")
                                st.metric("最高价", f"¥{price_data.get('high', 'N/A')}")
                                st.metric("最低价", f"¥{price_data.get('low', 'N/A')}")
                                st.metric("成交量", f"{price_data.get('volume', 'N/A')}")
                                st.metric("成交额", f"¥{price_data.get('amount', 'N/A')}")
                            else:
                                st.warning("暂时无法获取实时行情，请稍后再试")
                        except Exception as e:
                            st.error(f"获取实时行情失败：{str(e)}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("暂时无法获取股票列表，请稍后再试")
        except Exception as e:
            st.error(f"获取股票列表失败：{str(e)}")
    
    with tab2:
        st.subheader("市场指数")
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                # 选择指数
                index_options = {
                    "上证指数": "000001.SH",
                    "深证成指": "399001.SZ",
                    "创业板指": "399006.SZ",
                    "沪深300": "000300.SH"
                }
                selected_index = st.selectbox("选择指数", list(index_options.keys()))
                index_code = index_options[selected_index]
                
                # 选择时间范围
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                date_range = st.date_input(
                    "选择时间范围",
                    value=(start_date, end_date),
                    max_value=end_date
                )
            except Exception as e:
                st.error(f"选择指数失败：{str(e)}")
            
        with col2:
            if 'date_range' in locals() and len(date_range) == 2:
                try:
                    start = date_range[0].strftime('%Y%m%d')
                    end = date_range[1].strftime('%Y%m%d')
                    index_data = tushare_service.get_index_data(index_code, start, end)
                    
                    if index_data is not None and not index_data.empty:
                        # 显示最新数据
                        latest = index_data.iloc[0]
                        st.write(f"当前点位: {latest.get('close', 'N/A')}")
                        st.write(f"涨跌幅: {((latest.get('close', 0)/latest.get('pre_close', 1)-1)*100):.2f}%")
                        st.write(f"成交量: {latest.get('vol', 'N/A')}")
                        st.write(f"成交额: {latest.get('amount', 'N/A')}")
                        
                        # 转换日期格式
                        index_data['trade_date'] = pd.to_datetime(index_data['trade_date'])
                        
                        # 绘制K线图
                        fig = go.Figure(data=[go.Candlestick(
                            x=index_data['trade_date'],
                            open=index_data['open'],
                            high=index_data['high'],
                            low=index_data['low'],
                            close=index_data['close'],
                            name='K线'
                        )])
                        
                        # 添加移动平均线
                        index_data['MA5'] = index_data['close'].rolling(window=5).mean()
                        index_data['MA10'] = index_data['close'].rolling(window=10).mean()
                        index_data['MA20'] = index_data['close'].rolling(window=20).mean()
                        
                        fig.add_trace(go.Scatter(
                            x=index_data['trade_date'],
                            y=index_data['MA5'],
                            name='MA5',
                            line=dict(color='blue')
                        ))
                        fig.add_trace(go.Scatter(
                            x=index_data['trade_date'],
                            y=index_data['MA10'],
                            name='MA10',
                            line=dict(color='orange')
                        ))
                        fig.add_trace(go.Scatter(
                            x=index_data['trade_date'],
                            y=index_data['MA20'],
                            name='MA20',
                            line=dict(color='red')
                        ))
                        
                        fig.update_layout(
                            title=f"{selected_index} K线图",
                            yaxis_title="点位",
                            xaxis_title="日期",
                            xaxis_rangeslider_visible=False,
                            height=600,
                            xaxis=dict(
                                type='date',
                                tickformat='%Y-%m-%d',
                                tickangle=45
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("暂时无法获取指数数据，请稍后再试")
                except Exception as e:
                    st.error(f"获取指数数据失败：{str(e)}")
    
    with tab3:
        st.subheader("财务数据")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'ts_code' in locals():
                try:
                    # 选择财务数据
                    financial_type = st.selectbox(
                        "选择财务数据",
                        ["财务指标", "利润表", "资产负债表", "现金流量表"]
                    )
                    
                    # 选择报告期
                    period = st.selectbox(
                        "选择报告期",
                        ["20231231", "20230930", "20230630", "20230331"]
                    )
                except Exception as e:
                    st.error(f"选择财务数据类型失败：{str(e)}")
        
        with col2:
            if 'ts_code' in locals() and 'financial_type' in locals():
                try:
                    # 获取财务数据
                    if financial_type == "财务指标":
                        data = tushare_service.get_financial_data(ts_code, period)
                    elif financial_type == "利润表":
                        data = tushare_service.get_income_data(ts_code, period)
                    elif financial_type == "资产负债表":
                        data = tushare_service.get_balance_data(ts_code, period)
                    else:
                        data = tushare_service.get_cashflow_data(ts_code, period)
                    
                    if data is not None and not data.empty:
                        # 显示主要财务指标
                        st.dataframe(data)
                    else:
                        st.warning("暂时无法获取财务数据，请稍后再试")
                except Exception as e:
                    st.error(f"获取财务数据失败：{str(e)}")

# 投资分析页面
elif page == "投资分析":
    st.header("📊 投资分析")
    
    # 创建标签页
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["资产配置", "收益分析", "风险评估", "技术分析", "基本面分析", "投资报告"])
    
    with tab1:
        st.subheader("资产配置分析")
        
        # 创建投资组合表单
        with st.form("portfolio_form"):
            st.write("### 创建投资组合")
            
            # 投资组合基本信息
            portfolio_name = st.text_input("投资组合名称")
            risk_tolerance = st.selectbox(
                "风险承受能力",
                ["保守", "稳健", "激进"]
            )
            investment_goal = st.selectbox(
                "投资目标",
                ["保值", "稳健增值", "高收益"]
            )
            
            # 添加资产
            st.write("### 添加资产")
            assets = []
            num_assets = st.number_input("资产数量", min_value=1, max_value=10, value=1)
            
            for i in range(num_assets):
                with st.expander(f"资产 {i+1}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        symbol = st.text_input(f"股票代码 {i+1}")
                        name = None
                        current_price = 0.0
                        
                        # 自动获取股票信息
                        if symbol:
                            try:
                                stock_info = tushare_service.get_stock_basic()
                                if stock_info is not None and not stock_info.empty:
                                    matched_stock = stock_info[stock_info['ts_code'] == symbol]
                                    if not matched_stock.empty:
                                        name = matched_stock.iloc[0]['name']
                                        st.text_input(f"股票名称 {i+1}", value=name, disabled=True)
                                    else:
                                        st.warning("未找到该股票信息")
                            except Exception as e:
                                st.error(f"获取股票信息失败：{str(e)}")
                        
                        # 获取实时价格
                        if symbol:
                            try:
                                price_data = market_service.get_stock_price(symbol.split('.')[0])
                                if price_data and "error" not in price_data:
                                    current_price = price_data.get('current', 0)
                                    st.number_input(f"当前价格 {i+1}", value=current_price, min_value=0.0, step=0.01, format="%.2f", disabled=True)
                            except Exception as e:
                                st.error(f"获取实时行情失败：{str(e)}")
                        
                        quantity = st.number_input(f"持仓数量 {i+1}", min_value=1, step=1)
                        cost_price = st.number_input(f"成本价 {i+1}", min_value=0.0, step=0.01, format="%.2f")
                    
                    with col2:
                        if name and current_price > 0:
                            # 计算资产价值
                            market_value = quantity * current_price
                            cost_value = quantity * cost_price
                            profit = market_value - cost_value
                            profit_rate = (profit / cost_value * 100) if cost_value > 0 else 0
                            
                            st.metric(f"当前市值 {i+1}", f"¥{market_value:,.2f}")
                            st.metric(f"盈亏 {i+1}", f"¥{profit:,.2f} ({profit_rate:.2f}%)")
                            
                            # 保存资产信息
                            assets.append({
                                'symbol': symbol,
                                'name': name,
                                'quantity': quantity,
                                'cost_price': cost_price,
                                'current_price': current_price,
                                'market_value': market_value,
                                'profit': profit,
                                'profit_rate': profit_rate
                            })
            
            # 添加提交按钮
            if st.form_submit_button("创建投资组合"):
                if portfolio_name and assets:
                    try:
                        # 计算投资组合总价值
                        total_value = sum(asset['market_value'] for asset in assets)
                        total_profit = sum(asset['profit'] for asset in assets)
                        total_profit_rate = (total_profit / (total_value - total_profit) * 100) if (total_value - total_profit) > 0 else 0
                        
                        # 保存投资组合
                        if st.session_state.user_id:
                            portfolio_id = db_service.create_portfolio(
                                user_id=st.session_state.user_id,
                                name=portfolio_name,
                                risk_tolerance=risk_tolerance,
                                investment_goal=investment_goal,
                                total_value=total_value,
                                total_profit=total_profit,
                                total_profit_rate=total_profit_rate,
                                initial_capital=total_value
                            )
                            
                            if portfolio_id:
                                # 保存 portfolio_id 到会话状态
                                st.session_state.portfolio_id = portfolio_id
                                
                                # 保存投资组合数据到会话状态
                                st.session_state.portfolio_data = {
                                    "id": portfolio_id,
                                    "name": portfolio_name,
                                    "risk_tolerance": risk_tolerance,
                                    "investment_goal": investment_goal,
                                    "total_value": total_value,
                                    "total_profit": total_profit,
                                    "total_profit_rate": total_profit_rate
                                }
                                
                                # 保存资产
                                for asset in assets:
                                    db_service.add_asset(
                                        portfolio_id=portfolio_id,
                                        symbol=asset['symbol'],
                                        name=asset['name'],
                                        quantity=asset['quantity'],
                                        cost_price=asset['cost_price'],
                                        current_price=asset['current_price'],
                                        market_value=asset['market_value'],
                                        profit=asset['profit'],
                                        profit_rate=asset['profit_rate']
                                    )
                                
                                st.success("投资组合创建成功！")
                                st.write(f"投资组合名称：{portfolio_name}")
                                st.write(f"总市值：¥{total_value:,.2f}")
                                st.write(f"总盈亏：¥{total_profit:,.2f} ({total_profit_rate:.2f}%)")
                                
                                # 显示资产配置饼图
                                fig = go.Figure(data=[go.Pie(
                                    labels=[asset['name'] for asset in assets],
                                    values=[asset['market_value'] for asset in assets],
                                    hole=.3
                                )])
                                fig.update_layout(title="资产配置")
                                st.plotly_chart(fig)
                            else:
                                st.error("创建投资组合失败，请重试")
                        else:
                            st.warning("请先登录后再创建投资组合")
                    except Exception as e:
                        st.error(f"创建投资组合失败：{str(e)}")
                else:
                    st.warning("请填写完整的投资组合信息")
            
            # 显示当前投资组合信息
            if st.session_state.portfolio_id:
                try:
                    # 从数据库获取最新的投资组合数据
                    portfolio = db_service.get_portfolio(st.session_state.portfolio_id)
                    if portfolio:
                        st.write("### 当前投资组合")
                        st.write(f"名称：{portfolio.get('name', 'N/A')}")
                        st.write(f"风险承受能力：{portfolio.get('risk_tolerance', 'N/A')}")
                        st.write(f"投资目标：{portfolio.get('investment_goal', 'N/A')}")
                        st.write(f"总市值：¥{float(portfolio.get('total_value', 0)):,.2f}")
                        st.write(f"总盈亏：¥{float(portfolio.get('total_profit', 0)):,.2f}")
                        st.write(f"收益率：{float(portfolio.get('total_profit_rate', 0)):.2f}%")
                        
                        # 显示资产列表
                        assets = db_service.get_assets(st.session_state.portfolio_id)
                        if assets:
                            st.write("#### 资产列表")
                            for asset in assets:
                                st.write(f"- {asset.get('name', 'N/A')} ({asset.get('symbol', 'N/A')})")
                                st.write(f"  持仓数量：{asset.get('quantity', 0)}")
                                st.write(f"  成本价：¥{float(asset.get('cost_price', 0)):,.2f}")
                                st.write(f"  当前价：¥{float(asset.get('current_price', 0)):,.2f}")
                                st.write(f"  市值：¥{float(asset.get('market_value', 0)):,.2f}")
                                st.write(f"  盈亏：¥{float(asset.get('profit', 0)):,.2f}")
                                st.write(f"  盈亏率：{float(asset.get('profit_rate', 0)):.2f}%")
                except Exception as e:
                    st.warning(f"获取投资组合信息失败：{str(e)}")
    
    with tab2:
        st.subheader("收益分析")
        
        # 创建收益分析表单
        with st.form("profit_analysis_form"):
            st.write("### 投资计划分析")
            st.info("""
            收益分析功能帮助您：
            1. 计算投资计划的预期收益
            2. 评估不同投资策略的效果
            3. 规划长期投资目标
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                initial_capital = st.number_input("初始资金", min_value=0.0, step=1000.0, format="%.2f")
                investment_period = st.number_input("投资期限(月)", min_value=1, step=1)
                expected_return = st.number_input("预期年化收益率(%)", min_value=0.0, step=0.1, format="%.1f")
            
            with col2:
                monthly_investment = st.number_input("每月追加投资", min_value=0.0, step=1000.0, format="%.2f")
                risk_tolerance = st.selectbox(
                    "风险承受能力",
                    ["保守", "稳健", "激进"]
                )
            
            if st.form_submit_button("分析"):
                try:
                    # 计算预期收益
                    monthly_rate = expected_return / 12 / 100
                    total_investment = initial_capital + monthly_investment * investment_period
                    
                    # 计算复利收益
                    future_value = initial_capital * (1 + monthly_rate) ** investment_period
                    if monthly_investment > 0:
                        future_value += monthly_investment * ((1 + monthly_rate) ** investment_period - 1) / monthly_rate
                    
                    # 计算总收益
                    total_profit = future_value - total_investment
                    annualized_return = ((future_value / total_investment) ** (12 / investment_period) - 1) * 100
                    
                    # 保存分析结果
                    if st.session_state.user_id:
                        db_service.save_profit_analysis(
                            st.session_state.user_id,
                            initial_capital,
                            investment_period,
                            expected_return,
                            monthly_investment,
                            risk_tolerance,
                            total_investment,
                            total_profit,
                            annualized_return
                        )
                    
                    # 显示分析结果
                    st.success("分析完成！")
                    
                    # 显示投资概览
                    st.write("### 投资概览")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("总投资", f"¥{total_investment:,.2f}")
                    with col2:
                        st.metric("预期总收益", f"¥{total_profit:,.2f}")
                    with col3:
                        st.metric("年化收益率", f"{annualized_return:.2f}%")
                    
                    # 显示详细分析
                    st.write("### 详细分析")
                    
                    # 投资构成分析
                    st.write("#### 投资构成")
                    investment_data = {
                        "初始资金": initial_capital,
                        "每月追加": monthly_investment * investment_period
                    }
                    fig_pie = go.Figure(data=[go.Pie(
                        labels=list(investment_data.keys()),
                        values=list(investment_data.values()),
                        hole=.3
                    )])
                    fig_pie.update_layout(title="投资构成分析")
                    st.plotly_chart(fig_pie)
                    
                    # 收益增长曲线
                    st.write("#### 收益增长曲线")
                    months = list(range(investment_period + 1))
                    values = [initial_capital * (1 + monthly_rate) ** m + 
                             (monthly_investment * ((1 + monthly_rate) ** m - 1) / monthly_rate if monthly_investment > 0 else 0)
                             for m in months]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=months,
                        y=values,
                        mode='lines',
                        name='资产价值'
                    ))
                    fig.update_layout(
                        title='预期资产增长曲线',
                        xaxis_title='投资月数',
                        yaxis_title='资产价值(元)'
                    )
                    st.plotly_chart(fig)
                    
                    # 显示投资建议
                    st.write("### 投资建议")
                    if risk_tolerance == "保守":
                        st.info("""
                        💡 保守型投资建议：
                        1. 建议选择低风险投资品种
                        2. 可以考虑货币基金、国债等
                        3. 保持稳定的投资节奏
                        """)
                    elif risk_tolerance == "稳健":
                        st.info("""
                        💡 稳健型投资建议：
                        1. 建议选择中等风险投资品种
                        2. 可以考虑债券基金、蓝筹股等
                        3. 适当配置不同资产类别
                        """)
                    else:
                        st.info("""
                        💡 激进型投资建议：
                        1. 建议选择高风险高收益品种
                        2. 可以考虑股票、期货等
                        3. 注意控制风险，设置止损
                        """)
                    
                except Exception as e:
                    st.error(f"分析失败：{str(e)}")
        
        # 显示历史分析记录
        if st.session_state.user_id:
            try:
                history = db_service.get_profit_analysis(st.session_state.user_id)
                if history:
                    st.write("### 历史分析记录")
                    st.write(f"分析时间：{history['created_at']}")
                    st.write(f"初始资金：¥{history['initial_capital']:,.2f}")
                    st.write(f"投资期限：{history['investment_period']}个月")
                    st.write(f"预期年化收益率：{history['expected_return']:.2f}%")
                    st.write(f"每月追加投资：¥{history['monthly_investment']:,.2f}")
                    st.write(f"风险承受能力：{history['risk_tolerance']}")
                    st.write(f"预期总收益：¥{history['expected_profit']:,.2f}")
                    st.write(f"年化收益率：{history['annualized_return']:.2f}%")
            except Exception as e:
                st.error(f"获取历史记录失败：{str(e)}")
    
    with tab3:
        st.subheader("风险评估")
        
        # 创建风险评估表单
        with st.form("risk_assessment_form"):
            st.write("### 风险承受能力评估")
            
            # 投资经验
            experience = st.selectbox(
                "您的投资经验",
                ["新手", "有一定经验", "资深投资者"]
            )
            
            # 投资目标
            investment_goal = st.selectbox(
                "您的投资目标",
                ["保值", "稳健增值", "高收益"]
            )
            
            # 投资期限
            time_horizon = st.selectbox(
                "您的投资期限",
                ["短期(1年以内)", "中期(1-3年)", "长期(3年以上)"]
            )
            
            # 风险承受能力
            risk_tolerance = st.slider(
                "您的风险承受能力",
                min_value=1,
                max_value=10,
                value=5,
                help="1表示最低风险承受能力，10表示最高风险承受能力"
            )
            
            if st.form_submit_button("评估"):
                try:
                    # 计算风险评分
                    experience_score = {"新手": 3, "有一定经验": 6, "资深投资者": 9}[experience]
                    goal_score = {"保值": 3, "稳健增值": 6, "高收益": 9}[investment_goal]
                    time_score = {"短期(1年以内)": 3, "中期(1-3年)": 6, "长期(3年以上)": 9}[time_horizon]
                    
                    total_score = (experience_score + goal_score + time_score + risk_tolerance) / 4
                    
                    # 确定风险等级
                    if total_score <= 4:
                        risk_level = "保守型"
                        risk_description = "适合低风险投资，如货币基金、国债等"
                    elif total_score <= 7:
                        risk_level = "稳健型"
                        risk_description = "适合中等风险投资，如债券基金、蓝筹股等"
                    else:
                        risk_level = "进取型"
                        risk_description = "适合高风险投资，如股票、期货等"
                    
                    # 显示评估结果
                    st.success("评估完成！")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("风险评分", f"{total_score:.1f}/10")
                        st.metric("风险等级", risk_level)
                    with col2:
                        st.write("### 投资建议")
                        st.write(risk_description)
                    
                    # 绘制风险评分雷达图
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=categories + [categories[0]],
                        fill='toself',
                        name='风险评分'
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 10]
                            )
                        ),
                        showlegend=False
                    )
                    st.plotly_chart(fig)
                    
                except Exception as e:
                    st.error(f"评估失败：{str(e)}")
    
    with tab4:
        st.subheader("技术分析")
        
        # 创建技术分析表单
        with st.form("technical_analysis_form"):
            st.write("### 技术指标分析")
            col1, col2 = st.columns(2)
            
            with col1:
                symbol = st.text_input("股票代码")
                if symbol:
                    try:
                        # 获取历史数据
                        end_date = datetime.now()
                        start_date = end_date - timedelta(days=365)
                        historical_data = tushare_service.get_stock_daily(symbol, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
                        
                        if historical_data is not None and not historical_data.empty:
                            # 计算技术指标
                            import pandas as pd
                            import numpy as np
                            
                            # 计算移动平均线
                            historical_data['MA5'] = historical_data['close'].rolling(window=5).mean()
                            historical_data['MA10'] = historical_data['close'].rolling(window=10).mean()
                            historical_data['MA20'] = historical_data['close'].rolling(window=20).mean()
                            
                            # 计算MACD
                            exp1 = historical_data['close'].ewm(span=12, adjust=False).mean()
                            exp2 = historical_data['close'].ewm(span=26, adjust=False).mean()
                            historical_data['MACD'] = exp1 - exp2
                            historical_data['Signal'] = historical_data['MACD'].ewm(span=9, adjust=False).mean()
                            
                            # 计算RSI
                            delta = historical_data['close'].diff()
                            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                            rs = gain / loss
                            historical_data['RSI'] = 100 - (100 / (1 + rs))
                            
                            # 显示技术指标图表
                            fig = go.Figure()
                            
                            # 添加K线图
                            fig.add_trace(go.Candlestick(
                                x=historical_data['trade_date'],
                                open=historical_data['open'],
                                high=historical_data['high'],
                                low=historical_data['low'],
                                close=historical_data['close'],
                                name='K线'
                            ))
                            
                            # 添加移动平均线
                            fig.add_trace(go.Scatter(
                                x=historical_data['trade_date'],
                                y=historical_data['MA5'],
                                name='MA5',
                                line=dict(color='blue')
                            ))
                            fig.add_trace(go.Scatter(
                                x=historical_data['trade_date'],
                                y=historical_data['MA10'],
                                name='MA10',
                                line=dict(color='orange')
                            ))
                            fig.add_trace(go.Scatter(
                                x=historical_data['trade_date'],
                                y=historical_data['MA20'],
                                name='MA20',
                                line=dict(color='red')
                            ))
                            
                            fig.update_layout(
                                title='K线图与技术指标',
                                yaxis_title='价格',
                                xaxis_title='日期'
                            )
                            st.plotly_chart(fig)
                            
                            # 显示MACD图表
                            fig_macd = go.Figure()
                            fig_macd.add_trace(go.Scatter(
                                x=historical_data['trade_date'],
                                y=historical_data['MACD'],
                                name='MACD',
                                line=dict(color='blue')
                            ))
                            fig_macd.add_trace(go.Scatter(
                                x=historical_data['trade_date'],
                                y=historical_data['Signal'],
                                name='Signal',
                                line=dict(color='orange')
                            ))
                            
                            fig_macd.update_layout(
                                title='MACD指标',
                                yaxis_title='MACD',
                                xaxis_title='日期'
                            )
                            st.plotly_chart(fig_macd)
                            
                            # 显示RSI图表
                            fig_rsi = go.Figure()
                            fig_rsi.add_trace(go.Scatter(
                                x=historical_data['trade_date'],
                                y=historical_data['RSI'],
                                name='RSI',
                                line=dict(color='purple')
                            ))
                            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                            
                            fig_rsi.update_layout(
                                title='RSI指标',
                                yaxis_title='RSI',
                                xaxis_title='日期'
                            )
                            st.plotly_chart(fig_rsi)
                            
                            # 显示技术分析建议
                            st.write("### 技术分析建议")
                            
                            # 分析移动平均线
                            current_price = historical_data['close'].iloc[-1]
                            ma5 = historical_data['MA5'].iloc[-1]
                            ma10 = historical_data['MA10'].iloc[-1]
                            ma20 = historical_data['MA20'].iloc[-1]
                            
                            if current_price > ma5 > ma10 > ma20:
                                st.success("多头排列：短期、中期、长期均线呈多头排列，显示强势上涨趋势")
                            elif current_price < ma5 < ma10 < ma20:
                                st.warning("空头排列：短期、中期、长期均线呈空头排列，显示下跌趋势")
                            else:
                                st.info("震荡整理：均线系统显示市场处于震荡整理阶段")
                            
                            # 分析MACD
                            macd = historical_data['MACD'].iloc[-1]
                            signal = historical_data['Signal'].iloc[-1]
                            
                            if macd > signal and macd > 0:
                                st.success("MACD金叉：显示买入信号")
                            elif macd < signal and macd < 0:
                                st.warning("MACD死叉：显示卖出信号")
                            
                            # 分析RSI
                            rsi = historical_data['RSI'].iloc[-1]
                            
                            if rsi > 70:
                                st.warning("RSI超买：显示市场可能过热，注意回调风险")
                            elif rsi < 30:
                                st.success("RSI超卖：显示市场可能超跌，存在反弹机会")
                            
                            # 构建大模型分析提示词
                            analysis_prompt = f"""
                            请基于以下技术指标数据进行分析：

                            股票代码：{symbol}
                            当前价格：{current_price:.2f}
                            移动平均线：
                            - MA5：{ma5:.2f}
                            - MA10：{ma10:.2f}
                            - MA20：{ma20:.2f}
                            
                            MACD指标：
                            - MACD：{macd:.2f}
                            - Signal：{signal:.2f}
                            
                            RSI指标：
                            - RSI：{rsi:.2f}
                            
                            请从以下几个方面进行分析：
                            1. 趋势分析（基于移动平均线）
                            2. 动量分析（基于MACD）
                            3. 超买超卖分析（基于RSI）
                            4. 综合技术面分析
                            5. 具体的交易建议和风险提示

                            注意：请用专业、客观的语气进行分析，并提供具体的建议。
                            """
                            
                            # 调用大模型API进行分析
                            try:
                                headers = {
                                    "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
                                    "Content-Type": "application/json"
                                }
                                
                                data = {
                                    "model": "deepseek-chat",
                                    "messages": [{"role": "user", "content": analysis_prompt}],
                                    "temperature": 0.7
                                }
                                
                                with st.spinner("🤔 正在生成技术分析..."):
                                    response = requests.post(config.DEEPSEEK_API_URL, headers=headers, json=data)
                                    response.raise_for_status()
                                    analysis_result = response.json()["choices"][0]["message"]["content"]
                                    
                                    # 显示分析结果
                                    st.markdown("### 智能技术分析")
                                    st.markdown(analysis_result)
                            except Exception as e:
                                st.error(f"生成技术分析失败：{str(e)}")
                        else:
                            st.warning("暂时无法获取历史数据，请稍后再试")
                    except Exception as e:
                        st.error(f"技术分析失败：{str(e)}")
            
            # 添加提交按钮
            if st.form_submit_button("分析"):
                st.rerun()
            else:
                st.warning("请点击分析按钮生成技术分析报告")
    
    with tab5:
        st.subheader("基本面分析")
        
        # 创建基本面分析表单
        with st.form("fundamental_analysis_form"):
            st.write("### 基本面指标分析")
            
            # 股票代码输入
            symbol = st.text_input("股票代码")
            
            # 提交按钮
            submit_button = st.form_submit_button("获取财务数据")
            
            if submit_button and symbol:
                try:
                    # 确保股票代码格式正确（添加市场后缀）
                    if not symbol.endswith('.SH') and not symbol.endswith('.SZ'):
                        if symbol.startswith('6'):
                            symbol = f"{symbol}.SH"
                        else:
                            symbol = f"{symbol}.SZ"
                            
                    # 获取最新报告期
                    current_date = datetime.now()
                    if current_date.month <= 3:
                        # 如果当前是1-3月，获取上一年年报
                        period = f"{current_date.year-1}1231"
                        st.info(f"当前为{current_date.year}年{current_date.month}月，获取{current_date.year-1}年年报数据")
                    elif current_date.month <= 4:
                        # 如果当前是4月，获取上一年年报
                        period = f"{current_date.year-1}1231"
                        st.info(f"当前为{current_date.year}年{current_date.month}月，获取{current_date.year-1}年年报数据")
                    elif current_date.month <= 5:
                        # 如果当前是5月，获取一季度报
                        period = f"{current_date.year}0331"
                        st.info(f"当前为{current_date.year}年{current_date.month}月，获取{current_date.year}年一季度报数据")
                    elif current_date.month <= 8:
                        # 如果当前是6-8月，获取半年报
                        period = f"{current_date.year}0630"
                        st.info(f"当前为{current_date.year}年{current_date.month}月，获取{current_date.year}年半年报数据")
                    elif current_date.month <= 10:
                        # 如果当前是9-10月，获取三季度报
                        period = f"{current_date.year}0930"
                        st.info(f"当前为{current_date.year}年{current_date.month}月，获取{current_date.year}年三季度报数据")
                    else:
                        # 如果当前是11-12月，获取三季度报
                        period = f"{current_date.year}0930"
                        st.info(f"当前为{current_date.year}年{current_date.month}月，获取{current_date.year}年三季度报数据")
                        
                    st.info(f"正在获取 {symbol} 的财务数据，报告期：{period[:4]}年{period[4:6]}月{period[6:]}日")
                        
                    # 获取财务指标数据
                    financial_data = tushare_service.get_financial_indicators(symbol, period)
                    
                    if financial_data is None:
                        st.error("获取财务数据失败：返回数据为空")
                        st.stop()
                    elif financial_data.empty:
                        st.warning(f"未找到 {symbol} 在 {period} 的财务数据，请检查股票代码是否正确或尝试其他报告期")
                        st.stop()
                    else:
                        # 将 Series 转换为字典
                        financial_dict = financial_data.iloc[0].to_dict()
                        
                        # 显示财务指标
                        st.subheader("财务指标")
                        indicators = financial_data  # 直接使用已获取的数据
                        
                        # 定义要显示的指标
                        indicator_groups = {
                            "每股指标": {
                                "eps": "基本每股收益",
                                "dt_eps": "稀释每股收益",
                                "total_revenue_ps": "每股营业总收入",
                                "revenue_ps": "每股营业收入",
                                "capital_rese_ps": "每股资本公积",
                                "surplus_rese_ps": "每股盈余公积",
                                "undist_profit_ps": "每股未分配利润",
                                "bps": "每股净资产",
                                "ocfps": "每股经营活动现金流",
                                "retainedps": "每股留存收益",
                                "cfps": "每股现金流量净额",
                                "ebit_ps": "每股息税前利润",
                                "fcff_ps": "每股企业自由现金流",
                                "fcfe_ps": "每股股东自由现金流"
                            },
                            "盈利能力": {
                                "roe": "净资产收益率",
                                "roe_waa": "加权平均净资产收益率",
                                "roe_dt": "扣非净资产收益率",
                                "roa": "总资产报酬率",
                                "npta": "总资产净利润",
                                "roic": "投入资本回报率",
                                "roe_yearly": "年化净资产收益率",
                                "roa2_yearly": "年化总资产报酬率",
                                "netprofit_margin": "销售净利率",
                                "grossprofit_margin": "销售毛利率",
                                "profit_to_gr": "净利润/营业总收入",
                                "op_of_gr": "营业利润/营业总收入",
                                "ebit_of_gr": "息税前利润/营业总收入"
                            },
                            "成长能力": {
                                "basic_eps_yoy": "基本每股收益同比增长率",
                                "dt_eps_yoy": "稀释每股收益同比增长率",
                                "cfps_yoy": "每股经营活动现金流同比增长率",
                                "op_yoy": "营业利润同比增长率",
                                "ebt_yoy": "利润总额同比增长率",
                                "netprofit_yoy": "净利润同比增长率",
                                "dt_netprofit_yoy": "扣非净利润同比增长率",
                                "ocf_yoy": "经营活动现金流同比增长率",
                                "roe_yoy": "净资产收益率同比增长率",
                                "bps_yoy": "每股净资产同比增长率",
                                "assets_yoy": "总资产同比增长率",
                                "eqt_yoy": "股东权益同比增长率",
                                "tr_yoy": "营业总收入同比增长率",
                                "or_yoy": "营业收入同比增长率"
                            },
                            "偿债能力": {
                                "current_ratio": "流动比率",
                                "quick_ratio": "速动比率",
                                "cash_ratio": "保守速动比率",
                                "debt_to_assets": "资产负债率",
                                "debt_to_eqt": "产权比率",
                                "eqt_to_debt": "权益乘数",
                                "tangibleasset_to_debt": "有形资产/负债合计",
                                "ocf_to_debt": "经营活动现金流/负债合计",
                                "ebit_to_interest": "息税前利润/利息支出"
                            },
                            "运营能力": {
                                "invturn_days": "存货周转天数",
                                "arturn_days": "应收账款周转天数",
                                "inv_turn": "存货周转率",
                                "ar_turn": "应收账款周转率",
                                "ca_turn": "流动资产周转率",
                                "fa_turn": "固定资产周转率",
                                "assets_turn": "总资产周转率",
                                "turn_days": "营业周期"
                            },
                            "现金流量": {
                                "fcff": "企业自由现金流",
                                "fcfe": "股东自由现金流",
                                "ocf_to_or": "经营活动现金流/营业收入",
                                "ocf_to_opincome": "经营活动现金流/营业利润",
                                "ocf_to_profit": "经营活动现金流/净利润",
                                "cash_to_liqdebt": "现金及现金等价物/流动负债",
                                "cash_to_liqdebt_withinterest": "现金及现金等价物/带息流动负债",
                                "ocf_to_shortdebt": "经营活动现金流/短期借款",
                                "ocf_to_debt": "经营活动现金流/负债合计"
                            },
                            "成本费用": {
                                "cogs_of_sales": "营业成本/营业收入",
                                "expense_of_sales": "销售期间费用率",
                                "saleexp_to_gr": "销售费用/营业总收入",
                                "adminexp_of_gr": "管理费用/营业总收入",
                                "finaexp_of_gr": "财务费用/营业总收入",
                                "impai_ttm": "资产减值损失/营业总收入",
                                "gc_of_gr": "营业总成本/营业总收入"
                            },
                            "资本结构": {
                                "currentdebt_to_debt": "流动负债/负债合计",
                                "longdeb_to_debt": "长期借款/负债合计",
                                "debt_to_eqt": "负债合计/股东权益合计",
                                "eqt_to_debt": "股东权益合计/负债合计",
                                "tangibleasset_to_debt": "有形资产/负债合计",
                                "tangibleasset_to_netdebt": "有形资产/净债务",
                                "assets_to_eqt": "资产总计/股东权益合计",
                                "dp_assets_to_eqt": "归属母公司股东的权益/股东权益合计"
                            }
                        }
                        
                        # 显示指标
                        for group_name, group_indicators in indicator_groups.items():
                            st.markdown(f"**{group_name}**")
                            cols = st.columns(3)
                            for i, (code, name) in enumerate(group_indicators.items()):
                                col = cols[i % 3]
                                value = indicators.iloc[0].get(code)
                                if pd.isna(value):
                                    col.metric(name, "暂无数据")
                                else:
                                    if 'ratio' in code or 'rate' in code or 'margin' in code or 'yoy' in code or 'qoq' in code:
                                        col.metric(name, f"{value:.2%}")
                                    elif 'ps' in code or 'bps' in code or 'eps' in code:
                                        col.metric(name, f"{value:.2f}")
                                    else:
                                        col.metric(name, f"{value:,.2f}")
                        
                        # 保存数据到会话状态
                        st.session_state.financial_data = financial_data
                        st.session_state.financial_dict = financial_dict
                        st.session_state.symbol = symbol
                        st.session_state.period = period
                except Exception as e:
                    st.error(f"获取财务数据失败：{str(e)}")
        
        # 在表单外部添加分析按钮
        if 'financial_data' in st.session_state:
            if st.button("生成财务分析"):
                try:
                    # 构建大模型分析提示词
                    analysis_prompt = f"""
                    请基于以下财务数据进行分析：

                    股票代码：{st.session_state.symbol}
                    报告期：{st.session_state.period[:4]}年{st.session_state.period[4:6]}月{st.session_state.period[6:]}日

                    主要财务指标：
                    - 基本每股收益：{st.session_state.financial_dict.get('eps', 'N/A')}
                    - 稀释每股收益：{st.session_state.financial_dict.get('dt_eps', 'N/A')}
                    - 每股净资产：{st.session_state.financial_dict.get('bps', 'N/A')}
                    - 净资产收益率：{st.session_state.financial_dict.get('roe', 'N/A')}%
                    - 总资产报酬率：{st.session_state.financial_dict.get('roa', 'N/A')}%
                    - 销售毛利率：{st.session_state.financial_dict.get('grossprofit_margin', 'N/A')}%
                    - 销售净利率：{st.session_state.financial_dict.get('netprofit_margin', 'N/A')}%
                    - 资产负债率：{st.session_state.financial_dict.get('debt_to_assets', 'N/A')}%
                    - 流动比率：{st.session_state.financial_dict.get('current_ratio', 'N/A')}
                    - 速动比率：{st.session_state.financial_dict.get('quick_ratio', 'N/A')}
                    - 存货周转率：{st.session_state.financial_dict.get('inv_turn', 'N/A')}
                    - 应收账款周转率：{st.session_state.financial_dict.get('ar_turn', 'N/A')}
                    - 总资产周转率：{st.session_state.financial_dict.get('assets_turn', 'N/A')}
                    - 经营活动现金流/营业收入：{st.session_state.financial_dict.get('ocf_to_or', 'N/A')}%

                    请从以下几个方面进行分析：
                    1. 盈利能力分析
                    2. 偿债能力分析
                    3. 运营能力分析
                    4. 成长性分析
                    5. 现金流分析
                    6. 投资建议

                    注意：请用专业、客观的语气进行分析，并提供具体的建议。
                    """
                    
                    # 调用大模型API进行分析
                    try:
                        headers = {
                            "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
                            "Content-Type": "application/json"
                        }
                        
                        data = {
                            "model": "deepseek-chat",
                            "messages": [{"role": "user", "content": analysis_prompt}],
                            "temperature": 0.7
                        }
                        
                        with st.spinner("🤔 正在生成财务分析..."):
                            response = requests.post(config.DEEPSEEK_API_URL, headers=headers, json=data)
                            response.raise_for_status()
                            analysis_result = response.json()["choices"][0]["message"]["content"]
                            
                            # 显示分析结果
                            st.markdown("### 智能财务分析")
                            st.markdown(analysis_result)
                    except Exception as e:
                        st.error(f"生成财务分析失败：{str(e)}")
                except Exception as e:
                    st.error(f"分析失败：{str(e)}")

    with tab6:
        st.subheader("投资报告")
        
        # 创建两个列
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # 创建投资报告生成表单
            with st.form("investment_report_form"):
                st.write("### 一键生成投资报告")
                st.info("""
                投资报告功能将：
                1. 分析您的投资组合表现
                2. 评估市场环境和风险
                3. 提供个性化的投资建议
                """)
                
                if st.form_submit_button("生成投资报告"):
                    try:
                        # 获取用户信息
                        if not st.session_state.user_id:
                            st.error("请先登录后再生成报告")
                            st.stop()
                        
                        user_info = db_service.get_user(st.session_state.user_id)
                        if not user_info:
                            st.error("获取用户信息失败，请重新登录")
                            st.stop()
                        
                        # 获取投资组合信息
                        portfolios = db_service.get_portfolios(st.session_state.user_id)
                        if not portfolios:
                            st.error("您还没有创建投资组合，请先创建投资组合")
                            st.stop()
                        
                        # 获取市场数据
                        try:
                            market_data = market_service.get_market_overview()
                            if not market_data:
                                market_data = {
                                    'sh_index': 'N/A',
                                    'sz_index': 'N/A',
                                    'cyb_index': 'N/A',
                                    'market_sentiment': 'N/A'
                                }
                        except Exception as e:
                            st.warning(f"获取市场数据失败：{str(e)}")
                            market_data = {
                                'sh_index': 'N/A',
                                'sz_index': 'N/A',
                                'cyb_index': 'N/A',
                                'market_sentiment': 'N/A'
                            }
                        
                        # 构建报告内容
                        report_content = f"""
# 投资分析报告
**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 一、用户概况
- 姓名：{user_info.get('name', 'N/A')}
- 投资经验：{user_info.get('experience', 'N/A')}

## 二、投资组合分析
"""
                        
                        # 添加投资组合分析
                        total_value = 0
                        total_profit = 0
                        portfolio_assets = []
                        
                        for portfolio in portfolios:
                            try:
                                assets = db_service.get_assets(portfolio['id'])
                                if not assets:
                                    continue
                                    
                                portfolio_value = sum(float(asset.get('market_value', 0)) for asset in assets)
                                portfolio_profit = sum(float(asset.get('profit', 0)) for asset in assets)
                                total_value += portfolio_value
                                total_profit += portfolio_profit
                                
                                portfolio_assets.extend(assets)
                                
                                report_content += f"""
### 投资组合：{portfolio.get('name', 'N/A')}
- 风险承受能力：{portfolio.get('risk_tolerance', 'N/A')}
- 投资目标：{portfolio.get('investment_goal', 'N/A')}
- 组合市值：¥{portfolio_value:,.2f}
- 组合收益：¥{portfolio_profit:,.2f}
- 收益率：{(portfolio_profit / (portfolio_value - portfolio_profit) * 100) if (portfolio_value - portfolio_profit) > 0 else 0:.2f}%

#### 资产配置
"""
                                
                                # 添加资产配置分析
                                for asset in assets:
                                    report_content += f"""
- {asset.get('name', 'N/A')} ({asset.get('symbol', 'N/A')})
  - 持仓数量：{asset.get('quantity', 0)}
  - 成本价：¥{float(asset.get('cost_price', 0)):,.2f}
  - 当前价：¥{float(asset.get('current_price', 0)):,.2f}
  - 市值：¥{float(asset.get('market_value', 0)):,.2f}
  - 盈亏：¥{float(asset.get('profit', 0)):,.2f}
  - 盈亏率：{float(asset.get('profit_rate', 0)):.2f}%
"""
                            except Exception as e:
                                st.warning(f"处理投资组合 {portfolio.get('name', 'N/A')} 时出错：{str(e)}")
                                continue
                        
                        # 添加市场分析
                        report_content += f"""
## 三、市场环境分析
- 上证指数：{market_data.get('sh_index', 'N/A')}
- 深证成指：{market_data.get('sz_index', 'N/A')}
- 创业板指：{market_data.get('cyb_index', 'N/A')}
- 市场情绪：{market_data.get('market_sentiment', 'N/A')}
"""
                        
                        # 构建大模型分析提示词
                        analysis_prompt = f"""
                        请基于以下投资数据进行分析：

                        用户信息：
                        - 姓名：{user_info.get('name', 'N/A')}
                        - 投资经验：{user_info.get('experience', 'N/A')}

                        投资组合概况：
                        - 总市值：¥{total_value:,.2f}
                        - 总收益：¥{total_profit:,.2f}
                        - 总收益率：{(total_profit / (total_value - total_profit) * 100) if (total_value - total_profit) > 0 else 0:.2f}%

                        资产配置：
                        {[f"{asset.get('name', 'N/A')} ({asset.get('symbol', 'N/A')}) - 市值：¥{float(asset.get('market_value', 0)):,.2f} - 盈亏率：{float(asset.get('profit_rate', 0)):.2f}%" for asset in portfolio_assets]}

                        市场环境：
                        - 上证指数：{market_data.get('sh_index', 'N/A')}
                        - 深证成指：{market_data.get('sz_index', 'N/A')}
                        - 创业板指：{market_data.get('cyb_index', 'N/A')}
                        - 市场情绪：{market_data.get('market_sentiment', 'N/A')}

                        请从以下几个方面进行分析：
                        1. 投资组合表现评估
                        2. 资产配置合理性分析
                        3. 风险控制建议
                        4. 市场环境对投资组合的影响
                        5. 具体的投资建议和调整方案

                        注意：请用专业、客观的语气进行分析，并提供具体的建议。
                        """
                        
                        # 调用大模型API进行分析
                        try:
                            headers = {
                                "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
                                "Content-Type": "application/json"
                            }
                            
                            data = {
                                "model": "deepseek-chat",
                                "messages": [{"role": "user", "content": analysis_prompt}],
                                "temperature": 0.7
                            }
                            
                            with st.spinner("🤔 正在生成投资分析..."):
                                response = requests.post(config.DEEPSEEK_API_URL, headers=headers, json=data)
                                response.raise_for_status()
                                analysis_result = response.json()["choices"][0]["message"]["content"]
                                
                                # 添加分析结果到报告
                                report_content += f"""
## 四、智能投资分析

{analysis_result}
"""
                        except Exception as e:
                            st.error(f"生成投资分析失败：{str(e)}")
                            report_content += """
## 四、投资建议

（由于技术原因，暂时无法生成智能分析。请稍后重试。）
"""
                        
                        # 显示报告
                        st.markdown(report_content)
                        
                        # 保存报告内容到会话状态
                        st.session_state.report_content = report_content
                        
                    except Exception as e:
                        st.error(f"生成报告失败：{str(e)}")
                        st.stop()
        
        with col2:
            # 在右侧列中添加下载按钮
            if "report_content" in st.session_state:
                st.download_button(
                    label="下载报告",
                    data=st.session_state.report_content,
                    file_name=f"投资分析报告_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )

# 添加页脚
st.markdown("---")
st.markdown("© 2025 投资理财分析助手 | 基于DeepSeek AI") 