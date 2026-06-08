# HelloAgents智能旅行助手 🌍✈️

基于HelloAgents框架构建的智能旅行规划助手，集成高德地图MCP服务和RAG知识库，提供个性化的旅行计划生成。

## ✨ 功能特点

- 🤖 **AI驱动的旅行规划**: 基于HelloAgents框架的SimpleAgent，智能生成详细的多日旅程
- 🗺️ **高德地图集成**: 通过MCP协议接入高德地图服务，支持景点搜索、路线规划、天气查询
- 📚 **RAG知识库增强**: 内置中国7大城市旅行攻略和饮食文化知识库，通过向量检索为行程规划提供专业知识参考
- 🧠 **多智能体协作**: 5个专业化Agent（知识检索、景点搜索、天气查询、酒店推荐、行程规划）协同工作
- 🎨 **现代化前端**: Vue3 + TypeScript + Vite，响应式设计，流畅的用户体验
- 📱 **完整功能**: 包含住宿、交通、餐饮、景点游览时间、预算明细和交互式地图

## 🏗️ 技术栈

### 后端
- **框架**: HelloAgents (基于SimpleAgent多智能体协作)
- **API**: FastAPI
- **MCP工具**: amap-mcp-server (高德地图)
- **向量数据库**: ChromaDB (知识库存储与检索)
- **嵌入模型**: TF-IDF字符级n-gram (完全离线，无需下载模型)
- **LLM**: 支持多种LLM提供商 (OpenAI, DeepSeek等)

### 前端
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design Vue
- **地图服务**: 高德地图 JavaScript API
- **HTTP客户端**: Axios

## 📁 项目结构

```
helloagents-trip-planner/
├── backend/                        # 后端服务
│   ├── app/
│   │   ├── agents/                 # Agent实现
│   │   │   └── trip_planner_agent.py  # 多智能体旅行规划系统
│   │   ├── api/                    # FastAPI路由
│   │   │   ├── main.py             # 应用入口
│   │   │   └── routes/
│   │   │       ├── trip.py         # 旅行规划API
│   │   │       ├── map.py          # 地图服务API
│   │   │       ├── poi.py          # POI详情API
│   │   │       └── knowledge.py    # 知识库API
│   │   ├── services/               # 服务层
│   │   │   ├── amap_service.py     # 高德地图服务
│   │   │   ├── llm_service.py      # LLM服务
│   │   │   ├── knowledge_service.py # 知识库服务 (ChromaDB + TF-IDF)
│   │   │   └── unsplash_service.py # 图片服务
│   │   ├── tools/                  # Agent工具
│   │   │   └── rag_tool.py         # RAG知识检索工具
│   │   ├── models/                 # 数据模型
│   │   │   └── schemas.py
│   │   └── config.py               # 配置管理
│   ├── data/
│   │   ├── knowledge/              # 知识库Markdown文档
│   │   │   ├── beijing.md          # 北京旅游攻略
│   │   │   ├── shanghai.md         # 上海旅游攻略
│   │   │   ├── guangzhou.md        # 广州旅游攻略
│   │   │   ├── shenzhen.md         # 深圳旅游攻略
│   │   │   ├── chengdu.md          # 成都旅游攻略
│   │   │   ├── hangzhou.md         # 杭州旅游攻略
│   │   │   ├── xian.md             # 西安旅游攻略
│   │   │   ├── general_tips.md     # 中国旅行通用贴士
│   │   │   └── food_guide.md       # 中国饮食文化指南
│   │   └── chromadb/               # ChromaDB持久化数据
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/                       # 前端应用
│   ├── src/
│   │   ├── services/               # API服务
│   │   ├── types/                  # TypeScript类型
│   │   └── views/                  # 页面视图
│   │       ├── Home.vue            # 首页（旅行表单）
│   │       └── Result.vue          # 结果页（行程展示+知识参考）
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## 🚀 快速开始

### 前提条件

- Python 3.10+
- Node.js 16+
- 高德地图API密钥 (Web服务API和Web端JS API)
- LLM API密钥 (OpenAI/DeepSeek等)

### 后端安装

1. 进入后端目录
```bash
cd backend
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入你的API密钥
```

5. 启动后端服务
```bash
# 方式一：直接运行
python run.py

# 方式二：使用uvicorn命令
uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

> 首次启动时会自动索引知识库文档（9个Markdown文件），大约需要几秒钟。

### 前端安装

1. 进入前端目录
```bash
cd frontend
```

2. 安装依赖
```bash
npm install
```

3. 配置环境变量
```bash
# 创建.env文件，填入高德地图Web API Key和Web端JS API Key
cp .env.example .env
```

4. 启动开发服务器
```bash
npm run dev
```

5. 打开浏览器访问 `http://localhost:5173`

## 📝 使用指南

1. 在首页填写旅行信息：
   - 目的地城市
   - 旅行日期和天数
   - 交通方式偏好
   - 住宿偏好
   - 旅行风格标签（历史文化、自然风光、美食、购物、艺术、休闲）

2. 点击「开始规划我的旅行」按钮

3. 系统将执行5步智能体协作流程：
   - 📚 **知识检索Agent**：从知识库中检索目的地相关的旅行攻略、美食推荐、文化知识
   - 📍 **景点搜索Agent**：调用高德地图MCP工具搜索景点
   - 🌤️ **天气查询Agent**：获取目的地天气信息
   - 🏨 **酒店推荐Agent**：搜索并推荐合适的酒店
   - 📋 **行程规划Agent**：整合所有信息（含知识库参考），生成完整行程

