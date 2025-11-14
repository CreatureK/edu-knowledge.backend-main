# 教育知识库文档对话后端
## 项目描述
该项目为教育知识库文档对话的后端模块，负责提供链接微信、链接数据库、链接大模型的接口。
## 功能描述
- 链接微信服务
- 提供向量数据库服务
- 链接大模型

## 快速部署
将.env.sample文件复制一份到.env文件中，修改如下环境变量
`OPENAI_API_KEY=sk-xxxx` 对应apikey
`OPENAI_API_BASE=https://api.openai.com/v1`  对应apikey
`PYTHON_SUPABASE_URL=http://your-supabase-url` 对应supabaseurl
`PYTHON_SUPABASE_ANNOKEY=your-supabase-annokey` 对应supabase annokey
`WECHAT_APPID=wxxxx` 对应微信AAPID
`WECHAT_APPSECRET=xxxx`对应微信AAPSECRET

修改config.py 中
ChatGLM3_endpoint_url为对应clm3以本地部署

使用 `pip install -r requirements.txt` 下载依赖
开发环境使用`python app.py` 启动

生产环境使用`gunicorn app:app`启动