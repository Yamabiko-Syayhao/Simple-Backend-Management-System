# 开发规范（新增模块照着抄就行）

> 目标：任何人 / 任何模型接手，都能写出 **风格一致**的代码。
> 业务细节看 `README02.md`；本文只讲 **怎么写**。

---

## 0. 一句话流程

新增一个后台模块 = **后端四件套 → 注册路由 → 前端 api → 前端页面 → 菜单入库 → 冒烟测试 → 补文档**。

---

## 1. 目录约定（照着放，别自创）

### 后端 `backend/app/api/v1/system/<模块>/`

| 文件 | 职责 | 禁止 |
|---|---|---|
| `__init__.py` | 空文件 | — |
| `model.py` | ORM 模型，继承 `Base`，含 `_build_stmt` / `get_list` | 写 HTTP 逻辑 |
| `schema.py` | Pydantic 契约，继承 `BaseSchema`（`XxxQuery / XxxIn / XxxDel`） | 访问数据库 |
| `service.py` | 业务逻辑、`_decorate` 派生字段、导出 | 直接用 `Request` |
| `controller.py` | `APIRouter(prefix="/xxx")` + 调 service + `HttpResponse` | 写 SQL |

注册：`app/api/v1/system/router.py` 加 **两行**（import + `include_router`）。

### 前端

| 内容 | 位置 |
|---|---|
| 接口封装 | `frontend/src/api/useSystemApi/<模块>.ts` → `export function useXxxApi()` |
| 列表页 | `frontend/src/views/system/<模块>/index.vue` |
| 弹窗 | 同目录 `<模块>Dialog.vue`，通过 `defineExpose({ openDialog })` 暴露 |
| 菜单 | 数据库 `sys_menu` + `app/scripts/data/sys_menu.json`（两处都要改） |

命名：多词模块用 camelCase（`afterSale`、`searchHistory`）；后端包名用 snake_case（`after_sale`）。

**最佳参考实现**（不确定就打开照抄）：
- 简单增删改查 + 图片上传 → `brand/`
- 树形结构 → `category/`、`region/`
- 复杂列表 + 弹窗 + 占位接口 → `order/`
- 批量操作 → `after_sale/`

---

## 2. 后端范式

### 2.1 表与模型

- 表名统一 `mal_` 前缀（会员/地址等商城业务）。
- 继承 `app.models.base.Base`，自带 `id / creation_date / created_by / updation_date / updated_by / enabled_flag / trace_id`。
- **不用手写建表 SQL**：启动时 `ImportUtil` 扫 `model.py` + `create_all` 自动建表。

```python
class Xxx(Base):
    __tablename__ = "mal_xxx"
    name = Column(String(128), nullable=False, comment="名称", index=True)

    @classmethod
    async def get_list(cls, params):
        return await cls.pagination(cls._build_stmt(params))

    @classmethod
    def _build_stmt(cls, params):
        q = [cls.enabled_flag.is_(True)]
        if getattr(params, "name", None):
            q.append(cls.name.like(f"%{params.name}%"))
        return (
            select(cls.get_table_columns())
            .where(*q)
            .order_by(cls.id.asc() if getattr(params, "sort_order", None) == "asc" else cls.id.desc())
        )
```

### 2.2 Controller（固定 5 个接口）

```python
XxxRouter = APIRouter(prefix="/xxx", tags=["中文名"])

@XxxRouter.post("/list", description="列表")
async def xxx_list(params: XxxQuery, _auth=Depends(AuthPermission(["xxx:query"]))):
    data = await XxxService.list(params)
    return await HttpResponse.success(data)
```

| 接口 | 方法 | 权限码 |
|---|---|---|
| `/list` | POST | `xxx:query` |
| `/detail` | POST | `xxx:query`（加 `check_data_scope=False`） |
| `/saveOrUpdate` | POST | `xxx:add` / `xxx:edit` |
| `/deleted` | POST | `xxx:delete` |
| `/export` | POST | `xxx:export` |

### 2.3 硬性规定

| 事项 | 写法 |
|---|---|
| 分页 | `page / pageSize` 放 **body**，`Base.pagination` 自动读；返回 `{rows,rowTotal,...}` |
| 排序 | `XxxQuery` 加 `sort_order`，`_build_stmt` 按它切 `asc/desc` |
| 删除 | **物理删除**：`await Xxx.delete(id, True)` |
| 派生字段 | service 里 `_decorate(row)` 补 `xxx_name`，前端不维护字典 |
| 必填校验 | service 里 `raise ValueError("xxx不能为空")`，全局中间件转 `code=-1` |
| 金额 | `Numeric(12,2)`，返回前 `float()` |
| 导出 | openpyxl 生成 → `StreamingResponse` + `filename*=UTF-8''` |
| 公开接口 | 不加 `AuthPermission`，并把路径加进 `setting.py` 的 `WHITE_ROUTER` |

