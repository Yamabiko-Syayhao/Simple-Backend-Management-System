<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="700px"
    class="coupon-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="!state.saving"
    :show-close="!state.saving"
    destroy-on-close
    @close="onDialogClose"
  >
    <el-form
      ref="formRef"
      v-loading="state.fetching"
      :model="state.ruleForm"
      :rules="rules"
      :disabled="state.fetching || state.saving || state.loadFailed"
      label-width="125px"
      class="coupon-dialog-form"
    >
      <el-form-item label="优惠券名称" prop="name"
        ><el-input v-model="state.ruleForm.name" maxlength="128"
      /></el-form-item>
      <el-form-item label="介绍" prop="description"
        ><el-input v-model="state.ruleForm.description" maxlength="500"
      /></el-form-item>
      <el-form-item label="标签" prop="tag"
        ><el-input v-model="state.ruleForm.tag" maxlength="128"
      /></el-form-item>
      <el-form-item label="最低消费" prop="min"
        ><el-input v-model="state.ruleForm.min"
          ><template #append>元</template></el-input
        ></el-form-item
      >
      <el-form-item label="满减金额" prop="discount"
        ><el-input v-model="state.ruleForm.discount"
          ><template #append>元</template></el-input
        ></el-form-item
      >
      <el-form-item label="每人限领" prop="limit"
        ><el-input v-model="state.ruleForm.limit"
          ><template #append>张</template></el-input
        ></el-form-item
      >
      <el-form-item label="分发类型" prop="type"
        ><el-select v-model="state.ruleForm.type" class="coupon-dialog-select"
          ><el-option :value="0" label="通用领券" /><el-option
            :value="1"
            label="注册赠券" /><el-option
            :value="2"
            label="兑换码" /></el-select
      ></el-form-item>
      <el-form-item label="优惠券数量" prop="total"
        ><el-input v-model="state.ruleForm.total"
          ><template #append>张</template></el-input
        ></el-form-item
      >
      <el-form-item label="有效期" prop="time_type">
        <div class="coupon-time-field">
          <el-radio-group
            v-model="state.ruleForm.time_type"
            @change="clearTimeValidation"
            ><el-radio-button :value="0">领券相对天数</el-radio-button
            ><el-radio-button :value="1"
              >指定绝对时间</el-radio-button
            ></el-radio-group
          >
          <el-form-item
            v-if="state.ruleForm.time_type === 0"
            prop="days"
            class="coupon-time-input"
            ><el-input v-model="state.ruleForm.days"
              ><template #append>天</template></el-input
            ></el-form-item
          >
          <div v-else class="coupon-date-range">
            <el-form-item prop="start_time"
              ><el-date-picker
                v-model="state.ruleForm.start_time"
                type="datetime"
                placeholder="选择日期"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
            /></el-form-item>
            <span>至</span>
            <el-form-item prop="end_time"
              ><el-date-picker
                v-model="state.ruleForm.end_time"
                type="datetime"
                placeholder="选择日期"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
            /></el-form-item>
          </div>
        </div>
      </el-form-item>
      <el-form-item label="商品限制范围" prop="goods_type">
        <div class="coupon-scope-field">
          <el-radio-group
            v-model="state.ruleForm.goods_type"
            @change="onScopeChange"
            ><el-radio-button :value="0">全场通用</el-radio-button
            ><el-radio-button :value="1">指定分类</el-radio-button
            ><el-radio-button :value="2"
              >指定商品</el-radio-button
            ></el-radio-group
          >
          <template v-if="state.ruleForm.goods_type === 1">
            <div class="coupon-scope-picker">
              <el-cascader
                v-model="state.selectedCategoryId"
                :options="state.categoryOptions"
                :props="{
                  value: 'id',
                  label: 'name',
                  emitPath: false,
                  checkStrictly: true,
                }"
                placeholder="请选择分类名称"
                clearable
                filterable
                :disabled="state.categoryLoading"
              />
              <el-button @click="addCategory">添加</el-button>
            </div>
            <el-table
              :data="state.categories"
              border
              empty-text="暂无数据"
              :header-cell-style="scopeHeaderStyle"
            >
              <el-table-column label="分类名称" min-width="170" align="center"
                ><template #default="{ row }">{{
                  row.path_name || row.name
                }}</template></el-table-column
              >
              <el-table-column label="操作" width="90" align="center"
                ><template #default="{ $index }"
                  ><el-button
                    type="primary"
                    link
                    @click="state.categories.splice($index, 1)"
                    >删除</el-button
                  ></template
                ></el-table-column
              >
            </el-table>
          </template>
          <template v-if="state.ruleForm.goods_type === 2">
            <div class="coupon-scope-picker">
              <el-select
                v-model="state.selectedGoodsId"
                filterable
                remote
                :remote-method="searchGoods"
                :loading="state.goodsLoading"
                placeholder="商品名称/商品编号"
                clearable
                @visible-change="onGoodsSelectVisible"
              >
                <el-option
                  v-for="goods in state.goodsOptions"
                  :key="goods.id"
                  :value="goods.id"
                  :label="goodsLabel(goods)"
                  ><div class="coupon-goods-option">
                    <span>{{ goods.name }}</span
                    ><span class="coupon-goods-sn"
                      >NO.{{ goods.goods_sn || goods.id }}</span
                    >
                  </div></el-option
                >
              </el-select>
              <el-button @click="addGoods">添加</el-button>
            </div>
            <el-table
              :data="state.goods"
              border
              empty-text="暂无数据"
              :header-cell-style="scopeHeaderStyle"
            >
              <el-table-column
                prop="name"
                label="商品名称"
                min-width="140"
                align="center"
              />
              <el-table-column
                prop="goods_sn"
                label="商品编号"
                min-width="100"
                align="center"
              />
              <el-table-column label="操作" width="75" align="center"
                ><template #default="{ $index }"
                  ><el-button
                    type="primary"
                    link
                    @click="state.goods.splice($index, 1)"
                    >删除</el-button
                  ></template
                ></el-table-column
              >
            </el-table>
          </template>
        </div>
      </el-form-item>
      <el-form-item v-if="state.editType === 'edit'" label="状态" prop="status"
        ><el-select v-model="state.ruleForm.status" class="coupon-dialog-select"
          ><el-option :value="0" label="正常" /><el-option
            :value="1"
            label="已过期" /><el-option :value="2" label="已下架" /></el-select
      ></el-form-item>
    </el-form>
    <template #footer
      ><div class="coupon-dialog-footer">
        <el-button :disabled="state.saving" @click="state.visible = false"
          >取消</el-button
        ><el-button
          type="primary"
          :loading="state.saving"
          :disabled="state.fetching || state.loadFailed"
          @click="onSubmit"
          >确定</el-button
        >
      </div></template
    >
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'CouponDialog' });
import { nextTick, onBeforeUnmount, reactive, ref } from 'vue';
import { ElMessage, ElNotification } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import { useCouponApi } from '/@/api/useSystemApi/coupon';
import { useCategoryApi } from '/@/api/useSystemApi/category';
import { useGoodsApi } from '/@/api/useSystemApi/goods';

