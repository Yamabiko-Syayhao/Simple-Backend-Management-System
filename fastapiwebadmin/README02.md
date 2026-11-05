# 商城管理 · 业务逻辑说明

> 本文件记录「商城」业务的设计与实现。**每完成一个模块、确认验证无误后，都在此追加/更新对应章节与变更记录。**
>
> 编码规范（目录放哪、接口怎么写、自检清单）见 **[CODING_GUIDE.md](./CODING_GUIDE.md)**。
>
> 最后更新：2026-11-01

---

## 一、整体架构

| 端 | 目录 | 技术栈 | 面向谁 |
|---|---|---|---|
| 管理后台（前端） | `frontend/` | Vue3 + Element Plus + Pinia + Vite | 商城运营 / 管理员 |
| 后端服务 | `backend/` | FastAPI + SQLAlchemy 2.0(async) + MySQL 8 + Redis | 同时服务下面两端 |
| 客户端（移动端/H5） | `Mall_Front‑end_Page/` | uni-app（Vue3，HBuilderX 工程） | 商城 C 端消费者 |

三端关系：

```
uni-app（H5/小程序）  ──┐
                        ├──>  /api/member/*  ──>  mal_member 表
Vue3 管理后台（PC）    ──┘
```

**核心原则：管理与客户端共用同一张 `mal_member` 表。**
后台维护会员资料与状态，客户端用同一账号登录；后台把状态改成「禁用/注销」，客户端立刻无法登录。二者不是两套账号体系。

---

## 二、当前模块清单

| 一级菜单 | 二级菜单 | 前端页面 | 接口前缀 | 状态 |
|---|---|---|---|---|
| 首页 | 商城数据概览 | `views/home/index.vue` | `/api/statistic` | ✅ 欢迎条及会员/商品/SKU/订单真实总量 |
| 全局悬浮入口 | AI 助手 | `views/system/aiAssistant/index.vue` | `/api/ai-assistant/chat` | ✅ 后台登录后可用，填写模型配置后启用对话 |
| 用户管理 | 会员管理 | `views/system/member/index.vue` | `/api/member` | ✅ 已完成 |
| 用户管理 | 收货地址 | `views/system/address/index.vue` | `/api/address` | ✅ 已完成 |
| 用户管理 | 会员收藏 | `views/system/favorite/index.vue` | `/api/favorite` | ✅ 已完成 |
| 用户管理 | 会员足迹 | `views/system/footprint/index.vue` | `/api/footprint` | ✅ 已完成 |
| 用户管理 | 搜索历史 | `views/system/searchHistory/index.vue` | `/api/searchHistory` | ✅ 已完成 |
| 用户管理 | 意见反馈 | `views/system/feedback/index.vue` | `/api/feedback` | ✅ 已完成 |
| 商场管理 | 行政区域 | `views/system/region/index.vue` | `/api/region` | ✅ 已完成 |
| 商场管理 | 品牌制造商 | `views/system/brand/index.vue` | `/api/brand` | ✅ 已完成 |
| 商场管理 | 商品类目 | `views/system/category/index.vue` | `/api/category` | ✅ 已完成 |
| 商场管理 | 订单管理 | `views/system/order/index.vue` | `/api/order` | ✅ 已完成 |
| 商场管理 | 售后管理 | `views/system/afterSale/index.vue` | `/api/afterSale` | ✅ 已完成 |
| 商场管理 | 通用问题 | `views/system/faq/index.vue` | `/api/faq` | ✅ 已完成 |
| 商场管理 | 关键词 | `views/system/keyword/index.vue` | `/api/keyword` | ✅ 已完成 |
| 商品管理 | 商品列表及独立编辑页 | `views/system/goods/index.vue`、`edit.vue` | `/api/goods` | ✅ 已实现，接口/构建验证通过，浏览器验收待补 |
| 商品管理 | 商品上架（与列表“添加”共用） | `views/system/goods/create.vue` | `/api/goods/saveOrUpdate` | ✅ 已实现，新增/编辑分流检查与构建通过 |
| 商品管理 | 商品评论 | `views/system/goodsComment/index.vue` | `/api/goodsComment` | ✅ 已完成 |
| 推广管理 | 广告管理 | `views/system/ad/index.vue` | `/api/ad` | ✅ 已完成（接口、组件逻辑及构建验证通过） |
| 推广管理 | 优惠券管理及独立详情 | `views/system/coupon/index.vue`、`detail.vue` | `/api/coupon` | ✅ 已完成；会员领取、限领与订单用券同步同一领取表 |
| 推广管理 | 专题管理 | `views/system/topic/index.vue`、`create.vue`、`edit.vue` | `/api/topic` | ✅ 已完成，预置 3 条图文专题 |
| 推广管理 | 团购规则 | `views/system/groupRule/index.vue` | `/api/groupRule` | ✅ 已完成，预置 4 条规则 |
| 推广管理 | 团购活动 | `views/system/groupActivity/index.vue` | `/api/groupActivity` | ✅ 已完成，预置 3 条活动 |
| 统计报表 | 用户统计 | `views/system/statistics/user/index.vue` | `/api/statistic/userChart` | ✅ 每日新增会员柱状图 |
| 统计报表 | 订单统计 | `views/system/statistics/order/index.vue` | `/api/statistic/orderChart` | ✅ 订单量/下单用户/订单总额/客单价折线 |
| 统计报表 | 商品统计 | `views/system/statistics/goods/index.vue` | `/api/statistic/goodsChart` | ✅ 订单量/货品数量/货品总额折线 |
| 客户端 | 商品详情与规格加购 | `Mall_Front‑end_Page/pages/goods/detail.vue` | `/api/goods/clientDetail`、`/api/cart` | ✅ 图集、规格加购及立即购买已接确认订单；真实支付待接 |
| 客户端 | 购物车 | `Mall_Front‑end_Page/pages/cart/index.vue` | `/api/cart` | ✅ 已完成会员隔离、数量修改、持久化勾选、合计、物理删除与侧滑删除 |
| 客户端 | 分类页面 | `Mall_Front‑end_Page/pages/category/index.vue` | `/api/category/clientTree` | ✅ 已实现一级/二级分类联动、类目图片与图标展示，复用已有类目表 |
| 客户端 | 分类商品列表 | `Mall_Front‑end_Page/pages/goods/list.vue` | `/api/category/clientTree`、`/api/goods/clientList` | ✅ 已实现同父分类横向切换、父子范围筛选与分页，商品进入既有详情页 |
| 客户端 | 收货地址 | `Mall_Front‑end_Page/pages/address/index.vue`、`edit.vue` | `/api/address/my*`、`/api/region/tree` | ✅ 本人地址维护、默认地址及区域校验 |
| 客户端 | 确认订单 | `Mall_Front‑end_Page/pages/order/confirm.vue` | `/api/order/preview`、`/submit` | ✅ 服务端计价、库存与订单原子提交 |
| 客户端 | 支付方式占位 | `Mall_Front‑end_Page/pages/order/payment.vue` | `/api/order/myDetail` | ✅ 15 种方式，仅弹窗、不扣款或改已付款 |
| 客户端 | 优惠券领取与选用 | 首页、`pages/order/coupons.vue` | `/api/coupon/claim`、`/myList`、`/api/order/coupons` | ✅ 发行/限领、有效期、范围门槛及订单核销 |
| 客户端 | 个人主页与信息设置 | `pages/profile/index.vue`、`settings.vue`、`nickname.vue`、`mobile.vue`、`password.vue` | `/api/member`、`/api/order/mySummary` | ✅ 本人资料、真实数量角标、头像上传及手机号修改；密码只占位，浏览器完整流程通过 |
| 客户端 | 我的订单与详情 | `pages/order/list.vue`、`detail.vue` | `/api/order/myList`、`/myDetail`、`/myDeleted` | ✅ 本人分页与状态分组、快照详情、待付款进既有支付页、已取消记录删除 |
| 客户端 | 我的优惠券与收藏 | `pages/profile/coupons.vue`、`favorites.vue` | `/api/coupon/myList`、`/api/favorite/my*` | ✅ 本人三状态持券、使用订单、收藏读取及取消；商品详情支持收藏设置 |
| 客户端 | 服务中心 | `pages/profile/service.vue`、`feedback.vue`、`faq.vue` | `/api/feedback/contact`、`/mySubmit`、`/api/faq/list` | ✅ 真实公开客服配置、反馈入库、常见问题搜索；无配置如实显示 |

> 「用户管理」为新增的一级菜单（排序 10），位于「首页」(1) 与「系统设置」(60) 之间。

### 2.1 页面响应式规范（新增页面必读）

管理后台的内容区必须适配窄屏（平板 / 手机浏览器），所有新页面统一按下面这套规则写：

| 断点 | 作用范围 |
|---|---|
| `@media (max-width: 900px)` | 平板 / 窄窗口 |
| `@media (max-width: 560px)` | 手机 |

**搜索栏**
- 容器加 `flex-wrap: wrap`、`gap: 8px`
- 输入框：`flex: 1 1 calc(50% - 4px)`（窄屏一行两个）
- 按钮：`flex: 0 1 auto`，去掉 `margin-left`
- 手机端输入框改 `flex: 1 1 100%`（整行），按钮 `flex: 1 1 40%`

**表格**
- 列宽保持固定，**不要压缩**；容器变窄时由 `el-table` 内部产生**横向滚动条**
- 页面容器加 `overflow-x: hidden`，避免整页横向滚动

**分页**
- 容器 `overflow-x: auto`
- `el-pagination` 加 `flex-wrap: wrap; row-gap: 8px`

**弹窗**
- `el-dialog` 会被 teleport 到 `body`，scoped 样式作用不到，需在组件里再写一个**非 scoped** 的 `<style>` 块
- 宽度改 `92% !important`，`label` 宽度收窄到 `78px`，`content` 的 `margin-left` 同步

已实现：会员管理、收货地址。后续页面照此编写。

### 2.2 表头排序规范（新增页面必读，踩过坑）

**禁止直接用 el-table 默认的 `sortable`。**
它只对**当前页的 10 条数据**做前端排序，和分页是冲突的：升序时第 1 页会显示 6~15，第 2 页却还是 11~15，数据看起来"乱了"。

统一改成**服务端排序**：

```
前端
  <el-table :default-sort="{ prop: 'id', order: 'descending' }" @sort-change="onSortChange">
  <el-table-column prop="id" ... sortable="custom">

  const onSortChange = ({ prop, order }) => {
    if (prop !== 'id') return
    listQuery.sortOrder = order === 'ascending' ? 'asc' : 'desc'
    listQuery.page = 1        // 排序变化必须回到第 1 页
    getList()
  }

  payload.sort_order = listQuery.sortOrder   // 列表和导出都要带

后端
  schema 里加  sort_order: Optional[str] = None
  _build_stmt 里
    .order_by(cls.id.asc() if params.sort_order == "asc" else cls.id.desc())
```

要点：
1. 列必须写 `sortable="custom"`，否则 el-table 仍会本地排序；
2. 排序变化时把 `page` 重置为 1；
3. **导出接口也要带同样的 `sort_order`**，保证导出顺序和列表一致；
4. 默认降序（`desc`），与设计稿一致。

已实现：会员管理、收货地址、会员收藏。

### 2.3 删除规范（新增页面必读）

**商城业务模块统一使用「物理删除」**，即调用 `Base.delete(id, True)`，数据库中该行会被真正删除。

```python
@staticmethod
async def deleted(xxx_id: int) -> int:
    # 物理删除：直接 DELETE 行
    return await Xxx.delete(xxx_id, True)
```

- 前端：`ElMessageBox` 二次确认 → 调 `/deleted` → `ElNotification` 右上角提示「成功 / 删除成功」→ 刷新列表
- 若删除后当前页为空，自动回退一页
- 框架原有的系统模块（用户/角色/菜单/字典/部门等）**仍保持逻辑删除**，未做改动

已按此规范实现：会员管理、收货地址、会员收藏、会员足迹、搜索历史、意见反馈、品牌制造商。

---

## 三、会员模块

### 3.1 数据模型

表名：`mal_member`（模型类 `Member`，位于 `backend/app/api/v1/system/member/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 用户ID（主键，自增） |
| username | varchar(64) | 登录账号，唯一 |
| password | varchar(128) | 登录密码，bcrypt 加密存储 |
| nickname | varchar(64) | 用户昵称 |
| avatar | text | 用户头像 URL（空则前端显示默认头像） |
| mobile | varchar(20) | 手机号码 |
| gender | int | 性别：0 未知 / 1 男 / 2 女 |
| birthday | date | 生日 |
| level | int | 用户等级：0 普通用户 / 1 高级VIP用户 |
| status | int | 状态：**1 可用 / 2 禁用 / 0 注销** |
| — | — | 以下为 `Base` 公共字段 |
| creation_date / created_by | — | 创建时间 / 创建人 |
| updation_date / updated_by | — | 更新时间 / 更新人 |
| enabled_flag | bool | 逻辑删除标记（false = 已删） |
| trace_id | varchar(255) | 链路追踪 ID |

**字段派生**：后端 `MemberService._decorate()` 会把 `gender / level / status` 翻译成 `gender_name / level_name / status_name` 一并返回，前端直接展示，不再自己维护字典。

| 字段值 | 展示文案 |
|---|---|
| gender 0 / 1 / 2 | 未知 / 男 / 女 |
| level 0 / 1 | 普通用户 / 高级VIP用户 |
| status 1 / 2 / 0 | 可用 / 禁用 / 注销 |

### 3.2 接口清单

统一前缀 `/api`，除登录/注册外全部需要登录态。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/member/list` | `member:query` | 分页列表，支持 `username` / `member_id` / `mobile` 模糊筛选 |
| 2 | POST | `/api/member/detail` | `member:query` | 会员详情（供编辑弹窗回显） |
| 3 | POST | `/api/member/saveOrUpdate` | `member:add` / `member:edit` | 新增或编辑 |
| 4 | POST | `/api/member/deleted` | `member:delete` | 删除（**物理删除**，直接 DELETE 行） |
| 5 | POST | `/api/member/export` | `member:export` | 导出 xlsx，返回文件流 |
| 6 | POST | `/api/member/login` | 公开（白名单） | 客户端登录 |
| 7 | POST | `/api/member/register` | 公开（白名单） | 客户端注册 |
| 8 | POST | `/api/member/profile` | 需会员 token | 当前登录会员信息 |
| 9 | POST | `/api/member/logout` | 需会员 token | 退出登录（删 Redis 会话） |
| 10 | POST | `/api/member/updateProfile` | 需本人有效会员 token | 仅按提交字段修改昵称、性别 |
| 11 | POST | `/api/member/uploadAvatar` | 需本人有效会员 token | multipart `file`，上传后直接保存本人头像，3MiB 内栅格图片 |
| 12 | POST | `/api/member/changeMobile` | 需本人有效会员 token | 校验当前登录密码、手机号格式和占用后保存 |

**分页约定**：与项目既有风格一致——`page` / `pageSize` 放在 **POST body** 里，由 `Base.parse_pagination()` 读取；返回结构 `{ rows, rowTotal, page, pageSize, pageTotal }`。

**响应约定**：统一 `{ code, msg, data, success, trace_id }`，`code=0` 为成功。

### 3.3 鉴权设计（重点，后续模块沿用）

后台与客户端共用一套 Redis 会话机制，但**刻意使用不同的载荷结构**：

| | 后台管理员 | 商城会员 |
|---|---|---|
| Redis Key | `fastapiwebadmin:user_token:{token}` | 同左（同一个前缀） |
| 载荷字段 | 含 `id`（= sys_user.id） | **只有 `member_id`，没有 `id`** |
| 生成入口 | `UserService.create_login_session` | `MemberService.create_login_session` |

**为什么会员 token 不写 `id`**：
后台接口的 `AuthPermission` 依赖会拿 token 载荷里的 `id` 去查 `sys_user`。会员 token 没有 `id`，因此：
- 会员 token 调任何后台接口 → 直接 `AccessTokenFail`（code 11000），**不会因为 id 恰好撞上管理员而越权**；
- 会员接口则改用 `current_user()` 取 `member_id`。

实测验证：用会员 token 调 `/api/member/list` 返回 `code: 11000` ✅

**白名单**：`setting.py` 的 `WHITE_ROUTER` 中新增
```
/api/member/login
/api/member/register
```
不加入白名单会被全局登录中间件拦掉。

### 3.4 导出 xlsx 逻辑

- 后端：`MemberService.export()` 用 `openpyxl` 在内存中生成工作簿（表头加粗、灰底、居中、列宽设定），再通过 `StreamingResponse` 返回。
- MIME：`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- 文件名：`Content-Disposition: attachment; filename=member.xlsx; filename*=UTF-8''会员列表_时间戳.xlsx`
- 导出的列：用户ID、用户昵称、手机号码、性别、生日、用户等级、状态、注册时间（与列表页同源，走同一套筛选条件、不分页）。
- 前端：`api/useSystemApi/member.ts` 中 `responseType: 'blob'` → 页面 `createObjectURL` 生成 `<a download>` 触发下载。

> 依赖：`openpyxl==3.1.5`，已写入 `pyproject.toml` 与 `requirements.txt`，虚拟环境已安装。

### 3.5 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/member/index.vue` | 列表页：3 个搜索框（用户名 / 用户ID / 手机号）+「查找」+「导出」；9 列表格；底部分页（可选 10/20/30/40/50/100 条每页） |
| `frontend/src/views/system/member/MemberDialog.vue` | 「用户编辑」弹窗：用户名(编辑态禁用) / 昵称 / 手机 / 性别 / 等级 / 状态，取消 + 确定 |
| `frontend/src/api/useSystemApi/member.ts` | 接口封装（5 个方法） |

**状态标签配色**：可用=蓝、禁用=红、注销=灰。

**菜单数据**：写在 `backend/app/scripts/data/sys_menu.json`（`/member` → `/member/list`），同时已插入线上库并绑定「管理员」角色。新增菜单排序 `sort=10`。

---

## 四、收货地址模块

### 4.1 数据模型

继续使用 `mal_address`（`backend/app/api/v1/system/address/model.py`），不另建客户端地址表。字段：`id`、`member_id`、`receiver_name`、`mobile`、`region`、`detail`、`is_default` 和 Base 公共字段；`member_id` 对应 `mal_member.id`，默认地址用 1/0 保存。地区继续使用 `mal_region`。

### 4.2 接口清单

所有请求为 POST，保留现有响应封装。

| 路径 | 身份与用途 |
|---|---|
| `/api/address/list` | 后台 `address:query`；member_id/receiver_name 筛选、分页 |
| `/api/address/detail` | 后台 `address:query`；查看地址详情 |
| `/api/address/export` | 后台 `address:export`；同筛选导出 xlsx |
| `/api/address/saveOrUpdate`、`/deleted` | 旧后台写入口保留权限，但服务端明确拒绝：收货地址仅支持会员本人维护 |
| `/api/address/myList` | 会员 token；本人地址数组、总数、default_id |
| `/api/address/myDetail` | 会员 token，`{id}`；本人地址与可回显的 region_ids |
| `/api/address/mySave` | 会员 token；本人新增或编辑，不能指定 member_id |
| `/api/address/myDeleted` | 会员 token，`{id}`；物理删除本人地址 |
| `/api/address/myDefault` | 会员 token，`{id}`；设为本人默认地址 |
| `/api/region/tree`、`/children` | 原有公开行政区域接口，客户端与后台共用 |

### 4.3 业务规则

1. 会员身份来自 token，每次验证会员存在、未删除且状态可用；拒绝管理员 token 与跨会员读写。
2. 收货人、详细地址必填，手机号按 `^1[3-9]\d{9}$` 校验。提交真实 `region_ids` 三元组，由服务端验证有效省→市→区链并生成地区文字，不接受伪造地区名称。
3. 默认设置在会员行锁及事务内取消其他默认再保存；没有默认地址时保存的地址自动成为默认。删除默认地址后，剩余最早地址自动接替。
4. 地区仍存入既有 `region` 文字列；编辑旧地址时按现有区域表解析 region_ids，无法匹配时需重新选择，不编造区域 ID。
5. 确认订单优先使用默认地址，无默认则选本人最早有效地址；下单把收货信息复制进订单快照，后续修改地址不会改写历史订单。

### 4.4 后台页面

后台 `views/system/address/index.vue` 继续只显示用户归属、姓名、手机号、地区、详细地址与默认标记，支持查询、排序、分页和导出，没有编辑或删除操作。旧后台写方法也已拒绝，不能只补按钮绕过本人维护规则。

### 4.5 客户端

`pages/address/index.vue` 支持管理与结算选择两种模式；`edit.vue` 支持地区级联、默认开关、保存与删除确认。页面和确认订单复用 `api/address.js` 的显式 POST 请求，具体流程见第二十八章。

---

## 五、会员收藏模块

### 5.1 数据模型

表名：`mal_favorite`（模型类 `Favorite`，位于 `backend/app/api/v1/system/favorite/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 收藏ID（主键，自增） |
| member_id | bigint | 用户ID，对应 `mal_member.id` |
| goods_id | bigint | 商品ID（商品表尚未创建，先存整型） |
| creation_date | datetime | **即「添加时间」**，复用 `Base` 的创建时间，不额外建字段 |
| — | — | 其余为 `Base` 公共字段 |

### 5.2 接口清单

统一前缀 `/api/favorite`，全部需要后台登录态。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/favorite/list` | `favorite:query` | 分页列表，支持 `member_id` / `goods_id` 精确筛选 |
| 2 | POST | `/api/favorite/detail` | `favorite:query` | 详情 |
| 3 | POST | `/api/favorite/saveOrUpdate` | `favorite:add` / `favorite:edit` | 新增或编辑 |
| 4 | POST | `/api/favorite/deleted` | `favorite:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/favorite/export` | `favorite:export` | 导出 xlsx |

### 5.3 业务规则

1. `member_id`、`goods_id` 必填；
2. **同一会员对同一商品只能收藏一次**，重复保存返回「该用户已收藏过该商品」；
3. 「添加时间」直接取 `creation_date`，序列化格式 `YYYY-MM-DD HH:mm:ss`；
4. 列表按 `id` 倒序，`pageSize` 默认 **10**（对齐设计稿）；
5. 导出列：收藏ID、用户ID、商品ID、添加时间。

### 5.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/favorite/index.vue` | 用户ID + 商品ID 两个搜索框、「查找」「导出」、4 列表格、分页（默认 10 条/页） |
| `frontend/src/api/useSystemApi/favorite.ts` | 5 个接口封装（导出走 `responseType: 'blob'`） |

表格列：收藏ID（可排序）、用户ID、商品ID、添加时间。已按 **2.1 响应式规范**适配窄屏。

### 5.5 客户端

暂未接入。后续 H5 商品详情页的「收藏」按钮将走 C 端接口（`/api/favorite/my*`，需会员 token）。

---

## 六、会员足迹模块

### 6.1 数据模型

表名：`mal_footprint`（模型类 `Footprint`，位于 `backend/app/api/v1/system/footprint/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 足迹ID（主键，自增） |
| member_id | bigint | 用户ID，对应 `mal_member.id` |
| goods_id | bigint | 商品ID（商品表尚未创建，先存整型） |
| creation_date | datetime | **即「添加时间」**，复用 `Base` 的创建时间 |
| — | — | 其余为 `Base` 公共字段 |

### 6.2 接口清单

统一前缀 `/api/footprint`，全部需要后台登录态。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/footprint/list` | `footprint:query` | 分页列表，支持 `member_id` / `goods_id` 精确筛选 |
| 2 | POST | `/api/footprint/detail` | `footprint:query` | 详情 |
| 3 | POST | `/api/footprint/saveOrUpdate` | `footprint:add` / `footprint:edit` | 新增或编辑 |
| 4 | POST | `/api/footprint/deleted` | `footprint:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/footprint/export` | `footprint:export` | 导出 xlsx |

### 6.3 业务规则

1. `member_id`、`goods_id` 必填；
2. **足迹是浏览记录，同一会员对同一商品可产生多条**（与收藏不同，不做唯一性校验）；
3. 「添加时间」取 `creation_date`，格式 `YYYY-MM-DD HH:mm:ss`；
4. 列表按 `id` 倒序，`pageSize` 默认 **20**（对齐设计稿）；
5. 导出列：足迹ID、用户ID、商品ID、添加时间。

### 6.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/footprint/index.vue` | 用户ID + 商品ID 两个搜索框、「查找」「导出」、4 列表格、分页（默认 20 条/页） |
| `frontend/src/api/useSystemApi/footprint.ts` | 5 个接口封装（导出走 `responseType: 'blob'`） |

表格列：足迹ID（可排序）、用户ID、商品ID、添加时间。已按 **2.1 响应式规范** 与 **2.2 服务端排序规范** 实现。

### 6.5 客户端

暂未接入。后续 H5 浏览商品详情时写入足迹，C 端接口形如 `/api/footprint/my*`（需会员 token）。

---

## 七、搜索历史模块

### 7.1 数据模型

表名：`mal_search_history`（模型类 `SearchHistory`，位于 `backend/app/api/v1/system/search_history/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 搜索ID（主键，自增） |
| member_id | bigint | 用户ID，对应 `mal_member.id` |
| keyword | varchar(255) | 搜索关键字 |
| creation_date | datetime | **即「添加时间」**，复用 `Base` 的创建时间 |
| — | — | 其余为 `Base` 公共字段 |

### 7.2 接口清单

统一前缀 `/api/searchHistory`（多词前缀沿用 `loginRecord` / `operationLog` 的 camelCase 风格），全部需要后台登录态。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/searchHistory/list` | `searchHistory:query` | 分页列表，支持 `member_id`（精确）/ `keyword`（模糊） |
| 2 | POST | `/api/searchHistory/detail` | `searchHistory:query` | 详情 |
| 3 | POST | `/api/searchHistory/saveOrUpdate` | `searchHistory:add` / `edit` | 新增或编辑 |
| 4 | POST | `/api/searchHistory/deleted` | `searchHistory:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/searchHistory/export` | `searchHistory:export` | 导出 xlsx |

### 7.3 业务规则

1. `member_id`、`keyword` 必填（关键字为空返回「搜索关键字不能为空」）；
2. 搜索历史允许重复关键字（同一词可被搜多次），与足迹一致、不做唯一性校验；
3. 列表按 `id` 倒序，`pageSize` 默认 **20**（对齐设计稿）；
4. 导出列：搜索ID、用户ID、关键字、添加时间。

### 7.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/searchHistory/index.vue` | 用户ID + 搜索关键字两个搜索框、「查找」「导出」、4 列表格、分页（默认 20 条/页） |
| `frontend/src/api/useSystemApi/searchHistory.ts` | 5 个接口封装（导出走 `responseType: 'blob'`） |

表格列：搜索ID（可排序）、用户ID、关键字、添加时间。已按 **2.1 响应式规范** 与 **2.2 服务端排序规范** 实现。

### 7.5 客户端

暂未接入。后续 H5 搜索框提交时写入，C 端接口形如 `/api/searchHistory/my*`（需会员 token）。

---

## 八、意见反馈模块

### 8.1 数据模型

表名：`mal_feedback`（模型类 `Feedback`，位于 `backend/app/api/v1/system/feedback/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 反馈ID（主键，自增） |
| member_id | bigint | 用户ID（可空，允许游客反馈） |
| username | varchar(64) | 用户名（提交时快照） |
| mobile | varchar(20) | 手机号码（提交时快照） |
| feedback_type | varchar(32) | 反馈类型，如「功能建议 / 商品问题 / 其他」 |
| content | text | 反馈内容 |
| images | text | 反馈图片 URL，多个用英文逗号分隔 |
| creation_date | datetime | **即「时间」**，复用 `Base` 的创建时间 |

**派生字段**：后端把 `images` 拆成 `image_list` 数组返回，前端直接渲染缩略图。

> 设计取舍：`username / mobile` 存的是**提交时的快照**，而不是每次 join `mal_member`。这样即使会员后来改昵称或换手机号，历史反馈仍保留当时的联系方式。

### 8.2 接口清单

统一前缀 `/api/feedback`，全部需要后台登录态。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/feedback/list` | `feedback:query` | 分页列表，支持 `username`（模糊）/ `feedback_id`（精确） |
| 2 | POST | `/api/feedback/detail` | `feedback:query` | 详情 |
| 3 | POST | `/api/feedback/saveOrUpdate` | `feedback:add` / `edit` | 新增或编辑 |
| 4 | POST | `/api/feedback/deleted` | `feedback:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/feedback/export` | `feedback:export` | 导出 xlsx |

### 8.3 业务规则

1. `content` 必填（为空返回「反馈内容不能为空」）；
2. 列表按 `id` 倒序，`pageSize` 默认 **20**（对齐设计稿）；
3. 反馈图片存逗号串，读取时转 `image_list` 数组；
4. 导出列：反馈ID、用户名、手机号码、反馈类型、反馈内容、反馈图片、时间。

### 8.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/feedback/index.vue` | 用户名 + 反馈ID 两个搜索框、「查找」「导出」、7 列表格、分页（默认 20 条/页） |
| `frontend/src/api/useSystemApi/feedback.ts` | 5 个接口封装（导出走 `responseType: 'blob'`） |