---

## 3. 前端范式

### 3.1 页面骨架（照抄）

```
<div class="xxx-page">
  <div class="xxx-panel">
    <div class="xxx-toolbar"> 搜索框 + 查找 / 添加 / 导出 </div>
    <el-table border :header-cell-style="headerCellStyle" :cell-style="cellStyle">…</el-table>
    <div class="xxx-pagination"><el-pagination layout="total, sizes, prev, pager, next, jumper" background /></div>
  </div>
  <XxxDialog ref="xxxDialogRef" @getList="getList" />
</div>
```

- 类名前缀 = 模块名（`.faq-page` / `.keyword-toolbar`），**scoped scss**。
- 主色 `#1890ff`，表格头 `#f7f9fc`，边框 `#e8edf3`。
- 按钮：编辑蓝、删除红、通过绿（`#2fc96b`）。

### 3.2 接口调用

```ts
useXxxApi().getList(payload).then((res: any) => {
  state.listData = res.data?.rows || []
  state.total = res.data?.rowTotal || 0
})
```

- `code=0` 由拦截器直接返回 `data`，非 0 已弹 toast 并 reject。
- 需要**自己处理错误提示**时传 `silent: true`（用 `ElNotification` 弹右上角）。
- 导出：`responseType: 'blob'` + `createObjectURL` 下载。
- 上传：`${getApiBaseUrl()}/file/upload`（`getApiBaseUrl()` 已含 `/api`，**别再拼 `/api`**）。

### 3.3 固定交互

| 场景 | 写法 |
|---|---|
| 分页 | 默认 `pageSize: 20`，`@size-change` / `@current-change` 都重置或刷新 |
| 排序 | 列 `sortable="custom"` + 表格 `@sort-change` + `:default-sort`，**禁用前端默认排序** |
| 删除 | `ElMessageBox.confirm` → 接口 → `ElNotification({title:'成功',message:'删除成功',type:'success',position:'top-right'})` → 刷新；当前页删空回退一页 |
| 弹窗 | `:close-on-click-modal="false"`、`destroy-on-close`；`el-dialog` 的响应式要写**非 scoped** `<style>` |
| 校验 | `el-form :rules`，必填项带红星 |

### 3.4 响应式（每个页面必做）

- `@media (max-width: 900px)`：搜索栏 `flex-wrap`，输入框 `flex: 1 1 calc(50% - 4px)`，表格横向滚动
- `@media (max-width: 560px)`：输入框整行，按钮 `flex: 1 1 40%`
- 列一律**不要** `fixed="right"`（会脱离表格滚动）

---

## 4. 菜单与权限

1. 后台「系统设置 → 菜单管理」加菜单，或直接插 `sys_menu`。
2. **同时**把同样的结构写进 `app/scripts/data/sys_menu.json`（重置数据库时用）。
3. 按钮权限写成 `menu_type=20` 的子节点，`roles` 填权限码。
4. 新菜单要绑定到「管理员」角色（`sys_role_menu`）。
5. 菜单有缓存：改完要**退出重新登录**才生效。

---

## 5. 完成前必做

```bash
# 后端：临时脚本调接口冒烟（TestClient），验证列表/筛选/详情/增改/删除/导出
cd backend && .\.venv\Scripts\python.exe _verify_xxx.py

# 前端：编译通过
cd frontend && npm run build
```

自检清单：
- [ ] 接口 5 个齐、权限码齐
- [ ] 删除是物理删除且查库为 0
- [ ] 导出是合法 xlsx（文件头 `PK`）
- [ ] 页面窄屏能横向滚动、无 `fixed` 列
- [ ] 菜单已入库 + 已写 `sys_menu.json`
- [ ] 临时脚本已删除

---

## 6. 文档

每完成一个模块，更新 `README02.md` **三处**：
1. 第二章「模块清单」状态 ⬜ → ✅
2. 新增对应章节（数据模型 / 接口 / 业务规则 / 页面 / 客户端对接）
3. 变更记录追加一条（编号 + 做了什么 + 验证结果）

---

## 7. 已踩过的坑（别再踩）

| 坑 | 正解 |
|---|---|
| `getApiBaseUrl()` 又拼 `/api` → 404 | 它已含 `/api`，只拼 `/file/upload` |
| el-table 默认 `sortable` 只排当前页 | 用 `sortable="custom"` + 服务端排序 |
| `fixed="right"` 让操作列悬浮 | 去掉 |
| 编辑弹窗藏字段导致数据卡死 | 能改的字段都要能改（如类目的父类目） |
| CORS 预检 400 | 已在 `init_app.py` 处理，改中间件顺序时别破坏 |
| 业务错误弹两次提示 | 接口传 `silent: true`，页面自己弹 |
