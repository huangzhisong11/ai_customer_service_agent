# AI Customer Service Agent

一个可直接运行的 AI 客服系统 Demo，包含：

- FastAPI 后端
- RAG 知识库检索
- 多 Agent 流程：意图识别、知识检索、答案生成、质检
- SQLite 会话记录
- 简单前端聊天页面
- 可接入 OpenAI API，也支持无 API Key 的本地规则模式

## 1. 安装环境

```bash
cd ai_customer_service_agent
python -m venv .venv
```

Windows：

```bash
.\.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

## 2. 配置环境变量

复制配置文件：

```bash
copy .env.example .env
```

如果你有 OpenAI API Key，把 `.env` 里的内容改成：

```env
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4o-mini
USE_LLM=true
```

没有 API Key 也能跑，保持：

```env
USE_LLM=false
```

## 3. 启动项目

```bash
uvicorn app.main:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000
```

## 4. 添加知识库

把企业 FAQ、售后规则、产品说明写进：

```text
data/knowledge_base.md
```

然后重启服务即可。