interface CategoryRow {
  id: number;
  name: string;
  parent_id?: number;
  path_name?: string;
  children?: CategoryRow[];
}
interface GoodsRow {
  id: number;
  name: string;
  goods_sn: string;
}
const emit = defineEmits(['getList']);
const formRef = ref<FormInstance>();
const blankForm = () => ({
  id: undefined as number | undefined,
  name: '',
  description: '',
  tag: '',
  min: 0 as string | number,
  discount: 0 as string | number,
  limit: 1 as string | number,
  type: 0,
  total: 0 as string | number,
  time_type: 0,
  days: 0 as string | number,
  start_time: '' as string | null,
  end_time: '' as string | null,
  goods_type: 0,
  status: 0,
});
const state = reactive({
  visible: false,
  saving: false,
  fetching: false,
  loadFailed: false,
  editType: 'add' as 'add' | 'edit',
  ruleForm: blankForm(),
  categoryLoading: false,
  categoryOptions: [] as CategoryRow[],
  categoryRows: [] as CategoryRow[],
  selectedCategoryId: undefined as number | undefined,
  categories: [] as CategoryRow[],
  goodsLoading: false,
  goodsOptions: [] as GoodsRow[],
  selectedGoodsId: undefined as number | undefined,
  goods: [] as GoodsRow[],
});
const scopeHeaderStyle = {
  background: '#f7f9fc',
  color: '#909399',
  textAlign: 'center',
};
const moneyValidator = (
  _rule: any,
  value: any,
  callback: (error?: Error) => void
) => {
  if (
    !/^\d+(\.\d{1,2})?$/.test(String(value)) ||
    !Number.isFinite(Number(value)) ||
    Number(value) > 9999999999.99
  )
    callback(new Error('请输入非负金额，最多两位小数'));
  else callback();
};
const integerValidator =
  (minimum: number) =>
  (_rule: any, value: any, callback: (error?: Error) => void) => {
    if (
      !/^\d+$/.test(String(value)) ||
      !Number.isSafeInteger(Number(value)) ||
      Number(value) < minimum ||
      Number(value) > 2147483647
    )
      callback(
        new Error(minimum === 1 ? '请输入大于等于 1 的整数' : '请输入非负整数')
      );
    else callback();
  };
