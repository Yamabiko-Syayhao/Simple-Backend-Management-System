<template>
  <div class="coupon-detail-page">
    <div class="coupon-detail-panel" v-loading="state.loading">
      <el-alert
        v-if="state.errorMessage"
        class="coupon-detail-error"
        :title="state.errorMessage"
        type="warning"
        :closable="false"
        show-icon
      />
      <div v-if="state.coupon" class="coupon-detail-summary-wrap">
        <table class="coupon-detail-summary">
          <thead>
            <tr>
              <th scope="col">名称</th>
              <th scope="col">介绍名称</th>
              <th scope="col">标签</th>
              <th scope="col">优惠券类型</th>
              <th scope="col">最低消费</th>
              <th scope="col">优惠面值</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ state.coupon.name }}</td>
              <td>{{ state.coupon.description || '' }}</td>
              <td>{{ state.coupon.tag || '' }}</td>
              <td>{{ state.coupon.type_name }}</td>
              <td>{{ state.coupon.min_text }}</td>
              <td>{{ state.coupon.discount_text }}</td>
            </tr>
            <tr class="coupon-detail-summary-heading">
              <th scope="col">每人限领</th>
              <th scope="col">当前状态</th>
              <th scope="col">商品范围</th>
              <th scope="col">有效期</th>
              <th scope="col">优惠兑换码</th>
              <th scope="col">发行数量</th>
            </tr>
            <tr>
              <td>{{ state.coupon.limit }}</td>
              <td>{{ state.coupon.status_name }}</td>
              <td>{{ state.coupon.goods_type_name }}</td>
              <td>{{ state.coupon.time_text }}</td>
              <td>{{ state.coupon.code || '' }}</td>
              <td>{{ state.coupon.total_text }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="coupon-detail-toolbar">
        <el-input
          v-model="state.listQuery.user_id"
          class="coupon-detail-input"
          placeholder="请输入用户ID"
          clearable
          :disabled="!queryReady"
          @keyup.enter="onSearch"
        />
        <el-select
          v-model="state.listQuery.status"
          class="coupon-detail-input"
          placeholder="请选择使用状态"
          clearable
          :disabled="!queryReady"
        >
          <el-option :value="0" label="未使用" />
          <el-option :value="1" label="已使用" />
          <el-option :value="2" label="已过期" />
        </el-select>
        <el-button
          class="coupon-detail-search"
          type="primary"
          :icon="Search"
          :disabled="!queryReady"
          :loading="state.recordsLoading"
          @click="onSearch"
          >查找</el-button
        >
      </div>

      <el-table
        v-loading="state.recordsLoading"
        :data="state.rows"
        border
        row-key="id"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        :default-sort="{ prop: 'id', order: 'descending' }"
        empty-text="暂无数据"
        @sort-change="onSortChange"
      >
        <el-table-column
          prop="id"
          label="用户优惠券ID"
          min-width="160"
          align="center"
          sortable="custom"
        />
        <el-table-column
          prop="user_id"
          label="用户ID"
          min-width="130"
          align="center"
        />
        <el-table-column
          prop="receive_time"
          label="领取时间"
          min-width="180"
          align="center"
        />
        <el-table-column
          prop="status_name"
          label="使用状态"
          min-width="130"
          align="center"
        />
        <el-table-column label="订单ID" min-width="150" align="center">
          <template #default="{ row }">{{ row.order_id || '' }}</template>
        </el-table-column>
        <el-table-column label="使用时间" min-width="180" align="center">
          <template #default="{ row }">{{ row.use_time || '' }}</template>
        </el-table-column>
      </el-table>

      <div class="coupon-detail-pagination">
        <el-pagination
          v-model:current-page="state.listQuery.page"
          v-model:page-size="state.listQuery.pageSize"
          :page-sizes="[10, 20, 30, 40, 50, 100]"
          :total="state.total"
          :disabled="!queryReady"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="onSizeChange"
          @current-change="getUserList"
        />
      </div>
      <el-button
        v-if="state.errorMessage"
        @click="router.push('/promotion/coupon')"
        >返回优惠券管理</el-button
      >
    </div>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'promotionCouponDetail' });

import { computed, onBeforeUnmount, reactive, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { useCouponApi } from '/@/api/useSystemApi/coupon';

const route = useRoute();
const router = useRouter();
const detailPath = '/promotion/couponDetail';
const state = reactive({
  loading: false,
  recordsLoading: false,
  errorMessage: '',
  coupon: null as any,
  loadedCouponId: undefined as number | undefined,
  rows: [] as any[],
  total: 0,
  listQuery: {
    user_id: '',
    status: undefined as number | undefined,
    page: 1,
    pageSize: 20,
    sortOrder: 'desc',
  },
});

const couponId = computed(() => {
  const value = route.query.id;
  if (typeof value !== 'string' || !/^\d+$/.test(value)) return undefined;
  const id = Number(value);
  return Number.isSafeInteger(id) && id > 0 ? id : undefined;
});
const queryReady = computed(
  () =>
    route.path === detailPath &&
    !!state.loadedCouponId &&
    state.loadedCouponId === couponId.value &&
    !state.loading &&
    !state.errorMessage
);
const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  fontWeight: '500',
  height: '48px',
  borderColor: '#e8edf3',
};
const cellStyle = { height: '60px', borderColor: '#e8edf3' };

let detailRequestId = 0;
let recordsRequestId = 0;

const readUserId = () => {
  const text = state.listQuery.user_id.trim();
  if (!text) return undefined;
  const id = Number(text);
  if (!/^\d+$/.test(text) || !Number.isSafeInteger(id) || id <= 0)
    throw new Error('请输入有效的正整数用户ID');
  return id;
};

