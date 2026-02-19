# 🔑 API 密钥配置指南

## 问题症状
当发送请求时出现错误：
```
Error code: 401 - AuthenticationError
the API key or AK/SK in the request is missing or invalid
```

## 原因
Backend/.env 中的 API 密钥：
- ❌ 缺失或未配置
- ❌ 格式不正确
- ❌ 已过期或无效
- ❌ 没有相应的权限

或者配置参数不匹配：
- ❌ `ARK_MODEL` 设置不正确
- ❌ `ARK_BASE_URL` 设置不正确

## ✅ 快速修复步骤

### 第 1 步：打开 backend/.env 文件

```bash
cd d:\Project\Logene_NL2SQL
# Windows
notepad backend\.env

# 或在 VS Code 中打开
code backend\.env
```

### 第 2 步：检查和更新配置

**当前配置应该看起来像这样：**
```dotenv
ARK_API_KEY=your_api_key_here
ARK_MODEL=doubao-pro-32k-241215
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

如果配置与上面不同，请按照下面的说明进行更正。

### 第 3 步：获取有效的 API 密钥

#### 选项 A：使用火山引擎 (推荐)

1. 访问：https://console.volcengine.com/
2. 登录你的账户
3. 导航到 **API 管理** 或 **模型市场**
4. 创建或获取 API 密钥
5. 复制 API 密钥

#### 选项 B：使用 DeepSeek API（备选）

如果希望使用 DeepSeek 的 API 而不是火山引擎，需要更新配置：

```dotenv
ARK_API_KEY=your_deepseek_api_key
ARK_MODEL=deepseek-v3
ARK_BASE_URL=https://api.deepseek.com/v1
```

访问: https://platform.deepseek.com/ 获取密钥

### 第 4 步：配置 backend/.env

在 backend/.env 中替换 `your_api_key_here`：

```dotenv
ARK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxx
ARK_MODEL=doubao-pro-32k-241215
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

**不要使用：**
```dotenv
# ❌ 错误 - 添加多余的路径
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/chat/completions

# ❌ 错误 - 错误的模型名称
ARK_MODEL=doubao-seed-1-6-251015
```

### 第 5 步：重启后端服务

关闭当前运行的后端服务（如果正在运行），然后重新启动：

```bash
cd d:\Project\Logene_NL2SQL
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 第 6 步：测试配置

运行诊断脚本验证配置：

```bash
uv run scripts/diagnose.py
```

预期输出：
```
✓ 后端连接
✓ CORS 配置
✓ 表结构 API
✓ 聊天 API  ← 如果配置正确应该是绿色的✓
```

## 🔍 常见问题

### Q1: 我没有 API 密钥怎么办？

**A:** 
- 如果使用火山引擎，需要在控制台创建或购买 API 配额
- 可以尝试使用免费试用配额（如果可用）
- 或者使用 DeepSeek 的公共 API

### Q2: API 密钥格式是什么？

**A:** API 密钥通常看起来像这样：
```
sk-1234567890abcdef1234567890abcdef
20efb8c0-01f7-4d1d-a6d2-9fe6adc84d3c
```

### Q3: 我已经配置了密钥但仍然收到 401 错误

**A:** 检查以下几点：
1. 确保 `.env` 文件已保存
2. 确保后端服务已重启（ctrl+c 然后重新运行）
3. 检查密钥是否已过期
4. 检查 ARK_MODEL 和 ARK_BASE_URL 是否正确
5. 查看诊断日志获取更多信息

### Q4: 如何检查 .env 文件是否被正确加载？

**A:** 运行此命令检查：
```bash
cd d:\Project\Logene_NL2SQL
uv run -c "import os; from dotenv import load_dotenv; load_dotenv('backend/.env'); print(f'API Key: {os.getenv(\"ARK_API_KEY\", \"NOT FOUND\")}'); print(f'Model: {os.getenv(\"ARK_MODEL\", \"NOT FOUND\")}'); print(f'Base URL: {os.getenv(\"ARK_BASE_URL\", \"NOT FOUND\")}')"
```

## 📋 完整的配置文件示例

```dotenv
# Volcano Engine API 配置
ARK_API_KEY=sk-your-actual-api-key-here
ARK_MODEL=doubao-pro-32k-241215
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 不要编辑下面的内容（如果有的话）
# DATABASE_URL=...
# SQLALCHEMY_DATABASE_URL=...
```

## 🛠️ 故障排除

### 终端日志显示"缺少有效的 API 密钥配置"

这意味着启动时检测到了问题。解决方案：
1. 编辑 `backend/.env`
2. 设置有效的 `ARK_API_KEY`
3. 保存文件
4. 重启服务

### 服务器返回 503 错误

这通常表示配置文件有问题。检查：
1. `.env` 文件中是否有语法错误
2. API 密钥值是否正确（不要包含引号）
3. 模型名称是否拼写正确

### 诊断脚本显示"✗ 聊天 API"失败

这通常是 API 认证问题。按照上面的步骤重新配置并测试。

## 📞 获取帮助

如果问题仍未解决：

1. **查看后端日志**
   ```bash
   # 在启动后端时查看详细日志
   uv run uvicorn backend.main:app --reload --log-level debug
   ```

2. **运行诊断脚本**
   ```bash
   uv run scripts/diagnose.py
   ```

3. **检查网络连接**
   ```bash
   # 测试是否能连接到 API 服务器
   curl -I https://ark.cn-beijing.volces.com/api/v3
   ```

---

**更新时间**: 2026-02-19  
**状态**: ✅ 已解决认证错误问题