表格列：反馈ID、用户名、手机号码、反馈类型、反馈内容、反馈图片、时间。
按设计稿该表**没有排序按钮**，固定按 id 倒序即可。反馈图片为空时显示 `-`，有图时显示 40px 缩略图并支持点击放大。

### 8.5 客户端

暂未接入。后续 H5「意见反馈」页提交，C 端接口形如 `/api/feedback/submit`（需会员 token）。

---

## 九、行政区域模块

> **2026-10-30 重构**：原来是把区划数据写死在前端 `region-data.ts` 里，现在改成**数据库表 + 接口**，方便后台与客户端共用（客户端新增收货地址时的省市级联会调这两个接口）。

### 9.1 数据模型

表名：`mal_region`（模型类 `Region`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| name | varchar(64) | 区域名称 |
| code | varchar(12) | GB/T 2260 行政区划编码 |
| parent_id | bigint | 父级ID，省级为 0 |
| level | int | 层级：1 省 / 2 市 / 3 区 |
| sort | int | 同级排序 |

**编码规则**：

| 层级 | 规则 | 示例 |
|---|---|---|
| 省 | 前两位 + `0000` | 北京市 `110000` |
| 市 | 前四位 + `00` | 市辖区 `110100`、石家庄市 `130100` |
| 区县 | 完整 6 位 | 东城区 `110101` |

### 9.2 接口清单

前缀 `/api/region`，**不加权限校验、且在 `WHITE_ROUTER` 白名单里**，后台和客户端（含未登录场景）都能直接调。

| # | 方法 | 路径 | 说明 |
|---|---|---|---|
| 1 | POST | `/api/region/tree` | 返回完整的省→市→区三级树 |
| 2 | POST | `/api/region/children` | 入参 `{parent_id}`，返回直接下级（做省市级联时逐级拉取） |

返回字段：`id / name / code / parent_id / level / level_name / children`。

### 9.3 页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/region/index.vue` | 树形表格：区域名称（可展开）/ 区域类型 / 区域编码 |
| `frontend/src/api/useSystemApi/region.ts` | `getTree` / `getChildren` 两个方法 |

- 页面 `onMounted` 调 `/api/region/tree` 拿数据，不再有静态文件
- `el-table` 树形：`row-key="id"` + `:tree-props="{ children: 'children' }"`
- 默认展开第一个省及其下级（设计稿里展开的是北京 → 市辖区）
- 无搜索、无分页、无导出（按设计稿，整棵树直接铺开）
- 已按 2.1 响应式规范处理窄屏（表格横向滚动）

### 9.4 数据现状与扩展

当前已入库 **470 条**：

- ✅ 34 个省级行政区（含台湾、香港、澳门，无下级）
- ✅ 全部地级行政区
- ✅ 北京 / 天津 / 上海 / 重庆 的区县
- ⚠️ 其余省份的**县级数据未内置**（约 2800 条）

**扩展方式**：直接往 `mal_region` 表里插数据（`level=3`、`parent_id` 指向对应城市），接口和页面都不用改。若拿到民政部/高德的完整区划 JSON，写个导入脚本批量插入即可。

---

## 十、品牌制造商模块

### 10.1 数据模型

表名：`mal_brand`（模型类 `Brand`，位于 `backend/app/api/v1/system/brand/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 品牌商ID（主键，自增） |
| name | varchar(128) | 品牌商名称，**必填且不可重名** |
| image | text | 品牌商图片 URL（复用 `/api/file/upload`） |
| description | text | 介绍 |
| floor_price | decimal(10,2) | 底价 |
| — | — | 其余为 `Base` 公共字段 |

### 10.2 接口清单

统一前缀 `/api/brand`，全部需要后台登录态。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/brand/list` | `brand:query` | 分页列表，支持 `brand_id`（精确）/ `name`（模糊） |
| 2 | POST | `/api/brand/detail` | `brand:query` | 详情（编辑弹窗回显） |
| 3 | POST | `/api/brand/saveOrUpdate` | `brand:add` / `edit` | 新增或编辑，返回 `{id}` |
| 4 | POST | `/api/brand/deleted` | `brand:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/brand/export` | `brand:export` | 导出 xlsx |

### 10.3 业务规则

1. `name` 必填，且**同名不允许重复**（编辑时排除自身）；
2. `floor_price` 为 `decimal(10,2)`，返回前端时转成 `float`（`199.00` → `199`、`9.90` → `9.9`）；
3. 列表按 `id` 倒序，`pageSize` 默认 **20**；
4. 删除后若当前页已空，自动回退一页；
5. 导出列：品牌商ID、品牌商名称、介绍、底价、品牌商图片。

### 10.4 图片上传

复用项目已有的 `/api/file/upload`（`/api/file` 在鉴权中间件里是放行的）：

```
el-upload :action="`${getApiBaseUrl()}/file/upload`" :headers="{ token }"
```

> ⚠️ 注意别拼成 `/api/api/...`：`utils/config.ts` 里
> - `getApiBaseUrl()` = `origin + VITE_API_PREFIX`（**已包含** `/api`）
> - `getBaseApiUrl()` = 只有 origin
>
> 所以正确写法是 `getApiBaseUrl() + '/file/upload'`，或者 `getBaseApiUrl() + '/api/file/upload'`。

- 只接受 `image/*`，前端限制 10MB，后端 `UPLOAD_ALLOWED_EXTENSIONS` 再校验一次
- 上传成功返回 `{ id, url, ... }`，把 `url` 存进 `mal_brand.image` 即可

### 10.5 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/brand/index.vue` | 列表页：ID/名称搜索 + 查找/添加/导出 + 6 列表格 + 分页 |
| `frontend/src/views/system/brand/BrandDialog.vue` | 创建/编辑弹窗：名称(必填) / 介绍 / 图片上传 / 底价 |
| `frontend/src/api/useSystemApi/brand.ts` | 5 个接口封装（导出走 `responseType: 'blob'`） |

**删除交互**：`ElMessageBox` 二次确认 → 调 `/api/brand/deleted` → 右上角 `ElNotification`「成功 / 删除成功」→ 刷新列表。

> 说明：删除采用**物理删除**（`Brand.delete(id, True)`），数据库中该行会被直接移除，不是逻辑删除。

### 10.6 演示数据

已预置 **41 条**品牌商数据（ID、名称、介绍、底价对齐设计稿，图片为空显示占位），用于测试分页、搜索与删除。

---

## 十一、商品类目模块

### 11.1 数据模型

表名：`mal_category`（模型类 `Category`，位于 `backend/app/api/v1/system/category/model.py`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 类目ID（主键，自增） |
| name | varchar(128) | 类目名称，**必填** |
| keywords | varchar(255) | 关键字 |
| level | int | 级别：1 一级类目 / 2 二级类目 |
| parent_id | bigint | 父类目ID，一级类目固定为 0 |
| icon | text | 类目图标 URL；一级供首页快捷入口，二级供分类页格子图标 |
| image | text | 类目图片 URL；一级类目的 image 用作分类页右侧内容顶部图片，不用二级 image 替代 icon |
| description | varchar(500) | 类目简介 |
| — | — | 其余为 `Base` 公共字段 |

### 11.2 接口清单

统一前缀 `/api/category`。四个管理接口需要后台登录和对应权限；`clientList` / `clientTree` 是公开只读接口，均加入 `WHITE_ROUTER`，客户端未登录也能调用。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/category/list` | `category:query` | **全量**返回（不分页），前端组装成树 |
| 2 | POST | `/api/category/detail` | `category:query` | 详情 |
| 3 | POST | `/api/category/saveOrUpdate` | `category:add` / `edit` | 新增或编辑 |
| 4 | POST | `/api/category/deleted` | `category:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/category/clientList` | 无（公开） | 保持首页快捷入口契约，返回最多 10 个一级类目，字段为 id/name/icon/image |
| 6 | POST | `/api/category/clientTree` | 无（公开） | 完整有效两级树，不受首页 10 项限制，返回图片、图标、简介及直属 children |

> 类目数量少、又是树形结构，所以**没有做分页和导出**。管理 `/list` 返回 `{ rows, total }`，后台 `buildTree()` 按 `level` / `parent_id` 组装两级树；公开 `/clientTree` 的 data 直接是根节点数组，根节点带 `children`，客户端无需调用管理接口。

### 11.3 业务规则

1. `name` 必填（为空返回「类目名称不能为空」）；
2. `level=1` 时强制 `parent_id=0`；`level=2` 必须选择父类目，且父类目必须是一级类目；
3. **父类目不能是自己**；
4. **已经有子类目的一级类目，不允许改成二级**（否则子类目会变成孤儿）；
5. **同一父级下类目名不允许重复**（编辑时排除自身）；
6. 删除一级类目时，若下面还有二级类目，拒绝删除并提示「该类目下存在子类目，请先删除子类目」；
7. 删除为物理删除。
8. 公开分类树只展示未删除且 `level=1,parent_id=0` 的根及其未删除二级子类目；过滤孤儿，按 ID 稳定排序，裁剪后台审计字段。商品按一级分类查询时包含一级自身及有效直属二级，二级查询仅匹配自身；无效分类不返回全场商品。

### 11.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/category/index.vue` | 树形表格：类目ID / 类目名 / 图标 / 图片 / 关键字 / 简介 / 级别 / 操作 |
| `frontend/src/views/system/category/CategoryDialog.vue` | 创建/编辑弹窗 |
| `frontend/src/api/useSystemApi/category.ts` | 4 个接口封装 |

- 表格用 `el-table` 树形能力（`row-key="id"` + `tree-props`），点类目ID左侧箭头展开二级类目
- 工具栏按设计稿**只有「添加」按钮**（无搜索、无导出、无分页）
- 级别用标签区分：一级类目=蓝色、二级类目=灰色
- 「父类目」下拉**创建和编辑时都有**（仅 `level=2` 时显示），选项是一级类目并排除自己；切到一级时自动清空并隐藏
  > 早期版本编辑时隐藏了父类目，导致「二级 → 一级 → 再改回二级」时选不了父类目、直接卡死，已修复
- 图标、图片两个上传框都复用 `/api/file/upload`

### 11.5 测试数据

已预置 **20 条**：一级 6 条（配件 / 服装 / 婴童 / 杂货 / 洗护 / 周边），二级 14 条（挂在对应一级下）。

---

## 十二、订单管理模块

### 12.1 数据模型

两张表：

**`mal_order`（订单主表）**

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| order_no | varchar(32) | 订单编号（业务号，页面上显示的） |
| member_id / username / avatar | — | 下单用户信息 |
| order_time | datetime | 下单时间（列表按它倒序） |
| status | int | 订单状态（见 12.2） |
| total_amount / pay_amount | decimal(12,2) | 订单金额 / 实付金额 |
| pay_time / pay_channel | — | 支付时间 / 支付渠道 |
| user_message | varchar(500) | 用户留言 |
| receiver_name / receiver_phone / receiver_region / receiver_detail | — | 收货信息 |
| express_company / express_no | — | 物流渠道 / 物流单号 |
| deliver_time / confirm_time | datetime | 发货时间 / 确认收货时间 |
| refund_amount / refund_type / refund_note / refund_time | — | 退款信息 |

新增订单字段 `goods_amount / freight_amount / discount_amount` 金额快照、`coupon_user_id` 持券 ID、`checkout_key` 幂等键；`(member_id, checkout_key)` 唯一。已有库需运行 `install_checkout.py` 补字段和索引，不能仅依赖 create_all，详见第二十八章。

**`mal_order_item`（订单商品明细）**

| 字段 | 说明 |
|---|---|
| order_id | 所属订单 |
| goods_id / product_id | 下单商品和库存规格 ID 快照 |
| goods_name / goods_no / spec / price / quantity / image | 商品名称 / 编号 / 规格 / 价格 / 数量 / 图片 |

### 12.2 订单状态字典

| 值 | 文案 | 值 | 文案 | 值 | 文案 |
|---|---|---|---|---|---|
| 1 | 未付款 | 4 | 已付款 | 7 | 已发货 |
| 2 | 用户取消 | 5 | 申请退款 | 8 | 用户收货 |
| 3 | 系统取消 | 6 | 已退款 | 9 | 系统收货 |

后端 `ORDER_STATUS` 与前端 `ORDER_STATUS_OPTIONS` **必须保持一致**，改一处要同步另一处。

### 12.3 接口清单

统一前缀 `/api/order`。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/order/list` | `order:query` | 分页 + 多条件筛选（见下），返回的每条订单带 `items` 明细 |
| 2 | POST | `/api/order/detail` | `order:query` | 详情（含明细） |
| 3 | POST | `/api/order/deleted` | `order:delete` | **物理删除**；本次客户端未付款订单先原子恢复库存并释放本单持券，再删明细/订单，旧演示或已付款订单不恢复 |
| 4 | POST | `/api/order/collect` | `order:collect` | 线下收款（**占位**：返回「当前订单状态不支持线下收款」） |
| 5 | POST | `/api/order/deliver` | `order:deliver` | 发货（**占位**：参数缺失返回「参数不对」，否则「订单不能确认收货」） |
| 6 | POST | `/api/order/refund` | `order:refund` | 退款（**占位**：返回「当前订单不能进行退款」） |
| 7 | POST | `/api/order/export` | `order:export` | 导出 xlsx |
| 8 | POST | `/api/order/preview` | 会员 token | 服务端计价并生成 15 分钟报价 |
| 9 | POST | `/api/order/coupons` | 会员 token | 当前报价下本人可用与不可用优惠券及原因 |
| 10 | POST | `/api/order/submit` | 会员 token | 幂等提交未付款订单、扣库存、核销券、清理所选购物车 |
| 11 | POST | `/api/order/myDetail` | 会员 token | 本人订单快照与 15 种支付占位方式 |

**list 支持的筛选条件**：`username`、`receiver_name`、`order_no`（模糊）、`status`（精确）、`start_time` / `end_time`（按下单时间范围，格式 `YYYY-MM-DD HH:mm:ss`）。

> 收款 / 发货 / 退款三个接口目前只是**占位**，真实支付与履约流程接入后再补业务动作；客户端确认订单与支付方式弹窗已完成。

### 12.4 静默请求（silent）

收款/发货/退款失败时，页面要弹右上角「失败」通知，而全局拦截器默认会弹 toast，两者会重复。因此给 axios 请求加了 `silent: true` 支持：

```ts
// utils/request.ts
} else if (!(response.config as any)?.silent) {
  ElMessage.error(res.msg || '接口错误！');
}
```

带 `silent: true` 的接口由调用方自己处理错误提示。

### 12.5 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/order/index.vue` | 列表页：3 个输入框 + 日期时间范围 + 订单状态 + 查找/导出 + 树形展开 + 分页 |
| `frontend/src/views/system/order/OrderDetailDialog.vue` | 订单详情弹窗 + **打印** 按钮 |
| `frontend/src/views/system/order/OrderActionDialog.vue` | 收款 / 发货 / 退款三个弹窗（同一个组件按 mode 切换） |
| `frontend/src/api/useSystemApi/order.ts` | 7 个接口封装 |

**日期时间范围**：`el-date-picker type="datetimerange"`，自带「清空 / 确定」与双日历面板，`shortcuts` 提供最近一周 / 一个月 / 三个月（相对当前时间计算）。选择后自动写入 `start_time` / `end_time`，点「查找」才真正查询。

**表格**：13 列（订单编号 / 用户头像 / 下单用户 / 下单时间 / 订单状态 / 订单金额 / 实付金额 / 支付时间 / 收货人 / 收货电话 / 物流单号 / 物流渠道 / 操作），列宽固定 → 窄屏时表格内部横向滚动。

> 操作列**不要**加 `fixed="right"`：固定列会脱离表格横向滚动、浮在内容上方，看起来像"钉住不动"。所有列（含操作）都要随表格一起滚动。

**二级展开**：用 `type="expand"` 展开行，里面嵌一个商品明细小表格（商品名称 / 商品编号 / 货品规格 / 货品价格 / 货品数量 / 货品图片）。

**操作列 5 个按钮**：

| 按钮 | 行为 |
|---|---|
| 详情 | 调 `/detail`，弹详情窗；窗内「打印」打开新窗口并调 `window.print()` |
| 删除 | 二次确认 → 物理删除 → 右上角「成功 / 删除成功」 |
| 收款 | 弹收款窗（订单金额只读、付款金额可改）→ 确定 → 右上角「失败 / 当前订单状态不支持线下收款」 |
| 发货 | 弹发货窗（快递公司下拉 + 快递编号）→ 未填 → 「失败 / 参数不对」；填了 → 「失败 / 订单不能确认收货」 |
| 退款 | 弹退款窗（退款金额只读 = 实付金额）→ 确定 → 「失败 / 当前订单不能进行退款」 |

### 12.6 数据来源说明

后台订单表的数据**最终由客户端下单产生**，管理端只负责查询与运营操作。后续写 H5 时，下单逻辑要写入同一套 `mal_order` / `mal_order_item` 表，保证管理端能直接看到。

---

## 十三、售后管理模块

### 13.1 模块定位

售后记录**不是后台创建的**，而是客户端用户点击「申请退款 / 退货退款」后写入 `mal_after_sale`，后台在这里审核。当前客户端还没开发，所以**表已建好但没有预置任何数据**，页面初始为空（对应设计稿的「暂无数据」）。

### 13.2 数据模型

表名：`mal_after_sale`（模型类 `AfterSale`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| after_sale_no | varchar(32) | 售后编号 |
| order_id / order_no | — | 关联订单 |
| member_id / username | — | 申请用户 |
| type | varchar(32) | 售后类型：仅退款 / 退货退款 |
| reason | varchar(500) | 退款原因 |
| refund_amount | decimal(12,2) | 退款价格 |
| status | int | 1 待审核 / 2 待退款 / 3 已拒绝 / 4 已退款 |
| apply_time | datetime | 申请时间 |
| audit_time / audit_remark | — | 审核时间 / 备注 |

### 13.3 接口清单

统一前缀 `/api/afterSale`。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/afterSale/list` | `afterSale:query` | 分页列表，支持 `after_sale_no`（模糊）/ `order_id`（精确）/ `status` |
| 2 | POST | `/api/afterSale/detail` | `afterSale:query` | 详情 |
| 3 | POST | `/api/afterSale/audit` | `afterSale:audit` | **批量通过 / 批量拒绝**，入参 `{ids, action: 'pass'|'reject'}` |
| 4 | POST | `/api/afterSale/export` | `afterSale:export` | 导出 xlsx |

**audit 规则**：
- `ids` 为空 → `请选择至少一条记录`
- `action` 不是 pass/reject → `参数不对`
- 通过 → `status=2`（待退款）；拒绝 → `status=3`（已拒绝）
- 一条都没更新到 → `所选记录不存在或已处理`

### 13.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/afterSale/index.vue` | 搜索 + 批量按钮 + 状态页签 + 表格 + 分页 |
| `frontend/src/api/useSystemApi/afterSale.ts` | 4 个接口封装 |

- 顶部：售后编号、订单ID、查找、导出
- 右侧：**批量通过**（绿色）、**批量拒绝**（红色）
- 页签：**全部 / 待审核 / 待退款**（对应 `status` 不传 / 1 / 2）
- 表格：勾选列 + 售后编号 / 订单ID / 用户ID / 售后类型 / 退款原因 / 退款价格 / 申请时间 / 操作
- 操作列：仅「待审核」的行显示「通过 / 拒绝」，其余状态直接显示状态文字
- 批量/单条都走同一个 `audit` 接口；未勾选时弹 `ElMessage.error('请选择至少一条记录')`

### 13.5 客户端对接（待做）

H5 提交退款申请时写入 `mal_after_sale`（初始 `status=1`），后台就能看到；审核通过后管理端把状态改成 2（待退款），实际打款流程等支付模块完成后再补。

---

## 十四、通用问题模块（FAQ）

### 14.1 模块定位

一问一答的常见问题，**后台维护、客户端只读展示**（客户端将来「常见问题」页直接读这里的数据，不能编辑）。

### 14.2 数据模型

表名：`mal_faq`（模型类 `Faq`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 问题ID |
| question | varchar(500) | 问题内容（必填） |
| answer | text | 问题回复（必填） |
| — | — | `Base` 公共字段 |

### 14.3 接口清单

前缀 `/api/faq`。

| # | 方法 | 路径 | 权限码 | 说明 |
|---|---|---|---|---|
| 1 | POST | `/api/faq/list` | **无（公开）** | 分页列表，支持 `question` 模糊 + `sort_order` 排序；**已加入白名单**，客户端未登录也能读 |
| 2 | POST | `/api/faq/detail` | `faq:query` | 详情 |
| 3 | POST | `/api/faq/saveOrUpdate` | `faq:add` / `faq:edit` | 新增或编辑 |
| 4 | POST | `/api/faq/deleted` | `faq:delete` | 删除（**物理删除**） |
| 5 | POST | `/api/faq/export` | `faq:export` | 导出 xlsx |

> 只有 `list` 是公开的（客户端展示用），增删改仍然要后台权限，保证客户端改不了数据。

### 14.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/faq/index.vue` | 搜索 + 查找/添加/导出 + 4 列表格 + 分页 |
| `frontend/src/views/system/faq/FaqDialog.vue` | 创建 / 编辑弹窗（问题单行、回复多行文本域） |
| `frontend/src/api/useSystemApi/faq.ts` | 5 个接口封装 |

- 表格列：问题ID（可排序）、问题内容、问题回复、操作（编辑 / 删除）
- 分页默认 20 条
- 排序走服务端（`sortable="custom"` + `sort_order`），默认按 id 倒序
- 弹窗：问题、回复都是必填，为空分别提示「问题不能为空」「回复不能为空」

### 14.5 客户端对接（待做）

H5「常见问题」页直接 `POST /api/faq/list`（无需登录），把 `question / answer` 渲染成折叠问答列表即可。

---

## 十五、关键词模块

### 15.1 模块定位

后台维护的**搜索关键词**（热门词 / 推荐词），客户端搜索框下方展示，点击后跳到 `link` 指定的页面。

### 15.2 数据模型

表名：`mal_keyword`（模型类 `Keyword`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 关键词ID |
| keyword | varchar(64) | 关键词（必填） |
| link | varchar(500) | 跳转链接 |
| is_recommend | int | 是否推荐：1 推荐 / 0 普通 |
| is_default | int | 是否默认：1 默认 / 0 非默认 |
| — | — | `Base` 公共字段 |

派生字段：`is_recommend_text` / `is_default_text`（是 / 否）由后端 `_decorate` 生成，前端直接展示。

### 15.3 接口清单

前缀 `/api/keyword`，全部需要后台登录态。

| # | 方法 | 路径 | 权限码 |
|---|---|---|---|
| 1 | POST | `/api/keyword/list` | `keyword:query` |
| 2 | POST | `/api/keyword/detail` | `keyword:query` |
| 3 | POST | `/api/keyword/saveOrUpdate` | `keyword:add` / `edit` |
| 4 | POST | `/api/keyword/deleted` | `keyword:delete` |
| 5 | POST | `/api/keyword/export` | `keyword:export` |

`list` 支持：`keyword`（模糊）、`link`（模糊）、`sort_order`（服务端排序）。

