# Logene NL2SQL

A Natural Language to SQL application for the Logene pathology information system. Convert natural language queries into SQL using advanced LLM capabilities.

## 📋 系统要求

| 组件 | 版本 | 安装方式 |
|------|------|--------|
| Python | 3.11+ | uv |
| Node.js | 20.x | nvm |

## 🚀 快速开始

### 1. 环境准备

#### Python 环境（使用 uv）

```bash
# 如果还未安装 uv，请先安装
# Windows: iwr https://astral.sh/uv/install.ps1 | iex
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证 uv 安装
uv --version
```

#### Node.js 环境（使用 nvm）

```bash
# 如果还未安装 nvm，访问 https://github.com/coreybutler/nvm-windows/releases

# 验证 nvm 安装
nvm --version

# 切换到 Node 20
nvm use 20
```

### 2. 安装依赖

> **简单方式**：只需运行一条命令，所有依赖会自动安装

```bash
# Python 后端依赖和 Node 前端依赖
cd d:\Project\Logene_NL2SQL
uv sync
cd frontend && npm install
```

### 3. 环境配置

```bash
# 复制 backend 配置文件
cp backend/.env.example backend/.env

# 编辑 backend/.env，填入你的 API 密钥：
# ARK_API_KEY=你的_API_KEY
# ARK_MODEL=deepseek-v3-2-251201
# ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 4. 启动服务

**方式一：分离终端启动（推荐开发）**

终端 1 - 启动后端服务：
```bash
cd d:\Project\Logene_NL2SQL
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

终端 2 - 启动前端服务：
```bash
cd d:\Project\Logene_NL2SQL\frontend
npm run dev
```

**方式二：后台启动（使用 PowerShell）**

```powershell
# 后端
Start-Process powershell -ArgumentList "cd d:\Project\Logene_NL2SQL; uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

# 前端
Start-Process powershell -ArgumentList "cd d:\Project\Logene_NL2SQL\frontend; npm run dev"
```

### 5. 访问应用

| 应用 | 地址 | 功能 |
|------|------|------|
| 前端 UI | http://localhost:5173 | 用户界面 |
| 后端 API | http://localhost:8000 | API 服务 |
| API 文档 | http://localhost:8000/docs | Swagger 文档 |

## 📦 版本信息

### Python 依赖（已锁定版本）

主要依赖：
- `fastapi==0.129.0` - Web 框架
- `uvicorn==0.41.0` - ASGI 服务器
- `langchain==1.2.10` - LLM 框架
- `langchain-openai==1.1.10` - OpenAI 集成
- `sqlalchemy==2.0.46` - ORM
- `pydantic==2.12.5` - 数据验证
- `python-docx==1.2.0` - Word 文档处理
- `python-dotenv==1.2.1` - 环境变量管理

完整版本清单见 `uv.lock` 文件。

### Node.js 依赖（已锁定版本）

主要依赖：
- `react==19.2.0` - 前端框架
- `react-dom==19.2.0` - React DOM
- `antd==6.3.0` - UI 组件库
- `axios==1.13.5` - HTTP 客户端
- `typescript==5.9.3` - TypeScript
- `vite==7.3.1` - 构建工具

完整版本清单见 `package-lock.json` 文件。

## 🔧 开发命令

### Python 项目

```bash
# 创建开发环境快照
uv sync

# 运行 Python 代码
uv run python script.py

# 运行后端服务
uv run uvicorn backend.main:app --reload

# 之后加入新依赖
uv add package_name  # 自动锁定版本

# 更新依赖
uv lock --upgrade
```

### Node.js 项目

```bash
# 安装依赖（使用锁定版本）
npm install

# 开发服务器
npm run dev

# 构建
npm run build

# 代码检查
npm run lint
```

## 📁 项目结构

```
Logene_NL2SQL/
├── backend/                      # Python 后端
│   ├── main.py                  # FastAPI 应用入口
│   ├── database.py              # 数据库配置和模型
│   ├── nl2sql_service.py        # NL2SQL 核心服务
│   ├── schemas.py               # 数据库表架构定义
│   ├── .env.example             # 环境变量模板
│   ├── requirements.txt          # 依赖列表（已弃用，使用 pyproject.toml）
│   └── __init__.py              # 包初始化
├── frontend/                     # React + TypeScript 前端
│   ├── package.json             # Node 依赖配置
│   ├── package-lock.json        # Node 版本锁文件
│   ├── tsconfig.json            # TypeScript 配置
│   ├── vite.config.ts           # Vite 构建配置
│   ├── src/
│   │   ├── main.tsx             # React 入口
│   │   ├── App.tsx              # 主组件
│   │   ├── api.ts               # API 调用
│   │   ├── types.ts             # TypeScript 类型定义
│   │   └── components/          # React 组件
│   └── public/                  # 静态资源
├── pyproject.toml               # Python 项目配置（主配置文件）
├── uv.lock                      # Python 依赖版本锁文件
├── .python-version              # Python 版本指定（3.11）
├── .nvmrc                       # Node 版本指定（20）
├── .gitignore                   # Git 忽略配置
└── README.md                    # 本文件
```

## 🔑 环境变量

### Backend (.env)

```env
# Volcano Engine（火山引擎）API 配置
ARK_API_KEY=your_api_key_here
ARK_MODEL=deepseek-v3-2-251201
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### Frontend

前端使用 `src/api.ts` 中配置的后端地址：
```typescript
const API_BASE_URL = 'http://localhost:8000';
```

## 🎯 功能特性

- ✅ 自然语言转 SQL 查询
- ✅ 智能表选择（2 步 LLM 流程）
- ✅ 对话历史管理（SQLite 存储）
- ✅ 表关系可视化
- ✅ 完整的表架构浏览器
- ✅ 现代化 UI（Ant Design）
- ✅ 完整的 TypeScript 类型支持

## 🐛 常见问题

### Q: "无法找到模块"错误

A: 确保在项目根目录运行命令，且先执行 `uv sync` 安装依赖。

### Q: 前端无法连接后端

A: 检查后端是否运行在 `http://localhost:8000`，并确保 CORS 已启用。

### Q: 依赖版本冲突

A: 删除 `uv.lock` 和 `package-lock.json`，然后重新运行 `uv sync` 和 `npm install`。

## ✨ 新增依赖

### 添加 Python 依赖

```bash
uv add package_name==version
# 自动更新 pyproject.toml 和 uv.lock
uv sync
```

### 添加 Node 依赖

```bash
cd frontend
npm install package_name --save
# 手动更新 package.json 中的版本号为固定版本
npm install  # 更新 package-lock.json
```

## 📝 Git 工作流

所有文件都已配置在 `.gitignore` 中，推送时只包含：
- ✅ 源代码
- ✅ 配置文件（pyproject.toml, package.json）
- ✅ 版本锁文件（uv.lock, package-lock.json）

忽略以下文件：
- ❌ 虚拟环境 (.venv, node_modules)
- ❌ 环境变量 (.env)
- ❌ 构建输出 (dist, build)
- ❌ 缓存文件 (__pycache__, .cache)

## 🤝 贡献指南

1. 确保本地测试通过
2. 创建新分支进行开发
3. 推送前运行 `npm run lint`（前端）
4. 提交代码和必要的测试

## 📞 支持

如有问题，请提交 Issue 或联系开发团队。

---

**最后更新**: 2026-02-19
