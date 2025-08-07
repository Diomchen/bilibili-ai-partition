# bilibili-ai-partition

🤖 **哔哩哔哩关注列表智能分组工具**

一个基于AI的智能工具，帮助你自动分析和分组哔哩哔哩关注列表中的UP主。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

## ✨ 功能特性

- 🤖 **AI智能分析**: 使用OpenAI GPT模型分析UP主的用户名和签名，自动识别内容类型
- 📊 **自动分组**: 根据分析结果自动创建分组并批量分配用户
- 🔍 **试运行模式**: 支持试运行，预览分组结果而不执行实际操作
- 📈 **详细统计**: 提供完整的执行统计和成功率分析
- 🎯 **智能分类**: 支持40+种预定义分类标签，覆盖各种内容领域
- ⚡ **高效处理**: 异步处理，支持大量关注用户的批量操作
- 🛡️ **错误处理**: 完善的错误处理和重试机制

## � 安全提醒

**⚠️ 重要：本项目涉及敏感信息（Cookie、API密钥），请务必注意安全！**

- 📖 **必读文档**: [SECURITY.md](SECURITY.md) - 详细的安全配置指南
- 🚫 **禁止上传**: `.env` 和 `ai_config.json` 文件包含敏感信息，已在 `.gitignore` 中忽略
- 🔐 **定期更换**: 建议定期更换Cookie和API密钥
- 🛡️ **私有仓库**: 如需上传代码，建议使用私有仓库

## �🚀 快速开始

### 方式一：交互式配置（推荐）

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 运行配置向导

```bash
python main.py setup
```

配置向导将引导您：
- 🔐 **扫码登录**: 使用哔哩哔哩APP扫码登录，自动获取认证信息
- 🤖 **AI配置**: 输入OpenAI API密钥和相关设置
- 💾 **自动保存**: 配置信息自动保存，无需手动编辑文件

#### 3. 开始使用

试运行（预览结果）：
```bash
python main.py run --dry-run
```

正式运行：
```bash
python main.py run
```

### 方式二：传统配置

#### 1. 安装依赖

```bash
pip install -r requirements.txt
```

#### 2. 初始化配置

```bash
python main.py init
```

#### 3. 手动配置

编辑 `.env` 文件，填入以下信息：

```env
# 哔哩哔哩配置
BILIBILI_COOKIE=your_complete_cookie_here

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo
```

#### 4. 验证配置

```bash
python main.py validate
```

#### 5. 运行智能分组

```bash
python main.py run
```

## 📱 扫码登录详细说明

### 扫码登录流程

1. **生成二维码**: 工具自动调用哔哩哔哩API生成登录二维码
2. **显示二维码**: 在控制台显示ASCII格式的二维码
3. **扫码登录**: 使用哔哩哔哩APP扫描二维码并确认登录
4. **获取Cookie**: 自动获取登录后的完整Cookie信息
5. **保存配置**: 将Cookie保存到配置文件中

### 扫码登录优势

- **🔒 安全性**: 无需手动复制敏感的Cookie信息
- **⚡ 便捷性**: 一键扫码，自动完成认证
- **🎯 准确性**: 避免手动复制时的错误
- **🔄 实时性**: 实时获取最新的登录状态

### 使用扫码登录

```bash
# 方式一：使用配置向导（推荐）
python main.py setup

# 方式二：运行时临时配置
python main.py run --interactive
```

### 扫码登录故障排除

**Q: 二维码显示异常**
A: 确保终端支持ASCII字符显示，或查看显示的二维码链接

**Q: 扫码后没有反应**
A: 确保网络连接正常，稍等片刻后重试

**Q: 登录超时**
A: 默认超时时间为3分钟，请在时间内完成扫码登录

## 📋 命令说明

| 命令 | 说明 |
|------|------|
| `setup` | **交互式配置向导（推荐）** |
| `status` | 显示当前配置状态 |
| `run` | 运行智能分组 |
| `run --dry-run` | 试运行模式，不执行实际操作 |
| `run --interactive` | 临时使用交互式配置运行 |
| `init` | 初始化配置文件（传统方式） |
| `validate` | 验证配置是否正确 |
| `info` | 显示工具信息 |
| `cookie-help` | 显示Cookie获取帮助 |

### 🆕 新功能特性

- **📱 扫码登录**: 支持使用哔哩哔哩APP扫码登录，无需手动复制Cookie
  - 自动生成ASCII二维码显示在控制台
  - 实时轮询登录状态
  - 自动获取完整登录Cookie
- **🎯 交互式配置**: 友好的控制台向导，一步步完成所有配置
  - 美观的界面设计
  - 智能错误提示和恢复
  - 支持配置验证和预览
- **💾 配置保存**: AI配置自动保存，避免重复输入
  - AI配置保存到独立JSON文件
  - 支持配置复用和更新
  - 安全的密钥处理
- **📊 状态检查**: 随时查看配置完成情况
  - 实时配置状态显示
  - 详细的配置项检查
  - 友好的状态提示

## 🎯 支持的分类标签

工具支持以下预定义分类标签：