const dateValidator = (
  _rule: any,
  _value: any,
  callback: (error?: Error) => void
) => {
  if (state.ruleForm.time_type !== 1) {
    callback();
    return;
  }
  const start = parseDate(state.ruleForm.start_time),
    end = parseDate(state.ruleForm.end_time);
  if (!Number.isFinite(start) || !Number.isFinite(end))
    callback(new Error('请选择完整的起止日期时间'));
  else if (end <= start) callback(new Error('结束时间必须晚于开始时间'));
  else callback();
};
const rules: FormRules = {
  name: [
    {
      required: true,
      whitespace: true,
      message: '请输入优惠券名称',
      trigger: 'blur',
    },
  ],
  min: [{ validator: moneyValidator, trigger: 'blur' }],
  discount: [{ validator: moneyValidator, trigger: 'blur' }],
  limit: [{ validator: integerValidator(1), trigger: 'blur' }],
  total: [{ validator: integerValidator(0), trigger: 'blur' }],
  days: [
    {
      validator: (_r: any, v: any, cb: any) =>
        state.ruleForm.time_type === 0 ? integerValidator(0)(_r, v, cb) : cb(),
      trigger: 'blur',
    },
  ],
  start_time: [{ validator: dateValidator, trigger: 'change' }],
  end_time: [{ validator: dateValidator, trigger: 'change' }],
};
function parseDate(value: string | null) {
  return value ? new Date(value.replace(' ', 'T')).getTime() : Number.NaN;
}
const clearTimeValidation = () =>
  nextTick(() =>
    formRef.value?.clearValidate(['days', 'start_time', 'end_time'])
  );
let dialogRequestId = 0;
let goodsRequestId = 0;
let goodsTimer: ReturnType<typeof setTimeout> | undefined;

const loadCategories = async (requestId: number) => {
  state.categoryLoading = true;
  try {
    const res: any = await useCategoryApi().getList();
    if (requestId !== dialogRequestId || !state.visible) return;
    const rows = (res.data?.rows || []) as CategoryRow[];
    const lookup = new Map(rows.map((row) => [row.id, row]));
    state.categoryRows = rows.map((row) => ({
      ...row,
      path_name:
        row.parent_id && lookup.get(row.parent_id)
          ? `${lookup.get(row.parent_id)!.name}>${row.name}`
          : row.name,
    }));
    const nodes = state.categoryRows.map((row) => ({
      ...row,
      children: [] as CategoryRow[],
    }));
    const nodeMap = new Map(nodes.map((row) => [row.id, row]));
    const roots: CategoryRow[] = [];
    nodes.forEach((node) => {
      if (node.parent_id && nodeMap.has(node.parent_id))
        nodeMap.get(node.parent_id)!.children.push(node);
      else roots.push(node);
    });
    nodes.forEach((node) => {
      if (!node.children.length) delete (node as CategoryRow).children;
    });
    state.categoryOptions = roots;
  } catch {
    /* 统一拦截器提示，已有范围仍可回显。 */
  } finally {
    if (requestId === dialogRequestId) state.categoryLoading = false;
  }
};