### 15.4 后台页面

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/keyword/index.vue` | 搜索 + 查找/添加/导出 + 6 列表格 + 分页 |
| `frontend/src/views/system/keyword/KeywordDialog.vue` | 创建 / 编辑弹窗 |
| `frontend/src/api/useSystemApi/keyword.ts` | 5 个接口封装 |

- 表格列：关键词ID（可排序）、关键词、跳转链接、是否推荐、是否默认、操作
- 「是」绿色标签、「否」蓝色标签
- 弹窗四个字段：关键词（必填）、跳转链接、是否推荐（推荐/普通）、是否默认（默认/非默认）
- 确定后调 `/saveOrUpdate`：无 id 为新增，有 id 为更新

### 15.5 客户端对接（待做）

H5 搜索页调 `/api/keyword/list` 拉取推荐词（后续可再加一个免登录的公开接口）。

---

## 十六、客户端（uni-app）

### 4.1 工程说明

`Mall_Front‑end_Page/` 是 **HBuilderX 版 uni-app（Vue3）工程**：根目录直接放 `main.js` / `pages.json` / `manifest.json` / `App.vue`，`index.html` 引用 `/main.js`。

- **不需要 npm 依赖**：编译器与 Vue3 运行时由 HBuilderX 内置，用 HBuilderX 打开文件夹直接运行即可。
- 若改用 VS Code + CLI（`npm run dev:h5`），需要另建 `src/` 结构并安装 `@dcloudio/*`，属于另一套工程形态。

目录：

```
Mall_Front‑end_Page/         与 fastapiwebadmin/ 同级
├── pages/login/login.vue    会员登录
├── pages/index/index.vue    精选首页
├── pages/profile/           个人主页、资料设置、本人券/收藏、服务/反馈/FAQ
├── pages/category/index.vue 一级/二级分类联动与类目图片
├── pages/cart/index.vue     购物车与结算入口
├── pages/address/           本人地址列表、编辑与地区选择
├── pages/order/             确认订单、选券、支付占位、本人订单列表与详情
├── pages/goods/             商品列表、详情与规格加购
├── pages/search/            搜索及会员搜索历史
├── pages/brand/             品牌列表与详情
├── pages/group/             团购列表
├── pages/topic/             专题列表与详情
├── components/              tab-bar / nav-header / goods-cell / goods-row
├── api/config.js            后端地址配置（API_HOST / API_PREFIX）
├── api/request.js           uni.request 统一封装
├── api/member.js            会员登录/注册/本人资料与头像/手机号/退出
├── api/order.js             确认下单、本人订单列表/统计/详情/已取消记录删除
├── api/favorite.js          本人收藏读取/设置/取消
├── api/feedback.js          客服公开配置与本人意见反馈
├── api/faq.js               公开常见问题搜索和分页
├── api/cart.js              购物车列表、加购、数量、勾选、删除及角标
├── api/category.js          首页快捷分类与完整公开分类树
├── api/url.js               图片与富文本相对地址补全
└── static/                  默认头像、页面图标（svg）
```

### 4.2 登录流程

```
打开 App → pages/login/login（第一页）
  输入账号/密码
  └─ POST /api/member/login  {username, password}
       ├─ 成功：code=0，data 含 token
       ├─ 存 uni.setStorageSync('member_token', token)
       └─ uni.reLaunch → pages/index/index
            └─ POST /api/member/profile（header 带 token）→ 展示昵称/等级
```

登录校验规则（后端 `MemberService.login`）：
1. 账号不存在 / 密码错误 → 「账号或密码错误」
2. `status == 0` → 「该账号已注销，请联系客服」
3. `status == 2` → 「该账号已被禁用，请联系客服」
4. 通过 → 生成 token，24 小时有效（`CACHE_DAY`）

### 4.3 请求封装约定

`api/request.js` 对齐后端响应格式：

| 情况 | 处理 |
|---|---|
| `code === 0` | resolve，返回整个 body |
| `code === 11000` | 清除本地 token，提示后 `reLaunch` 回登录页 |
| 其它业务错误 | toast 提示 `msg` |
| 网络失败 | toast「网络异常，请确认后端已启动」 |

`api/config.js` 中 `API_HOST = 'http://127.0.0.1:8100'`：
**真机调试必须改成电脑内网 IP**（如 `http://192.168.1.10:8100`），因为手机上的 127.0.0.1 指向手机自己。

跨域：后端已新增 `CORS_ORIGIN_REGEX`（见 `backend/app/config/setting.py`），放行 **本机 / 局域网 IP 的任意端口**：

```
https?://(localhost | 127.0.0.1 | 0.0.0.0 | 10.x.x.x | 192.168.x.x | 172.16~31.x.x)(:任意端口)?
```

因此 HBuilderX 跑在 8080、8081，或手机用 `192.168.x.x` 访问，都能通过预检，不需要再改代码。
生产环境把该项置空，改用 `CORS_ORIGINS` 显式白名单。

### 4.4 页面

- **登录页**：默认头像 + 标题 `bs-mail-vue` + 账号/密码输入框 + 「免费注册 / 忘记密码」+ 红色通栏登录按钮 + 底部「技术支持: bs-mail」。
- **我的（个人中心）**：底部 tab「我的」进入，见 4.5。
- **精选首页**：登录成功后的默认页，见 4.6。
- **分类**：左侧一级分类、右侧类目图片和二级分类格子，点击二级分类进入带横向分类切换的商品列表，见 4.9。

### 4.5 底部导航与「我的」页面

**页面结构**（`pages.json`，登录页仍是启动页）：

| 路径 | 说明 |
|---|---|
| `pages/login/login` | 登录（启动页） |
| `pages/index/index` | 精选首页（已对接） |
| `pages/category/index` | 分类（已对接完整两级类目与后台图片） |
| `pages/cart/index` | 购物车（已对接真实会员购物车） |
| `pages/profile/index` | **我的（已实现）** |

**底部导航**：自定义组件 `components/tab-bar/tab-bar.vue`（uni-app easycom 自动引入，用 `<tab-bar current="profile" />`）。

- 不用系统 `tabBar`，因为设计稿的选中态是「红色圆底 + 白色图标」，系统 tabBar 只能用静态 PNG，做不出这个效果
- 未选中：灰色线性图标 22px + 灰字；选中：26px 红圆底 + 白色图标 15px + 红字
- 切换用 `uni.redirectTo`（没有配置系统 tabBar，所以不能用 `switchTab`）

**图标**：`static/icons/`，当前共 21 个 SVG，包含底部导航、订单/券、设置等页面图标（颜色已烘焙进文件）。

| 前缀 | 用途 |
|---|---|
| `tab-xxx.svg` / `tab-xxx-active.svg` | 四个 tab 的灰色 / 白色版本（精选、分类、购物车、我的） |
| `ic-order-*.svg` | 待付款、待发货、待收货、已完成 |
| `ic-coupon-*.svg` | 待使用、已使用、过期关闭 |
| `ic-star / ic-pin / ic-service` | 我的收藏、收货地址、服务中心 |

**我的页面**（`pages/profile/index.vue`）：

- 顶部红色渐变头图（`#ee4442 → #e03333`）+ 白色圆形头像 + 昵称（取 `/api/member/profile` 的 `nickname || username`）；右上角设置按钮进入 `pages/profile/settings`。
- 我的订单：4 个入口（待付款 / 待发货 / 待收货 / 已完成），右侧「全部订单 ›」；数量来自本人 `/api/order/mySummary`，分组与列表使用同一服务端状态映射。
- 我的优惠券：3 个入口（待使用 / 已使用 / 过期关闭），右侧「全部优惠券 ›」；进入独立本人券列表的对应状态，可切换三类，并查看已使用券关联订单。
- 列表入口已连接我的收藏 / 既有收货地址 / 服务中心，不再用开发中提示代替这些页面。
- 去掉无内容的灰色广告占位；退出当前账户移到个人设置，确认后调 `/api/member/logout`、清除本地 token 与会员资料再回登录。
- `onShow` 重新读取本人资料和统计，部分接口失败有重试；切账号先清旧资料/角标，晚到响应按 token 与请求版本拦截，避免上个会员内容回填。

个人设置含头像、昵称、性别、密码占位和手机号。昵称独立保存，性别底部选择「保密/男/女」；头像上传直接保存；手机号按用户确认方案使用当前登录密码校验，不展示未接入的短信验证码。实现、请求字段、状态分组和边界见第二十九章。

### 4.6 首页「精选」与相关子页面

**页面清单（`pages.json` 共 29 个，其中本轮个人中心新增 11 个路由）**

| 路径 | 说明 |
|---|---|
| `pages/index/index` | **精选首页**（登录后默认页） |
| `pages/search/index` | 搜索页（历史搜索 + 结果） |
| `pages/goods/list` | 商品列表：新品 / 人气 / 分类 / 品牌 / 搜索结果共用；分类模式支持同父类目横向切换 |
| `pages/goods/detail` | 商品详情、图集、属性与规格加购；立即购买进入统一确认页 |
| `pages/brand/list`、`pages/brand/detail` | 品牌商列表 / 详情 |
| `pages/group/list` | 团购列表 |
| `pages/topic/list`、`pages/topic/detail` | 专题精选 / 专题详情 |
| `pages/address/index`、`pages/address/edit` | 本人地址管理/选择、添加/编辑 |
| `pages/order/confirm`、`pages/order/coupons`、`pages/order/payment` | 确认订单、可用/不可用券选择、支付方式占位 |
| `pages/profile/settings`、`nickname`、`mobile`、`password` | 本人设置、昵称、手机号、密码占位 |
| `pages/order/list`、`pages/order/detail` | 本人订单分组分页与快照详情 |
| `pages/profile/coupons`、`favorites` | 本人优惠券、收藏 |
| `pages/profile/service`、`feedback`、`faq` | 服务中心、意见反馈、常见问题 |

二级页统一用 `components/nav-header`（左上角「‹ 返回」）+ `navigationStyle: custom`。

**首页板块与数据来源**

| 板块 | 接口 | 来源表 |
|---|---|---|
| 搜索框 | POST `/api/goods/clientList`，body 传 keyword | `mal_goods`（名称 + keywords 字段） |
| 轮播 | `/api/ad/banners` | `mal_ad`（启用状态） |
| 快捷分类 | `/api/category/clientList` | `mal_category`（一级，最多 10 个） |
| 优惠券 | `/api/coupon/clientList` | `mal_coupon`（正常且在有效期的普通领券，最多 10 张；点击走会员 claim） |
| 团购专区 | `/api/groupRule/clientList` | `mal_group_rule`（未过期，限 6 条） |
| 品牌商直供 | `/api/brand/clientList` | `mal_brand`（取 4 个） |
| 新品首发 | POST `/api/goods/clientList`，body 传 scene=new | `mal_goods`（按创建时间倒序） |
| 人气推荐 | POST `/api/goods/clientList`，body 传 scene=hot | `mal_goods`（按 `is_hot` 倒序） |
| 专题精选 | `/api/topic/clientList` | `mal_topic` |

**C 端只读接口（均免后台权限，已进 `WHITE_ROUTER`）**

| 接口 | 说明 |
|---|---|
| `/api/goods/clientList` | 分页 + `keyword`（名称/关键字）+ `scene`(new/hot) + 分类/品牌筛选 |
| `/api/goods/clientDetail` | 商品详情（含图集、规格、参数、真实库存行 `products`、`stock` 与 `cart_available`） |
| `/api/brand/clientList` / `clientDetail` | 品牌列表 / 详情 |
| `/api/category/clientList` | 首页一级类目快捷入口，最多 10 项 |
| `/api/category/clientTree` | 分类页与分类商品列表共用的完整两级类目树，含图标/图片/简介 |
| `/api/coupon/clientList` | 可领取优惠券（已算好 `min_text` / `time_text`） |
| `/api/groupRule/clientList` | 进行中的团购（联商品名称、图片、售价） |

**搜索页与搜索历史（写已有表）**

- 搜索页：输入框 + 「历史搜索」标签 + 「清空历史记录」+ 结果列表
- 历史读写走 `mal_search_history`，新增客户端接口（需会员 token）：
  - `/api/searchHistory/myList`：最近的搜索词（去重，最多 10 个）
  - `/api/searchHistory/add`：记录一次搜索（同一关键字先删后插，只保留最新一条）
  - `/api/searchHistory/clear`：清空本人历史（物理删除）

**说明**：商品列表暂不按 `is_on_sale` 过滤——后台新保存的商品默认是「未售」，如果过滤会让首页空白；等上架流程真正跑起来再打开过滤。

### 4.7 图片地址处理（重要）

后台表单里上传的图片，数据库存的是**相对路径**：`/api/files/2026/10/30/xxx.png`。

客户端 H5 如果直接 `<image :src="/api/files/...">`，浏览器会去前端 dev server（如 `localhost:5173`）找这个地址 → **404，图裂**。

统一用 `api/url.js` 处理：

```js
import { imageUrl, rewriteHtmlImages } from '@/api/url.js'

imageUrl('/api/files/a.png')   // → http://127.0.0.1:8100/api/files/a.png
imageUrl('https://cdn.x/a.png') // → 原样返回
imageUrl('')                    // → ''（模板里配合 v-if 显示占位）
```

- 规则：`http(s)://`、`data:`、`blob:` 原样返回；`/` 开头拼 `API_HOST`；其余补 `/` 再拼
- 已接入的位置：首页轮播/分类/团购/品牌/专题、商品卡片（`goods-cell` / `goods-row`）、商品详情、品牌列表与详情、团购列表、专题列表与详情、个人中心头像
- **富文本**用 `rewriteHtmlImages(html)` 把 `src="/api/...` 批量补全后再交给 `<rich-text>`
- 后端 `/api/files/...` 是公开可读的（`init_app` 里对 `/api/file` 前缀豁免登录），浏览器直接加载不需要 token

### 4.8 商品详情与购物车

商品详情页已替换原占位实现：公开读取 `POST /api/goods/clientDetail`，按商品图集轮播并支持图片预览，展示售价/市场价、名称、简介、富文本正文；点击「属性」查看已有商品参数，点击「规格」选择真实库存规格及购买数量。只有一个库存规格时自动选中，多个规格需主动选择；无货规格不可选，数量限制为 1～999 且不超过当前规格库存。底部购物车角标读取本人购物车总件数。

登录会员确认规格后调用 `POST /api/cart/add`，提交 `{goods_id, product_id, quantity}`；`product_id` 必须是 `mal_goods_product.id`，不是规格表 `mal_goods_specification.id`。相同库存规格合并数量；会员、商品在售状态、实际库存及合并后数量都由服务端重新核验。

购物车页已实现未登录/空车/加载失败状态、商品行、编辑数量、单选/全选、单删/批量删除及服务端合计。普通模式的勾选写入数据库，编辑模式的待删除选择独立保存在页面，不改变普通模式勾选。下架、删除、规格失效、售罄或库存不足条目保留展示，排除合计且可以删除；库存减少时可把原数量降到当前库存再继续使用。

点击「编辑」后，每个商品行右侧展开红色矩形删除区，勾选框和数量控件保留；点击「完成」统一收起。普通模式支持左滑单行展开、右滑或点击已展开的商品区域收起，同一时间只展开一行，H5 也支持鼠标横向拖动。横滑与上下滚动分开识别，滑动后的点击不会误进商品详情；删除继续使用原确认框和 `/api/cart/deleted`，底部批量删除保留。

六个购物车接口统一 POST `/api/cart/list`、`add`、`update`、`checked`、`deleted`、`count`，全部需要会员 token，不加入公开白名单，也不接受后台管理员 token。购物车整车返回，不分页；每次写入后刷新实时单价、库存、件数与金额。详情加购与购物车通过 `cart:change` 事件刷新数据，页面重新显示时也重新加载。

加购本身不扣库存、不创建订单；立即购买和购物车结算现已进入确认订单，提交时才创建未付款订单、扣减库存并核销券。确认订单按优惠前商品金额满 88 元免运费，否则 80 元；优惠券不抵运费，真实支付仍为占位。购物车商品合计仍不含运费，见第二十七、二十八章。

### 4.9 分类页面与分类商品列表

分类页调用公开 `POST /api/category/clientTree`，顶部搜索入口进入现有搜索页，左侧竖排展示全部有效一级类目；选中后，右侧展示该一级类目的 `image`、简介及直属二级类目。二级格子只读取自身 `icon`，不使用 `image` 替代；图片缺失、无效或加载失败时显示占位。左右内容分别滚动，底部继续使用现有分类 tab。页面每次显示时重新读取分类，保留仍有效的一级选择；缓存或传入的类目已失效时回退到第一个有效根。

点击二级类目进入现有 `pages/goods/list?category_id=类目ID`。分类商品列表上方横排展示同父的二级类目，切换后显示当前类目名称/简介并重新从第 1 页加载商品；「全部」是查询一级范围的页面控件，不是写入数据库的新类目。首页快捷一级入口进入同一列表，一级范围包含自身和有效直属二级下的商品。商品数据继续调用 `POST /api/goods/clientList`，每页 20 条，触底加载；没有商品、加载失败及分类已失效分别处理。

商品点击仍跳转到 `pages/goods/detail?id=商品ID` 并调用已有 `/api/goods/clientDetail`，没有另建分类专用商品详情。分类、图片、简介及商品都来自 `mal_category` / `mal_goods`，不新增表、静态分类或演示记录；完整字段、范围规则与验证见第二十六章。

### 4.10 地址、确认订单、优惠券与支付占位

首页普通领券真实写入 mal_coupon_user，发行量、每人限领、日期和订单适用条件都由服务端校验；独立选券页区分可用与不可用并说明原因，详见优惠券独立章节第二十七章。

商品立即购买提交真实商品/库存规格/数量，购物车结算提交当前选中的购物车 ID，都进入同一 pages/order/confirm。会员地址页复用 mal_address/mal_region，确认页优先默认地址，提交后订单直接显示在后台。支付页提供 15 种方式，只弹提示，不扣款或修改已付款状态；满 88 元包邮、否则 80 元的运费规则与提交事务详见第二十八章。

### 4.11 注册

登录页「免费注册」→ `pages/register/register`（不再弹「开发中」）。

- 表单：**账号 + 密码 + 确认密码**，其他资料（手机号、性别、头像等）注册后再到「我的 → 设置」补
- 校验：账号 4-20 位字母/数字/下划线；密码至少 6 位；两次密码一致
- 提交 `POST /api/member/register {username, password}`（该接口在 `WHITE_ROUTER` 里，无需登录）
- 成功后写入 `mal_member`：`nickname` 默认取账号、`status=1`（可用）、`level=0`，密码 bcrypt 存储，**后台「用户管理 → 会员管理」立即可见**
- 注册成功 → toast「注册成功」→ 返回登录页，账号已自动填入（通过 `uni.setStorageSync('register_username')` 传递，登录页 `onShow` 读取后清除），只需再输密码
- 账号重复时后端返回「登录账号已被注册」，由 `request.js` 统一 toast

---

## 十七、数据库建表机制（新增表时必读）

后端启动时：

```
lifespan → InitializeData().init_db()
  └─ create_tables()                       # app/database/database.py
       ├─ ImportUtil.find_models(...)      # 递归扫描全项目所有 model.py
       └─ metadata.create_all()            # 只创建缺失的表，不动已有表
```

**结论：新增表不需要手写 CREATE TABLE。**

1. 在模块目录下新建 `model.py`，定义继承 `Base` 的模型类；
2. 确保 `.env.dev` 中 `AUTO_CREATE_TABLES = True`；
3. 重启后端 → 表自动出现。

生产环境把 `AUTO_CREATE_TABLES` 关掉，改走 Alembic：
```bash
uv run main.py revision --env=prod -m "add xxx table"
uv run main.py upgrade --env=prod
```

表名前缀约定：商城业务表统一用 `mal_` 前缀（如 `mal_member`、后续的 `mal_category`、`mal_goods`、`mal_order`）。

---

## 十八、AI 助手

后台登录后可从页面右下角打开 AI 助手。聊天记录保存在当前窗口的内存中，发送时携带本轮提问和此前的问答，关闭窗口或退出登录即清空。

在 `backend/env/.env.dev` 或当前环境对应的 `backend/env/.env.prod` 填写以下配置，然后重启后端。模型服务需要支持 OpenAI 兼容的 Chat Completions 和函数调用。

```dotenv
AI_ASSISTANT_BASE_URL=""       # 模型服务的 base_url，例如 https://your-provider.example/v1
AI_ASSISTANT_API_KEY=""        # 模型服务的 API Key
AI_ASSISTANT_MODEL=""          # 服务方提供的模型名称
AI_ASSISTANT_SYSTEM_PROMPT=""  # 自定义系统提示词，可留空
```

- `GET /api/ai-assistant/chat` 使用后台登录 `token` 请求头。`X-AI-Conversation` 携带按时间顺序排列的 `{role, content}` 消息数组，编码为 UTF-8 JSON 后转为无填充的 Base64URL。
- 回复使用 UTF-8 NDJSON 流。`status` 更新处理状态，`delta` 追加文字，`done` 确认回复完成，`error` 显示生成失败。带 `reset` 的 `status` 会清除本轮尚未确认的文字。鉴权及请求格式错误沿用标准 JSON 错误响应。
- 模型通过后端只读工具查询当前应用库。已接入全部 47 张应用 ORM 表，并可读取同库的 Celery 日出日落计划表（如已创建）。普通后台账号受角色和数据范围限制，超级管理员可查询全部已接入的表。
- 工具提供筛选、精确计数、分组计数和分页。模型服务接收当前对话和答复所需的查询结果，密码、令牌等敏感字段在后端排除。
- 每次请求最多携带 40 条消息和 7,500 字节的编码历史，单条提问最多 2,000 字符。窗口到达上限时可新开对话。接口返回 `Cache-Control: no-store`。

---

## 十九、变更记录

### 2026-11-05

**1）新增后台 AI 助手**

- 登录布局加入右下角浮窗。后端接入 OpenAI Python SDK 和权限受控的只读查询工具，模型参数通过后端环境配置填写。
- 验证了中文多轮对话、后台鉴权、工具调用和真实 SQL 计数。模型服务使用模拟响应，前端生产构建通过。
- 助手改用流式回复，查询时显示进度，生成文字时逐段展示。

### 2026-10-29

**1）移除「项目管理」示例模块**
- 删除 `backend/app/plugin/fea_project/`、`frontend/src/views/system/project/`、`frontend/src/api/useSystemApi/project.ts`
- 解除 `fea_celery/model.py` 对 `ProjectInfo` / `ModuleInfo` 的依赖
- 清理数据库菜单 5 条（菜单 + 4 个按钮）与 `sys_role_menu` 关联
- 遗留：`project_info` / `module_info` 两张空表未删（确认无用后可 DROP）

**2）新增「用户管理 > 会员管理」模块**
- 后端：`backend/app/api/v1/system/member/`（model / schema / service / controller）
- 接口：9 个（列表、详情、增改、删除、导出、登录、注册、个人信息、退出）
- 数据库：新表 `mal_member`，预置 3 条演示数据（`user123 / user123`）
- 后台前端：列表页 + 编辑弹窗 + 接口封装
- 菜单：`用户管理(10) > 会员管理`，按钮权限 5 个
- 依赖：新增 `openpyxl==3.1.5`
- 配置：白名单 +2 条；CORS 白名单 +2 个来源

**3）会员状态新增「禁用」**
- 状态取值变为 `1 可用 / 2 禁用 / 0 注销`
- 前端下拉三项、列表标签三色（蓝/红/灰）
- 后端 `STATUS_TEXT` 同步；登录拦截对「注销」「禁用」分别提示
- 数据库：`status` 为 int，无需改结构，仅更新列注释为 `状态 1可用 2禁用 0注销`

**4）修复客户端登录跨域（CORS 预检 400）**
- 现象：uni-app H5 调 `/api/member/login` 时，浏览器预检 `OPTIONS` 返回 400 `Disallowed CORS origin`，页面提示「网络异常，请确认后端已启动」（接口日志里能看到 OPTIONS 到达后端）
- 原因：`allow_credentials=True` 时浏览器规范不允许 `Access-Control-Allow-Origin: *`，后端把来源替换成硬编码白名单（仅 `3000` / `8100` / `8080`）；H5 一旦换端口或改用内网 IP 打开，预检就被拒
- 修复：
  - `setting.py` 新增 `CORS_ORIGIN_REGEX`（本机 + 局域网私网地址、任意端口）
  - `init_app.py` 把该正则传给 `CORSMiddleware(allow_origin_regex=...)`
  - 客户端 `api/request.js` 的失败提示改为「后端未启动或跨域被拦截」，便于以后定位
- 验证：`localhost:8080` / `localhost:8081` / `192.168.1.10:8080` 预检均 `200` 且返回正确 `Access-Control-Allow-Origin`；带 `Origin` 的真实登录返回 `code=0` 并拿到 token
- 注意：改的是后端代码，**必须重启后端**才生效

**5）修复 profile / logout 仍报 CORS（预检被登录校验拦截）**
- 现象：登录成功进入会员中心后，`/api/member/profile`、`/api/member/logout` 在浏览器报 `CORS error`，而后端日志里只有 `OPTIONS`、没有对应的 `POST`
- 原因链：
  1. 浏览器先发 `OPTIONS` 预检，预检请求**不会携带**自定义头 `token`
  2. 全局中间件 `_login_verification` 比 CORS 先执行，判定“未登录” → 直接返回 11000
  3. 这个响应是中间件自己构造的，**没有经过 CORS 中间件**，因此缺少 `Access-Control-Allow-Origin`
  4. 浏览器判定预检失败 → 真正的 POST 根本没发出去
- 修复（`app/scripts/init_app.py`）：
  - `_login_verification` 遇到 `OPTIONS` 直接放行，交给 CORS 处理
  - 调整注册顺序：CORS 改为**最后注册（最外层）**，这样任何“提前返回”的错误响应也会带跨域头，客户端能读到真实的 `code`（如 11000），而不是只显示 `CORS error`
- 验证：预检 `200` 且带 `ACAO / ACAH / ACAM`；无 token 的 POST 返回 `code=11000` 且带 `ACAO`；有效 token 的 profile / logout 均 `code=0`
- 同样需要重启后端

**6）新增「用户管理 > 收货地址」模块**
- 后端：`backend/app/api/v1/system/address/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_address`，预置 3 条演示数据（`member_id = 1`）
- 业务规则：同一会员只保留一个默认地址，保存 `is_default=1` 时自动把其他地址置 0
- 后台前端：`views/system/address/index.vue`（用户ID / 收货人两个搜索框 + 7 列表格 + 分页）+ `api/useSystemApi/address.ts`
- 菜单：`/member/address`（`用户管理 > 收货地址`），按钮权限 5 个；同步写入 `sys_menu.json`
- 验证：列表、按用户ID/收货人筛选、详情、导出 xlsx（`PK` 魔数校验）、默认地址切换、编辑、删除 全部通过
- 说明：按设计稿页面**未放操作列**，属只读视角；后端增删改接口已就绪

**7）会员管理 / 收货地址 增加响应式布局**
- 目标：窄窗口（平板 / 手机浏览器）下布局不塌、表格横向滚动
- 改动文件：
  - `views/system/member/index.vue`、`views/system/address/index.vue`：新增 `900px` / `560px` 两个断点
  - `views/system/member/MemberDialog.vue`：新增非 scoped 样式块，弹窗宽度改 `92%`
- 具体表现：
  - 搜索栏自动换行，输入框窄屏两列、手机端整行，按钮自适应占位
  - 表格列宽保持固定，容器变窄时由 `el-table` 产生**横向滚动条**，不压缩列
  - 分页允许换行、横向可滚动
  - 弹窗宽度自适应、label 收窄，避免小屏被裁切
- 验证：`npm run build` 通过
- 规范已写入 **2.1 页面响应式规范**，后续页面一律照此实现

**8）新增「用户管理 > 会员收藏」模块**
- 后端：`backend/app/api/v1/system/favorite/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_favorite`，预置 3 条演示数据（`member_id = 1`，时间对齐设计稿）
- 字段：收藏ID / 用户ID / 商品ID，**「添加时间」直接复用 `creation_date`**，不额外建字段
- 业务规则：同一会员对同一商品只能收藏一次，重复保存返回「该用户已收藏过该商品」
- 后台前端：`views/system/favorite/index.vue`（用户ID / 商品ID 两个搜索框 + 4 列表格 + 分页）+ `api/useSystemApi/favorite.ts`
- 菜单：`/member/favorite`（`用户管理 > 会员收藏`），按钮权限 5 个；同步写入 `sys_menu.json`
- 响应式：按 2.1 规范一并实现
- 验证：列表、按用户ID/商品ID筛选、详情、重复收藏拦截、新增、导出 xlsx（`PK` 魔数）、删除 全部通过

**9）修复表格排序与分页冲突（三个页面）**
- 现象：数据超过 10 条时，点「收藏ID」升序，第 1 页出现 6~15、第 2 页却仍是 11~15，数据错乱
- 原因：列上用的是 el-table 默认 `sortable`，它**只排当前页的 10 条**，属于前端排序，和分页天然冲突
- 修复（会员管理 / 收货地址 / 会员收藏 三个页面同时改）：
  - 列改为 `sortable="custom"`，表格加 `:default-sort` + `@sort-change`
  - 排序变化时重置 `page = 1`，并把 `sort_order`（`asc` / `desc`）传后端；导出也带上，保证顺序一致
  - 后端 `MemberQuery / AddressQuery / FavoriteQuery` 增加 `sort_order` 字段，`_build_stmt` 按它决定 `order_by`
- 验证（会员收藏 15 条）：
  - `desc` 第1页 → `[15…6]`
  - `asc` 第1页 → `[1…10]`，`asc` 第2页 → `[11…15]` ✅
  - 收货地址、会员管理同样验证通过
- 规范已写入 **2.2 表头排序规范**，后续页面一律用服务端排序

**10）新增「用户管理 > 会员足迹」模块**
- 后端：`backend/app/api/v1/system/footprint/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_footprint`，预置 5 条演示数据
- 字段：足迹ID / 用户ID / 商品ID，**「添加时间」复用 `creation_date`**
- 业务规则：足迹是浏览记录，**同一商品可重复**（与收藏的幂等规则相反）
- 后台前端：`views/system/footprint/index.vue`（用户ID / 商品ID 两个搜索框 + 4 列表格 + 分页，默认 **20 条/页**）+ `api/useSystemApi/footprint.ts`
- 菜单：`/member/footprint`（`用户管理 > 会员足迹`），按钮权限 5 个；同步写入 `sys_menu.json`
- 已按 2.1 响应式 + 2.2 服务端排序实现
- 验证：降序/升序翻页、按用户ID/商品ID筛选、详情、重复新增（不拦截）、导出 xlsx（`PK` 魔数）、删除 全部通过

**11）新增「用户管理 > 搜索历史」模块**
- 后端：`backend/app/api/v1/system/search_history/`（model / schema / service / controller），接口 5 个，前缀 `/api/searchHistory`
- 数据库：新表 `mal_search_history`，预置 12 条演示数据（关键字 / 时间对齐设计稿）
- 字段：搜索ID / 用户ID / 关键字，**「添加时间」复用 `creation_date`**
- 业务规则：关键字必填；同一关键字可重复搜索（不做唯一性校验）
- 后台前端：`views/system/searchHistory/index.vue`（用户ID / 关键字两个搜索框 + 4 列表格 + 分页，默认 **20 条/页**）+ `api/useSystemApi/searchHistory.ts`
- 菜单：`/member/searchHistory`（`用户管理 > 搜索历史`），按钮权限 5 个；同步写入 `sys_menu.json`
- 已按 2.1 响应式 + 2.2 服务端排序实现
- 验证：列表、升序翻页、关键字/用户ID筛选、详情、重复新增、关键字必填校验、导出 xlsx、删除 全部通过

**12）新增「用户管理 > 意见反馈」模块**
- 后端：`backend/app/api/v1/system/feedback/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_feedback`，预置 2 条演示数据（对齐设计稿）
- 字段：反馈ID / 用户名 / 手机号码 / 反馈类型 / 反馈内容 / 反馈图片 / 时间
- 设计取舍：`username`、`mobile` 存**提交时快照**，不 join 会员表，历史记录不随会员改名而变
- 图片：`images` 存逗号串，后端返回时拆成 `image_list` 数组，前端渲染缩略图 + 点击放大
- 后台前端：`views/system/feedback/index.vue`（用户名 / 反馈ID 两个搜索框 + 7 列表格 + 分页，默认 **20 条/页**）+ `api/useSystemApi/feedback.ts`
- 菜单：`/member/feedback`（`用户管理 > 意见反馈`），按钮权限 5 个；同步写入 `sys_menu.json`
- 说明：设计稿该表无排序按钮，固定 id 倒序，故未接服务端排序
- 验证：列表、用户名/反馈ID筛选、详情、新增（带图，`image_list` 正确拆分）、内容必填校验、导出 xlsx（`PK` 魔数）、删除 全部通过
- **至此「用户管理」6 个子模块全部完成**

**13）新增「商场管理 > 行政区域」模块（纯前端静态页）**
- 新增一级菜单 `商场管理`（sort=20，位于「用户管理」10 与「系统设置」60 之间）+ 子菜单 `行政区域`
- **不建表、不调接口**：数据来自 `frontend/src/views/system/region/region-data.ts`
- 页面：树形表格（省 → 市 → 区），三列「区域名称 / 区域类型 / 区域编码」，默认展开「北京市 → 市辖区」
- 数据覆盖：34 个省级行政区 + 333 个地级行政区 + 4 个直辖市的区县（用 GB/T 2260 六位编码）
- 未内置其余省份的县级数据（约 2800 条），后续可往 `CITIES` / 新增 `COUNTIES` 里补，页面无需改动
- 菜单同步写入 `sys_menu.json`
- 验证：`npm run build` 通过；菜单已入库并绑定管理员角色

**14）新增「商场管理 > 品牌制造商」模块**
- 后端：`backend/app/api/v1/system/brand/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_brand`，预置 **41 条**演示数据（ID / 名称 / 介绍 / 底价对齐设计稿）
- 字段：品牌商ID / 品牌商名称 / 品牌商图片 / 介绍 / 底价（decimal 10,2）
- 业务规则：名称必填且不允许重名；底价 Decimal → float 返回
- 图片上传：复用 `/api/file/upload`，`el-upload` 直传，支持 jpg/png/gif/webp 等
- 后台前端：`views/system/brand/index.vue`（列表 + 查找/添加/导出）+ `BrandDialog.vue`（创建/编辑）+ `api/useSystemApi/brand.ts`
- **新增删除功能**：二次确认 → 调接口 → 右上角 `ElNotification`「成功 / 删除成功」→ 刷新；当前页删空会自动回退一页
- 菜单：`/mall/brand`（`商场管理 > 品牌制造商`，sort=2），按钮权限 5 个；同步写入 `sys_menu.json`
- 已按 2.1 响应式规范实现
- 验证：41 条分页（1/2/3 页）、按 ID / 名称筛选、详情、新增、编辑、重名校验、必填校验、导出 xlsx（`PK` 魔数）、删除 全部通过

**15）删除方式统一改为「物理删除」**
- 变更：商城业务模块的 `/deleted` 接口由逻辑删除（`enabled_flag=false`）改为物理删除（`Base.delete(id, True)`）
- 范围（7 个模块）：会员管理、收货地址、会员收藏、会员足迹、搜索历史、意见反馈、品牌制造商
- 未改动：框架原有的系统模块（用户 / 角色 / 菜单 / 字典 / 部门）仍为逻辑删除
- 规范已写入 **2.3 删除规范**，后续新模块一律物理删除
- 验证：新增记录 → 调用删除 → 用 pymysql 直查 `COUNT(*)`，品牌商 `1 → 0`、意见反馈 `1 → 0`，列表回归正常（品牌 41 条、反馈 2 条）

**16）修复品牌商图片上传地址拼错**
- 现象：创建/编辑品牌商时选图片，弹「图片上传失败，请检查后端服务」
- 原因：`BrandDialog.vue` 里写成 `${getApiBaseUrl()}/api/file/upload`，而 `getApiBaseUrl()` 本身已包含 `/api`，实际请求变成 `/api/api/file/upload` → 404 → el-upload 触发 `on-error`
- 修复：改为 `${getApiBaseUrl()}/file/upload`
- 附带：`on-error` 会带上 HTTP 状态码，便于以后定位
- 验证：后端 `/api/file/upload` 直测返回 `code=0`、`url=/api/files/2026/10/30/xxx.png`；前端重新构建通过
- 说明已写入 **10.4 图片上传**（含两个同名函数的区别）

**17）新增「商场管理 > 商品类目」模块（两级树）**
- 后端：`backend/app/api/v1/system/category/`（model / schema / service / controller），接口 4 个
- 数据库：新表 `mal_category`，预置 **20 条**测试数据（一级 6 / 二级 14）
- 字段：类目ID / 类目名 / 关键字 / 级别 / 父类目ID / 图标 / 图片 / 简介
- 结构：一级类目 `parent_id=0`，二级类目挂在对应一级下；`level` 区分层级
- 业务规则：名称必填；二级必须选父类目且父类目必须是一级；同级不允许重名；有子类目时拒绝删除父类目
- 后台前端：`views/system/category/index.vue`（树形表格）+ `CategoryDialog.vue`（创建/编辑）+ `api/useSystemApi/category.ts`
- 交互：工具栏只有「添加」；点类目ID左侧箭头展开二级；父类目下拉在创建/编辑时都可用（仅二级显示）
- 图片：图标 + 图片两个上传框，复用 `/api/file/upload`
- 菜单：`/mall/category`（`商场管理 > 商品类目`，sort=3），按钮权限 4 个；同步写入 `sys_menu.json`
- 删除：物理删除，沿用二次确认 + 右上角 `ElNotification`
- 验证：全量列表（6 一级 / 14 二级）、详情、新增一级、新增二级、不选父类目拦截、同级重名拦截、编辑、父类目删除保护、子→父顺序物理删除（查库行数为 0）全部通过；`npm run build` 通过

**18）修复「二级类目改回一级后无法再选父类目」**
- 现象：把二级类目改成一级（`parent_id` 被清 0），再改回二级时，编辑弹窗里没有「父类目」下拉，无法选择 → 该数据卡死
- 原因：早期按设计稿把编辑弹窗的「父类目」隐藏了，只在创建时显示
- 修复：
  - `CategoryDialog.vue`：**创建/编辑都显示「父类目」**，仅 `level=2` 时出现；选项为一级类目并排除自己；切到一级时自动清空
  - 后端补两条校验：`父类目不能是自己`、`有子类目的一级类目不能改为二级类目`
- 验证（完整来回切换）：
  - B（二级，父 A）→ 改一级：`parent_id` 变 0 ✅
  - B 再改回二级并选父 A：`code=0`，`level=2 / parent=A` ✅（关键是这条现在能过）
  - A 改成二级（A 有子类目）：`-1 该类目下存在子类目，不能改为二级类目` ✅
  - 父类目选自己：`-1 父类目不能是自己` ✅
- 测试数据已清理，类目总数回到 20

**19）新增「商场管理 > 订单管理」模块**
- 后端：`backend/app/api/v1/system/order/`（model / schema / service / controller），接口 7 个
- 数据库：新表 `mal_order` + `mal_order_item`，预置 **5 条**演示订单（含商品明细）
- 状态字典 9 种：未付款 / 用户取消 / 系统取消 / 已付款 / 申请退款 / 已退款 / 已发货 / 用户收货 / 系统收货
- 列表筛选：用户昵称、收货人、订单编号、**下单时间范围**、订单状态，分页 20 条
- 后台前端：
  - `views/system/order/index.vue`：`el-date-picker datetimerange`（含最近一周/一月/三月快捷键、清空/确定）+ 状态下拉 + 13 列表格（窄屏横向滚动）
  - `OrderDetailDialog.vue`：详情弹窗 + **打印**（新窗口 `window.print()`）
  - `OrderActionDialog.vue`：收款 / 发货 / 退款三个弹窗
  - `api/useSystemApi/order.ts`：7 个接口
- 二级展开：订单行 `type="expand"`，展开显示商品明细小表格
- 占位接口：收款 → 「当前订单状态不支持线下收款」；发货（未填）→「参数不对」、（已填）→「订单不能确认收货」；退款 →「当前订单不能进行退款」
- 新增 `silent: true` 请求选项，避免「全局 toast + 右上角通知」重复提示
- 菜单：`/mall/order`（`商场管理 > 订单管理`，sort=4），按钮权限 6 个；同步写入 `sys_menu.json`
- 验证：5 条订单列表、按昵称/编号/状态/时间范围筛选（10-30 全天命中 4 条）、详情带明细、收款/发货/退款三种错误提示、导出 xlsx、物理删除（订单 + 明细行数均归 0）全部通过；`npm run build` 通过

**20）修复订单表「操作」列固定悬浮**
- 现象：横向滚动表格时，「操作」列钉在右侧不动、盖在其它列上，与表格脱节
- 原因：操作列加了 `fixed="right"`
- 修复：去掉 `fixed="right"`，让操作列和普通列一样随表格横向滚动；列宽调整为 `min-width="260"`
- 验证：`npm run build` 通过
- 约定已写入 **12.5**：除非确有需要，列一律**不要**固定

**21）新增「商场管理 > 售后管理」模块**
- 后端：`backend/app/api/v1/system/after_sale/`（model / schema / service / controller），接口 4 个
- 数据库：新表 `mal_after_sale`，**未写入任何演示数据**（按需求：等客户端提交退款申请后自然产生记录）
- 状态：1 待审核 / 2 待退款 / 3 已拒绝 / 4 已退款
- 后台前端：`views/system/afterSale/index.vue`（搜索 + 批量通过/拒绝 + 三个页签 + 勾选表格 + 分页）+ `api/useSystemApi/afterSale.ts`
- 交互：
  - 未勾选点批量 → `ElMessage.error('请选择至少一条记录')`
  - 勾选后 → `/audit` 批量改状态，成功弹右上角通知并刷新
  - 操作列仅「待审核」行显示「通过 / 拒绝」
- 菜单：`/mall/afterSale`（`商场管理 > 售后管理`，sort=5），按钮权限 3 个；同步写入 `sys_menu.json`
- 验证：列表为空（0 条）、待审核页签 0 条、未选记录返回「请选择至少一条记录」、不存在的 id 返回「所选记录不存在或已处理」、导出 xlsx（`PK`）通过；`npm run build` 通过

**22）行政区域从「前端写死」重构为「数据库表 + 接口」**
- 背景：客户端新增收货地址时需要省市级联，静态数据没法给客户端用
- 数据库：新表 `mal_region`（name / code / parent_id / level / sort）
- 数据迁移：解析原 `region-data.ts`，一次性导入 **470 条**（34 省 + 地级市 + 4 直辖市市辖区与区县）
- 接口：`/api/region/tree`（整棵树）、`/api/region/children`（逐级拉取）
  - **不加 AuthPermission**，并加入 `WHITE_ROUTER` 白名单 → 客户端未登录也能用
- 前端：`views/system/region/index.vue` 改为 `onMounted` 调接口，默认展开第一个省；新增 `api/useSystemApi/region.ts`
- **删除** `frontend/src/views/system/region/region-data.ts`（不再有静态数据源）
- 验证：
  - 不带 token 调 `/tree` → `code=0`，34 个省级节点，整棵树 470 个节点
  - `/children` 北京市 → 市辖区（110100）；市辖区 → 16 个区
  - `npm run build` 通过

**23）新增「商场管理 > 通用问题」模块（FAQ）**
- 后端：`backend/app/api/v1/system/faq/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_faq`（question / answer），预置 **5 条**演示数据（含截图里的运费、快递、退货、发票四问）
- 接口：`/list` **公开**并加入白名单（客户端未登录也能读），增删改仍要后台权限
- 后台前端：`views/system/faq/index.vue`（搜索 + 查找/添加/导出 + 4 列表格 + 分页）+ `FaqDialog.vue`（创建/编辑，回复为多行文本域）
- 排序：服务端排序（`sortable="custom"`），默认 id 倒序
- 校验：问题、回复都必填，分别为「问题不能为空」「回复不能为空」
- 菜单：`/mall/faq`（`商场管理 > 通用问题`，sort=6），按钮权限 5 个；同步写入 `sys_menu.json`
- 验证：不带 token 列表 5 条、按问题筛选、asc/desc 排序、详情、新增（id=7）、编辑、两条必填校验、导出 xlsx、物理删除（查库 1→0）全部通过；`npm run build` 通过

**24）新增「商场管理 > 关键词」模块**
- 后端：`backend/app/api/v1/system/keyword/`（model / schema / service / controller），接口 5 个
- 数据库：新表 `mal_keyword`（keyword / link / is_recommend / is_default），预置 **9 条**演示数据（ID、关键词、推荐/默认状态对齐截图）
- 派生字段：`is_recommend_text` / `is_default_text`（是 / 否）
- 后台前端：`views/system/keyword/index.vue`（两个搜索框 + 查找/添加/导出 + 6 列表格 + 分页）+ `KeywordDialog.vue`（4 个字段，两个下拉）
- 编辑弹窗联动：确定时按有无 `id` 走新增或更新，两个下拉分别提交 `is_recommend` / `is_default` 的 1/0
- 菜单：`/mall/keyword`（`商场管理 > 关键词`，sort=7），按钮权限 5 个；同步写入 `sys_menu.json`
- 验证：列表 9 条（状态文本正确）、按关键词筛选、asc/desc 排序、详情、新增（id=10）、编辑（改推荐/默认生效）、必填校验、导出 xlsx、物理删除（查库 1→0）全部通过；`npm run build` 通过
- **至此「商场管理」7 个子模块全部完成**

---

**25）新增「商品管理 > 商品列表」及独立商品编辑页**
- 后端新增 goods 四件套及 10 个接口；四张表已在当前数据库建立，未保留演示商品。
- 列表：筛选、服务端排序、分页、展开、详情预览、单删/批量物理删除、xlsx 导出；无勾选禁用批量删除。
- 编辑：独立隐藏路由 `/goods/edit?id=...`，图片/画廊/关键字、类目级联、品牌选择、中文 TinyMCE 富文本、规格/库存/参数弹窗。
- 原子事务保证新增默认规格库存、批量关联删除整体成功或回滚；参数操作校验商品归属。
- 菜单 JSON 与数据库已同步并绑定管理员；安装脚本可重复运行。
- 验证：TestClient + 当前 MySQL/Redis 验证列表/筛选/排序分页/新增修改/子项保存删除/归属校验/负值与空值拦截/导出 PK/删除后四表计数为零。前端生产构建通过。
- 浏览器视觉检查未完成：电脑控制授权超时。临时测试数据与会话已清理。

---

**26）修复添加/编辑入口混用，补齐「商品上架」二级菜单**
- 原因：商品列表“添加”和“编辑”都调用 `edit()` 并跳转 `/goods/edit`，仅通过是否带 id 区分，页签均显示“商品编辑”。
- 修改：列表“添加”调用 `createGoods()` → `/goods/create`；侧栏“商品上架”也进入该路由，使用 `create.vue`、路由名 `goodsCreate`、独立“商品上架”页签。
- 编辑：调用 `edit(id)` → `/goods/edit?id=...`，使用 `edit.vue`、路由名 `goodsEdit`；读取原商品资料，缺失/非法 ID 或加载失败时禁止保存。
- 复用：原表单提取为 `GoodsForm.vue`，由两个独立页面显式传入 create/edit 模式；上架模式不读取查询参数中的 id，提交时强制不带商品 id，避免覆盖已有商品。
- 接口：继续遵守项目 `/saveOrUpdate` 范式。两个新增入口共用新增请求（goods:add）；编辑提交带 id（goods:edit）。此次未新增表或重复接口。
- 菜单：`sys_menu.json` 与数据库已同步新增 `/goods/create`，管理员角色已绑定；`install_goods` 保持可重复运行。菜单新增后退出重新登录刷新缓存。
- 验证：前端生产构建通过；运行 Vue SFC 脚本配合模拟 API 验证列表按钮分流、上架不加载/覆盖旧 ID、编辑加载及提交指定 ID、无效编辑入口禁止保存、上架菜单可见。数据库另查菜单与管理员绑定；未进行浏览器视觉验收。

---

**27）商品上架调整为“先保存，再设置，最后上架”**
- 前端：`GoodsForm.vue` 首次显示“保存商品”；保存成功留在原页面并展示规格/库存/参数，按钮随后变为“商品上架”。不再在首次保存后跳转编辑页。
- 状态：首次保存为未售；后端 schema/model 默认值调整为 false，service 对新增强制未售。已存在商品的在售状态未作批量修改。
- 第二步：只使用本页首次保存返回的商品 id 更新上架，避免重复新增；规格、库存、参数编辑不自动上架，最终发布保留已保存子项与库存售价。
- 验证：Vue SFC 脚本配合模拟接口验证两步按钮对应的提交/停留/显示子项/返回列表；TestClient + 当前数据库验证首次请求即使带 true 仍未售、保存库存参数后仍未售、再次显式上架且子项保留。前端生产构建通过；测试商品与临时会话已清理。

**28）商品规格拆成「默认标准规格 / 多规格支持」两种模式**
- 现象：规格卡片只有一种形态，多规格的「添加」入口被塞进单规格表格里，无法区分默认规格与自定义规格
- 前端 `GoodsForm.vue`：
  - 新增模式切换（`el-radio-group`），规则见 **19.5**
  - 默认模式：只读展示「规格 / 标准」，**移除操作列**
  - 多规格模式：`v-if="specMode === 'multi'"` 显示「添加」按钮，表格带操作列（设置），无数据时显示「暂无数据」
  - 模式只在首次加载按数据推断一次，手动切换后不被刷新重置
- 后端 `goods/service.py`：`save_child` 对规格放开「无 id 新建」（原逻辑强制要求记录已存在）；库存仍要求已有记录，不带 id 返回「库存记录不存在」
- 验证：新建商品自动生成默认规格（规格/标准）→ 连续新增「颜色/红色」「尺码/XL」→ 改「颜色/深红」→ 详情返回 3 条规格；库存不带 id 仍报错；测试商品已删除；`npm run build` 通过
- 顺带修正 README 章节号（商品模块原为“二十”却排在“十九”之前，已重排为 19.x，后续待开发改为二十）

**29）新增「商品管理 > 商品评论」模块**
- 后端：`backend/app/api/v1/system/goods_comment/`（model / schema / service / controller），接口 4 个
- 数据库：新表 `mal_goods_comment`，预置 **12 条**演示评论（8 条未回复 / 4 条已回复，商品ID 取自现有商品 10、11）
- 回复规则：一条评论只能回复一次，重复回复返回 `订单商品已回复！`；内容为空返回 `回复内容不能为空`
- 后台前端：`views/system/goodsComment/index.vue`（用户ID/商品ID 搜索 + 查找/导出 + 7 列表格 + 分页）+ `ReplyDialog.vue`（单个多行文本框）
- 提示：成功 `成功 / 回复成功`，失败 `失败 / 订单商品已回复！`，均为右上角 `ElNotification`
- 菜单：`/goods/comment`（`商品管理 > 商品评论`，sort=4），按钮权限 4 个；同步写入 `sys_menu.json`
- 验证：列表 12 条、按用户ID（5 条）/商品ID（6 条）筛选、回复未回复评论成功、再次回复与回复已回复评论均返回「订单商品已回复！」、空内容拦截、导出 xlsx（`PK`）、物理删除（查库 1→0，测试后已还原）全部通过；`npm run build` 通过

---

### 2026-10-31

**30）新增「推广管理 > 广告管理」模块**
- 后端：`backend/app/api/v1/system/ad/`（model / schema / service / controller）；按既有范式提供列表、详情、新增/编辑、物理删除、导出，并补充广告图片上传和公开首页轮播接口。
- 数据库：`mal_ad` 已通过 ORM 创建；标题、内容、图片必填，位置仅首页（1），状态为启用（1）/不启用（0），活动链接选填；不预置广告。
- 后台前端：`views/system/ad/index.vue` + `AdDialog.vue` + `api/useSystemApi/ad.ts`；请求逐项显式 `return request({ url, method: 'POST', data })`，后端先接收 service 返回的 `data` 再通过 `HttpResponse.success(data)` 响应。
- 列表：标题/内容模糊筛选、ID 服务端排序、分页（默认 20，支持 10/20/30/40/50/100）、图片预览、导出、编辑和删除；当前页删空自动回退。
- 创建/编辑：同一个弹窗通过 `openDialog` 区分新增与回显；标题/内容/图片红星校验，位置只有首页，状态下拉可切换启用/不启用。
- 图片：广告专用 `/api/ad/upload` 复用现有文件存储，前后端均限制 3MiB（3×1024×1024 字节，含边界），支持 jpg/jpeg/png/gif/bmp/webp/svg。保存广告时还会复核文件记录、本地实际大小，避免通用上传的大文件被用于广告。
- 客户端：`POST /api/ad/banners` 为白名单公开只读接口，只返回首页启用广告；后台停用或删除后不再返回。客户端首页轮播页面后续直接接入。
- 菜单：一级「推广管理」sort=40，子菜单 `/promotion/ad`，5 个按钮权限 `ad:query/add/edit/delete/export`；数据库与 `sys_menu.json` 同步并绑定管理员。`python -m app.scripts.install_ad` 支持幂等安装。
- 验证：TestClient + 当前 MySQL/Redis 验证 23 条分页、筛选/排序、详情/新增/编辑、必填与位置/状态校验、PNG/GIF/SVG 上传、3MiB 边界及超限、通用上传大图保存拦截、合法 xlsx、未登录读取启用广告、会员 token 无法访问后台、物理删除后查库为 0。组件脚本验证创建/编辑提交、上传期间防提交、晚到上传回调隔离和分页切换；`npm run build` 通过。测试广告、上传文件与会话已清理；未进行浏览器视觉验收。

---

**31）新增「推广管理 > 优惠券管理」模块**
- 后端：`backend/app/api/v1/system/coupon/` 四件套，5 个 POST 接口（list/detail/saveOrUpdate/deleted/export），请求/响应写法与既有品牌、收藏模块一致。
- 数据库：`mal_coupon` + `mal_coupon_category` + `mal_coupon_goods` 已创建；主记录与使用范围在同一事务里保存，删除优惠券由外键级联物理删除范围行。
- 页面：`views/system/coupon/index.vue` + `CouponDialog.vue` + `CouponDetailDialog.vue`；名称/分发类型/状态筛选、服务端排序分页、详情、创建/编辑、删除及 xlsx 导出。编辑成功右上角提示“修改成功”。
- 创建/编辑：名称必填，三种分发类型；有效期可选领取相对天数或两个日期时间选择器；范围支持全场通用、多个分类、多个商品。分类取 `/category/list`，商品按名称/编号复用 `/goods/list` 搜索，选择后添加到临时表，支持去重与删除；未选择分类点击添加提示“请先选择商品分类”。
- 业务：总量 0 表示不限；相对天数 0 表示领取当日有效。绝对时间校验结束晚于开始；绝对有效期已结束时列表/导出自动显示并按已过期筛选。保存时核验分类/商品真实存在，切换范围清理旧关联。
- 菜单：`/promotion/coupon`，sort=2，5 个权限码 `coupon:query/add/edit/delete/export`；JSON 与数据库已同步，管理员已绑定。
- 示例：安装脚本 `python -m app.scripts.install_coupon` 仅在优惠券表为空时填入 6 条示例，覆盖三种分发类型、两种有效期、三种使用范围；分类和商品引用当前库真实 ID。重复执行不重复插入、不重置已有数据。
- 验证：真实接口验证 23 条分页、筛选（含 type/status=0）、排序、详情/增改/导出、必填及数值日期校验、多范围去重增删、切换清理、无效 ID 回滚、父分类覆盖子分类、过期筛选、未登录/会员 token 访问拦截、删除后主表与关联表为 0。组件逻辑检查名称必填、空选提示、添加删除去重、编辑回显及“修改成功”、商品名称/编号搜索、日期校验、分页切换通过；金额文案保留分位、不用科学计数。前端构建通过，临时测试数据与会话已清理，保留 6 条用户要求的示例；未做浏览器视觉验收。

---

**32）优惠券详情改为独立标签页，并接入领取/使用记录查询**
- 前端：列表“详情”从弹窗改为跳转 `/promotion/couponDetail?id=...`，页签“优惠券详情”；新增 `views/system/coupon/detail.vue`，删除原 `CouponDetailDialog.vue` 及其引用。
- 布局：上方按参考图显示两组六列的券信息；下方按用户ID/使用状态查询，展示用户优惠券ID、用户ID、领取时间、使用状态、订单ID、使用时间，并使用后端分页及ID排序。
- 后端：新增 `mal_coupon_user`（会员领券表）及 `POST /api/coupon/userList`；必须携带 coupon_id，沿用 `coupon:query` 权限，查询限定当前券。支持未使用/已使用/已过期，领取有效期采用每张用户券的时间快照。
- 数据：当前领取表为空，不保留模拟领取；未来客户端领券/核销操作写入该表后，后台查询直接显示结果。原 6 条优惠券定义示例保留。
- 菜单：隐藏详情菜单已同步 JSON、数据库与管理员绑定，`install_coupon` 同步维护该路由，广告菜单不受影响。
- 验证：真实接口验证 25 条领取记录分页/排序、用户及三个状态筛选、不同券隔离、有效期快照、领取/使用时间与订单ID、无效参数、未登录/会员 token 拒绝，测试后领取表为 0；组件逻辑验证路由跳转、切换券重置筛选、非法 ID 禁用查询和晚到响应隔离。前端构建通过，未做浏览器视觉验收。

---

**33）新增「推广管理 > 专题管理」模块**
- 后端：`backend/app/api/v1/system/topic/` 四件套；列表、详情、创建/编辑、单删、批量删除、导出及客户端列表/详情接口，保持既有显式请求与 service → data → HttpResponse 格式。
- 数据库：`mal_topic` + `mal_topic_goods` 已建立。文章使用 MySQL LONGTEXT（utf8mb4），支持较长图文及表情字符；专题与商品关联在同一事务中保存，商品 ID 校验真实存在并去重，保留选择顺序。
- 列表：标题/子标题筛选、按序号/时间/价格三种服务端排序、分页、封面预览、富文本详情、导出、勾选单删/批量物理删除。空选批量按钮可点击，顶部提示“请选择至少一条记录”；删除清理关联，不删除商品。
- 创建/编辑：独立 `/promotion/topicCreate` 与 `/promotion/topicEdit?id=...` 标签页，复用 TopicForm；标题、子标题、内容必填，底价非负金额，阅读量支持整数或 76.5k；封面复用文件上传，文章复用现有中文富文本编辑器。商品选择弹窗复用 `/goods/list` 的商品编号/名称搜索及分页，多页勾选、确认后去重追加、支持移除，最终与专题一并保存。
- 客户端：公开只读 `/api/topic/clientList` 和 `/clientDetail`，返回封面/文章及在售商品，不返回后台审计字段。管理端“查看”预览使用 DOMPurify 清理 HTML；客户端展示时同样应清理富文本。
- 菜单：专题管理及创建/编辑隐藏路由，五项权限 `topic:query/add/edit/delete/export` 已同步 JSON、数据库并绑定管理员。
- 测试专题：按用户补充要求保留 3 条原创图文专题“居家好物指南”“日常穿搭灵感”“出行收纳清单”，含可访问封面及真实现有商品关联。安装脚本仅空表预置，重复运行不新增或重置。
- 验证：真实接口验证 23 条分页、三排序双方向及导出同源、筛选、默认每页20、增改/关联增删去重顺序/无效商品回滚、空段落/纯脚本/未上传blob拦截、仅图片/视频文章、长文章及表情、k阅读量、未登录/会员 token 无法访问后台、公开字段与在售商品过滤、空选提示、批量原子性、物理删除后专题与关联为0且商品仍保留；3条示例的封面和文章均可访问。Vue脚本/模板编译及生产构建通过；临时测试数据、会话已清理，未做浏览器视觉验收。

**34）新增「推广管理 > 团购规则」模块**
- 后端：`backend/app/api/v1/system/group_rule/` 四件套，5 个接口（list/detail/saveOrUpdate/deleted/export）
- 数据库：新表 `mal_group_rule`（goods_id / discount / people / end_time）；状态不落库，按 `end_time` 与当前时间比较派生 `到期下线` / `进行中`
- 列表：`outerjoin mal_goods` 返回商品名称/图片/编号；`keyword` 同时匹配商品编号、商品名称、商品ID
- 页面：`views/system/groupRule/index.vue` + `GroupRuleDialog.vue`（商品ID、团购折扣、团购人数要求、过期时间），9 列表格 + 分页 20
- 菜单：`/promotion/groupRule`（sort=6），5 个权限码；已同步 `sys_menu.json` 并绑定管理员
- 安装：`python -m app.scripts.install_group_rule`，幂等；空表时写入 4 条演示规则（引用现有商品 10、11）
- 修复脚手架细节：查询结果经 `default_serialize` 后 `datetime` 变字符串，比较前需 `_to_datetime()` 还原，否则 `str < datetime` 报错
- 验证：列表 4 条（名称/图片联表正确、状态派生正确）、按商品名称与商品ID筛选、新增（折扣 12.5/人数 3）、编辑（改 8/5 后状态变到期下线）、商品不存在与缺结束时间拦截、导出 xlsx（`PK`）、物理删除（查库 1→0）全部通过；`npm run build` 通过

**35）新增「推广管理 > 团购活动」模块**
- 后端：`backend/app/api/v1/system/group_activity/` 四件套，2 个接口（list/export），后台只读
- 数据库：**两张表** `mal_group_activity`（活动主表：rule_id / order_id / member_id / participants / discount / people / share_image / start_time / end_time）+ `mal_group_activity_member`（参与记录：activity_id / order_id / member_id / join_time）
- 列表：每条活动挂 `members` 数组，前端用 `type="expand"` 展开显示「订单ID / 用户ID」子表
- 页面：`views/system/groupActivity/index.vue`（规则ID 搜索 + 查找/导出 + 8 列表格 + 展开行 + 分页 20），无增删改
- 菜单：`/promotion/groupActivity`（sort=7），2 个权限码；已同步 `sys_menu.json` 并绑定管理员
- 安装：`python -m app.scripts.install_group_activity`，幂等；空表时写入 3 条演示活动（成员数 2 / 1 / 0）
- 验证：列表 3 条（成员数组分别 2/1/0，折扣与规则快照一致）、按规则ID筛选（规则1 → 2 条）、不存在的规则 → 0、导出 xlsx（`PK`）、未登录被中间件拦截，全部通过；`npm run build` 通过
- 顺手修掉后续待开发清单里重复的编号（原有两个「3.」）

**36）客户端开始落地：底部导航 + 「我的」个人中心**
- 页面：新增 `pages/profile/index.vue`（我的）、`pages/category/index.vue`、`pages/cart/index.vue`（占位），`pages/index/index.vue` 改为「精选」占位
- 导航：自定义组件 `components/tab-bar/tab-bar.vue`（easycom 自动引入），四个 tab：精选 / 分类 / 购物车 / 我的；选中态为红圆底白图标，未选中为灰色线性图标；用 `uni.redirectTo` 切换
- 图标：`static/icons/` 新增 18 个 SVG（tab 8 个、页面内 10 个），颜色烘焙在文件里
- 我的页面：红色渐变头图 + 头像/昵称（`/api/member/profile`，带本地缓存兜底）+ 订单四入口 + 优惠券三入口 + 收藏/地址/服务中心 + 广告位 + 退出登录
- 登录成功后跳转由 `/pages/index/index` 改为 `/pages/profile/index`（第 37 条已改回首页：登录后默认进「精选」）
- 未做的入口统一 `uni.showToast({ title: 'xx功能开发中' })`，等对应页面完成再逐个接
- 验证：用 `@vue/compiler-sfc` 对 6 个 `.vue` 做 parse / compileScript / compileTemplate 校验全部通过；`pages.json` JSON 结构校验通过（5 个页面登记齐全）

**37）客户端首页「精选」+ 搜索 + 品牌 / 团购 / 专题子页面**
- 后端新增 8 个 C 端只读接口（均免 `AuthPermission`，其中 6 个 + 分类加入 `WHITE_ROUTER`）：
  - `/api/goods/clientList`（keyword 同时匹配名称与 keywords 字段，scene=new/hot 排序）、`/api/goods/clientDetail`
  - `/api/brand/clientList`、`/api/brand/clientDetail`
  - `/api/category/clientList`、`/api/coupon/clientList`、`/api/groupRule/clientList`
- 搜索历史（写已有 `mal_search_history` 表）新增 3 个会员接口：`myList` / `add` / `clear`，同一关键字先删后插只保留最新一条
- 客户端新增 8 个页面 + 3 个组件：
  - `pages/index/index`（精选首页：搜索框、轮播、快捷分类、优惠券、团购、品牌、新品、人气、专题）
  - `pages/search/index`（历史搜索 + 清空 + 结果）
  - `pages/goods/list`（新品/人气/分类/品牌/搜索共用）、`pages/goods/detail`（占位）
  - `pages/brand/list`、`pages/brand/detail`、`pages/group/list`、`pages/topic/list`、`pages/topic/detail`
  - 组件：`nav-header`（‹ 返回）、`goods-row`、`goods-cell`
- 各级「更多 xxx」与卡片点击均已接通跳转；商品详情页先展示真实信息 + 占位提示
- 验证：6 个新接口免登录返回正常（商品 2 条、品牌 39 条、优惠券 6 张、团购 2 条、专题 2 个、分类 5 个）；搜索按名称/关键字均命中；搜索历史 记录→去重→清空 全通过；未登录访问历史返回 11000；17 个 `.vue` 通过 `@vue/compiler-sfc` 校验，`pages.json` 13 个页面 JSON 合法

**38）修复客户端首页白屏**
- 现象：登录后进入首页整页空白，连搜索框和底部导航都不显示
- 原因：首页用 `reactive({ banners, categories … })` 存数据，但模板里直接写 `banners.length`。`<script setup>` 不会自动把 `state` 的字段暴露给模板，`banners` 实际是 `undefined`，渲染时 `undefined.length` 抛错 → 组件渲染中断 → 白屏
- 修复：`const { banners, categories, coupons, groups, brands, newGoods, hotGoods, topics } = toRefs(state)`，模板继续用简写，数据仍写回 `state`
- 排查范围：逐个核对了其余 8 个页面（搜索/商品列表/商品详情/品牌/团购/专题/我的），模板变量均为 `ref`/`computed`/`const`，无同类问题
- 验证：17 个 `.vue` 重新通过 `@vue/compiler-sfc` 校验

**39）修复客户端图片不显示**
- 现象：后台为品牌 / 商品 / 专题 / 分类上传的图片，在客户端精选页全部裂图
- 原因：数据库存的是相对路径 `/api/files/2026/10/30/xxx.png`，客户端 H5 直接当 `src` 用，浏览器会去前端 dev server 找 → 404
- 修复：新增 `api/url.js`
  - `imageUrl(path)`：http(s)/data/blob 原样返回，`/` 开头拼 `API_HOST`，其余补 `/`
  - `rewriteHtmlImages(html)`：富文本里的 `src="/api/...`（单双引号都兼容）批量补全后端域名
- 接入范围：首页（轮播/分类/团购/品牌/专题）、`goods-cell`、`goods-row`、商品详情、品牌列表/详情、团购列表、专题列表/详情（含富文本）、个人中心头像
- 验证：直接 `GET /api/files/2026/10/30/xxx.png` 返回 `200 image/png`（无需 token，`/api/file` 前缀已豁免登录）；17 个 `.vue` 通过 `@vue/compiler-sfc` 校验

**40）客户端商品详情与会员购物车接入真实数据库**
- 页面：重做 `pages/goods/detail.vue`，接入图集预览、售价/简介/富文本、商品属性弹层、真实库存规格选择、数量输入及购物车角标；重做 `pages/cart/index.vue`，接入单选/全选、编辑数量、单删/批量删除、空车/未登录/失败重试和实时合计。
- 后端：新增 `cart/` 四件套、`CartRouter` 注册及六个显式 POST 接口；新增 `mal_cart` 表，会员+库存规格唯一，会员删除级联清理，商品/库存删除后保留可删除的失效条目。`goods/clientDetail` 补 `products`、`is_on_sale`、`stock`、`cart_available`，继续复用既有 `mal_goods_product` 库存表。
- 规则：会员身份来自服务端 token；拒绝后台 token、伪造会员/价格字段与跨会员操作；同规格累加、数量 1～999 且不超过实时库存，普通勾选持久化，失效商品不参与合计；加购不预占库存、不建订单，立即购买/结算支付仍待实现，运费未预设。
- 初始化：`backend/app/scripts/install_cart.py` 只调用 `create_tables()` 创建缺失表，购物车初始为空，不写种子记录或改动原有商品、库存、会员。
- 验证：真实数据库 TestClient 共 47 次 API 请求通过，覆盖详情字段、同规格合并、两会员隔离、伪造字段、非法数量、库存变化、实时价格、持久化勾选、并发累加、会员禁用及商品/库存物理删除；接口测试临时会员/商品/购物车/token 已清理。SFC 编译与模拟交互通过，HBuilderX 5.33 的 H5 production build 通过并在导航/安全区修正后复验通过。390px 宽浏览器完成临时会员登录、图集/富文本展示、标准规格选数量 2 加购、角标 2、属性「纯棉 / 中国」、购物车 ×2 与总计 39.80、取消全选后合计 0.00、编辑步进和删除选择的检查；下单支付未实现。

**41）购物车编辑删除改为右侧展开，并支持侧滑**
- 页面：`pages/cart/index.vue` 将行内小号删除文字改为右侧 76px 宽的红色矩形删除区；编辑时每行展开并保留勾选、数量修改，完成时收起，底部批量删除保留。
- 交互：普通模式左滑展开、右滑或点击展开行收起，一次只开一行；区分横向手势和竖向滚动，多指及取消手势会回到稳定状态，避免滑动后误触商品详情。H5 额外支持鼠标拖动，并兼容 uni-app 包装后不带 `button` / `cancelable` 字段的事件；页面隐藏/销毁时重置手势并移除鼠标监听。
- 接口：沿用现有会员购物车接口、删除确认和物理删除逻辑，本次没有新增接口或修改数据库结构。
- 验证：SFC 脚本/模板/样式、触摸及鼠标交互逻辑校验通过，H5 production build 通过。390px 浏览器实测编辑展开/完成收起、普通模式左拖展开与右拖收起且不误进详情；320px 窄屏无横向溢出。临时预览会员、购物车和会话检查后清理，未改动原有商品或库存。

### 2026-11-01

**42）客户端分类页与分类商品列表对接已有类目和商品**
- 数据与接口：复用 `mal_category` / `mal_goods`；新增公开只读 `/api/category/clientTree`，复用 `Category.get_all()`，返回完整有效两级树和图标/图片/简介，过滤孤儿及已删除类目，裁剪后台字段。原首页 `/category/clientList` 的最多 10 个一级入口契约保留。`goods/clientList` 的一级筛选包含自身及有效二级，二级仅自身，无效分类返回空；零/负数分类 ID 被契约拒绝。
- 页面：分类页左侧为一级类目，右侧为当前一级的 `image`、简介和二级 `icon` 格子，缺图使用占位；二级 `image` 不代替图标。分类商品列表复用既有 `pages/goods/list` 与商品接口，提供同父类目横向切换、当前分类介绍、每页 20 条触底加载；「全部」仅是一级范围查询控件，商品仍进入同一个商品详情页。
- 验证：真实数据库接口检查共 29 次请求通过，覆盖公开字段、完整树超过首页 10 项、孤儿/已删除节点、一级/二级商品范围、分页和下一页、无效 ID、brand/keyword/scene 兼容及旧首页/后台权限保留。临时 15 个根类目、有效/已删除/孤儿子类目及 29 个商品均已清理，不新增表或保留测试示例。HBuilderX 5.33 的 H5 production build 通过；390px 浏览器以既有业务数据只读确认一级图片、父子分类切换、横向标签、无商品空态、父「全部」范围及原商品详情跳转。未新建浏览器预览数据，二级 icon 为空时正确使用文字占位，没有使用 image 代替图标。

**43）会员地址、首页领券、订单确认及支付方式占位**
- 已实现：本人地址维护/默认/地区验证和后台只读；首页普通领券及发行量/限领/有效期；订单可用不可用券与真实范围门槛；立即购买和购物车进入统一确认页；服务端运费、报价、幂等提交及库存/订单/用券/购物车原子事务；支付页 15 种方式仅弹窗。
- 数据：继续使用既有地址/地区/券/持券/商品/库存/订单/明细表；install_checkout.py 已幂等补订单快照和请求号列/索引，不重置旧业务数据。
- 业务流程与实现原理：优惠券单独作为第二十七章；地址、确认订单和支付占位为第二十八章。普通 claim 不冒充注册赠券/兑换码，支付弹窗不改已付款，未实现半小时自动取消及后台真实收款/发货/退款。
- 验证：地址 55 次、领取/订单 66 次真实接口共 **121 次通过**，覆盖限领/发行并发、优惠范围与门槛、报价变化回滚、幂等、库存竞争、后台同步及一次性报价防重放；迁移、SFC/模拟交互、HBuilderX 5.33 的 H5 production build 和浏览器真实操作流通过。接口及浏览器临时数据、会话、报价与脚本已清理，SQL 复核无残留，临时预览服务已停止，逐项结果见 28.8。

**44）个人信息设置与个人中心各入口接通现有数据**
- 已实现：右上角设置入口、本人头像/昵称/性别/手机号与退出；订单/券真实数量角标、本人订单列表/详情、本人券三状态、收藏读取与取消、商品收藏入口、服务中心/意见反馈/常见问题。
- 数据与接口：复用既有会员、文件、订单/明细、持券、收藏、反馈、FAQ 和数据字典表；新增严格本人接口，不新增业务表、迁移或公开白名单。密码设置只展示禁用占位；手机号按用户确认方案校验当前登录密码，未伪造短信验证。
- 流程说明：新增第二十九章，列出字段、状态分组、分页策略、身份隔离、真实保存与尚未接入的边界；后续待办顺延为第三十章。
- 验证：会员设置 **59 次**与个人中心列表 **56 次**真实请求分别通过，共 **115 次**；子页 SFC/模拟交互、旧账号鉴权响应隔离 3 项模拟及 390px 浏览器完整操作通过，覆盖资料真实保存、订单各分组/支付入口、三状态券、收藏、服务/反馈/FAQ 和退出。HBuilderX 5.33 全量 29 路由 H5 production build 及末尾合并后的最终重建均通过。本轮接口及浏览器夹具、上传文件、会话和临时脚本均已清理，数据库 10 项复核无残留，见 29.8。

---

**45）后台首页改为商城统计概览（2026-11-02）**
- 页面：保留「你好，当前后台用户」、时段问候、「欢迎回来」和日期/每秒更新的时间；按用户最终确认保留原有圆角白卡、渐变图标、悬浮效果和「数值在上、名称在下」的卡片风格，只将四项内容换为用户、商品、货品、订单真实总量；移除旧系统信息、快捷操作、通知和待办演示区。沿用原 Element 栅格，桌面四列、中等宽度两列、手机一列。
- 登录文案：登录页右侧标题改为「后台商场管理系统」，左侧说明标题改为「后台商场管理平台」；只调整这两处展示文案，不修改全局主题名称或其他登录行为。
- 数据：复用原 `useStatisticsApi().countStatistic()`，补齐 `POST /api/statistic/countStatistic {}`；只读取既有会员、商品、货品和订单表，不新增表或菜单。用户指商城会员，货品指 SKU 条目数而非库存件数，订单包含所有状态。
- 验证：12 次真实接口请求通过，四项计数与现库独立 SQL 一致；普通后台权限分支、会员/无效会话和非法参数检查通过。最终 production build 及浏览器 1920px 四列、900px 两列、390px 单列与原圆角/渐变卡片样式检查通过，两处登录标题已确认；临时预览会话、状态文件和构建日志已清理。详见第三十章。

**46）修复「已领取优惠券不跟随后台改期过期」**
- 现象：后台把某张券的结束时间改成已过去（立刻过期），客户端「我的优惠券」里已领取的那张仍显示未使用
- 原因：领取时把券的 start_time/end_time 复制成了持券快照，`_client_user_row` 只判断快照是否过期，完全不看券定义当前时间；后台改期只影响定义行，持券行不动 → 永远停在未使用（直到快照自己到期）
- 修复（统一口径，三处一起改）：
  - `CouponService._validity_window()`：绝对有效期券（time_type=1）用**券定义当前**起止时间，相对天数券（time_type=0）用领取快照
  - `CouponService._effective_status()`：已使用优先；券删除/下架/手动置过期 → 已过期；有效期已过 → 已过期
  - 客户端 `myList`、订单 `mySummary` 角标、下单校验 `_use_reason` 全部改走同一套判断
  - 后台 `CouponUser._status_expression()` 改为 JOIN 券定义的条件表达式（下架/定义过期/快照过期），使后台「领取记录」筛选与客户端一致
- 效果：后台改结束时间 → 已领取的券立刻进「已过期」；后台延长 → 跟着延长；订单用掉的券始终在「已使用」
- 验证（真实库，改库后已还原）：
  - 持券改期前：未使用含该券 ✅ / 已过期不包含
  - 后台把结束时间改到 1 小时前：未使用 3→2 条、已过期 10→11 条，该券显示 `2 已过期`，有效期同步为新的定义时间
  - 个人中心角标同步为 `{'unused': 2, 'used': 0, 'expired': 11}`
  - 后台领取记录：status=0 查不到该券、status=2 查得到
  - 还原定义后回到未使用 ✅
  - 已使用分支：临时置 status=1 后该券出现在「已使用」（含订单ID和使用时间），角标 used=1，还原后恢复

**47）修复后台「个人中心」保存资料 / 更换头像失败**
- 现象：个人中心点「更新个人信息」「更换头像」都报错；头像弹窗里主图和预览都是裂图
- 原因（实测复现）：
  1. **头像过大**：`sys_user.avatar` 是 MySQL `TEXT`（上限 64KB），cropper 输出的 base64 JPEG 动辄 100KB+ → `(1406) Data too long for column 'avatar'` → 接口 500
  2. **局部更新写空**：`UserIn.status / user_type / dept_id` 未传时为 `None`，服务端直接写库 → `(1048) Column 'status' cannot be null`（400「数据与数据库约束冲突」）
  3. **密码会被重置**：`UserIn.password` 默认值是加密后的 123456，不传密码时更新分支会当成新密码重新哈希
  4. 没有头像时 `<img src="">` 渲染成裂图，cropper 在没有图片的情况下点「更换」会取到空画布
- 修复：
  - 后端 `user/schema.py`：`password` 默认改为 `None`（不传=不改密码）
  - 后端 `user/service.py`：新增时补 `status=1 / user_type=20`；更新时对未提交的 `username/nickname/avatar/tags/email/remarks/status/user_type/dept_id` **沿用原值**
  - 后端 `user/model.py` + `app/scripts/install_personal_avatar.py`：`avatar` 改为 `MEDIUMTEXT`（幂等 ALTER，已在本库执行）
  - 后端 `user/service.py#update_user_avatar`：校验格式（data:image / 绝对路径 / http(s)）与大小（≤800KB）
  - 后端 `user/controller.py`：本人可改自己的资料和头像，改他人仍需 `user:edit` 权限
  - 前端 `components/seePictures/index.vue`：空头像用 1x1 透明占位、裁剪输出固定 **200x200 JPEG(0.9)**、未选图点「更换」给出提示、切换图片时释放 blob URL、关闭时销毁 cropper；预览容器交给 cropper 自身渲染
  - 前端 `views/system/personal/index.vue`：保存只提交个人字段（不再回传 roles/status/password 等），失败不再弹“更新成功”
- 验证：局部保存 `code=0` 且 `status/user_type/avatar/密码哈希` 均未被改动；改昵称/签名/标签/邮箱生效；300KB 头像保存成功（长度 300023）；>800KB 返回「头像图片过大」；`javascript:` 返回「头像格式不支持」；全部测试数据已还原（nickname=admin、remarks=超级管理员、tags=['ymmt']、头像为空）；`npm run build` 通过

**48）新增「统计报表」一级菜单（用户 / 订单 / 商品趋势）**
- 后端：`statistic/` 扩展 3 个接口 `userChart / orderChart / goodsChart`，复用既有 `mal_member` / `mal_order` / `mal_order_item`，**不新建表**
  - `Statistic.user_daily / order_daily / goods_daily`：按 `DATE(creation_date|order_time)` 分组聚合
  - 客单价在服务层算（订单总额 ÷ 订单量），`days` 参数 0=全部、>0=最近 N 天（0~3650）
- 前端：新增 `components/statisticChart`（ECharts 封装）+ 三个页面 + `useStatisticsApi` 三个方法
  - 用户统计：柱状图「用户增长数」
  - 订单统计：折线「订单量 / 下单用户 / 订单总额 / 客单价」
  - 商品统计：折线「订单量 / 下单货品数量 / 下单货品总额」
  - 每页支持近 7/30/90 天与全部切换，无数据显示空态
- 菜单：`/statistics`（sort=50）+ 三个子页，`install_statistics.py` 幂等安装并绑定管理员；已同步 `sys_menu.json`
- 验证：真实库接口返回 `userChart` 2026-10-29 → 3 人；`orderChart` 2026-11-02 → 1 单 / 买家 1 / 总额 696 / 客单价 696；`goodsChart` 同日 → 货品 3 件 / 696 元；`days=-1` 与 `99999` 返回参数错误；未登录返回 11000；菜单接口返回 `/statistics` 根节点与三个子页且组件路径正确；`npm run build` 通过（echarts 单独 chunk 1.0MB / gzip 336KB）

**49）客户端新增注册功能（账号 + 密码）**
- 页面：新增 `Mall_Front‑end_Page/pages/register/register.vue`（沿用登录页视觉：白色底、红按钮 `#d9534f`、`nav-header` 返回）；登录页「免费注册」由 toast 改为跳转
- 交互：账号（4-20 位字母/数字/下划线）+ 密码（≥6 位）+ 确认密码；成功后 toast「注册成功」并返回登录页，账号自动填入（`register_username` 本地存储传递，登录页 `onShow` 读取后清除）
- 后端：直接复用已有 `POST /api/member/register`（`WHITE_ROUTER` 白名单，无需登录）；写入 `mal_member`，`nickname` 默认取账号、`status=1`、`level=0`，密码 bcrypt
- 配置：`pages.json` 注册页排在登录页之后，`navigationStyle: custom`
- 验证（真实库，测试数据已清理）：
  - 注册 `regtest54591` → `code=0 注册成功`
  - 同账号重复注册 → `-1 登录账号已被注册`
  - 新账号登录 → `code=0`；`/api/member/profile` 返回 `username=regtest54591 / nickname=regtest54591 / status=1`
  - 后台会员列表按账号搜索命中 1 条，状态「可用」
  - 清理后 `mal_member` 中该账号数量为 0
  - 客户端 34 个 `.vue` 通过 `@vue/compiler-sfc` 校验；`pages.json` 30 个页面合法

---

## 十九、商品管理模块（列表 / 上架 / 编辑 / 评论）

### 19.1 数据模型

四表均继承 Base；金额采用 Numeric(12,2)，详情返回前转为 float。

| 表 | 主要字段 |
|---|---|
| `mal_goods` | name、goods_sn（可空唯一）、market_price、retail_price、is_new/is_hot/is_on_sale、image/share_image、gallery/keywords（JSON）、unit、category_id/brand_id、brief、detail（HTML） |
| `mal_goods_specification` | goods_id、name、value、image |
| `mal_goods_product` | goods_id、specification、price、quantity、image |
| `mal_goods_attribute` | goods_id、name、value |

后三表通过外键关联商品，并支持 ON DELETE CASCADE。服务层在同一数据库事务中物理删除关联行及商品（直接 DELETE，避免 Base.execute 每条单独提交造成半删除）。订单历史快照不变。

### 19.2 接口

统一 POST `/api/goods`，仅后台登录可用。

| 路径 | 权限 | 说明 |
|---|---|---|
| `/list` | goods:query | goods_id 精确，goods_sn/name 模糊；page/pageSize/sort_order |
| `/detail` | goods:query | `{id}`；含 specifications/products/attributes |
| `/saveOrUpdate` | 新增 goods:add，修改 goods:edit | 完整基本信息；返回 id |
| `/deleted`、`/batchDeleted` | goods:delete | `{id}` 或 `{ids:[...]}`；原子物理删除 |
| `/export` | goods:export | 同列表筛选排序，返回 xlsx |
| `/specification/save` | goods:edit | id/goods_id/name/value/image |
| `/product/save` | goods:edit | id/goods_id/price/quantity/image |
| `/attribute/save` | goods:edit | goods_id/name/value，带 id 修改 |
| `/attribute/deleted` | goods:edit | id/goods_id，物理删除 |

### 19.3 保存行为与页面

**保存 → 设置 → 上架**：新增页初始按钮为“保存商品”，首次请求不带 id。后端强制新商品 `is_on_sale=false`（即使首次提交 true 也不会直接上架）；前端保存服务端返回的 id，并显示规格、库存、参数区域，底部按钮改为“商品上架”。子项设置立即持久化，但不会改变未售状态。第二步提交同一 id 与 `is_on_sale=true`，成功后回到列表。新增流程中的“是否在售”只读，由最后的上架操作控制；已有商品编辑页仍可调整在售状态。保存后取消离开会保留未售商品，可从列表编辑继续处理。

| 入口 | 路由 / 页签 | 页面与行为 |
|---|---|---|
| 商品列表 → 添加 | `/goods/create` / 商品上架 | `create.vue`，空白新增表单；与二级菜单共用同一页面 |
| 商品管理 → 商品上架 | `/goods/create` / 商品上架 | 同上；提交不带 id，调用 `/api/goods/saveOrUpdate` 新增商品 |
| 商品列表 → 编辑 | `/goods/edit?id=商品ID` / 商品编辑 | `edit.vue`，调用详情接口回显；提交携带 id 更新商品 |

两页复用 `GoodsForm.vue` 的字段、图片上传、富文本和子项编辑逻辑，模式由页面显式指定。商品上架页关闭页面缓存，重新进入时初始化空表单；编辑页面必须传入有效商品 ID，不会退回新增模式。新增采用两步流程：首次点击“保存商品”后留在当前商品上架页，显示规格、库存和参数设置；配置完成后点击“商品上架”，更新同一商品为在售并返回商品列表。

- 商品列表每页条数支持 **10 / 20 / 30 / 40 / 50 / 100**，默认 **20 条/页**；切换条数时回到第一页，按新的 `pageSize` 请求后端分页数据。
- 新商品先保存基本信息为未售，自动建立一条「规格/标准」及库存（数量 0），随后在当前上架页显示并设置子项。
- **商品规格有两种模式（19.5）**：「默认标准规格」只读展示自动生成的「规格 / 标准」；「多规格支持」列出默认规格之外的规格，可点「添加」新增。多规格只做规格行的增改，不做笛卡尔积 SKU 生成。
- 规格、库存、参数弹窗确认立即调用对应 API；关闭弹窗不写库。底部取消返回列表，不撤销已经确认保存的子项。
- 库存售价同步商品当前价格；基本信息保存不会覆盖库存刚更新的价格。价格非负，库存为非负整数。
- 参数名和值必填，商品名称去空格后必填；重复编号、无效分类品牌、越商品修改子项均拦截。
- 类目使用 `/category/list` 全量接口组装树；品牌使用 `/brand/list` 分页获取全部选项。非管理员需另具 category:query/brand:query 以加载选项。
- 图片和画廊复用 `/file/upload`（10MB 前端限制，格式受后端上传白名单约束）；富文本支持图片/文件链接/媒体/表格/源码/预览/全屏。
- TinyMCE 自托管资源由 `scripts/prepare-tinymce.mjs` 在 dev/build 前复制，中文包本地加载；采用 `license_key=gpl` 开源许可配置，商业许可项目应替换为相应授权配置。接入参考：https://www.tiny.cloud/docs/tinymce/latest/vue-ref/
- 列表 HTML 预览使用 DOMPurify 清理，后续客户端展示 HTML 时同样需要安全清理。
- 页面使用 900px/560px 断点；宽表横向滚动，无 fixed 操作列。

### 19.4 安装与验证

当前库已执行安装。其他已有数据库在 backend 下运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_goods
```

该脚本只创建缺失表并幂等安装商品菜单/管理员绑定，不重置已有数据。新库菜单同时收录于 sys_menu.json。更新后重启后端并退出重新登录以刷新菜单缓存。

前端安装沿用现有依赖组合：`npm install --legacy-peer-deps`，再 `npm run build`。现有 Pinia 与持久化插件的 peer 版本约束冲突未在本模块升级处理。

商品管理下的商品列表、商品上架、商品评论三个二级模块均已实现，商品评论详见 19.6。客户端商品评价提交接口与页面尚未接入，见「三十、后续待开发」。

### 19.5 商品规格：默认标准规格 / 多规格支持

商品规格卡片顶部有模式切换（`el-radio-group`），两种模式**共用同一批 `mal_goods_specification` 数据**，只是展示与可操作性不同：

| 模式 | 判定 | 展示 | 操作 |
|---|---|---|---|
| 默认标准规格 | 无自定义规格时默认选中 | 只展示后端自动生成的「规格 / 标准」，**无操作列** | 只读 |
| 多规格支持 | 存在自定义规格时自动选中 | 只展示**除默认规格之外**的行；无数据时显示「暂无数据」 | 「添加」+ 操作列「设置」 |

- 判定规则：`name === '规格' && value === '标准'` 视为默认规格（后端 `GoodsService.save_or_update` 新建商品时写入）。
- 模式只在**首次加载**时按数据推断一次（`specModeInited`），之后用户手动切换不会被刷新重置。
- 「添加」走 `openChild('specification')`（不带 row），弹窗提交时无 `id` → 后端按新增处理。
- 后端 `save_child` 已放开：规格允许不带 `id` 新建；库存（product）仍要求记录已存在，避免出现无规格的库存行。

### 19.6 商品评论

**数据模型**：`mal_goods_comment`（模型类 `GoodsComment`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 评论ID |
| member_id / username | — | 用户ID / 昵称 |
| goods_id | bigint | 商品ID（对应 `mal_goods.id`） |
| score | int | 打分 1-5 |
| content | text | 评论内容 |
| images | text | 评论图片，多张用英文逗号分隔 |
| comment_time | datetime | 评论时间 |
| reply_content / reply_time | — | 商家回复内容 / 回复时间 |

派生字段：`image_list`（图片数组）、`replied`（是否已回复）。

**接口**：前缀 `/api/goodsComment`

| # | 路径 | 权限码 | 说明 |
|---|---|---|---|
| 1 | `/list` | `goodsComment:query` | 分页 + `member_id` / `goods_id` 精确筛选 |
| 2 | `/reply` | `goodsComment:reply` | 回复评论，入参 `{comment_id, content}` |
| 3 | `/deleted` | `goodsComment:delete` | 物理删除 |
| 4 | `/export` | `goodsComment:export` | 导出 xlsx |

**回复规则（与客户端参考实现一致）**：
- 回复内容为空 → `回复内容不能为空`
- **一条评论只能回复一次**：已回复再调 → `订单商品已回复！`
- 成功 → 返回 `msg=回复成功`

**页面**：`views/system/goodsComment/index.vue` + `ReplyDialog.vue` + `api/useSystemApi/goodsComment.ts`

- 搜索：用户ID、商品ID；按钮：查找、导出
- 表格：用户ID / 商品ID / 打分 / 评论内容 / 评论图片 / 时间 / 操作（回复、删除）
- 评论图片用 `el-image` 缩略图，支持点击预览，加载失败显示「加载失败」
- 回复弹窗只有一个「回复内容」多行文本框；确定后成功弹右上角「成功 / 回复成功」，失败弹「失败 / 订单商品已回复！」
- 分页默认 20 条

**数据来源**：客户端（会员）对已购商品发表评价后写入，后台只做查看、回复、删除。

---

## 二十、广告管理模块

### 20.1 模块定位与数据模型

位于「推广管理 → 广告管理」。后台维护首页轮播图片及活动链接；客户端通过公开接口读取启用的广告。推广管理当前已实现广告管理、优惠券管理和专题管理，其他推广功能后续按需求开发。

表名：`mal_ad`（模型类 `Ad`，位于 `backend/app/api/v1/system/ad/model.py`），继承 `Base`，启动自动创建缺失表。

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 广告ID，自增主键 |
| title | varchar(128) | 广告标题，必填 |
| content | text | 广告内容，必填，接口最多 1000 字符 |
| image | varchar(1000) | 已上传广告图片 URL，必填 |
| position | int | 位置：1 首页，当前仅此选项 |
| link | varchar(1000) | 活动链接，选填，可编辑清空 |
| status | int | 1 启用 / 0 不启用，默认启用 |
| — | — | Base 公共字段：creation_date / created_by / updation_date / updated_by / enabled_flag / trace_id |

`status` 控制广告是否投放，与公共字段 `enabled_flag` 不同。`AdService._decorate` 统一补充 `position_name`（首页）、`status_name`（启用/不启用），前端直接展示。

### 20.2 接口清单

统一前缀 `/api/ad`，全部采用 POST。除 `banners` 外，需后台登录及对应权限。

| # | 路径 | 权限码 | 说明 |
|---|---|---|---|
| 1 | `/list` | `ad:query` | title/content 模糊筛选，sort_order asc/desc，page/pageSize 放 body |
| 2 | `/detail` | `ad:query` | `{id}`，编辑弹窗回显，check_data_scope=False |
| 3 | `/saveOrUpdate` | `ad:add` / `ad:edit` | 无 id 新增、有 id 更新；返回 `{id}` |
| 4 | `/deleted` | `ad:delete` | `{id}`，`Ad.delete(id, True)` 物理删除 |
| 5 | `/export` | `ad:export` | 同列表筛选与排序、不分页，xlsx 文件流 |
| 6 | `/upload` | `ad:add` / `ad:edit` | multipart 表单 file，3MiB 内图片，返回标准文件信息（id/url/size 等） |
| 7 | `/banners` | 无（公开） | `{position:1}` 或 `{}`，只返回启用且未删除的首页广告 |

列表返回 `data = {rows, rowTotal, page, pageSize, pageTotal}`，默认 20 条/页、ID 倒序。导出含广告ID、标题、内容、图片、位置、活动链接、是否启用；响应使用 XLSX MIME 与 UTF-8 文件名。

### 20.3 业务规则

1. 标题、内容、图片不能为空或全空格；新建和更新均在 service 层复核。不存在的记录不能编辑或删除；广告标题允许重复。
2. 广告位置仅支持 `position=1`，是否启用仅支持 `status=1/0`；其他值通过契约校验拦截。
3. 创建和编辑使用同一个弹窗：点击确定后调用 `/saveOrUpdate`，成功通知并刷新列表。加载详情失败、上传中或提交中不能再次提交。
4. 图片前端 `accept="image/*"`，最大 3MiB；广告上传服务端也精确限制。支持 jpg/jpeg/png/gif/bmp/webp/svg，受系统上传白名单进一步限制。保存广告要求图片对应有效的 `sys_file` 上传记录，并校验类型和大小；本地文件读取实际字节数。
5. 删除弹二次确认后执行物理 DELETE，成功右上角通知并刷新；当前页删空回退。删除广告业务行不会删除共用图片文件，文件仍由现有文件管理维护。
6. `status=1` 的图片可被客户端首页轮播接口读取；改为 0 或删除后，下一次请求不再返回，无需重启服务。后台列表仍能看到停用广告。

### 20.4 后台页面与菜单

| 文件 | 职责 |
|---|---|
| `frontend/src/api/useSystemApi/ad.ts` | 5 个后台接口逐项封装，导出使用 blob |
| `frontend/src/views/system/ad/index.vue` | 标题/内容搜索、查找/添加/导出、8 列表格、服务端分页排序、编辑与物理删除 |
| `frontend/src/views/system/ad/AdDialog.vue` | 创建/编辑弹窗、3 个必填项、图片上传、位置/启用状态下拉、活动链接 |
| `backend/app/scripts/install_ad.py` | 创建缺失表、幂等同步菜单及管理员权限 |

表格列顺序：广告ID、广告标题、广告内容、广告图片、广告位置、活动链接、是否启用、操作。位置显示 1，与参考图一致，悬浮提示“首页”。采用模块 scoped scss、900px/560px 响应式断点，窄屏表格横向滚动，不固定操作列；弹窗响应式使用非 scoped 样式。

当前数据库已安装 `mal_ad` 与「推广管理 → 广告管理」菜单；新库初始化菜单已收录于 `sys_menu.json`。其他已有库可在 backend 下运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_ad
```

更新代码后重启后端，并退出重新登录刷新菜单缓存。

### 20.5 客户端首页轮播对接（待接页面）

不修改客户端工程。后续首页加载时调用：

```http
POST /api/ad/banners
Content-Type: application/json

{"position": 1}
```

无需 token。返回 `data.rows` 数组及 `data.rowTotal` 总数，每项为 `id / title / content / image / position / link`，按广告ID升序稳定排列，不包含后台审计字段。

客户端用 `image` 作为轮播图片，点击后按业务处理 `link`；没有链接时可仅展示图片，数组为空时隐藏轮播。相对图片地址如 `/api/files/ads/...` 需结合后端域名解析。不要以后台 `/list` 接口作为公开轮播数据源。

---

## 二十一、优惠券管理模块

### 21.1 数据模型

模块目录：`backend/app/api/v1/system/coupon/`。四表均继承 Base；金额为 Numeric(12,2)，返回前转 float。

**`mal_coupon`（优惠券定义）**

| 字段 | 类型 | 说明 |
|---|---|---|
| id / name | bigint / varchar(128) | 主键 / 优惠券名称（唯一必填文本，允许重名） |
| description / tag | varchar(500) / varchar(128) | 介绍 / 标签，选填 |
| min / discount | decimal(12,2) | 最低消费 / 满减金额，非负、最多两位小数，默认 0 |
| limit | int | 每人限领，正整数，默认 1 |
| type | int | 分发类型：0 通用领券 / 1 注册赠券 / 2 兑换码 |
| total | int | 发行数量，非负整数；0 为不限 |
| time_type / days | int | 0 领取相对天数 / 1 指定绝对时间；days 为非负整数，0 领取当日有效 |
| start_time / end_time | datetime | 绝对有效期起止，使用本地时间 YYYY-MM-DD HH:mm:ss |
| goods_type | int | 0 全场通用 / 1 指定分类 / 2 指定商品 |
| status | int | 0 正常 / 1 已过期 / 2 已下架，默认 0 |
| — | — | 其余为 Base 公共字段 |

**`mal_coupon_category`**：coupon_id、category_id；**`mal_coupon_goods`**：coupon_id、goods_id。每组券/目标设唯一约束；coupon_id 外键 ON DELETE CASCADE。目标 ID 对应已有 `mal_category` / `mal_goods`，保存时校验，不复制商品或分类数据。

**`mal_coupon_user`（会员领取记录）**：coupon_id、user_id（对应 mal_member.id）、receive_time、status（0 未使用 / 1 已使用 / 2 已过期）、order_id、use_time、start_time/end_time（领取时有效期快照）。券定义与每次领取是不同记录，同一会员可按限领规则领取多张。coupon_id 为外键，删除优惠券时领取记录随之物理级联删除。


### 21.2 接口清单

统一 POST `/api/coupon`。下表是原有管理端接口，继续要求后台登录和权限；首页展示、会员领取与订单抵扣见第二十七章。

| # | 路径 | 权限码 | 说明 |
|---|---|---|---|
| 1 | `/list` | `coupon:query` | name 模糊、type/status 精确、sort_order；page/pageSize 放 body |
| 2 | `/detail` | `coupon:query` | `{id}`；完整定义及分类/商品范围，check_data_scope=False |
| 3 | `/saveOrUpdate` | `coupon:add` / `coupon:edit` | 无 id 新增、有 id 编辑，返回 `{id}`；主记录和范围一次提交 |
| 4 | `/deleted` | `coupon:delete` | `{id}`，物理删除优惠券、范围关联及领取记录 |
| 5 | `/export` | `coupon:export` | 同列表条件和排序、不分页，返回 xlsx |
| 6 | `/userList` | `coupon:query` | coupon_id 必填；user_id/status 筛选、page/pageSize/sort_order，返回领取/使用记录分页 |

列表返回 `{rows,rowTotal,page,pageSize,pageTotal}`，默认 20 条/页、ID 倒序，支持 10/20/30/40/50/100；下拉值 0 也参与筛选，不当作未选择。

保存字段包括 name、description、tag、min、discount、limit、type、total、time_type、days、start_time、end_time、goods_type、category_ids、goods_ids、status。仅保存当前范围对应的 ID 数组，其他范围自动清空。

后端派生字段：`min_text`、`discount_text`、`type_name`、`goods_type_name`、`status_name`、`effective_status`、`total_text`、`time_type_name`、`time_text`。详情额外返回 `category_ids` / `goods_ids` 和 `categories[{id,name,path_name}]` / `goods[{id,name,goods_sn}]`，名称从现有表查询。

### 21.3 创建、编辑与范围规则

1. 名称去空格后不能为空；其余字段按截图给出默认值。金额非负且最多两位小数；限领为至少 1 的整数；数量和相对天数为非负整数。
2. 分发类型仍为通用领券、注册赠券、兑换码。首页已实现通用领券及发行量/限领校验；注册赠券和兑换码不允许通过普通领取接口冒充赠送或兑换。
3. 相对券领取时写入持券有效期快照：days=0 截止领取当日 23:59:59；正数为领取时刻加 N 天，券定义的 start_time/end_time 仍保持为空。
4. 绝对有效期使用两个支持日历与时分秒的 datetime 选择器，必须填写完整且结束晚于开始；保存后 days 归 0。正常券的绝对结束时间已过时，服务端计算 effective_status=1，列表筛选和导出同步生效；原始 status 保留，可通过修改日期恢复正常。已下架优先保留已下架状态。
5. 全场通用不保存范围关联；指定分类/商品时至少添加一项。分类可选一级或二级，多项可去重添加和删除；商品支持按名称或编号远程搜索（复用 `/goods/list` 两种条件合并去重）。未选择点击添加只提示，不插入空行。
6. 弹窗内的范围添加/删除先修改当前表单，点击“确定”后才和优惠券一起提交；取消不修改数据库。编辑可移除旧项、加新项或切换范围，事务中同步清理旧关联，避免残留。
7. 分类/商品 ID 必须真实存在且未删除；非法目标拒绝整次保存，已有券和范围保持原样。后续目标被删除时详情展示“已删除分类/商品”，编辑时需移除失效项。
8. `CouponService.matches_goods(coupon_id, goods_id)` 是原有单商品范围辅助方法：全场匹配所有现存商品；指定商品按 ID 匹配；指定父分类也覆盖其子分类商品。当前订单使用 order_coupons()/validate_order_coupon() 同时校验持券、日期、状态、适用金额和门槛，在提交事务内核销，详见第二十七章。

### 21.4 后台页面与菜单

| 文件 | 职责 |
|---|---|
| `frontend/src/api/useSystemApi/coupon.ts` | 按现有显式 request 写法封装 6 接口，新增 getUserList |
| `frontend/src/views/system/coupon/index.vue` | 搜索筛选、12 列宽表、分页排序、创建/编辑、详情、删除、导出 |
| `frontend/src/views/system/coupon/CouponDialog.vue` | 创建/编辑，共用 openDialog；三种分发、两种有效期、三种范围及多目标临时表 |
| `frontend/src/views/system/coupon/detail.vue` | 独立“优惠券详情”标签页，两组券信息及领取/使用记录查询 |
| `backend/app/scripts/install_coupon.py` | 幂等建表、菜单/管理员权限安装、空表预置 6 条示例 |

菜单：「推广管理 → 优惠券管理」，路由 `/promotion/coupon`，name=promotionCoupon，排序 2。隐藏详情路由 `/promotion/couponDetail`，name=promotionCouponDetail、isHide=1、isKeepAlive=0，页签“优惠券详情”。分类/商品选择分别需要已有 `category:query` / `goods:query` 权限。遵循 900px/560px 响应式，宽表横向滚动、不固定操作列；弹窗响应式使用非 scoped 样式。

创建成功通知“创建成功”，编辑成功右上角通知“修改成功”；删除沿用二次确认、物理删除和成功通知，当前页删空回退一页。

### 21.5 示例数据与安装

当前库已预置 **6 条**：限时满减券3（满10减3、总量1）、限时满减券3（满99减20、不限）、可兑换优惠券（满99减15）、限时满减券1（满99减5）、指定分类的限时满减券2（满99减10）、指定商品的新用户优惠券（满99减10）。两条同名券按截图保留，以 ID 区分；关联分类和商品使用当前数据库真实数据。

其他已有库可在 backend 下运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_coupon
```

只在 `mal_coupon` 完全为空时创建示例；重复执行不会重置或重复插入。没有分类或商品时，相关示例回退为全场通用，不编造 ID。当前绝对时间示例截至初次安装后 30 天。更新后重启后端，并退出重新登录刷新菜单缓存。

客户端首页普通领券与订单核销已接入同一套定义和领取表；注册赠送及兑换码流程仍待独立实现。

---

### 21.6 独立优惠券详情与领取记录

列表点击“详情”进入 `/promotion/couponDetail?id=优惠券ID`，使用现有后台标签页机制。上方两组字段：

| 分组 | 六列内容 |
|---|---|
| 第一组 | 名称、介绍名称、标签、优惠券类型、最低消费、优惠面值 |
| 第二组 | 每人限领、当前状态、商品范围、有效期、优惠兑换码、发行数量 |

“优惠兑换码”展示位置已预留；当前尚未实现兑换码生成，未生成时保持空白。其他字段读取现有 `/detail` 返回值，不在前端重新计算优惠金额或券状态。

下方领取记录请求示例：

```http
POST /api/coupon/userList
Content-Type: application/json
token: 管理员登录令牌

{"coupon_id": 1, "user_id": 123, "status": 0, "page": 1, "pageSize": 20, "sort_order": "desc"}
```

- user_id 和 status 可省略；0 未使用、1 已使用、2 已过期，区别于优惠券定义表的 status 枚举。
- 返回 `data.rows` / `data.rowTotal` 等标准分页字段；每行含 id、coupon_id、user_id、receive_time、status、effective_status、status_name、order_id、use_time、start_time、end_time 及 Base 字段。
- 必须指定真实券 ID，查询固定加 coupon_id 条件；没有领取记录显示“暂无数据”。非法 ID 禁止查询，不存在的券返回业务错误。切换券会清空旧记录和筛选，旧异步响应不能覆盖新券。
- 状态口径与客户端一致：绝对有效期券跟随后台当前定义时间，相对券看领取快照；券下架/删除/手动置过期一律算过期。已使用状态始终保留，不因到期改为已过期。
- 领取表不预置模拟数据。/coupon/claim 校验会员、分发类型、数量和限领后写入领取时间及有效期快照；提交订单事务内写 status=1、order_id、use_time。后台详情读取同一张表即可显示领取和使用记录，客户端不能任意提交已使用状态或伪造订单 ID。

---

## 二十二、专题管理模块

### 22.1 数据模型

目录：`backend/app/api/v1/system/topic/`，主表与关联表继承 Base，由启动建表机制或安装脚本自动创建。

| 表 | 主要字段与规则 |
|---|---|
| `mal_topic` | title varchar(128)、subtitle varchar(500)、image varchar(1000)、content 富文本（MySQL LONGTEXT）、price Numeric(12,2)、read_count bigint，以及 Base 公共字段 |
| `mal_topic_goods` | topic_id、goods_id、sort，以及 Base 公共字段；topic_id/goods_id 唯一，sort 保存专题内商品顺序 |

两项外键分别引用专题与现有商品，ON DELETE CASCADE。删除专题只清理专题和关联，不删除商品；删除商品会自动清理对应关联，不删除专题。

### 22.2 接口清单

统一 POST `/api/topic`，除客户端两个只读接口外需后台登录和权限。

| 路径 | 权限 | 说明 |
|---|---|---|
| `/list` | topic:query | title/subtitle 模糊筛选，sort_by/sort_order，page/pageSize |
| `/detail` | topic:query | `{id}`，完整文章及关联商品，供编辑回显/内容预览 |
| `/saveOrUpdate` | topic:add / topic:edit | 无 id 新建，有 id 更新；提交 goods_ids，返回 `{id}` |
| `/deleted` | topic:delete | `{id}`，调用 `Topic.delete(id, True)`，级联删除关联 |
| `/batchDeleted` | topic:delete | `{ids:[...]}`，同一事务校验及物理删除，返回删除数量 |
| `/export` | topic:export | 同列表筛选/排序，不分页，返回 xlsx |
| `/clientList` | 无（公开白名单） | 客户端专题分页列表，裁剪后台审计字段与文章正文 |
| `/clientDetail` | 无（公开白名单） | `{id}`，客户端专题封面、完整正文与在售关联商品 |

保存字段：id（编辑时）、title、subtitle、image、content、price、read_count、goods_ids。列表返回标准 `{rows,rowTotal,page,pageSize,pageTotal}`，默认 20 条/页，前端可选 10/20/30/40/50/100。列表不携带正文，点击“查看”再取 `/detail`。

详情额外返回 `goods_ids` 与 `goods[{id,name,goods_sn,image,brief,is_on_sale,retail_price}]`；商品信息实时取自原 `mal_goods`，不复制商品定义。金额转 float，阅读量派生为 read_count_text（例如 42500 → 42.5k），原 read_count 整数保留。

### 22.3 业务与页面规则

1. 标题、子标题、内容去空格后必填；空段落、空格占位、只有注释/脚本/样式不算文章内容，图片或媒体文章可保存。后台可存储较长正文及表情字符；浏览器 blob 临时媒体地址必须完成上传后再保存。
2. 封面选填，前端复用 `/file/upload` 并限制图片 10MiB，后端沿用项目通用上传配置。富文本复用中文 GoodsRichEditor，支持图片、文件链接、媒体、表格、源码、预览和全屏。
3. 底价非负且最多两位小数；阅读量为非负安全整数，也支持 k 输入，76.5k 保存为 76500。阅读量当前由后台维护，读取接口不自动增加。
4. 三种排序：id 按序号默认升序，time 按创建时间默认降序，price 按底价默认升序；可提交 sort_order 指定方向。相同时间或价格用 ID 稳定排序，分页与导出同源。
5. 勾选列表行后可批量删除；未勾选点击按钮在顶部提示“请选择至少一条记录”。批量中含不存在的记录时整批拒绝，不发生部分删除。成功后通知并刷新，页空自动回退。
6. 创建和编辑使用独立标签页，编辑必须携带有效专题 ID，加载失败不能误新增。保存成功提示“创建成功”或“修改成功”，返回专题列表。
7. “专题商品 → 创建商品”实际打开“添加商品”选择框：编号/名称查找已有商品、分页、多选；跨页保留勾选，确定去重加入当前专题表格，可移除关联。不会新建商品；仅点击专题底部确定后才写入主表与关联表，取消不更改数据库。
8. 保存时核对商品存在且未删除，主表和关联替换使用同一事务，非法目标整次回滚。管理端可关联未上架商品，客户端详情只返回当前在售且未删除商品。
9. 管理端文章预览用 DOMPurify 清理后展示。保存的专题可由公开接口读取，客户端接入时也应清理 HTML，并结合后端域名解析相对图片 URL。

### 22.4 文件与菜单

| 文件 | 职责 |
|---|---|
| `frontend/src/api/useSystemApi/topic.ts` | 六个后台接口逐项显式 request 封装 |
| `views/system/topic/index.vue` | 搜索排序、分页、文章预览、单删/批量删除与导出 |
| `views/system/topic/create.vue` / `edit.vue` | 专题创建/编辑独立路由页面 |
| `views/system/topic/TopicForm.vue` | 共用表单、中文富文本、关联商品临时列表 |
| `views/system/topic/TopicGoodsDialog.vue` | 复用商品接口搜索、分页和跨页勾选 |
| `views/system/topic/TopicImageUpload.vue` | 封面上传、回调隔离及上传忙态 |
| `backend/app/scripts/install_topic.py` | 幂等建表、菜单/管理员权限安装及空表三条测试专题 |

菜单 `/promotion/topic`（name=promotionTopic，排序3）；隐藏创建路由 `/promotion/topicCreate`、隐藏编辑路由 `/promotion/topicEdit`，均不缓存，active_menu 指向专题管理。图片、宽表和弹窗按 900px/560px 响应式规范处理，不固定操作列。商品选择需已有 goods:query 权限。

### 22.5 测试专题、安装与客户端对接

当前库保留 3 条原创测试专题：

| 标题 | 底价 | 阅读量 |
|---|---|---|
| 居家好物指南 | 29.90 | 42500 |
| 日常穿搭灵感 | 59.90 | 12800 |
| 出行收纳清单 | 15.00 | 7800 |

每条含文章和封面，关联当前数据库的真实商品。封面优先复用可访问的现有商品图片，否则生成原创 SVG 并通过统一文件服务保存。已有专题时安装脚本不覆盖、不重复添加。

其他已有库在 backend 下运行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_topic
```

客户端专题列表调用 `POST /api/topic/clientList`（可提交标题/子标题、排序与分页），详情调用 `POST /api/topic/clientDetail`、body `{id}`；两接口无需 token。详情返回封面、文章及在售商品，没有后台操作接口权限。客户端专题页面本次未修改，后续按此接口对接。

更新后重启后端，并退出重新登录刷新新增菜单及创建/编辑路由。

---

## 二十三、团购规则模块

### 23.1 模块定位

一条规则绑定一个商品：满 N 人成团、享受团购价，到「过期时间」自动下线。后台维护，客户端商品详情页读取后展示「去拼团」。

### 23.2 数据模型

表名：`mal_group_rule`（模型类 `GroupRule`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 团购规则ID |
| goods_id | bigint | 商品ID（关联 `mal_goods.id`） |
| discount | decimal(12,2) | 团购优惠 / 团购折扣 |
| people | int | 团购人数要求 |
| end_time | datetime | 过期时间 |

**状态是派生的，不落库**：`end_time < 当前时间` → `到期下线`，否则 `进行中`。列表返回 `status`（1/0）与 `status_text`。

### 23.3 接口清单

前缀 `/api/groupRule`。

| # | 路径 | 权限码 | 说明 |
|---|---|---|---|
| 1 | `/list` | `groupRule:query` | 分页列表，**联 `mal_goods` 返回 `goods_name` / `goods_image` / `goods_sn`** |
| 2 | `/detail` | `groupRule:query` | 详情（含商品名称、图片、编号） |
| 3 | `/saveOrUpdate` | `groupRule:add` / `edit` | 新增或编辑 |
| 4 | `/deleted` | `groupRule:delete` | 物理删除 |
| 5 | `/export` | `groupRule:export` | 导出 xlsx |

**搜索框**（`keyword`）同时匹配三种：商品编号（`goods_sn` LIKE）、商品名称（`name` LIKE）、商品ID（输入纯数字时精确匹配），所以占位文案是「请输入商品编号」但实际更好用。

**校验**：商品必须存在 → `商品不存在`；未选过期时间 → `请选择过期时间`；折扣 ≥ 0、人数 ≥ 1（schema 约束）。

> 坑：查询结果统一走 `default_serialize`，`datetime` 会被转成字符串。比较过期状态前必须先用 `_to_datetime()` 还原，否则 `str < datetime` 报错。

### 23.4 后台页面与菜单

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/groupRule/index.vue` | 搜索 + 查找/添加/导出 + 9 列表格 + 分页 |
| `frontend/src/views/system/groupRule/GroupRuleDialog.vue` | 创建 / 编辑弹窗（商品ID、团购折扣、团购人数要求、过期时间） |
| `frontend/src/api/useSystemApi/groupRule.ts` | 5 个接口封装 |

- 表格列：团购规则ID / 商品ID / 名称 / 图片 / 团购优惠 / 团购要求 / 状态 / 结束时间 / 操作（编辑、删除）
- 状态标签：`到期下线` 蓝色、`进行中` 绿色
- 过期时间用 `el-date-picker type="datetime"`，格式 `YYYY-MM-DD HH:mm:ss`
- 商品ID、人数用 `el-input-number :controls="false"`，折扣用普通输入框（保持整数/小数原样显示）
- 分页默认 20 条；无排序（按设计稿）

### 23.5 安装

```powershell
cd backend
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_group_rule
```

幂等：只建缺失表、同步菜单与管理员绑定；仅当规则表为空时写入 4 条演示规则（引用当前库真实商品）。

### 23.6 客户端对接（待做）

商品详情页调 `/api/groupRule/list`（或后续新增公开接口）按 `goods_id` 取「进行中」的规则，展示拼团价与成团人数。

---

## 二十四、团购活动模块

### 24.1 模块定位

一条「团购活动」= 某个用户对某条团购规则**开的一次团**。后台只读：看开团记录、展开看谁参了团、导出。

数据由客户端产生：用户点「开团」→ 写 `mal_group_activity`；别人点「参团」→ 写 `mal_group_activity_member`。

### 24.2 数据模型（两张表）

**`mal_group_activity`（团购活动主表）**

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 活动ID |
| rule_id | bigint | 团购规则ID（关联 `mal_group_rule.id`） |
| order_id | bigint | 发起人订单ID |
| member_id | bigint | 发起人用户ID |
| participants | int | 参与人数 |
| discount | decimal(12,2) | 团购折扣（下单时的快照） |
| people | int | 团购要求（成团人数） |
| share_image | varchar(500) | 分享图片 |
| start_time / end_time | datetime | 开始时间 / 结束时间 |

**`mal_group_activity_member`（参与记录表）**

| 字段 | 说明 |
|---|---|
| activity_id | 所属活动 |
| order_id | 订单ID |
| member_id | 用户ID |
| join_time | 参与时间 |

> 折扣、人数要求存的是**快照**：规则后来被改，历史活动仍按当时的条件展示。

### 24.3 接口清单

前缀 `/api/groupActivity`，后台只读。

| # | 路径 | 权限码 | 说明 |
|---|---|---|---|
| 1 | `/list` | `groupActivity:query` | 分页，支持 `rule_id` 精确筛选；每条活动带 `members` 数组 |
| 2 | `/export` | `groupActivity:export` | 导出 xlsx |

### 24.4 后台页面与菜单

| 文件 | 职责 |
|---|---|
| `frontend/src/views/system/groupActivity/index.vue` | 搜索 + 查找/导出 + 8 列表格（含展开行）+ 分页 |
| `frontend/src/api/useSystemApi/groupActivity.ts` | 2 个接口封装 |

- 表格列：订单ID / 用户ID / 参与人数 / 团购折扣 / 团购要求 / 分享图片 / 开始时间 / 结束时间
- **左侧箭头展开**：`type="expand"`，子表格列为「订单ID / 用户ID」，即该团的参与成员（无成员显示「暂无数据」）
- 只有查找 / 导出，没有添加、编辑、删除（数据来自客户端）
- 菜单：`/promotion/groupActivity`（sort=7），权限 2 个

### 24.5 安装

```powershell
cd backend
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_group_activity
```

幂等；空表时写入 3 条演示活动（分别有 2 / 1 / 0 个参与成员，引用现有规则、订单、会员）。

### 24.6 客户端对接（待做）

开团：写 `mal_group_activity`（带 rule_id、自己的 order_id/member_id、participants=1）。
参团：写 `mal_group_activity_member` 并把 `participants` +1；满 `people` 即成团。
分享：`share_image` 用于生成分享海报。

---

## 二十五、客户端商品详情与购物车模块

### 25.1 模块定位与数据模型

客户端复用后台已有的商品、库存、规格与参数数据，不另建客户端商品库。商品详情允许公开查看；购物车是会员私有数据，保存待购数量及勾选，不代表下单或锁定库存。

新增表：`mal_cart`（模型 `Cart`，继承 `Base` 的主键、审计字段和 `enabled_flag`）。

| 字段 | 类型 | 说明 |
|---|---|---|
| member_id | bigint，非空、索引 | 当前会员，关联 `mal_member.id`，删除会员时级联删除购物车 |
| goods_id | bigint，可空、索引 | 关联既有 `mal_goods.id`，删除商品时置空，保留失效条目供本人清理 |
| product_id | bigint，可空、索引 | 关联既有 `mal_goods_product.id`，删除库存行时置空 |
| quantity | int，默认 1 | 加入数量，服务端限制为 1～999；不预占库存 |
| checked | boolean，默认 true | 普通模式是否勾选，保存在数据库 |

唯一约束 `uq_cart_member_product(member_id, product_id)` 保证同一会员的同一库存规格只保留一行；不同库存规格或不同会员互不合并。购物车不保存商品售价快照，展示价格、规格、库存及图片实时关联 `mal_goods` / `mal_goods_product`；SKU 图片为空时使用商品主图。

### 25.2 接口清单与返回字段

统一 POST，请求参数放 JSON body；响应沿用 `{code, msg, data, success}`，成功 `code=0`。`/api/goods/clientDetail` 保持公开白名单，六个 `/api/cart/*` 均需请求头 `token`，不使用后台权限码，不加入 `WHITE_ROUTER`。

| 接口 | 请求体 | 说明 |
|---|---|---|
| `/api/goods/clientDetail` | `{id}` | 商品信息、图集、正文、参数、规格及库存行；本次新增在售/可加购状态 |
| `/api/cart/list` | `{}` | 本人整车列表及实时合计，不分页 |
| `/api/cart/add` | `{goods_id, product_id, quantity}` | 新增或合并同一库存规格，默认勾选，返回整车及合计 |
| `/api/cart/update` | `{id, quantity}` | 修改本人某条购物车数量，返回整车及合计 |
| `/api/cart/checked` | `{ids, checked}` | 单选/批量勾选或取消；`checked` 必须是布尔值 |
| `/api/cart/deleted` | `{ids}` | 物理删除本人单条/多条购物车，返回剩余整车及合计 |
| `/api/cart/count` | `{}` | `{count}`，本人购物车全部记录的总件数，包含保留的失效条目 |

`clientDetail.products` 每项只返回库存行 `id`、`specification`、`price`、`quantity`、`image`，同时返回 `is_on_sale`、库存总和 `stock`、`cart_available`（在售且有库存）。参数 `attributes` 仅返回名称和值，商品/库存不返回后台审计信息；加购必须提交这里返回的真实库存行 ID。

购物车整车结果：

| 字段 | 说明 |
|---|---|
| rows / rowTotal | 条目与行数，按加入时间倒序；失效条目仍保留 |
| total_quantity | 整车所有条目的总件数，包含失效项 |
| selected_quantity / selected_count | 当前勾选且有效的总件数 / 行数 |
| total_amount / total_amount_text | 当前勾选且有效的商品金额；`Decimal` 计算，文本保留两位小数，不含运费 |

每条 `rows` 含 `id`、`goods_id`、`product_id`、名称/编号/图片/规格、实时 `price` / `price_text`、`quantity`、`stock`、`checked`、`available`、`invalid_reason`、`subtotal` / `subtotal_text` 及添加时间。失效条目返回的 `checked=false` 只是本次展示结果，读取不会改写原数据库勾选值。

### 25.3 业务规则

1. 会员身份仅从 Redis 会话的 `member_id` 读取，拒绝后台管理员 token；每次购物车请求还验证会员存在、未删除且状态为「可用」。请求契约禁止额外字段，不能提交 `member_id`、`price` 等覆盖服务端身份或价格。
2. 所有修改、勾选、删除都限定当前会员，批量操作先核对全部 ID；混入他人或不存在的记录时整次失败，不部分修改。删除只物理清理购物车记录，不删除商品、库存或其他会员数据。
3. 加购和改数量重新校验商品存在且在售、库存行有效且归属当前商品、数量为 1～999 的整数且不超过实际库存；布尔值/小数/零/负数均不能作为数量。同规格加购校验的是合并后的总量。
4. 同一会员的写操作通过会员行锁串行处理，配合唯一约束与事务保证同规格并发加购累加到一条记录。库存只复用 `GoodsProduct`，加购不扣库存、不锁定库存名额、不创建订单。
5. 购物车每次读取/写入都重新计算实时单价、库存和小计，只将有效且勾选的条目计入总额；不相信页面提交的金额。后台改价后下次刷新即使用新价。
6. 商品删除/下架、库存规格删除/失效、售罄、购买数量超过现有库存时返回原因，失效条目不能勾选计价但可以删除；商品/库存物理删除使用外键 `SET NULL` 保留购物车行。库存不足时页面允许把数量降到当前库存，成功后恢复有效。
7. 普通模式的单选/全选保存到 `checked`；编辑模式的删除选择独立存于页面，支持选择失效项，不覆盖普通勾选。批量勾选为 true 时重新校验每项商品状态，取消勾选不要求商品仍有效。
8. 详情的单库存规格自动选中，多库存规格由会员选择，无货规格不可选；数量与价格随库存规格切换。详情返回时的库存仅供展示，确认加购仍以服务端实时检查为准。
9. 立即购买和结算已进入确认订单。购物车合计仍仅含商品；确认订单按满 88 免运费、否则 80 元计算，提交时重新验证价格、库存、地址、优惠并以事务处理，见第二十八章。
10. 编辑模式在商品行右侧展开红色删除区；普通模式可单行左滑展开、右滑收起，H5 支持鼠标拖动。手势不会改变结算勾选，也不会自动删除；点击删除仍需确认后调用原接口。

### 25.4 文件与页面

| 文件 | 职责 |
|---|---|
| `backend/app/api/v1/system/cart/model.py` | `Cart` 模型、唯一约束及商品/库存外关联查询 |
| `backend/app/api/v1/system/cart/schema.py` | 六个接口的请求契约，禁止身份/价格等额外字段 |
| `backend/app/api/v1/system/cart/service.py` | 会员隔离、加购合并、数量/勾选/删除、实时有效性及金额计算 |
| `backend/app/api/v1/system/cart/controller.py` | `CartRouter` 六个显式 POST 接口，service → data → HttpResponse |
| `backend/app/api/v1/system/router.py` | 导入并注册 `CartRouter` |
| `backend/app/api/v1/system/goods/service.py` | 公开详情补真实库存行、库存总和及加购状态 |
| `backend/app/scripts/install_cart.py` | 仅调用统一 `create_tables()` 创建缺失表 |
| `Mall_Front‑end_Page/api/cart.js` | 六个购物车请求逐项显式封装 |
| `Mall_Front‑end_Page/pages/goods/detail.vue` | 图集/富文本、属性与规格弹层、数量、加购、角标 |
| `Mall_Front‑end_Page/pages/cart/index.vue` | 空车/未登录/失败状态、商品、勾选、编辑数量、删除及实时合计 |
| `Mall_Front‑end_Page/pages.json` | 购物车自定义导航样式，继续复用已有页面路由 |
| `Mall_Front‑end_Page/components/tab-bar/tab-bar.vue` | 底部导航高度包含安全区，购物车合计栏同步避让 |

客户端与 `fastapiwebadmin/` 为同级目录。页面复用 `nav-header`、`tab-bar` 和既有红色主题，适配手机窄屏与底部安全区；相对图片地址通过 `api/url.js` 补后端域名，富文本图片适配内容宽度。详情进入购物车以及底部导航均指向已有 `pages/cart/index`。

### 25.5 初始化与验证

启动时按既有模型扫描自动建缺失表，已有库也可在 backend 下运行：

```powershell
cd backend
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_cart
```

脚本仅调用 `create_tables()`，不装菜单、不补商品/库存、不修改会员，`mal_cart` 初始化为空，不预置任何模拟购物车。库存、规格与参数直接使用管理后台已维护的表。

验证结果：

- 临时 TestClient 脚本在真实数据库完成 **47 次 API 请求**，覆盖公开详情字段、加购/同规格合并、多规格、两会员隔离、管理员/未登录拒绝、非法数量与伪造字段、改价/减库存、勾选持久化、并发累加、禁用会员、商品/库存删除后的失效项及物理删除。
- 接口验证及浏览器预览的临时会员、商品、库存/参数、购物车及 Redis token 均已清理，没有保留测试购物车。
- SFC 编译、页面模拟交互校验通过；使用 **HBuilderX 5.33** 实际完成 uni-app **H5 production build**。
- 390px 宽浏览器使用真实临时会员登录，确认图集与富文本显示、标准规格选数量 2 加购成功、购物车角标 2；属性弹层显示「材质：纯棉」「产地：中国」。购物车显示该规格 ×2、合计 39.80，取消全选后单项及全选均取消、合计 0.00；编辑模式数量由 2 增至 3，完成后全选显示合计 59.70。检查后修正购物车原生标题重复及底部导航安全区，H5 production build 再次通过，最终浏览器预览确认没有重复标题。

### 25.6 客户端对接与后续边界

详情可免登录查看，进入购物车或提交加购需会员 token；未登录时引导登录，鉴权失效沿用统一请求封装的 `11000` 清 token 与跳转处理。购物车 `onShow` 重新拉取，写操作后重新加载，`cart:change` 通知详情刷新角标；异步回调会核对页面状态、请求版本及当前 token，避免切换账号后回填上一会员数据。

目前已接通浏览商品、立即购买或购物车、确认地址与优惠、提交未付款订单、支付方式占位。只有提交订单才写订单、扣库存与核销所选券；真实扣款、支付回调和后续履约仍待实现。

---

## 二十六、客户端分类模块

### 26.1 模块定位与数据来源

客户端分类与管理后台共用 `mal_category`，商品继续读取 `mal_goods`。本次只扩展读取接口和客户端页面，不新增表、安装脚本、菜单或演示数据。

| 既有字段 | 客户端用途 |
|---|---|
| `id / name` | 一级选项、二级格子、商品列表横向分类切换及标题 |
| `level / parent_id` | 组成一级根和直属二级类目的两级结构 |
| 一级 `image` | 分类页右侧内容顶部类目图片 |
| 二级 `icon` | 二级类目格子图标；不使用二级 `image` 替代 |
| `description` | 当前一级类目与分类商品列表的介绍文案 |
| `mal_goods.category_id` | 商品所属真实类目，服务端按一级/二级范围筛选 |

图片使用原有 `imageUrl()` 补后端域名。没有上传图片、图标并非有效图片地址或加载失败时使用页面占位，不伪造图片地址，也不把类别名或后台图标名当上传图片请求。

### 26.2 接口与字段

三个列表接口均为公开 POST；后台的类目增删改查仍保留原权限。

| 接口 | 请求 body | 返回及用途 |
|---|---|---|
| `/api/category/clientList` | `{}` | 原首页快捷一级类目数组，最多 10 个，契约不变 |
| `/api/category/clientTree` | `{}` | 完整有效一级根数组，每个根带直属 `children`，没有首页 10 项限制 |
| `/api/goods/clientList` | `{category_id, page: 1, pageSize: 20}`，可组合既有 keyword/brand_id/scene | 复用商品分页结果 `{rows,rowTotal,...}`，当前类目与触底加载共用 |

公开分类节点只返回 `id/name/level/parent_id/icon/image/description`，根额外带 `children` 数组，子节点不带 `children`。图片/图标/简介为空时返回空串，不返回 keywords、创建人、修改人等后台字段。`clientTree` 加入 `WHITE_ROUTER`，未登录也可加载分类页；前端不调用需要后台权限的 `/category/list` 或 `/detail`。

### 26.3 分类与商品范围规则

1. 复用 `Category.get_all()` 读取现有有效类目，仅以 `level=1,parent_id=0` 作为根，将有效 `level=2` 且父级存在的记录挂入 `children`。根和子节点均按 ID 升序；过滤已删除根/子类、孤儿及异常层级。
2. 首页一级快捷入口继续最多 10 项；分类页读取完整树，一级选项和二级类目不会被首页限制截断。
3. 一级商品范围包含直接归于该一级的商品及有效直属二级下的商品；二级范围仅匹配该二级，不混入其他兄弟类目。
4. `category_id` 提供时必须为正整数。不存在、已删除或孤儿类目不匹配商品，不能因为查不到类目而退回全场；SQL 范围由 `Category.client_scope_ids()` 和 `Goods.client_stmt()` 组合完成。
5. 商品列表继续使用原接口、排序、关键字/品牌条件及分页契约，当前分类每页 20 条；切换分类清空原结果并从第一页重新查询，避免快速切换时把其他分类的旧响应混进当前列表。
6. 分类商品页的横向选项来自当前一级下的二级类目；「全部」只是选中一级范围的界面控件，不生成或写入类目表。当前类目名称和简介均来自真实分类数据。
7. 顶部图片取一级 `image`，二级格子只取自身 `icon`；缺失或加载失败使用占位，二级 `image` 不作为图标回退。
8. 点击商品沿用 `/pages/goods/detail?id=商品ID` 和 `/api/goods/clientDetail`，没有新增商品详情或购买接口。分类请求不会修改商品、类目、库存或购物车；在售展示与购买校验继续遵循既有商品/购物车规则。

### 26.4 文件与页面

| 文件 | 职责 |
|---|---|
| `backend/app/api/v1/system/category/model.py` | 既有类目读取及客户端商品范围子查询 |
| `backend/app/api/v1/system/category/service.py` | 公开分类树、展示字段裁剪及有效父子关系 |
| `backend/app/api/v1/system/category/controller.py` | 显式 `/clientTree`，service → data → HttpResponse |
| `backend/app/api/v1/system/goods/model.py` | 在原商品客户端查询中组合分类范围 |
| `backend/app/api/v1/system/goods/schema.py` | 客户端分类 ID 正数约束 |
| `backend/app/config/setting.py` | 分类树公开白名单 |
| `Mall_Front‑end_Page/api/category.js` | 保留 `categoryClientList`，新增显式 `categoryClientTree` POST 请求 |
| `Mall_Front‑end_Page/pages/category/index.vue` | 顶部搜索、左侧一级选择、右侧图片/简介/二级格子与底部分类导航 |
| `Mall_Front‑end_Page/pages/goods/list.vue` | 分类横向切换、当前分类介绍、20 条分页及原有商品详情跳转 |
| `Mall_Front‑end_Page/pages.json` | 分类页自定义导航样式，避免系统标题栏与顶部搜索重复 |

分类页左右区域可分别滚动，切换一级时重置右侧内容位置；底部导航及搜索继续复用现有组件/页面。商品列表保留新品、人气、品牌和搜索等原有入口，在分类模式下增加顶部同父类目切换。

### 26.5 验证与数据清理

- 真实数据库接口检查共 **29 次请求** 通过：公开树字段、超过首页 10 项的完整结果、孤儿/已删除节点过滤、一级包含自身及有效二级、二级精确范围、每页 20 条和下一页、无效分类 ID、brand/keyword/scene 组合，以及首页旧契约与后台权限保留。
- 临时 15 个根类目、有效/已删除/孤儿子类目及 29 个商品均已清理，没有新增表、保留种子数据或修改已有业务记录。
- 使用 **HBuilderX 5.33** 实际完成 uni-app **H5 production build**，编译通过。
- 390px 宽浏览器只读使用现有业务数据：一级「配件」显示后台维护的 `image`；切换「服装」并点击二级「上衣」进入当前类目商品，横向切换「裤装」显示空态，切「全部」显示父「服装」范围的商品及数据库简介，点击现有商品进入原商品详情页。现库二级 `icon` 多数为空，页面正确显示文字占位，没有用二级 `image` 代替图标。本次浏览器检查未新建类目、商品或会员记录。
- 首页「服装」快捷入口确认进入父分类的「全部」范围并显示子类商品；320px 窄屏分类页仍保持三列图标，文档宽度为 320px、右侧内容宽 242px，没有横向溢出。

---

## 二十七、客户端优惠券领取与订单抵扣

### 27.1 模块定位与数据原理

这是独立的会员优惠券业务模块，首页领券、订单选券、后台领取记录使用同一套数据，不在客户端另外维护券余额。代码仍放在既有 `backend/app/api/v1/system/coupon/` 四件套，前端请求逐项显式 POST。

| 既有表 | 含义与责任 |
|---|---|
| `mal_coupon` | 管理员维护的券定义：面额、最低消费、发行量、每人限领、分发类型、有效期、范围、状态 |
| `mal_coupon_category` / `mal_coupon_goods` | 券允许使用的类目或商品 ID，继续关联现有类目/商品 |
| `mal_coupon_user` | 每一次真实领取的记录：coupon_id、user_id、receive_time、status、有效期快照、order_id、use_time |
| `mal_order` | 下单后保存 coupon_user_id 和真实 discount_amount；券定义以后改价不重算已生成订单 |

券定义和持券不是同一个 ID：`coupon.id` 表示一款券，`coupon_user_id` 表示某会员领到的其中一张。首页 claim 传定义 ID，订单选择传本人持券 ID；同一会员可在限领内拥有多张独立记录。

状态也分两套：定义 `status=0正常/1过期/2下架`；持券 `status=0未使用/1已使用/2已过期`。展示状态按“定义当前状态 + 有效期口径”派生：绝对有效期券看定义当前时间，相对券看领取快照；已使用不会因为日期经过而改成过期。

### 27.2 对外接口及职责

全部 POST，参数在 JSON body，响应沿用 `{code,msg,data,success}`。只有 clientList 是公开白名单；会员接口不放白名单，也不接受管理员 token。

| 接口 | 请求 | 实现职责 |
|---|---|---|
| `/api/coupon/clientList` | `{}` | 首页可展示的普通领券数组，保留原金额文字，补发行余量及 can_claim |
| `/api/coupon/claim` | `{id: 券定义ID}` | 校验并真实领取一张，返回本人持券 ID、有效期、规则及剩余限额 |
| `/api/coupon/myList` | `{}` 或 `{status:0/1/2}` | 本人已领券，返回 rows/rowTotal 与使用状态，不接受 user_id |
| `/api/order/preview` | 当前结算来源、商品/购物车、可选 coupon_user_id | 实时计算商品与运费、所选券折扣，同时返回可用/不可用券列表 |
| `/api/order/coupons` | `{quote_token}` | 当前报价下的本人券；available、reason、eligible_amount 与 discount_amount |
| `/api/order/submit` | `{quote_token,request_key,user_message}` | 最终重验后，在订单事务内核销所选券，客户端不能直接提交核销结果 |

持券展示字段包括 `id/coupon_user_id/coupon_id/name/min/discount/min_text/discount_text/goods_type/goods_type_name`、领取/起止/使用时间、状态、order_id。订单选券额外有 `available`、不可用 `reason`、适用商品小计和本单实际抵扣金额，金额同时提供数值与两位小数字符串。

### 27.3 首页领取流程与数量限制

1. 会员点击首页券卡，前端对该券禁重复请求；未登录先引导登录。服务端从 token 取 member_id，检查会员存在、未删除、状态可用，拒绝客户端伪造 user_id、price 等额外字段。
2. 事务先锁会员，再锁该 Coupon 定义行。发行量是跨会员共享资源，券行锁让同一款券的并发领取串行计算，避免最后一张发给两人；会员锁也与下单、地址维护保持一致顺序。
3. 只有 `type=0` 通用领券能从首页领取。`type=1` 注册赠券、`type=2` 兑换码依然是不同分发规则，本次不伪造赠送或兑换成功；普通 claim 会拒绝。
4. 当前定义必须有效、status 正常；绝对时间尚未开始或已经结束不能领取。公开首页只展示已开始且未过期/未下架的普通券。
5. `total=0` 表示不限发行；正数为发行总量。计数使用该定义全部历史领取记录，已使用、已过期、逻辑隐藏的记录仍占发行量，不因状态变化变回库存。
6. 每人限领 `limit` 同样按该会员全部历史领取数判断，不是只数当前未使用的张数。用完一张不会凭空增加领取名额；同一人领多张必须是后台配置允许。
7. 通过后向既有 mal_coupon_user 插入一条记录，写 user_id、receive_time、status=0 和有效期快照；不减少 total 定义值，剩余量由 total 减实际发行记录派生。失败整次回滚，不插入空券或部分领取记录。

因此后台数量的含义一直是管理员设定的总发行量，`claimed_count` 是已发行数，`remaining_total=null` 表示不限。达到发行量或个人限领时，即使页面没有及时刷新，也由后端拒绝再次领取。

### 27.4 有效期口径与后台修改

- 相对券（time_type=0）：领取时刻为开始；days=0 截止领取当日 23:59:59，正数 days 按领取时刻加 N 天。每一张持券保存自己的起止时间，晚领取不会共用另一人的日期。**这类券以持券快照为准**，后台改天数不影响已领取的券。
- 绝对券（time_type=1）：领取时复制定义的 start_time/end_time 作为快照留存，但**展示、筛选、结算都以券定义当前时间为准**。后台把结束时间改成已过去 → 已领取的券立刻进「已过期」；后台把时间延长 → 已领取的券同样跟着延长。这样管理员在后台改期，客户端的「我的优惠券 / 个人中心角标 / 后台领取记录」三处口径一致。
- 券定义被删除、下架（status=2）或手动置为已过期（status=1）时，已领取的券一律算过期，不能仅因领取时曾有效就绕过管理员后续停用。
- 已使用状态优先保留，便于后台查订单和使用时间；客户端不能通过重领、改状态字段或换用户 ID 恢复使用。
- 统一判定函数：`CouponService._effective_status(user_coupon, coupon, now)`（0 未使用 / 1 已使用 / 2 已过期），客户端 `myList`、订单 `mySummary` 角标、后台 `userList` 的 SQL 表达式都按这套口径实现。

### 27.5 范围、满减门槛与真实抵扣

先从服务端现有 Goods/GoodsProduct 取得价格和数量，再按券范围筛出适用商品，不相信页面传入的金额。

| goods_type | 适用范围 |
|---|---|
| 0 全场 | 本次订单所有有效商品 |
| 1 指定分类 | 指定有效二级仅本类；指定有效一级包含本级及有效直属二级商品；已删除/孤儿类别不匹配 |
| 2 指定商品 | 只有 CouponGoods 中允许的真实商品 ID，不把同名商品算入 |

计算使用 Decimal：

```text
适用商品小计 = Σ(范围匹配商品的库存售价 × 下单数量)
可用条件 = 本人未使用且有效的券 + 当前定义有效 + 适用商品小计达到 min
实际抵扣 = min(券面额 discount, 适用商品小计)
订单应付 = 全部商品金额 + 运费 - 实际抵扣
```

**非适用商品不能凑门槛，也不能被该券抵扣。运费既不计入优惠券门槛，也不被抵扣。** 当前一次订单只选一张持券，不叠券。

例如：指定分类 A 的券满 100 减 20，订单 A 商品 60 元、其他商品 100 元，虽然全单 160 元，该券仍不可用；A 商品 60 元、其他商品 40 元，券门槛为 50 元时可抵 20 元，运费按全单优惠前商品金额计算。

订单选券页分成可用/不可用列表，已使用券不再进入候选列表；不可用原因包括过期、未到使用时间、定义停用/删除、有效期信息不完整、没有匹配范围的商品、适用金额未到门槛、没有可抵扣金额等。不可用行不允许选中；直接伪造 coupon_user_id 提交也会再被后端拒绝，包括伪造已使用券的 ID。

### 27.6 提交时核销、后台同步与回滚

预览不会核销券，也不扣库存。提交时在同一订单事务内重新检查券：先锁定义，再锁本人持券行并刷新 ORM 状态；读取当前范围重新算折扣，防止旧报价或其他请求已经使用后仍通过。

生成订单及商品明细、扣库存、写持券 `status=1/order_id/use_time`、删除本次已下单购物车记录在同一事务中完成。任一库存、地址、价格、券或数据库检查失败，整个事务回滚，不会只扣券却没有订单。相同会员和 request_key 的重试返回同一订单，不重复扣库存、用券或清购物车。

后台优惠券详情原 `/coupon/userList` 直接查询同一个 mal_coupon_user，所以领取后出现记录，提交订单后可看到使用状态、订单 ID 和使用时间；没有再建一套后台同步队列或假记录。

本次核销发生在**创建未付款订单**时，支付页弹窗不会再次核销或把订单变为已付款。管理员物理删除本次客户端创建的未付款订单时，在同一事务内恢复对应库存，把确实关联该订单的持券恢复为 status=0，并清除 order_id/use_time，随后删除明细和主单；恢复后仍按原快照有效期和当前券规则判断能否再使用。旧演示订单或已付款订单不执行该恢复。当前未实现客户端取消/超时释放，等待半小时不会自动恢复；后续取消、支付超时和退款仍需各自的补偿流程。

### 27.7 代码位置、验证与当前进度

| 文件 | 职责 |
|---|---|
| `backend/app/api/v1/system/coupon/model.py` | 原券定义、范围及持券模型；首页只读普通有效券 |
| 同目录 `schema.py` / `controller.py` | 严格会员领券/持券契约及显式 claim/myList POST 接口 |
| 同目录 `service.py` | 发行/限领锁、快照、本人持券、范围门槛、可用原因及订单内校验辅助函数 |
| `backend/app/api/v1/system/order/client_service.py` | 报价和提交时调用上述规则，在订单事务中写核销记录 |
| `Mall_Front‑end_Page/api/marketing.js` | 首页领取与本人持券请求 |
| `Mall_Front‑end_Page/pages/index/index.vue` | 首页点击领券、按券防重复请求与结果提示 |
| `Mall_Front‑end_Page/pages/order/coupons.vue` | 可用/不可用分组、原因展示、选择或不使用 |

领券与抵扣的 AST/SQL/契约及纯内存规则检查通过。领取/订单真实联测 **66 次请求通过**，包含发行量和个人限领并发各仅一次成功、范围内金额门槛、超面额截断且保留邮费、领取→下单→后台使用记录、订单删除恢复、回滚及报价消费后的防重放；测试数据已清理。逐项结果见第二十八章进度表。

---

## 二十八、客户端地址、订单确认与支付占位

### 28.1 数据复用与迁移

地址仍使用 mal_address，地区仍使用 mal_region；订单及明细仍写 mal_order/mal_order_item，后台原查询立即可见，不新建客户端订单库。原订单、会员、商品等业务数据保留。

| 既有表的新增/调整字段 | 用途 |
|---|---|
| mal_order.goods_amount / freight_amount / discount_amount | 下单时商品金额、运费和优惠的快照，Numeric(12,2) |
| mal_order.coupon_user_id | 本次使用的会员持券 ID |
| mal_order.checkout_key | 会员下单请求号；会员+请求号唯一保证重试幂等 |
| mal_order_item.goods_id / product_id | 下单真实商品和库存行 ID 快照 |
| mal_order_item.spec | 扩为 varchar(128)，与既有库存规格长度一致 |

已有库的 create_all 只补缺表，不会自动增加旧表列，因此提供幂等脚本：

```powershell
cd backend
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_checkout
```

脚本检查缺失列/索引后才 ALTER，保留旧订单；新增字段允许 NULL 以兼容旧数据，新库则直接按 ORM 模型建齐。本次该迁移已实际执行成功。

其他环境部署时先备份并执行迁移，再启动加载新模型的后端服务；后端仍需正常连接 MySQL 和 Redis。不能省略迁移直接调用下单，否则旧表缺列或缺幂等索引。该脚本没有新增测试会员、商品或优惠券。

### 28.2 地址及地区选择流程

「我的→收货地址」和确认订单的地址入口共用 pages/address/index，选择模式带 select=1，编辑模式进入 pages/address/edit。前端调用已有 region/tree，底部三级选择器展示数据库中的省/市/区；切换上级重置下级，不使用写死行政区列表。

保存时传 receiver_name、mobile、region_ids[省ID,市ID,区ID]、detail、is_default，可选 id 表示编辑。前后端都校验大陆 11 位手机号 `^1[3-9]\d{9}$`、姓名和详细地址非空；服务端还验证真实有效的三级父子关系，并根据区域名称写入原 region 列。

身份从会员 token 取，不能传 member_id 冒充他人。默认设置与地址写入使用会员行锁+事务，同会员最多一个默认；无默认时保存地址自动设默认，删除默认后剩余最早记录接替。旧地址能按现有区域名称匹配路径则回显，否则要求重新选择。

确认订单优先取默认地址，没有默认则取本人最早有效地址；可以进入列表切换或新增。新建订单保存地址文字快照，之后编辑或删除地址不改变已有订单收货信息。后台只保留查看/查询/导出用途，旧管理端写入方法明确拒绝。

### 28.3 从两种入口进入同一确认页

1. 购物车结算：只传所选本人购物车 ID 列表，服务端读取每条实际商品、库存规格和数量；无效或他人记录整次拒绝。
2. 商品立即购买：选真实库存规格及数量，传 source=buy_now、goods_id、product_id、quantity；不先往购物车插入假记录。
3. 两种来源都进入 pages/order/confirm，展示地址、当前持券优惠、商品明细、商品金额、邮费、抵扣、备注及总计。
4. `POST /order/preview` 重新读取在售商品、真实价格、库存、地址和券，返回 quote_token、明细与金额文本。报价存在 Redis 900 秒，并绑定会员、所选 ID、地址、券及完整金额指纹。
5. 地址或券改变后重新预览，金额以服务端结果展示；报价过期或商品/地址/优惠信息变化时要求重新确认，不能凭旧页面总价提交。

### 28.4 运费与金额规则

按用户已确认规则：**优惠前商品金额满 88 元免运费，不满收 80 元。** 门槛比较的是全单商品金额，券后低于 88 元不会再补运费。运费不参加优惠券满减，也不被优惠券面额抵扣。

```text
商品金额 = Σ(当前库存售价 × 数量)
运费 = 商品金额 >= 88 ? 0 : 80
应付金额 = 商品金额 + 运费 - 适用优惠券实际抵扣
```

例如商品 36 元、无券应付 116 元；商品 100 元、可用券减 20 元，应付 80 元；面额超过适用商品金额时截断，不抵运费、不出现负数。金额由 Decimal 计算并保存两位小数，前端不提交可信的单价、折扣、应付或支付状态。

### 28.5 提交订单、幂等与库存事务

会员点击提交时传 quote_token、固定 request_key 和 user_message。服务端先锁会员并查该会员/请求号是否已有订单；有则直接返回原订单，即使首次响应丢失、报价后来过期也不重复下单。

未创建时读取会员绑定报价，按固定商品/库存 ID 顺序锁真实库存，重新检查在售、规格归属、数量、地址归属和有效券，重新计算并比较报价指纹。发生价格、地址或折扣变化就整次拒绝，要求重新确认，不能静默加价。

通过后在同一事务中：创建 status=1 未付款订单、写商品/收货/金额快照和 OrderItem、扣减对应 GoodsProduct.quantity、核销券并写订单 ID/使用时间、删除本次选中的购物车记录。没有下单的购物车商品继续保留；直接购买不清理其他购物车。任一步失败整次回滚。

订单 total_amount 是本次应付，pay_amount=0，pay_time/pay_channel 仍为空，不冒充已收款。支付展示使用订单快照，后台原订单列表/展开明细/详情/导出也读取这笔真实订单。

报价 token 只能提交一次：持有会员锁时，在提交数据库事务前从 Redis 删除本次临时报价；同 request_key 重试优先查已有订单，仍返回原结果，不同请求号不能重放已消费报价。管理员删单后旧报价也不能再次建单。Redis 删除失败会使本次数据库写入回滚；若报价已消费而数据库最终提交失败，则需要重新预览，不能认为缓存删除能随数据库事务恢复。

确认页对网络结果不明确的提交保存同一请求号，恢复或重试仍按原请求确认；提交明确失败后才允许刷新报价。切换登录账号、过期响应和页面卸载不回填上一会员数据。

管理员物理删除带 checkout_key 的本次客户端未付款订单时，同样先锁会员，再锁订单和相关库存/券，原子恢复库存、释放本单持券并删除订单。库存恢复若超出字段上限整次回滚；旧演示订单、已付款订单不按该规则恢复，也不会重新写回购物车。客户端取消和超时关单仍未开放。

### 28.6 支付页与 15 种方式

支付页 pages/order/payment 只调用会员本人 `/order/myDetail` 取订单和支付列表，服务器验证归属。当前提供：微信支付、支付宝、Visa、Mastercard 万事达、PayPay、PayPal、Apple Pay、Google Pay、银联、JCB、American Express 美国运通、Discover、楽天ペイ Rakuten Pay、Amazon Pay、AlipayHK，共 15 项。

选中方式后点击「去支付」只弹出所选名称及演示说明，不调用真实支付 API，不创建支付凭据、不扣款，不设置 pay_time/pay_channel 或 status=4；订单保持未付款。已有订单不是未付款状态时，前端不能继续点占位支付。

没有实现参考图中的“半小时自动取消”，所以界面不假装存在倒计时或自动关单。真实支付、支付回调验签、订单取消/超时释放、退款与发货后续另做；后台 collect/deliver/refund 仍是原有占位接口，不能把支付演示当成已能收款或发货。

### 28.7 接口与文件

| 位置 | 实现 |
|---|---|
| backend/app/api/v1/system/address/ | 本人地址五接口、手机号/真实区域链、默认与只读后台边界 |
| backend/app/api/v1/system/order/client_service.py | preview/coupons/submit/myDetail、计价、Redis 报价、幂等和事务 |
| backend/app/api/v1/system/order/model.py、schema.py、controller.py | 旧订单表扩展、严格会员请求契约、显式 POST 接口 |
| backend/app/scripts/install_checkout.py | 补原有订单字段/索引及规格长度，不重置数据 |
| Mall_Front‑end_Page/api/address.js、order.js、marketing.js | 地址/地区、订单和领券的显式请求 |
| Mall_Front‑end_Page/pages/address/index.vue、edit.vue | 本人地址管理、选择、三级地区与默认开关 |
| Mall_Front‑end_Page/pages/order/confirm.vue、coupons.vue、payment.vue | 确认报价、选券、提交和支付占位 |
| Mall_Front‑end_Page/pages/goods/detail.vue、cart/index.vue、profile/index.vue | 立即购买、结算和收货地址入口 |
| Mall_Front‑end_Page/pages.json | 5 个新页面路由，继续自定义导航避免标题重复 |

地址会员接口见第四章；订单确认新增 preview/coupons/submit/myDetail 四项均为 POST，不加入公开白名单，不允许管理员 token 代替会员，不接受会员 ID、单价、订单总额或已付款状态等伪造字段。

| 订单请求 | JSON body 契约 | data 主要返回 |
|---|---|---|
| preview：购物车 | `{source:"cart",cart_ids:[本人购物车ID],address_id?,coupon_user_id?}` | quote_token、items、address、coupons、所选持券 ID、金额及两位金额文本 |
| preview：立即购买 | `{source:"buy_now",goods_id,product_id,quantity,address_id?,coupon_user_id?}` | 同上；product_id 是库存表 ID，不能用规格表 ID 代替 |
| coupons | `{quote_token}` | `{rows:[本人未使用券及 available/reason/适用小计/实际折扣]}` |
| submit | `{quote_token,request_key,user_message?}` | 已创建或幂等命中的本人订单快照：id、order_no、status、明细、地址、金额 |
| myDetail | `{id:订单主键}` | 本人订单快照、payment_methods 15 项、payment_placeholder=true |

问号表示可选字段，不作为实际 JSON 键名。数量限 1～999；报价 token 为服务端生成的 32 位十六进制字符串，请求号为 8～80 位字母/数字/下划线/连字符。所有响应外层继续使用 `{code,msg,data,success}`。该 id 是订单主键，order_no 只用于展示业务编号。

### 28.8 当前进度与验证记录

文档随实现同步更新，以下只记录已完成结果；未验证项明确保留待检查，收尾时再更新。

| 项目 | 当前进度 |
|---|---|
| 地址真实接口 | **55 次请求通过**：本人维护、默认、手机号、地区链、越权与后台只读；临时会员/地址/会话已清理 |
| 订单旧表迁移 | **已实际执行成功**：补金额/券/幂等/商品快照列与唯一索引，旧记录保留 |
| 优惠券规则静态/内存检查 | **通过**：类型、有效期、范围小计门槛、面额截断、Decimal、状态和契约 |
| 新页面与路由 | **SFC/模拟交互通过**，5 个新路由登记齐全，支付 15 项只弹窗 |
| 领取与订单真实事务联测 | **66 次请求通过**（60 次计数及 6 次并发）：发行/限领并发、满 99 减 30、邮费不凑门槛、范围外商品不凑门槛、超面额只抵商品、报价变化回滚、同键并发仅一单、最后库存并发仅一单、会员隔离、无地址拒绝、后台订单/用券与过期查询、管理员删未付款订单恢复库存和释放券、不同请求号/删单后旧报价均不能重放；临时会员/商品/类目/券/订单/领取/报价/会话已清理 |
| uni-app H5 production build | **通过**：HBuilderX 5.33 实际 production build 成功 |
| 浏览器页面与完整操作流 | **通过**：真实会员登录→首页领券→立即购买选规格→确认页默认地址→独立选券→99 减 30 应付 69、运费 0→地址列表/编辑/三级地区弹层→提交真实订单→15 种支付方式及 PayPay 占位弹窗；关闭弹窗订单仍未付款。另确认购物车进入同一确认页，已使用券不再可选。数据库读回实付 0、优惠 30、运费 0，持券 status=1、order_id/use_time 已写入。截图已保存 |
| 测试数据与临时资源清理 | **完成**：SQL 复核临时会员、商品、库存、规格、券、领取、订单/明细、地址、购物车均无残留；Redis 临时会话/报价按归属清除。临时验证/预览脚本及状态文件已删除，8310 预览服务停止，浏览器标签关闭并恢复视口；原有业务数据保留 |

真实接口累计 **121 次**：地址 55 次 + 本轮领取/订单 66 次。此前同一轮的 58/64 次及累计 119 次是阶段结果，不重复累计；浏览器真实操作已独立验证并通过，不再把构建成功代替页面操作验收。本轮接口和浏览器夹具均已清理并复核。

---

## 二十九、个人中心与本人资料维护

### 29.1 范围、现有数据与页面关系

这次把「我的」各入口接到真实本人数据，并优先完成参考图中的个人信息修改。主页负责展示和导航，设置页负责资料维护，订单/券/收藏/服务分别有独立页面；没有复制一份客户端会员或订单库。密码设置按要求是占位，手机号修改采用用户确认的「校验当前登录密码后保存」方案。

| 现有表 | 本模块用途 |
|---|---|
| `mal_member` | 当前会员昵称、头像、性别、手机号，以及每次请求的可用状态校验 |
| `sys_file` 与既有文件存储 | 头像文件信息与真实图片，会员头像 URL 存回 mal_member |
| `mal_order` / `mal_order_item` | 本人订单分组、数量、商品/金额/地址等历史快照 |
| `mal_coupon` / `mal_coupon_user` | 本人领取券及有效状态、使用订单和时间；规则仍见第二十七章 |
| `mal_favorite` / `mal_goods` | 本人收藏记录、实时商品展示和失效原因 |
| `mal_feedback` | 本人提交反馈及当时用户名/联系电话快照，后台仍查同一张表 |
| `mal_faq`、`sys_dict_type` / `sys_dict_data` | 常见问题、公开客服配置；不伪造客服号码或协议 |

本轮没有新增表或修改既有表结构，部署无需额外迁移；沿用前一轮订单字段时，仍需先完成 28.1 所述 install_checkout.py。`pages.json` 新增 11 页，工程从 18 页增至 29 页。

### 29.2 身份隔离与统一请求

所有新本人接口均为显式 POST，controller 只收 schema、调用 service、返回 `HttpResponse.success(data)`。除原有公开 FAQ 查询以外，不把会员资料、订单、收藏、反馈接口加入 WHITE_ROUTER。服务端从 Redis token 取 member_id，拒绝带后台 id 的管理员载荷，并读取数据库确认会员有效、status=1；客户端传 member_id/id/username/level/status 等额外身份或权限字段会被严格契约拒绝。

前端继续用 `api/member.js`、`order.js`、`favorite.js`、`marketing.js`、`feedback.js`、`faq.js` 的逐项请求，JSON 字段放 body；头像是 `uni.uploadFile` 的 multipart `file`，也带相同 token 并处理统一错误码。页面加载、更新和列表返回时核对 token、请求版本及卸载状态，避免切换账号后旧请求写入当前界面。手机号当前密码仅用于此次请求，页面隐藏/卸载或保存结束即清空，不写本地缓存。

统一 `api/request.js` 还检查请求发起时的 token：旧账号请求晚到 code=11000 时，不清除新账号 token；准备延后跳登录时再次确认没有新登录信息，避免旧响应把刚登录的新会员退出。此处有 3 项独立模拟检查通过。

### 29.3 个人主页、资料保存与头像

主页右上角齿轮进入 `pages/profile/settings`。设置表单先调 profile 回显数据库内容，修改成功用响应刷新本地 member_info 并通知 member:change；返回主页时 onShow 重读，昵称和头像无需重新登录就更新。登录用户名不随昵称或手机号改变。

| POST 路径 | 请求 | 成功结果与约束 |
|---|---|---|
| `/api/member/profile` | `{}` | 本人公开资料；不返回 password、创建人或其它后台审计字段 |
| `/api/member/updateProfile` | `{nickname? , gender?}` | 按提交字段更新本人；昵称 trim 后非空、最多 64 字符且无控制字符；gender 为严格整数 0/1/2 |
| `/api/member/uploadAvatar` | multipart `file` | 上传后直接保存本人 avatar；返回文件信息及完整 profile，不需要再传 URL 保存 |
| `/api/member/changeMobile` | `{password,mobile}` | 校验当前登录密码、手机号格式和其他账号占用后保存；返回完整本人资料 |
| `/api/member/logout` | `{}` | 删除当前 Redis 会话；前端清 token/资料再回登录页 |

问号表示可选字段，不是 JSON 键名。updateProfile 只开放 nickname/gender；头像 URL、文件 ID、密码、用户名和等级不能通过这个接口直接写入。部分字段更新持有会员行锁，同会员同时改昵称和性别不会互相覆盖未提交的字段。

- 昵称单独进入 nickname.vue 编辑，保存后返回设置；前后端均拒绝全空白，后端同时限制长度及控制字符。
- 性别底部 picker-view 提供「保密、男、女」，对应数据库 0、1、2；管理端 gender_name 对 0 仍按原字典返回「未知」，没有增加另一套存储编码。
- 头像支持 jpg/jpeg/png/gif/bmp/webp，大小大于 0 且不超过 **3×1024×1024 字节**，含 3MiB 边界；SVG 不作为会员头像接受。前端先检查文件大小，服务端再次核对扩展名、MIME 大类和文件签名。
- 头像在服务端固定放入当前会员的 `members/{member_id}/avatars` 目录，再保存本人 avatar。客户端不能提交其他会员的 URL 或任意外链来冒用文件；原来的通用 FileService 负责文件存储及 sys_file 入库。更换头像不会批量删除历史上传文件。
- 图片检查的实际边界是**签名匹配，不是完整像素解码**：PNG 检查头/IHDR/尾，JPEG 和 GIF 检查标记，BMP/WebP 检查文件头；未加入 Pillow，也未实现完整重编码、损坏像素或超大分辨率检测。后续生产图片处理应单独补解码与像素上限，不能把当前检查写成完整图像安全验证。

### 29.4 手机号和密码占位的业务边界

手机号按 `^1[3-9]\d{9}$` 校验中国大陆 11 位号码；先验证当前会员数据库中的 bcrypt 密码，再检查该号码没有被其他有效账号占用。写入使用当前会员锁和手机号索引范围锁；MySQL 1205/1213 并发锁冲突会回滚后最多重试三次，每次重试都重新校验，不吞掉真实占用错误。两会员同时绑定同一新号码的实测仅一个成功。

这表示已验证当前账号密码，**没有验证新手机号的短信归属**。界面不展示虚假的验证码输入或发送成功。手机号保存不改 username、不改登录密码，不把收货地址的收件人手机号或历史订单/反馈快照一起覆盖；这些字段各有自身业务含义。

password.vue 按参考保留手机号、验证码、新密码、确认密码的禁用展示，并明确「密码修改暂未开放」。没有修改密码请求、验证码发送或假保存成功；可前往服务中心。手机号修改成功后原密码仍可正常登录。

### 29.5 我的订单、数量角标与状态映射

主页同时读取 profile 和 `/order/mySummary {}`；summary 返回 `counts:{all,pay,send,receive,done}` 和 `coupon_counts:{unused,used,expired}`。角标超过 99 显示 99+，数量来自本人有效记录，不使用页面假数字。

| 页面 tab | 既有 order.status | 页面含义 |
|---|---|---|
| all | 全部状态 | 包含未付款、已取消、退款和收货等现有记录 |
| pay | 1 | 待付款 |
| send | 4 | 待发货（数据库已付款） |
| receive | 7 | 待收货（数据库已发货） |
| done | 8、9 | 已完成（用户或系统收货） |

`POST /api/order/myList {page:1,pageSize:20,tab:"all"}` 服务端分页，pageSize 允许 1～100，按 order_time/id 倒序。每条返回 id/order_no/status/status_name/order_time/order_amount(_text)/items/can_pay/can_delete，items 为下单时商品、规格、价格、数量和图片快照；订单主键 id 用于详情和支付，order_no 只展示。

列表点击进入 `pages/order/detail?id=订单ID`，继续调用既有 `/order/myDetail {id}`，只返回本人订单。详情展示收货、金额、商品、备注和当前状态等快照；当 status=1 时才显示去支付，进入既有 15 种方式占位页。没有把「待评价」混入已完成，也不伪造评价、确认收货或真实付款。

`POST /api/order/myDeleted {id}` 仅允许本人 status=2/3 的已取消记录，确认后物理删除该主单及明细；其它状态被拒绝。这是清理**已经取消的记录**，不是取消订单动作，不再补库存或释放券。未付款订单取消、超时关闭和补偿仍待独立实现；后台管理员删除本轮客户端未付款订单的恢复逻辑仍按 28.5 执行，不能将两种删除混为一谈。

### 29.6 本人优惠券、收藏与商品详情

`pages/profile/coupons?status=0/1/2` 调既有 `/api/coupon/myList {status}`，分别显示未使用、已使用、已过期。状态沿用领取表有效状态：未使用过了 end_time 按过期；已使用优先保留。个人中心的「未使用」不代表任意订单都能用，最终范围、门槛及折扣仍由确认订单校验。已使用券可查看 order_id 关联的本人订单。

此接口当前一次返回选定状态的全部 rows/rowTotal；客户端每次先显示 20 张，触底或加载更多再追加展示 20 张，**不是服务端分页**。不能把选券页的当前订单可用性和个人券页的持券状态混写为同一种状态。

| 收藏 POST 路径 | 请求 | 职责 |
|---|---|---|
| `/api/favorite/myList` | `{page:1,pageSize:20}` | 只返回本人收藏，服务端分页并关联当前商品 |
| `/api/favorite/myDeleted` | `{id:收藏记录ID}` | 确认后物理取消本人这一条收藏，不删除商品 |
| `/api/favorite/mySet` | `{goods_id,collected:true/false}` | 商品详情设置或取消本人收藏；会员锁使重复设置幂等 |

收藏条目里的 id 是收藏记录 ID，goods_id 才是商品 ID。商品有效且在售时进入原 `goods/detail?id=goods_id`；已删/已下架显示 invalid_reason、不可跳转，但允许取消收藏。设置 collected=true 只接受在售商品；取消按本人+商品清理历史重复记录。本人列表不会暴露其他会员收藏。

### 29.7 服务中心、意见反馈与常见问题

服务中心提供联系客服、意见反馈、常见问题。`POST /api/feedback/contact {}` 读取后台已有数据字典 **mall_public**，只公开白名单条目 `name/phone/qq/version/agreement`，不导出配置全集。没有配置时名称默认「商城服务中心」，版本回退服务端 VERSION，电话/QQ/协议如实显示暂未配置；不硬编码虚构号码。协议和 FAQ 答案按纯文本展开，不执行后台文本中的 HTML。

后台配置方式：在已有数据字典中创建类型 code=mall_public，然后以条目 lookup_code 填 name、phone、qq、version 或 agreement，在 lookup_value 写公开值，并保持类型和条目有效。沿用既有字典字段长度，不能把敏感配置或超长协议全文放进此接口期待自动公开；未列出的键即使存在也不会返回。

contact 同时返回反馈类型 `功能建议/商品问题/物流问题/其他`。`POST /api/feedback/mySubmit {feedback_type,content,mobile?}` 要求内容 trim 后非空、最多 2000 字，选填手机号须符合 11 位格式。member_id、username 由服务端本人会员生成；mobile 有填写则存填写值，否则取当前会员手机号，作为提交时快照。反馈真实写入 mal_feedback，后台原意见反馈页面可以看到，不另建同步记录。本轮不开放反馈图片或代他人提交；前端提交中禁重复，成功后显示已提交。

FAQ 复用已有公开 `/api/faq/list`：question 查询、page/pageSize 默认每页 20，触底加载和点击展开答案。没有新增第二份问题库。收藏/订单/券列表有空态、错误重试；反馈切换账号会清草稿及旧成功状态。

### 29.8 文件位置、当前验证与接手提示

| 文件或目录 | 职责 |
|---|---|
| `backend/app/api/v1/system/member/` | 本人 profile、昵称性别、头像上传、当前密码校验改手机 |
| `backend/app/api/v1/system/order/` | 本人列表、summary 状态数量、已取消记录删除；复用既有 checkout/detail |
| `backend/app/api/v1/system/favorite/` | 本人收藏分页/取消/幂等设置 |
| `backend/app/api/v1/system/feedback/` | 本人反馈入库与服务中心配置白名单 |
| `Mall_Front‑end_Page/pages/profile/` | 主页与设置、昵称、手机号、密码占位、券、收藏、服务、反馈、FAQ |
| `Mall_Front‑end_Page/pages/order/list.vue`、`detail.vue` | 本人订单分组、快照详情与既有支付入口 |
| `Mall_Front‑end_Page/pages/goods/detail.vue` | 既有商品详情补本人收藏设置，商品购买仍走原流程 |
| `Mall_Front‑end_Page/api/request.js` | 统一鉴权失败处理核对请求所属 token，保护账号切换后的新登录态 |

| 验证项目 | 本轮结果 |
|---|---|
| 会员资料真实 API | **59 次通过**：字段/越权/管理员/禁用限制、昵称性别并发部分更新、当前密码、同号抢绑、图片签名及精确 3MiB/超限边界；临时会员/头像文件与记录/会话/脚本已清理 |
| 订单/收藏/反馈真实 API | **56 次通过**：本人隔离、分页/状态/summary、非法字段、收藏设置幂等和失效商品、删除范围、反馈快照、公开配置白名单；临时数据/会话/脚本已清理 |
| 前端子页 SFC 与模拟交互 | **通过**：7 个列表/服务子页的 script/template/style 及相关 API，分页、券状态、失效收藏、反馈防重与 FAQ 搜索；统一 request.js 旧账号鉴权响应和延后登录跳转隔离另有 **3 项模拟通过** |
| H5 production build | **通过**：HBuilderX 5.33 全量 29 个页面编译成功；末尾合并后的最终 production build 再次返回 DONE / Build complete |
| 浏览器真实完整操作 | **通过**：390px 宽真实临时会员登录，主页订单/券各状态角标为 1；设置中昵称即时回显、PNG 头像真实保存、滚动选择女并保存、当前密码改手机号、密码禁用占位；订单 all/pay/send/receive/done 分组准确，详情可进入既有 15 项支付占位；未使用/已使用/已过期券各 1，收藏进入原商品详情；客服未配置如实显示、反馈真实提交且 SQL 确认本人/登录用户名/联系电话快照，FAQ 展开及「快递」关键词搜索，退出回登录。截图 profile-home.png 已保存 |
| 本轮全部临时资源 | **清理完成**：接口及浏览器临时会员、商品/库存、订单/明细、券/领取、收藏、反馈、头像 sys_file 与物理文件、Redis 会话均已清理；SQL 复核 10 项全为 0。预览脚本、状态和临时 PNG 已删，8310 服务停止，浏览器标签关闭且视口恢复；原有业务数据保留 |

本轮后端真实检查 **115 次 = 59 + 56**，与上一轮 121 次属于不同测试轮次，不重复累计成同一轮结果；浏览器操作和脚本模拟独立记录，不再加进 API 请求数。接手时先看本节验证状态，再按页面→接口→对应表追查；待完成项不以页面或构建存在代替验收。

---

## 三十、后台首页商城统计

### 30.1 页面与接口

后台首页仍在 `frontend/src/views/home/index.vue`。欢迎卡片使用后台用户 store 的 nickname，缺省时依次取 username 和「管理员」；客户端会员资料不参与后台问候。日期、时间和时段问候随本地时钟更新，页面缓存离开或卸载时停止定时器，返回首页时刷新时间与统计。

登录页右侧 `views/login/index.vue` 标题为「后台商场管理系统」，左侧 `views/login/component/LoginLeftView.vue` 标题为「后台商场管理平台」。右侧不再被浏览器缓存的旧 globalTitle 覆盖；全局主题、浏览器页签命名与登录校验仍沿用原逻辑。

统计区按用户最终要求沿用原 UI：8px 圆角白色 el-card、shadow=hover、悬浮上移效果、56px 渐变图标底块、32px 白色图标、28px 数值和14px 名称，不采用参考图中的方形简化卡片。仅替换原用户/菜单/角色/在线人数对应的显示名称和数量；下方原系统信息、快捷操作、通知和待办演示区不再显示。栅格沿用 xs=24、sm=12、md/lg/xl=6；欢迎条在手机窄屏纵向排布。

复用 `frontend/src/api/useSystemApi/statistic.ts` 中显式 POST 请求；后端遵循 `system/statistic/{model,schema,service,controller}.py` 分层并在原 system/router.py 注册。该模块只做既有表的聚合查询，不创建统计实体表，也不需要菜单初始化或迁移。

```text
POST /api/statistic/countStatistic
body: {}
data: {users: 整数, goods: 整数, products: 整数, orders: 整数}
```

### 30.2 统计口径、权限与失败处理

| 卡片 | 返回字段 | 既有数据表 | 口径 |
|---|---|---|---|
| 用户数量 | users | mal_member | enabled_flag=true 的会员数，不是后台 sys_user 账号数；含禁用/注销状态的现存有效记录 |
| 商品数量 | goods | mal_goods | enabled_flag=true 的商品条目数，包含上架和未上架 |
| 货品数量 | products | mal_goods_product | enabled_flag=true 的 SKU 记录数，不对 quantity 求和，零库存仍是一条货品 |
| 订单数量 | orders | mal_order | enabled_flag=true 的订单数，包含未付款、取消、付款等所有已有状态 |

一条 SQL 中读取四个 count，返回同一读快照的整数总量，不载入业务明细。接口要求有效后台账号会话，不要求另外具有四个业务模块的操作权限，不加入公开白名单；客户端会员 token 不能读取后台总量。请求只允许空对象，不能传入会员 ID 或任意过滤条件。

首页进入/从缓存返回时重新请求，加载或失败时以「—」占位而非显示伪造的 0，失败可点击重新加载。过期响应按请求版本、页面活跃状态及当前后台 token 过滤。

### 30.3 本次验证与接手状态

- 前端：production build 通过；构建保留原项目的背景图/字体引用、已有全局 deep 样式及大包提示，本次首页没有新增构建错误。
- 后端：**12 次真实 ASGI/API 请求通过**，四项 count 与现库独立 SQL 一致（本次快照 users=3、goods=2、products=2、orders=1；数值随业务数据变化，不写死）。验证无/无效 token、会员 token、不存在的后台用户、额外 member_id/page/price/enabled_flag、GET 方法和缺失 body 均不能通过；现库只有超级管理员，普通后台分支通过临时 mock is_super_admin=false 验证，不宣称新建或实际登录了另一个普通管理员。
- 浏览器：两处登录标题分别展示「后台商场管理系统」「后台商场管理平台」；真实后台短期会话进入首页，问候、日期和时钟保留，统计值与接口一致。1920px 下四张卡片同一行，900px 下两行两列，390px 下四行单列，均无页面横向溢出；复核卡片 8px 圆角、原渐变图标、数值和名称顺序，最终手机验收图保存为 admin-home-mobile.png。
- 收尾：统计测试全程只读，没有插入或修改业务数据；测试与预览 Redis 会话已显式撤销并复核无效，临时脚本、预览 JSON 和构建日志已删除。临时预览服务停止、浏览器临时标签关闭且视口恢复。

---

## 三十一、统计报表

### 31.1 模块定位

后台「统计报表」一级菜单（sort=50），三个只读图表页面：用户统计 / 订单统计 / 商品统计。
**不建统计表**，全部按天实时聚合现有业务表（`mal_member` / `mal_order` / `mal_order_item`），数据随客户端下单即时变化。

### 31.2 接口

前缀 `/api/statistic`，均为 POST + 空对象或 `{days}`，需要有效后台会话（`AuthPermission(check_data_scope=False)`，不额外要求业务权限）。

| 接口 | 说明 | 返回 |
|---|---|---|
| `/userChart` | 每日新增会员数 | `dates[]` + `series.user_count[]` |
| `/orderChart` | 每日订单量、下单用户数、订单总额、客单价 | `series.order_count/buyer_count/order_amount/avg_amount` |
| `/goodsChart` | 每日订单量、下单货品数量、下单货品总额 | `series.order_count/goods_quantity/goods_amount` |
| `/countStatistic` | 首页四张总量卡片（原有） | 保持不变 |

**`days` 参数**：`0`=全部历史（默认），`>0`=最近 N 天（含今天），取值范围 0~3650，超范围返回参数错误。

### 31.3 统计口径

| 指标 | 口径 |
|---|---|
| 用户增长数 | `mal_member` 按 `DATE(creation_date)` 分组计数，只统计 `enabled_flag=1` |
| 订单量 | `mal_order` 按 `DATE(order_time)` 分组计数 |
| 下单用户 | 同一天 `COUNT(DISTINCT member_id)` |
| 订单总额 | 同日 `SUM(total_amount)`（订单应付金额，不是实付） |
| 客单价 | 订单总额 ÷ 订单量，保留两位；当天无单时为 0 |
| 下单货品数量 | `mal_order_item.quantity` 按订单日期汇总 |
| 下单货品总额 | `SUM(price * quantity)`，即明细金额合计 |

> 横轴只出现**有数据的日期**（不补零），和参考稿一致；数据量少时只有一个点属于正常现象。

### 31.4 前端实现

| 文件 | 职责 |
|---|---|
| `frontend/src/components/statisticChart/index.vue` | ECharts 通用封装（init / setOption / resize / dispose） |
| `views/system/statistics/user/index.vue` | 用户统计：柱状图 + 数值标签 |
| `views/system/statistics/order/index.vue` | 订单统计：四条平滑折线（订单量/下单用户/订单总额/客单价） |
| `views/system/statistics/goods/index.vue` | 商品统计：三条平滑折线 |
| `api/useSystemApi/statistic.ts` | 新增 `userChart / orderChart / goodsChart` |

- 每页顶部有「近 7 / 30 / 90 天 / 全部」区间切换，切换即重新请求
- 无数据时显示 `el-empty`，有数据才渲染图表
- 订单/商品页底部有一行统计口径说明
- 已按 900px 断点做窄屏适配

### 31.5 菜单安装

```powershell
cd backend
.\.venv\Scripts\python.exe -X utf8 -m app.scripts.install_statistics
```

幂等：只同步 `sys_menu.json` 里的 `/statistics` 菜单树并绑定管理员，不建表、不写业务数据。
菜单有缓存，安装后需**退出重新登录**才会出现。

---

## 三十二、后续待开发

1. **真实支付接入**：当前已建未付款订单并提供 15 项占位；需平台下单、支付回调验签、对账，不能由前端确认“已付款”
2. **客户端订单取消/超时释放**：本人订单列表、详情和已取消记录删除已完成；取消/关单及库存/优惠券补偿事务仍待做
3. **注册赠券与兑换码**：普通首页领券已完成，赠送和兑换需独立验证流程，不使用普通 claim 冒充
4. **首页广告/专题/团购落地动作**：轮播业务跳转、开团参团等尚待完成
5. **搜索热门词**：需补公开关键词查询并展示
6. **客户端商品评价与售后申请**：写入现有评论/售后表，后台继续查看和审核
7. **客户端足迹与更多反馈能力**：常见问题、本人收藏与文字反馈已接通；浏览足迹页面、反馈图片及反馈历史/处理进度仍待完善
8. **后台订单收款/发货/退款真实动作**：仍是原占位，后续与真实支付和履约流程一起实现
9. 登录图形/短信验证码、第三方登录等

> 继续按 CODING_GUIDE.md 的目录、显式接口、分层、验证和文档步骤实现后续模块。
