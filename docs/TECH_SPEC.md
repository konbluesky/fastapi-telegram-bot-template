# 技术规范 (Technical Specification)

## 技术栈

| 类型         | 选型        | 版本要求     |
| ------------ | ----------- | ------------ |
| 语言         | Python      | 3.11+        |
| Web 框架     | FastAPI     | 0.100+       |
| ORM          | SQLAlchemy  | 2.0+ (async) |
| 数据库       | MySQL       | 8.0+         |
| 缓存         | Redis       | 7.0+         |
| 数据校验     | Pydantic    | 2.0+         |
| YAML         | PyYAML      | 6.0.2+       |
| Telegram Bot | aiogram     | 3.21+        |
| APScheduler  | APScheduler | 3.11+        |
| 日志框架     | loguru      | 0.7.0+       |
| 数据库迁移   | Alembic     | 1.13+        |

---

## 项目结构

```
fastapi-telegram-bot-template/
├── app/
│   ├── __init__.py
│   ├── api/                       # API 路由层
│   │   ├── __init__.py
│   │   ├── dependencies.py        # 依赖注入
│   │   ├── telegram_router.py     # Telegram Webhook 路由
│   │   └── v1/                    # v1 版本 API
│   │       └── __init__.py
│   ├── bot/                       # Telegram Bot 代码
│   │   ├── __init__.py
│   │   ├── bot_manager.py         # Bot 管理器
│   │   ├── keyboards.py           # 键盘组件
│   │   ├── middlewares.py         # 中间件
│   │   └── handlers/              # 消息处理器
│   │       ├── __init__.py
│   │       └── common.py          # 通用处理器
│   ├── core/                      # 核心模块（配置、数据库、日志等）
│   │   ├── __init__.py
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库连接
│   │   ├── logger.py              # 日志配置
│   │   └── redis.py               # Redis 连接
│   ├── models/                    # 数据模型 (SQLAlchemy)
│   │   ├── __init__.py
│   │   └── base.py                # 模型基类
│   ├── schemas/                   # Pydantic 模型
│   │   └── __init__.py
│   ├── services/                  # 业务服务层
│   │   └── __init__.py
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── security.py            # 安全工具（HMAC签名等）
│       └── snowflake.py           # 雪花ID生成器
├── main.py                        # 应用入口
├── alembic/                       # 数据库迁移
│   ├── env.py                     # Alembic 环境配置
│   ├── script.py.mako             # 迁移脚本模板
│   └── versions/                  # 迁移版本文件
├── alembic.ini                    # Alembic 配置文件
├── tests/                         # 测试目录
│   └── __init__.py
├── deploy/                        # 部署相关
├── docs/                          # 文档目录
├── logs/                          # 日志目录
├── base.config.yml                # 基础配置
├── dev.config.yml                 # 开发环境配置
├── test.config.yml                # 测试环境配置
├── prod.config.yml                # 生产环境配置
├── requirements.txt               # Python 依赖
└── docker-compose.yml             # Docker 编排
```
