# 📚 教育知识库文档对话后端系统

<div align="center">

**基于AI技术的新一代智能教学支持平台**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📖 项目简介

本项目聚焦于**人工智能与高等教育深度融合**的创新实践，致力于构建以AI赋能为核心的新一代教学支持体系。通过自主研发智能教学平台、重构课程内容与教学方法，项目探索出一条"理论—实验协同、目标导向驱动、学生中心主导"的新型教学路径。

### 🎯 核心价值

- **智能问答助手**：基于RAG（检索增强生成）技术，为学生提供实时、精准的知识问答服务
- **学习行为分析**：通过智能对话记录，实现对学生学习过程的实时辅助与精准反馈
- **教学效率提升**：显著提升教学效率与学习体验，推动学生从被动接受知识转向主动建构能力
- **产教融合实践**：探索产教融合背景下高校课程改革的新路径，为国产化技术生态在高等教育中的落地提供支撑

### 🌟 项目意义

本项目积极响应国家关于**教育数字化**与**信创人才培养**的战略部署，为破解当前高校教学中存在的资源不足、模式滞后、支撑薄弱等共性难题提供了系统性解决方案。通过将人工智能技术深度融入教学全流程，项目不仅提升了课程的互动性、实用性与前瞻性，更有效激发了学生的内生学习动力与工程创新能力。

更重要的是，该项目探索出一条产教融合背景下高校课程改革的新路径，为国产化技术生态在高等教育中的落地提供了教育学层面的支撑范例。其形成的"**智能助学+协同育人**"模式，具有广泛的适用性和推广价值，对推动高等教育高质量发展、培养具备数字素养与创新能力的新时代人才具有重要意义。

---

## ✨ 核心功能

### 🔍 智能问答系统
- **向量检索**：基于BGE Embeddings和Supabase向量数据库的语义相似度搜索
- **多表查询**：支持跨多个知识库表的联合检索
- **RAG增强**：结合大模型（OpenAI/ChatGLM3）生成精准答案
- **参考链接**：自动提供相关文档参考链接

### 📚 知识库管理
- **多种导入方式**：支持JSON格式、文本内容、文件上传等多种数据导入方式
- **批量处理**：支持批量添加问答对到向量数据库
- **元数据管理**：支持文档URL等元数据关联
- **分表存储**：支持按不同表名分类存储知识内容

### 💬 微信集成
- **自动回复**：微信公众号智能问答自动回复
- **多账号支持**：支持多个微信公众号账号配置
- **消息分片**：自动处理超长消息的分片发送
- **异步处理**：采用多线程异步处理，提升响应速度

### 🤖 大模型支持
- **OpenAI API**：支持OpenAI系列模型
- **ChatGLM3**：支持本地部署的ChatGLM3模型
- **灵活切换**：可配置切换不同的大模型服务

---

## 🏗️ 技术架构

### 核心技术栈

- **Web框架**：Flask 3.0.2
- **向量数据库**：Supabase (PostgreSQL + pgvector)
- **RAG框架**：LangChain
- **文本嵌入**：BGE Embeddings / OpenAI Embeddings
- **大模型**：OpenAI API / ChatGLM3
- **微信SDK**：wechatpy

### 系统架构

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  微信客户端  │────▶│  Flask API   │────▶│  向量数据库  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌─────────────┐
                    │  LangChain   │────▶│  大模型服务  │
                    │    RAG       │     │ OpenAI/GLM │
                    └──────────────┘     └─────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Supabase 账户（用于向量数据库）
- OpenAI API Key 或 ChatGLM3 本地部署服务
- 微信公众号（可选，用于微信集成）

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd eduknowledge.backend-main
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

创建 `.env` 文件（可参考 `.env.sample`），配置以下环境变量：

```bash
# OpenAI配置
OPENAI_API_KEY=sk-xxxx                    # OpenAI API密钥
OPENAI_API_BASE=https://api.openai.com/v1 # OpenAI API基础URL

# Supabase配置
PYTHON_SUPABASE_URL=http://your-supabase-url      # Supabase项目URL
PYTHON_SUPABASE_ANNOKEY=your-supabase-annokey     # Supabase匿名密钥

# 微信配置（可选）
WECHAT_APPID=wxxxx                      # 微信公众号AppID
WECHAT_APPSECRET=xxxx                   # 微信公众号AppSecret
WECHAT_APPID_DXY=wxxxx                  # 第二个公众号AppID（可选）
WECHAT_APPSECRET_DXY=xxxx               # 第二个公众号AppSecret（可选）
```

#### 4. 配置大模型服务

编辑 `config.py` 文件，配置ChatGLM3服务地址：