const openDialog = async (editType: 'add' | 'edit', row?: { id: number }) => {
  const requestId = ++dialogRequestId;
  goodsRequestId++;
  if (goodsTimer) clearTimeout(goodsTimer);
  state.editType = editType;
  state.ruleForm = blankForm();
  state.categories = [];
  state.goods = [];
  state.goodsOptions = [];
  state.categoryRows = [];
  state.categoryOptions = [];
  state.selectedCategoryId = undefined;
  state.selectedGoodsId = undefined;
  state.goodsLoading = false;
  state.saving = false;
  state.loadFailed = false;
  state.fetching = true;
  state.visible = true;
  await nextTick();
  if (requestId !== dialogRequestId || !state.visible) return;
  formRef.value?.clearValidate();
  const categoriesTask = loadCategories(requestId);
  try {
    if (editType === 'edit') {
      if (!row?.id) {
        state.loadFailed = true;
        ElMessage.error('优惠券不存在，请刷新列表');
        return;
      }
      const res: any = await useCouponApi().getDetail({ id: row.id });
      if (requestId !== dialogRequestId || !state.visible) return;
      const data = res.data || {};
      if (!data.id) {
        state.loadFailed = true;
        ElMessage.error('优惠券不存在，请刷新列表');
        return;
      }
      state.ruleForm = {
        id: data.id,
        name: data.name || '',
        description: data.description || '',
        tag: data.tag || '',
        min: data.min ?? 0,
        discount: data.discount ?? 0,
        limit: data.limit ?? 1,
        type: data.type ?? 0,
        total: data.total ?? 0,
        time_type: data.time_type ?? 0,
        days: data.days ?? 0,
        start_time: data.start_time || '',
        end_time: data.end_time || '',
        goods_type: data.goods_type ?? 0,
        status: data.status ?? 0,
      };
      state.categories = data.categories || [];
      state.goods = data.goods || [];
      state.goodsOptions = [...state.goods];
    }
    await categoriesTask;
  } catch {
    if (requestId === dialogRequestId) state.loadFailed = true;
  } finally {
    if (requestId === dialogRequestId) state.fetching = false;
  }
};
const onDialogClose = () => {
  dialogRequestId++;
  goodsRequestId++;
  if (goodsTimer) clearTimeout(goodsTimer);
  state.goodsLoading = false;
};
const addCategory = () => {
  if (!state.selectedCategoryId) {
    ElMessage.warning('请先选择商品分类');
    return;
  }
  const category = state.categoryRows.find(
    (row) => row.id === state.selectedCategoryId
  );
  if (!category) {
    ElMessage.warning('请先选择商品分类');
    return;
  }
  if (state.categories.some((row) => row.id === category.id)) {
    ElMessage.warning('该商品分类已添加');
    return;
  }
  state.categories.push({ ...category });
  state.selectedCategoryId = undefined;
};
const goodsLabel = (goods: GoodsRow) =>
  `${goods.name} NO.${goods.goods_sn || goods.id}`;
const loadGoods = async (
  keyword: string,
  requestId: number,
  currentDialogId: number
) => {
  state.goodsLoading = true;
  try {
    // 复用商品列表两种现有筛选，按名称或编号检索后合并。
    const filters = keyword ? [{ name: keyword }, { goods_sn: keyword }] : [{}];
    const results = await Promise.all(
      filters.map((filter) =>
        useGoodsApi().getList({ ...filter, page: 1, pageSize: 20 })
      )
    );
    if (
      requestId !== goodsRequestId ||
      currentDialogId !== dialogRequestId ||
      !state.visible
    )
      return;
    const unique = new Map<number, GoodsRow>();
    results.forEach((res: any) =>
      (res.data?.rows || []).forEach((goods: GoodsRow) =>
        unique.set(goods.id, goods)
      )
    );
    state.goodsOptions = [...unique.values()];
  } catch {
    /* 统一拦截器提示。 */
  } finally {
    if (requestId === goodsRequestId && currentDialogId === dialogRequestId)
      state.goodsLoading = false;
  }
};
const searchGoods = (query: string) => {
  if (goodsTimer) clearTimeout(goodsTimer);
  const requestId = ++goodsRequestId,
    currentDialogId = dialogRequestId;
  state.goodsLoading = true;
  goodsTimer = setTimeout(() => {
    loadGoods(query.trim(), requestId, currentDialogId);
  }, 250);
};
const onGoodsSelectVisible = (visible: boolean) => {
  if (visible && !state.goodsOptions.length) searchGoods('');
};
const onScopeChange = () => {
  state.selectedCategoryId = undefined;
  state.selectedGoodsId = undefined;
  if (state.ruleForm.goods_type === 2 && !state.goodsOptions.length)
    searchGoods('');
};
const addGoods = () => {
  if (!state.selectedGoodsId) {
    ElMessage.warning('请先选择商品');
    return;
  }
  const goods = state.goodsOptions.find(
    (row) => row.id === state.selectedGoodsId
  );
  if (!goods) {
    ElMessage.warning('请先选择商品');
    return;
  }
  if (state.goods.some((row) => row.id === goods.id)) {
    ElMessage.warning('该商品已添加');
    return;
  }
  state.goods.push({ ...goods });
  state.selectedGoodsId = undefined;
};
const onSubmit = async () => {
  if (state.fetching || state.saving || state.loadFailed) return;
  state.saving = true;
  try {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) return;
    if (state.ruleForm.goods_type === 1 && !state.categories.length) {
      ElMessage.warning('请先选择商品分类并添加');
      return;
    }
    if (state.ruleForm.goods_type === 2 && !state.goods.length) {
      ElMessage.warning('请先选择商品并添加');
      return;
    }
    const form = state.ruleForm;
    const payload = {
      id: form.id,
      name: form.name.trim(),
      description: form.description.trim(),
      tag: form.tag.trim(),
      min: Number(form.min),
      discount: Number(form.discount),
      limit: Number(form.limit),
      type: form.type,
      total: Number(form.total),
      time_type: form.time_type,
      days: form.time_type === 0 ? Number(form.days) : 0,
      start_time: form.time_type === 1 ? form.start_time : null,
      end_time: form.time_type === 1 ? form.end_time : null,
      goods_type: form.goods_type,
      status: form.status,
      category_ids:
        form.goods_type === 1 ? state.categories.map((row) => row.id) : [],
      goods_ids: form.goods_type === 2 ? state.goods.map((row) => row.id) : [],
    };
    await useCouponApi().saveOrUpdate(payload);
    ElNotification({
      title: '成功',
      message: state.editType === 'add' ? '创建成功' : '修改成功',
      type: 'success',
      position: 'top-right',
    });
    state.visible = false;
    emit('getList');
  } catch {
    /* 统一拦截器提示。 */
  } finally {
    state.saving = false;
  }
};
onBeforeUnmount(onDialogClose);
defineExpose({ openDialog });
</script>

