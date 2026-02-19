# 🚀 快速入门卡

## 一句话启动

```bash
# 第一次
uv sync && cd frontend && npm install && cd .. && cp backend/.env.example backend/.env

# 之后每次
cd d:\Project\Logene_NL2SQL
.\scripts\start.ps1  # 或 .\scripts\start-backend.ps1 和 .\scripts\start-frontend.ps1
```

## 环境版本

- **Python**: 3.11 (via `uv`)
- **Node.js**: 20.x (via `nvm`)
- **FastAPI**: 0.129.0
- **React**: 19.2.0
- **Vite**: 7.3.1

## 核心依赖锁文件

- `pyproject.toml` + `uv.lock` → Python 所有依赖已锁定
- `frontend/package.json` + `frontend/package-lock.json` → Node 所有依赖已锁定

## 新版本成员加入流程

```bash
# 1. 克隆代码
git clone <repo>
cd Logene_NL2SQL

# 2. 一键安装
uv sync
cd frontend && npm install

# 3. 配置 API
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 API_KEY

# 4. 启动开发
cd ..
.\scripts\start.ps1  

# 5. 访问
# - 前端: http://localhost:5173
# - 后端: http://localhost:8000
```

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 安装依赖 | `uv sync && cd frontend && npm install` |
| 启动全部 | `.\scripts\start.ps1` |
| 启动后端 | `.\scripts\start-backend.ps1` |
| 启动前端 | `.\scripts\start-frontend.ps1` |
| 添加 Python 包 | `uv add package_name==version` |
| 添加 Node 包 | `cd frontend && npm install --save package_name` |
| 更新 Python 锁 | `uv lock --upgrade` |
| 前端代码检查 | `cd frontend && npm run lint` |
| 前端构建 | `cd frontend && npm run build` |

## 重要文件说明

```
pyproject.toml          ← Python 核心配置（所有依赖版本已固定）
uv.lock                 ← Python 依赖锁文件（git 推送）
.python-version         ← Python 版本指定 (3.11)
frontend/package.json   ← Node 核心配置（所有依赖版本已固定）
frontend/package-lock.json ← Node 依赖锁文件（git 推送）
.nvmrc                  ← Node 版本指定 (20)
```

## 版本更新流程

### 更新 Python 依赖

```bash
# 修改 pyproject.toml 中的版本号，然后
uv lock --upgrade
uv sync
git add pyproject.toml uv.lock
git commit -m "chore: update python dependencies"
```

### 更新 Node 依赖

```bash
# 修改 frontend/package.json 中的版本号，然后
cd frontend
npm install
git add package.json package-lock.json
git commit -m "chore: update node dependencies"
```

## 🆘 常见问题

**Q: "找不到模块"错误**
```bash
# 确保运行了 uv sync
uv sync
```

**Q: 前端连不上后端**
```bash
# 确保后端运行在 8000 端口
uv run uvicorn backend.main:app --reload
```

**Q: 版本冲突**
```bash
# 重新安装
rm uv.lock
uv sync
rm frontend/package-lock.json
cd frontend && npm install
```

---

**最后更新**: 2026-02-19
