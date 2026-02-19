# 🔧 故障排除指南

本文档帮助您解决常见的跨域和连接问题。

## 🚨 常见错误及解决方案

### 1. 跨域错误 (CORS Error)

**症状**：
```
Access to XMLHttpRequest at 'http://localhost:8000/api/chat' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**原因**：
- 后端 CORS 配置未正确设置
- 请求头信息不匹配

**解决方案**：

✅ **后端配置检查** (`backend/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["content-type", "authorization"],
)
```

✅ **前端请求检查** (`frontend/src/api.ts`):
```typescript
const api = axios.create({ 
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});
```

✅ **重启后端服务**:
```bash
# 停止现有的后端服务，然后重启
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 2. 400 Bad Request 错误

**症状**：
```
POST http://localhost:8000/api/chat 400 (Bad Request)
```

**原因**：
- 请求体格式不正确
- 问题字段为空
- Content-Type 头未正确设置

**解决方案**：

✅ **检查请求格式**：
```typescript
// 正确的请求格式
{
  "question": "你的问题内容",  // 必填，非空字符串
  "session_id": "optional-id"   // 可选
}
```

✅ **检查 Content-Type**：
```typescript
// 在 api.ts 中确保设置了正确的 header
headers: {
  'Content-Type': 'application/json',
}
```

✅ **查看浏览器控制台**：
1. 打开浏览器开发者工具 (F12)
2. 切换到 **Network** 标签
3. 查看失败的请求的 Request/Response 详情

---

### 3. 后端无法使用 LLM API

**症状**：
```
请求超时或显示 500 错误
API key 验证失败
```

**原因**：
- `.env` 文件中的 API 密钥未设置或错误
- ARK API 地址无法访问
- 网络连接问题

**解决方案**：

✅ **检查环境变量** (`backend/.env`):
```env
ARK_API_KEY=你的实际_API_KEY_HERE
ARK_MODEL=deepseek-v3-2-251201
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

✅ **验证 API 连接**：
```bash
# 测试 API 密钥是否有效
curl -X POST https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"model":"deepseek-v3-2-251201"}'
```

✅ **查看后端日志**：
- 后端启动时会显示加载的配置
- 查看是否有 API 连接错误

---

### 4. 前端无法连接后端

**症状**：
```
后端服务未响应
连接错误
```

**原因**：
- 后端服务未启动
- 端口被占用
- 防火墙阻止

**解决方案**：

✅ **检查后端服务状态**：
```bash
# 健康检查端点
curl http://localhost:8000/health
# 应该返回: {"status":"ok","message":"NL2SQL API is running"}
```

✅ **检查端口占用**：
```powershell
# Windows - 检查 8000 端口
netstat -ano | findstr :8000

# 如果被占用，找出进程并杀死
taskkill /PID <PID> /F
```

✅ **重启后端服务**：
```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔍 诊断工具

### 使用诊断脚本

我们提供了一个自动诊断脚本来检查所有连接：

```bash
# 运行诊断
uv run scripts/diagnose.py

# 或者使用 Python 直接运行
python scripts/diagnose.py
```

诊断脚本检查：
- ✓ 后端服务连接
- ✓ CORS 配置
- ✓ API 端点响应
- ✓ LLM API 连接

### 诊断输出示例

```
==================================================
NL2SQL 系统诊断
==================================================

✓ 后端服务运行中 (端口 8000)
  响应: {'status': 'ok', 'message': 'NL2SQL API is running'}

✓ CORS 已正确配置
  Access-Control-Allow-Origin: http://localhost:5173
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS

✓ 表结构加载成功 (12 个表)
  - T_JCXX
  - T_BLXX
  - T_YSXX

✓ 聊天 API 工作正常
  SQL 查询已生成 (432 字符)

==================================================
诊断总结:
==================================================

✓ 后端连接
✓ CORS 配置
✓ 表结构 API
✓ 聊天 API

✓ 所有测试通过! 系统可以正常使用.
```

---

## 🐛 调试技巧

### 1. 启用详细日志

**前端** (`frontend/src/api.ts`已启用):
```typescript
// 请求拦截器会打印每个请求
api.interceptors.request.use((config) => {
  console.log(`🚀 Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});
```

在浏览器控制台查看日志：
```
🚀 Request: POST http://localhost:8000/api/chat
✅ Response: 200 http://localhost:8000/api/chat
```

### 2. 检查浏览器请求

1. 打开浏览器开发者工具 (F12)
2. 切换到 **Network** 标签
3. 发送一个问题
4. 查看 `/api/chat` 请求：
   - **Headers**: 查看 Content-Type 和 Origin
   - **Payload**: 查看发送的 JSON 格式
   - **Response**: 查看返回的数据和任何错误信息

### 3. 后端日志

后端启动时会打印：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [1234] using WatchFiles
INFO:     Started server process [5678]
INFO:     Waiting for application startup.
```

处理请求时会看到：
```
🚀 Request: POST /api/chat
SQL 查询已生成
✅ Response: 200
```

---

## 📋 检查清单

启动前，确保检查以下项目：

- [ ] 后端服务已启动 (`uv run uvicorn ...`)
- [ ] 前端开发服务器已启动 (`npm run dev`)
- [ ] `backend/.env` 文件已创建且包含有效的 API 密钥
- [ ] 没有防火墙阻止 8000 和 5173 端口
- [ ] 使用的是正确的 URL (`http://localhost:8000`, 不是 `127.0.0.1`)  
- [ ] 运行了诊断脚本并确认所有测试通过

---

## 🆘 获取帮助

如果问题仍未解决：

1. **查看完整日志**：
   - 后端控制台输出
   - 浏览器开发者工具 Console 标签
   - Network 标签中的请求详情

2. **运行诊断脚本**：
   ```bash
   uv run scripts/diagnose.py
   ```

3. **检查 API 配置**：
   ```bash
   # 验证 ARK API 是否可访问
   curl https://ark.cn-beijing.volces.com/api/v3/health
   ```

4. **提交问题时包括**：
   - 诊断脚本的输出
   - 浏览器控制台的错误信息
   - 后端启动日志
   - Network 标签中的请求/响应详情

---

**最后更新**: 2026-02-19
