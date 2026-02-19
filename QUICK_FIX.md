# ⚡ 快速故障排除参考

## 跨域 (CORS) 错误或 400 错误？

### 🔍 第一步：诊断

```bash
# 运行诊断工具
uv run scripts/diagnose.py
```

### 📊 诊断结果解读

#### ✓ 所有测试通过
- **情况**：系统正常运行
- **操作**：检查浏览器 F12 的 Network 和 Console 标签，查看具体错误
- **常见原因**：API 密钥无效、LLM 服务无响应

#### ✗ 后端连接失败
- **错误**：`无法连接到后端服务`
- **解决**：
  ```bash
  # 确保后端已启动
  uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
  ```

#### ✗ CORS 配置失败
- **错误**：`CORS 未返回预期的头部`
- **解决**：
  ```bash
  # 检查后端代码中的 CORS 配置
  # 应该包含: allow_origins, allow_methods, allow_headers
  # 然后重启后端
  ```

#### ✗ 聊天 API 失败
- **错误**：`401 Unauthorized` → API 密钥无效
- **解决**：
  ```bash
  # 编辑 backend/.env
  # 检查 ARK_API_KEY 是否正确
  cp backend/.env.example backend/.env
  # 填入有效的 API 密钥
  ```

---

## 🚨 浏览器控制台错误速查

| 错误信息 | 原因 | 解决方案 |
|---------|------|--------|
| `Access to XMLHttpRequest ... blocked by CORS policy` | CORS 配置不正确 | 运行诊断，检查 CORS 头 |
| `POST /api/chat 400 (Bad Request)` | 请求格式错误或字段为空 | 查看浏览器 Network 的 Payload |
| `POST /api/chat 500 (Internal Server Error)` | 后端异常或 API 密钥无效 | 查看后端启动的控制台日志 |
| `Failed to fetch` | 后端服务未运行 | 启动后端：`uv run uvicorn ...` |
| `Timeout` | 请求响应超时 | 检查网络或 LLM API 连接 |

---

## 🔧 最常见的 5 个问题及解决方案

### 1️⃣ 后端服务未响应

```bash
# 检查 8000 端口是否被占用
netstat -ano | findstr :8000

# 如果被占用，杀死进程
taskkill /PID <PID> /F

# 重启后端
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2️⃣ CORS 错误

```bash
# ✅ 第一步：验证 CORS 配置
uv run scripts/diagnose.py

# ✅ 第二步：检查源地址
# URL 应该是 http://localhost:5173 
# 不要用 127.0.0.1:5173

# ✅ 第三步：重启后端
# (后端会重新加载 CORS 中间件)
```

### 3️⃣ 400 请求错误

```typescript
// ❌ 错误的请求：
api.post('/api/chat', { question: '' })  // 空问题

// ✅ 正确的请求：
api.post('/api/chat', { 
  question: '查询最近病理报告',  // 非空字符串
  session_id: 'optional'           // 可选
})
```

### 4️⃣ API 密钥错误

```bash
# 编辑 backend/.env
nano backend/.env  # 或用你的编辑器

# 确保包含有效的：
# ARK_API_KEY=your_real_key_here
# ARK_MODEL=deepseek-v3-2-251201
# ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 保存后重启后端
```

### 5️⃣ 前端无法连接后端

```typescript
// 检查 api.ts 中的 baseURL
// ✅ 应该是：
const api = axios.create({ baseURL: 'http://localhost:8000' });

// ❌ 不应该是：
// const api = axios.create({ baseURL: 'http://127.0.0.1:8000' });
// const api = axios.create({ baseURL: 'http://myserver.com:8000' });
```

---

## 📝 完整检查清单

发现问题前，确保检查：

```
启动前：
☐ backend/.env 文件已创建
☐ backend/.env 中有有效的 API 密钥
☐ backend/.env 中的 ARK_BASE_URL 可访问

启动中：
☐ 后端已启动：uv run uvicorn backend.main:app ...
☐ 前端已启动：npm run dev
☐ 没有看到错误日志

启动后：
☐ 打开 http://localhost:5173
☐ 浏览器不显示错误
☐ 运行诊断：uv run scripts/diagnose.py
☐ 诊断显示 ✓ 所有测试通过
```

---

## 🔍 调试步骤

### 第一步：查看前端日志
```
打开浏览器 → F12 → Console 标签
查找 "🚀 Request" 日志看请求内容
查找 "❌" 看错误信息
```

### 第二步：查看 Network 请求
```
打开浏览器 → F12 → Network 标签
发送一个问题
查找 /api/chat 请求
- Request 标签：查看发送什么数据
- Response 标签：查看返回什么错误
- Headers 标签：查看 Content-Type 和 CORS 头
```

### 第三步：查看后端日志
```
查看后端启动的控制台窗口
查找是否有错误日志
如果有 "Error code: 401"，说明 API 密钥无效
```

### 第四步：运行诊断
```bash
uv run scripts/diagnose.py
```

---

## 📞 需要帮助？

1. **确认诊断输出**
   ```bash
   uv run scripts/diagnose.py > diagnostic_report.txt
   # 分享 diagnostic_report.txt
   ```

2. **收集浏览器日志**
   ```
   F12 → Console → 右键 → Save as...
   ```

3. **收集后端日志**
   ```
   复制后端启动窗口的所有日志
   ```

4. **查看完整指南**
   ```bash
   # 打开故障排除指南
   cat TROUBLESHOOTING.md
   ```

---

**记住**：大多数问题分为三类：
1. 🎭 **设置问题**（env、端口等）→ 运行诊断
2. 🌐 **CORS 问题** → 检查源地址，重启后端
3. 🔑 **API 问题** → 检查 API 密钥，验证网络

**最后更新**: 2026-02-19