<style scoped lang="scss">
.coupon-dialog-form {
  padding: 8px 28px 10px;
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }
  :deep(.el-form-item__label) {
    color: #606266;
    font-weight: 600;
    justify-content: flex-end;
    padding-right: 18px;
  }
  :deep(.el-form-item__content) {
    min-width: 0;
  }
  :deep(.el-input) {
    width: 300px;
    max-width: 100%;
  }
  :deep(.el-input__wrapper) {
    min-height: 30px;
  }
  .coupon-dialog-select {
    width: 208px;
    max-width: 100%;
  }
}
.coupon-time-field,
.coupon-scope-field {
  width: 100%;
  min-width: 0;
}
.coupon-time-input {
  margin-top: 16px;
  margin-bottom: 0 !important;
}
.coupon-date-range {
  margin-top: 16px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  > .el-form-item {
    flex: 1;
    min-width: 0;
    margin-bottom: 0;
  }
  :deep(.el-date-editor.el-input) {
    width: 100%;
  }
}
.coupon-scope-field {
  max-width: 340px;
  :deep(.el-table) {
    margin-top: 18px;
  }
}
.coupon-scope-picker {
  display: flex;
  gap: 4px;
  margin-top: 16px;
  align-items: center;
  .el-cascader,
  .el-select {
    flex: 1;
    min-width: 0;
    width: 208px;
  }
  .el-button {
    margin-left: 0;
  }
}
.coupon-goods-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}
.coupon-goods-sn {
  color: #8c9bb3;
}
.coupon-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  .el-button {
    margin-left: 0;
  }
}
</style>
<style lang="scss">
.coupon-dialog {
  max-width: calc(100vw - 32px);
  --el-color-primary: #1890ff;
  .el-dialog__body {
    padding: 18px 20px 10px;
  }
}
@media (max-width: 900px) {
  .coupon-dialog {
    width: 92% !important;
    .coupon-dialog-form {
      padding: 8px 8px 10px;
    }
    .el-form-item__label {
      width: 115px !important;
      padding-right: 12px;
    }
    .el-form-item__content {
      margin-left: 0 !important;
    }
  }
}
@media (max-width: 560px) {
  .coupon-dialog {
    .el-dialog__body {
      padding: 12px 2px 6px;
    }
    .coupon-dialog-form {
      padding: 4px 0;
    }
    .el-form-item__label {
      width: 100px !important;
      padding-right: 8px;
    }
    .el-radio-button__inner {
      padding: 8px 7px;
    }
    .coupon-date-range {
      flex-wrap: wrap;
      > .el-form-item {
        flex-basis: 100%;
      }
    }
    .coupon-dialog-footer .el-button {
      flex: 1 1 40%;
    }
  }
}
</style>