const getUserList = async () => {
  if (!queryReady.value) return;
  let userId: number | undefined;
  try {
    userId = readUserId();
  } catch (error: any) {
    ElMessage.error(error.message);
    return;
  }
  const requestId = ++recordsRequestId;
  const currentCouponId = state.loadedCouponId;
  state.recordsLoading = true;
  try {
    const res: any = await useCouponApi().getUserList({
      coupon_id: currentCouponId,
      user_id: userId,
      status:
        typeof state.listQuery.status === 'number'
          ? state.listQuery.status
          : undefined,
      page: state.listQuery.page,
      pageSize: state.listQuery.pageSize,
      sort_order: state.listQuery.sortOrder,
    });
    if (
      requestId !== recordsRequestId ||
      currentCouponId !== state.loadedCouponId ||
      currentCouponId !== couponId.value ||
      route.path !== detailPath
    )
      return;
    state.rows = res.data?.rows || [];
    state.total = res.data?.rowTotal || 0;
    if (!state.rows.length && state.listQuery.page > 1) {
      state.listQuery.page = Math.max(
        1,
        Math.ceil(state.total / state.listQuery.pageSize)
      );
      await getUserList();
    }
  } catch {
    // 接口错误由统一拦截器提示。
  } finally {
    if (requestId === recordsRequestId) state.recordsLoading = false;
  }
};

const loadCoupon = async () => {
  const requestId = ++detailRequestId;
  recordsRequestId++;
  state.coupon = null;
  state.loadedCouponId = undefined;
  state.rows = [];
  state.total = 0;
  state.recordsLoading = false;
  state.loading = false;
  state.errorMessage = '';
  state.listQuery = {
    user_id: '',
    status: undefined,
    page: 1,
    pageSize: 20,
    sortOrder: 'desc',
  };
  if (route.path !== detailPath) return;
  const id = couponId.value;
  if (!id) {
    state.errorMessage = '缺少有效优惠券ID，请从优惠券管理进入详情。';
    return;
  }
  state.loading = true;
  try {
    const res: any = await useCouponApi().getDetail({ id });
    if (
      requestId !== detailRequestId ||
      id !== couponId.value ||
      route.path !== detailPath
    )
      return;
    if (!res.data?.id || Number(res.data.id) !== id) {
      state.errorMessage = '优惠券不存在，请返回优惠券管理重新选择。';
      return;
    }
    state.coupon = res.data;
    state.loadedCouponId = id;
  } catch {
    if (requestId === detailRequestId)
      state.errorMessage = '优惠券详情加载失败，请返回列表重试。';
  } finally {
    if (requestId === detailRequestId) state.loading = false;
  }
  if (requestId === detailRequestId && queryReady.value) await getUserList();
};

const onSearch = () => {
  if (!queryReady.value) return;
  try {
    readUserId();
  } catch (error: any) {
    ElMessage.error(error.message);
    return;
  }
  state.listQuery.page = 1;
  getUserList();
};
const onSizeChange = () => {
  state.listQuery.page = 1;
  getUserList();
};
const onSortChange = ({
  prop,
  order,
}: {
  prop: string;
  order: string | null;
}) => {
  if (prop && prop !== 'id') return;
  state.listQuery.sortOrder = order === 'ascending' ? 'asc' : 'desc';
  onSearch();
};

watch(() => [route.path, route.query.id], loadCoupon, { immediate: true });
onBeforeUnmount(() => {
  detailRequestId++;
  recordsRequestId++;
});
</script>

<style scoped lang="scss">
.coupon-detail-page {
  padding: 40px 16px 20px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
  overflow-x: hidden;
  --el-color-primary: #1890ff;
}
.coupon-detail-panel {
  min-width: 0;
}
.coupon-detail-error {
  margin-bottom: 20px;
}
.coupon-detail-summary-wrap {
  width: 100%;
  margin-bottom: 20px;
  overflow-x: auto;
}
.coupon-detail-summary {
  width: 100%;
  min-width: 960px;
  table-layout: fixed;
  border-collapse: collapse;
  color: #606266;
  font-size: 14px;
  th,
  td {
    width: calc(100% / 6);
    border: 1px solid #d8e0ed;
    text-align: center;
    vertical-align: middle;
    overflow-wrap: anywhere;
    line-height: 1.6;
  }
  th {
    height: 38px;
    padding: 6px 12px;
    background: #f3f6fc;
    color: #303133;
    font-weight: 400;
  }
  td {
    height: 60px;
    padding: 12px;
  }
}
.coupon-detail-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  .coupon-detail-input {
    width: 200px;
    :deep(.el-input__wrapper),
    :deep(.el-select__wrapper) {
      min-height: 30px;
      border-radius: 4px;
    }
  }
  .coupon-detail-search {
    margin-left: 0;
    min-width: 76px;
    height: 30px;
  }
}
.coupon-detail-pagination {
  padding-top: 24px;
  overflow-x: auto;
}
@media (max-width: 900px) {
  .coupon-detail-page {
    padding: 20px 12px;
  }
  .coupon-detail-toolbar .coupon-detail-input {
    flex: 1 1 calc(50% - 4px);
    width: auto;
    min-width: 0;
  }
  .coupon-detail-pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}
@media (max-width: 560px) {
  .coupon-detail-page {
    padding: 16px 8px;
  }
  .coupon-detail-toolbar {
    .coupon-detail-input {
      flex: 1 1 100%;
    }
    .coupon-detail-search {
      flex: 1 1 40%;
    }
  }
}
</style>
