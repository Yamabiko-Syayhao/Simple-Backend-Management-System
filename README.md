# 商城客户端与后台管理系统

本仓库包含面向会员的 uni-app 商城客户端，以及基于 FastAPI 和 Vue 3 的商城运营后台。

大部分使用ai进行修改，放在这里进行存档

本项目在 Rebort 的 FastAPI Web Admin 脚手架上扩展。感谢原作者及贡献者。[上游项目](https://github.com/rebort-hub/fastapiwebadmin)

## 项目目录

| 目录 | 用途 |
| --- | --- |
| [`Mall_Front‑end_Page/`](Mall_Front‑end_Page/) | 商城客户端，供会员浏览商品、加购物车、下单和查看订单。 |
| [`fastapiwebadmin/frontend/`](fastapiwebadmin/frontend/) | 后台管理界面，供运营人员管理商品、会员和订单。 |
| [`fastapiwebadmin/backend/`](fastapiwebadmin/backend/) | FastAPI 服务端，为商城客户端和后台管理界面提供 API。 |

## 主要功能

- 商品、分类、品牌、库存与评论管理
- 会员、订单、售后、优惠券和团购管理
- 数据概览、统计报表、角色权限与操作日志
- 登录后可用的 AI 助手，支持流式回复，并按账号权限只读查询商城数据

后端使用 FastAPI、SQLAlchemy、MySQL 和 Redis。管理端使用 Vue 3、Vite、TypeScript 和 Element Plus。

## 本地启动

准备 Python 3.11、uv、Node.js 22.12 或以上版本，以及运行中的 MySQL 和 Redis。

### 1. 配置数据库与后端

在 MySQL 中创建开发数据库。

```sql
CREATE DATABASE IF NOT EXISTS fastapiwebadmin CHARACTER SET utf8mb4;
```

首次运行时，将[开发配置示例](fastapiwebadmin/backend/env/.env.dev.example)复制为 `fastapiwebadmin/backend/env/.env.dev`，填写 MySQL 和 Redis 连接配置。从仓库根目录运行以下命令。

```sh
cd fastapiwebadmin/backend
uv sync
uv run main.py run --env=dev
```

### 2. 启动管理端

另开一个终端，从仓库根目录运行。

```sh
cd fastapiwebadmin/frontend
npm ci
npm run dev
```

打开[管理后台](http://localhost:3000)或 [API 文档](http://127.0.0.1:8100/docs)。按示例配置初始化后，本地种子账号为 `admin`，密码为 `123456`。

### 3. 运行商城客户端

后端启动后，用 HBuilderX 打开 `Mall_Front‑end_Page/`，选择运行到浏览器（H5）。客户端默认连接本机 `8100` 端口，可在[客户端接口配置](Mall_Front‑end_Page/api/config.js)中修改 `API_HOST`。

### 4. 启用 AI 助手（可选）

在 `fastapiwebadmin/backend/env/.env.dev` 中配置 `AI_ASSISTANT_BASE_URL`、`AI_ASSISTANT_API_KEY` 和 `AI_ASSISTANT_MODEL`，可通过 `AI_ASSISTANT_SYSTEM_PROMPT` 自定义提示词。模型需支持 OpenAI 兼容的 Chat Completions 和函数调用。保存后重启后端，登录并点击右下角的 AI 助手。

## 文档与许可

- [商城业务与接口说明](fastapiwebadmin/README02.md)
- [开发规范](fastapiwebadmin/CODING_GUIDE.md)
- [MIT 许可证](fastapiwebadmin/LICENSE)
