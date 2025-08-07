# 🔒 安全配置指南

## ⚠️ 重要安全提醒

**绝对不要将包含真实敏感信息的文件上传到GitHub！**

## 🛡️ 敏感文件说明

| 文件名 | 包含内容 | 风险等级 |
|--------|----------|----------|
| `.env` | Cookie、API密钥 | 🔴 极高 |
| `ai_config.json` | OpenAI API密钥 | 🔴 极高 |
| `*.log` | 运行日志 | 🟡 中等 |

## 🔧 正确的配置流程

1. **复制模板文件**:
   ```bash
   cp .env.example .env
   ```

2. **编辑配置文件**:
   - 在 `.env` 中填入真实的Cookie和API密钥
   - 注意：`.env` 文件已在 `.gitignore` 中，不会被上传

3. **配置示例**:
   ```bash
   # .env.example 中只放占位符
   BILIBILI_COOKIE=your_complete_cookie_here
   OPENAI_API_KEY=your_openai_api_key_here

   # .env 中放真实数据（不会被上传）
   BILIBILI_COOKIE=SESSDATA=真实的cookie值...
   OPENAI_API_KEY=sk-真实的API密钥...
   ```

## 🚨 如果意外上传了敏感信息

**立即行动**:
1. 立即删除仓库（如果是私人项目）
2. 更改所有泄露的密钥和密码
3. 重新生成OpenAI API密钥
4. 重新登录B站获取新Cookie

## 💡 最佳实践

- 永远不要在代码中硬编码密钥
- 定期更换API密钥和Cookie
- 使用环境变量管理敏感配置
- 使用私有仓库存储敏感项目

---

**记住：一旦敏感信息上传到公共仓库，就应该视为已泄露！**
