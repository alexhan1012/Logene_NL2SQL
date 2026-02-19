# 快速启动脚本 - Project Setup and Run

这个目录包含快捷脚本来帮助启动项目。

## 使用方法

### 首次设置（Windows PowerShell）

```powershell
# 1. 安装依赖
.\setup.ps1

# 2. 配置环境
cp backend\.env.example backend\.env
# 编辑 backend\.env 填入 API 密钥
```

### 启动服务

```powershell
# 后台启动所有服务
.\start.ps1

# 或分别启动
.\start-backend.ps1  # 启动后端
.\start-frontend.ps1 # 启动前端
```

### 访问应用

- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs
