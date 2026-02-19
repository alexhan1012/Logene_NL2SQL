# 🔑 API 密钥快速配置指南

## ⚡ 30 秒快速解决方案

### 步骤 1: 编辑文件
```bash
# Windows 用户，用记事本打开
notepad backend\.env
```

### 步骤 2: 复制正确的配置
```dotenv
ARK_API_KEY=你的实际API密钥
ARK_MODEL=doubao-pro-32k-241215
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

### 步骤 3: 获取 API 密钥
访问 → https://console.volcengine.com/

### 步骤 4: 重启后端
```bash
# Ctrl+C 停止当前后端
# 重新运行
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ 验证修复

运行诊断：
```bash
uv run scripts/diagnose.py
```

应该看到：
```
✓ 后端连接
✓ CORS 配置
✓ 表结构 API
✓ 聊天 API  ← 如果配置正确
```

## ❌ 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|--------|
| `401 AuthenticationError` | API 密钥无效 | 检查并更新 API 密钥 |
| `503 Service Unavailable` | 服务未初始化 | 检查是否有 API 密钥 |
| `缺少有效的 API 密钥配置` | `.env` 中没有密钥 | 添加有效的 `ARK_API_KEY` |

## 📚 详细指南

完整配置说明please see: `API_KEY_SETUP.md`

## 🆘 问题仍未解决？

1. 查看后端日志中的错误信息
2. 运行 `uv run scripts/diagnose.py`
3. 阅读 `API_KEY_SETUP.md`
4. 查看 `AUTH_ERROR_FIX_COMPLETE.md`

---

**快速参考** | **创建时间**: 2026-02-19