```python
ChatGLM3_endpoint_url = "http://your-chatglm3-server:8000/v1/chat/completions"
```

#### 5. 启动服务

**开发环境：**
```bash
python app.py
```

**生产环境：**
```bash
gunicorn app:app -c gunicorn.conf.py
```

服务将在 `http://0.0.0.0:5000` 启动。

---

## 📡 API接口文档

### 知识库管理接口

#### 1. 添加问答对（JSON格式）

```http
POST /addQaFromJson_bge
Content-Type: application/json

{
  "qa_json_list": [
    {
      "exampleQ": "什么是Python？",
      "exampleA": "Python是一种高级编程语言",
      "exampleUrl": "https://example.com/python"
    }
  ]
}
```

#### 2. 按表添加问答对

```http
POST /addQaFromJson_bge_by_table
Content-Type: application/json

{
  "table": "qadocuments_bge_guides",
  "qa_json_list": [...]
}
```

#### 3. 从文件添加

```http
POST /addQaFromJsonFile
Content-Type: multipart/form-data

file: <json_file>
```

#### 4. 从文本添加

```http
POST /addQaFromText
Content-Type: application/x-www-form-urlencoded

text: <text_content>
```

### 查询接口

#### 智能问答查询

```http
POST /queryQADB
Content-Type: application/json

{
  "query_message": "Python有哪些特点？"
}
```

**响应示例：**
```json
{
  "output_text": "Python具有以下特点：\n1. 简洁易读\n2. 跨平台...",
  "markdownurls": ["[参考链接](https://example.com)"]
}
```

### 微信接口

#### 微信公众号回调

```http
GET /wechat?signature=xxx&timestamp=xxx&nonce=xxx&echostr=xxx
POST /wechat
```

---

## 🐳 Docker部署

### 使用Docker Compose

```bash
docker-compose up -d
```

### 使用Dockerfile

```bash
docker build -t eduknowledge-backend .
docker run -d -p 5000:5000 --env-file .env eduknowledge-backend
```

---

## 📁 项目结构

```
eduknowledge.backend-main/
├── app.py                      # Flask应用主文件
├── config.py                   # 配置文件
├── requirements.txt            # Python依赖
├── gunicorn.conf.py           # Gunicorn配置
├── Dockerfile                  # Docker镜像配置
├── docker-compose.yml          # Docker Compose配置
│
├── lib/                        # 核心库
│   ├── chat_utils.py          # 聊天工具函数
│   ├── Embeddings/             # 嵌入模型
│   │   └── bgeEmbeddings.py   # BGE嵌入实现
│   ├── QaDocument/             # 问答文档模型
│   │   └── QaDocument.py
│   ├── QaVectorStore/          # 向量存储抽象
│   │   └── QaVectorStore.py
│   └── supabase/               # Supabase集成
│       ├── initSupabaseClient.py
│       └── QaVectorStore/
│           └── SupabaseQaVectorStore.py
│
└── scripts/                    # 脚本目录
    ├── queryWithOpenai.py     # 查询与OpenAI集成
    ├── wechatReply.py         # 微信回复处理
    └── fileLoadHelper.py      # 文件加载辅助
```

---

## 🔧 配置说明

### Supabase向量数据库配置

确保Supabase项目中已创建以下表结构：

- `qadocuments_bge`：主知识库表
- `qadocuments_bge_guides`：指南类知识表
- 每个表需包含：`id`, `question_content`, `answer_content`, `question_embedding`, `answer_embedding`, `metadata`

### 大模型配置

- **OpenAI**：通过环境变量 `OPENAI_API_KEY` 和 `OPENAI_API_BASE` 配置
- **ChatGLM3**：在 `config.py` 中配置 `ChatGLM3_endpoint_url`

### 微信配置

- 在微信公众平台配置服务器URL：`http://your-domain/wechat`
- 配置Token验证（当前代码中为 `this_is_a_wechat_token`）

---

## 🎓 使用场景

### 1. 课程知识问答
学生可通过微信或API接口，随时查询课程相关知识点，获得即时解答。

### 2. 学习辅助工具
集成到学习平台，为学生提供智能学习助手，解答疑问、提供参考资料。

### 3. 教学资源管理
教师可批量导入课程资料，构建结构化的知识库，支持多表分类管理。

### 4. 学习行为分析
通过对话记录分析学生学习热点和难点，为教学改进提供数据支持。

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。

### 开发规范

- 遵循PEP 8代码规范
- 添加必要的注释和文档
- 确保代码通过测试

---



<div align="center">

**让AI赋能教育，让学习更智能** ✨

Made with ❤️ for Education

</div>
