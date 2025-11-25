# -deepseek-tushare-
基于deepseek和tushare的投资理财工具，支持财务分析
# 投资理财分析助手

这是一个基于 DeepSeek AI 的投资理财分析工具，同时调用tushareapi，帮用户获取相关数据，可以更好帮助用户进行投资决策和理财规划。

## 功能特点

- 智能对话：通过 DeepSeek API 实现自然语言交互
- 投资分析：提供专业的投资建议和分析
- 理财规划：帮助制定个性化的理财计划
- 实时响应：快速获取投资理财相关问题的解答

## 安装说明

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 创建 `.env` 文件并添加 DeepSeek API 密钥：
   ```
   DEEPSEEK_API_KEY=your_api_key_here
   TUSHARE_TOKEN=hhhhhhhhhhhhhhhhhhh
   ```

## 运行应用

```bash
streamlit run app.py
```

## 使用说明

1. 启动应用后，在输入框中输入您的投资理财问题
2. 系统会通过 DeepSeek AI 进行分析并给出专业建议
3. 可以持续对话，系统会记住上下文信息

## 注意事项

- 请确保您的 DeepSeek API 密钥有效
- 建议在提问时尽量具体，以便获得更准确的回答
- 本工具提供的建议仅供参考，投资决策需谨慎 