4. 查看结果：
   - 📋 行程概览与建议
   - 💰 预算明细
   - 📍 景点交互式地图
   - 📅 每日详细行程（可折叠、可编辑）
   - 🏨 酒店推荐
   - 🍽️ 餐饮安排
   - 🌤️ 天气预报
   - 📚 **知识参考**（新增）：展示生成行程时参考的旅行知识

## 🔧 核心实现

### 多智能体协作架构

```
用户请求 → KnowledgeAgent(RAG检索) → AttractionAgent → WeatherAgent → HotelAgent → PlannerAgent(含知识上下文)
```

### HelloAgents Agent集成

```python
from hello_agents import SimpleAgent, HelloAgentsLLM
from hello_agents.tools import MCPTool
from app.tools.rag_tool import RAGTool

# 创建高德地图MCP工具
amap_tool = MCPTool(
    name="amap",
    server_command=["uvx", "amap-mcp-server"],
    env={"AMAP_MAPS_API_KEY": "your_api_key"},
    auto_expand=True
)

# 创建RAG知识检索工具
rag_tool = RAGTool()

# 创建知识检索Agent
knowledge_agent = SimpleAgent(
    name="旅行知识专家",
    llm=HelloAgentsLLM(),
    system_prompt="你是旅行知识专家..."
)
knowledge_agent.add_tool(rag_tool)

# 创建行程规划Agent
planner_agent = SimpleAgent(
    name="行程规划专家",
    llm=HelloAgentsLLM(),
    system_prompt="你是行程规划专家..."
)
```

### RAG知识库架构

```python
# 知识库服务（单例模式）
from app.services.knowledge_service import get_knowledge_service

service = get_knowledge_service()

# 索引文档（启动时自动执行）
service.ingest_documents(force=True)

# 语义检索
results = service.query("北京故宫攻略", city="北京", top_k=5)
```

**知识库特点**：
- 使用 ChromaDB 作为向量数据库，数据持久化存储
- 使用 TF-IDF 字符级 n-gram 嵌入，完全离线，无需下载模型
- 按 `##` 二级标题自动分块，保留文档结构
- 支持按城市过滤检索结果
- 知识库不可用时旅行规划仍可正常使用（优雅降级）

### MCP工具调用

Agent可以自动调用以下高德地图MCP工具：
- `maps_text_search`: 搜索景点POI
- `maps_weather`: 查询天气
- `maps_direction_walking_by_address`: 步行路线规划
- `maps_direction_driving_by_address`: 驾车路线规划
- `maps_direction_transit_integrated_by_address`: 公共交通路线规划

## 📄 API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

主要端点：

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/trip/plan` | POST | 生成旅行计划 |
| `/api/map/poi` | GET | 搜索POI |
| `/api/map/weather` | GET | 查询天气 |
| `/api/map/route` | POST | 规划路线 |
| `/api/poi/detail/{poi_id}` | GET | POI详情 |
| `/api/poi/photo` | GET | 获取景点图片 |
| `/api/knowledge/query` | POST | 查询知识库 |
| `/api/knowledge/add` | POST | 添加知识文档 |
| `/api/knowledge/stats` | GET | 知识库统计 |
| `/api/knowledge/{doc_id}` | DELETE | 删除知识文档 |

## 🔧 配置说明

### 后端环境变量 (`.env`)

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `LLM_MODEL_ID` | LLM模型名称 | `coding-glm-5-free` |
| `LLM_API_KEY` | LLM API密钥 | `sk-xxx` |
| `LLM_BASE_URL` | LLM API地址 | `https://aihubmix.com/v1` |
| `AMAP_API_KEY` | 高德地图Web服务API Key | - |
| `UNSPLASH_ACCESS_KEY` | Unsplash图片API Key | - |
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |

### 前端环境变量 (`.env`)

| 配置项 | 说明 |
|--------|------|
| `VITE_API_BASE_URL` | 后端API地址 |
| `VITE_AMAP_WEB_JS_KEY` | 高德地图Web端JS API Key |

### 知识库配置 (可选)

如需自定义知识库行为，可在 `.env` 中添加：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `KNOWLEDGE_DATA_DIR` | 知识文档目录 | `backend/data/knowledge` |
| `CHROMADB_PERSIST_DIR` | ChromaDB存储目录 | `backend/data/chromadb` |
| `KNOWLEDGE_TOP_K` | 检索返回数量 | `5` |

## 🤝 贡献指南

欢迎提交Pull Request或Issue！

### 添加自定义知识文档

在 `backend/data/knowledge/` 目录下创建新的 `.md` 文件，格式如下：

```markdown
# 城市名旅游攻略

## 章节标题
章节内容...

## 另一个章节
更多内容...
```

文档会在下次启动时自动索引。也可以通过 API 动态添加：

```bash
curl -X POST http://localhost:8000/api/knowledge/add \
  -H "Content-Type: application/json" \
  -d '{"content": "你的知识内容", "metadata": {"city": "北京", "title": "自定义攻略"}}'
```

## 📜 开源协议

CC BY-NC-SA 4.0

## 🙏 参考

- [HelloAgents](https://github.com/datawhalechina/Hello-Agents) - 智能体教程
- [HelloAgents框架](https://github.com/jjyaoao/HelloAgents) - 智能体框架
- [高德地图开放平台](https://lbs.amap.com/) - 地图服务
- [amap-mcp-server](https://github.com/sugarforever/amap-mcp-server) - 高德地图MCP服务器
- [ChromaDB](https://www.trychroma.com/) - 开源向量数据库

---

**HelloAgents智能旅行助手** - 让旅行计划变得简单而智能 🌈