**技术类**: 科技、编程、AI、数码、汽车
**娱乐类**: 游戏、音乐、舞蹈、影视、动漫、搞笑
**生活类**: 美食、旅游、时尚、美妆、生活、萌宠、母婴、家居、手工
**知识类**: 教育、知识、科学、历史、文学、心理、医学、法律
**商业类**: 财经、投资、创业、职场
**其他类**: 体育、健身、摄影、艺术、设计、新闻、时事

无法明确分类的UP主将被标记为"未知"。

## 🔧 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `BILIBILI_COOKIE` | 哔哩哔哩登录Cookie | 必填 |
| `OPENAI_API_KEY` | OpenAI API密钥 | 必填 |
| `OPENAI_BASE_URL` | OpenAI API地址 | https://api.openai.com/v1 |
| `OPENAI_MODEL` | 使用的AI模型 | gpt-3.5-turbo |
| `REQUEST_DELAY` | 请求间隔(秒) | 1.0 |
| `MAX_RETRIES` | 最大重试次数 | 3 |
| `TIMEOUT` | 请求超时时间(秒) | 30 |
| `PAGE_SIZE` | 每页获取数量 | 24 |
| `MAX_PAGES` | 最大页数 | 100 |
| `AI_BATCH_SIZE` | AI分析批次大小 | 10 |

## 📊 工作流程

1. **获取关注列表**: 通过哔哩哔哩API获取所有关注的UP主信息
2. **AI分析分类**: 使用OpenAI GPT模型分析UP主的用户名和签名，生成分类标签
3. **创建分组**: 根据分析结果自动创建对应的分组
4. **批量分组**: 将UP主批量分配到对应的分组中

## ⚠️ 注意事项

1. **Cookie安全**: Cookie包含敏感信息，请妥善保管，不要在公共场所暴露
2. **API限制**: 注意OpenAI API的使用限制和费用
3. **请求频率**: 工具已内置请求限制，避免触发哔哩哔哩的反爬机制
4. **分组限制**: 哔哩哔哩对分组数量和名称可能有限制
5. **网络环境**: 确保网络环境稳定，能够正常访问相关API

## 🐛 故障排除

### 常见问题

**Q: Cookie无效或过期**
A: 重新获取Cookie，确保包含所有必要字段

**Q: OpenAI API调用失败**
A: 检查API密钥是否正确，账户是否有足够余额

**Q: 分组创建失败**
A: 检查分组名称是否符合哔哩哔哩的规范，避免特殊字符

**Q: 网络请求超时**
A: 调整 `TIMEOUT` 和 `REQUEST_DELAY` 配置

### 日志调试

启用详细日志：
```bash
python main.py --log-level DEBUG run
```

保存日志到文件：
```bash
python main.py --log-file grouping.log run
```

## 📄 许可证

本项目仅供学习和个人使用，请遵守相关平台的使用条款。

## 📦 打包为可执行文件

### 自动打包

使用提供的构建脚本：

```bash
# Windows
build.bat

# Linux/macOS
python build.py
```

### 手动打包

```bash
# 安装打包依赖
pip install pyinstaller

# 使用spec文件打包
pyinstaller bilibili-ai-partition.spec

# 或者直接打包
pyinstaller --onefile --console --name bilibili-ai-partition main.py
```

### 发布包结构

```
release/
├── bilibili-ai-partition.exe  # 主程序
├── .env.example              # 配置模板
├── README.md                 # 说明文档
├── requirements.txt          # 依赖列表
└── 使用说明.txt              # 用户指南
```

## 🚀 可执行文件使用

1. **下载发布包**: 从release目录获取所有文件
2. **配置环境**: 复制`.env.example`为`.env`并填写配置
3. **运行程序**: 双击`bilibili-ai-partition.exe`或使用命令行

### 命令行使用

```bash
# 显示帮助
bilibili-ai-partition.exe --help

# 配置向导
bilibili-ai-partition.exe setup

# 试运行
bilibili-ai-partition.exe run --dry-run

# 正式运行
bilibili-ai-partition.exe run
```

## 🖼️使用截图
### 菜单界面
![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807084532562.png)

### AI 配置
![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807084817486.png)

### bilibili 登录认证
![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807084838106.png)

### 智能分组过程
![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807084946885.png)

![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807085012439.png)

![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807085042740.png)

![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807085104194.png)

### 最终效果
![](https://cdn.jsdelivr.net/gh/Diomchen/pic2.0@main/img/20250807085337874.png)

## 🔒 开发者安全提醒

如果你要fork或贡献代码：
- 📖 请先阅读 [SECURITY.md](SECURITY.md)
- 🚫 确保不提交 `.env` 和 `ai_config.json` 文件
- 🔐 不要在代码中硬编码任何密钥

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

**贡献前请确保**:
- 已阅读 [SECURITY.md](SECURITY.md)
- 代码中不包含任何敏感信息

---

**免责声明**: 本工具 99% 由 AI 自动生成，仅供学习和个人使用，使用时请遵守哔哩哔哩的服务条款。作者不对使用本工具造成的任何后果负责。
