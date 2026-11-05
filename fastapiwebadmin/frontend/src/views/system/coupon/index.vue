<template>
  <div class="coupon-page">
    <div class="coupon-panel">
      <div class="coupon-toolbar">
        <el-input
          v-model="state.listQuery.name"
          class="coupon-input"
          placeholder="请输入优惠券标题"
          clearable
          @keyup.enter="onSearch"
        />
        <el-select
          v-model="state.listQuery.type"
          class="coupon-input"
          placeholder="请选择优惠券类型"
          clearable
        >
          <el-option :value="0" label="通用领券" /><el-option
            :value="1"
            label="注册赠券"
          /><el-option :value="2" label="兑换码" />
        </el-select>
        <el-select
          v-model="state.listQuery.status"
          class="coupon-input"
          placeholder="请选择优惠券状态"
          clearable
        >
          <el-option :value="0" label="正常" /><el-option
            :value="1"
            label="已过期"
          /><el-option :value="2" label="已下架" />
        </el-select>
        <el-button
          class="coupon-btn"
          type="primary"
          :icon="Search"
          @click="onSearch"
          >查找</el-button
        >
        <el-button class="coupon-btn" type="primary" :icon="Plus" @click="onAdd"
          >添加</el-button
        >
        <el-button
          class="coupon-btn"
          type="primary"
          :icon="Download"
          :loading="state.exporting"
          @click="onExport"
          >导出</el-button
        >
      </div>
      <el-table
        v-loading="state.loading"
        :data="state.listData"
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
          label="优惠券ID"
          width="90"
          align="center"
          sortable="custom"
        />
        <el-table-column
          prop="name"
          label="优惠券名称"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="description"
          label="介绍"
          min-width="100"
          align="center"
        />
        <el-table-column
          prop="tag"
          label="标签"
          min-width="100"
          align="center"
        />
        <el-table-column
          prop="min_text"
          label="最低消费"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="discount_text"
          label="满减金额"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="limit"
          label="每人限领"
          width="95"
          align="center"
        />
        <el-table-column
          prop="goods_type_name"
          label="商品使用范围"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="type_name"
          label="优惠券类型"
          min-width="110"
          align="center"
        />
        <el-table-column
          prop="total_text"
          label="优惠券数量"
          min-width="100"
          align="center"
        />
        <el-table-column
          prop="status_name"
          label="状态"
          width="100"
          align="center"
        />
        <el-table-column label="操作" min-width="250" align="center">
          <template #default="{ row }"
            ><div class="coupon-actions">
              <el-button type="primary" size="small" @click="onDetail(row)"
                >详情</el-button
              >
              <el-button type="primary" size="small" @click="onEdit(row)"
                >编辑</el-button
              >
              <el-button
                type="danger"
                size="small"
                :loading="state.deletingId === row.id"
                :disabled="state.deletingId !== null"
                @click="onDelete(row)"
                >删除</el-button
              >
            </div></template
          >
        </el-table-column>
      </el-table>
      <div class="coupon-pagination">
        <el-pagination
          v-model:current-page="state.listQuery.page"
          v-model:page-size="state.listQuery.pageSize"
          :page-sizes="[10, 20, 30, 40, 50, 100]"
          :total="state.total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="onSizeChange"
          @current-change="getList"
        />
      </div>
    </div>
    <CouponDialog ref="couponDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'promotionCoupon' });
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
import { Search, Plus, Download } from '@element-plus/icons-vue';
import { useCouponApi } from '/@/api/useSystemApi/coupon';
import CouponDialog from './CouponDialog.vue';

const couponDialogRef = ref();
const router = useRouter();
const state = reactive({
  loading: false,
  exporting: false,
  deletingId: null as number | null,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    name: '',
    type: undefined as number | undefined,
    status: undefined as number | undefined,
    sortOrder: 'desc',
  },
});
const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  fontWeight: '500',
  height: '48px',
  borderColor: '#e8edf3',
};
const cellStyle = { height: '60px', borderColor: '#e8edf3' };
const buildQuery = () => ({
  name: state.listQuery.name.trim() || undefined,
  type:
    typeof state.listQuery.type === 'number' ? state.listQuery.type : undefined,
  status:
    typeof state.listQuery.status === 'number'
      ? state.listQuery.status
      : undefined,
  sort_order: state.listQuery.sortOrder,
});
let requestSequence = 0;
const getList = async () => {
  const requestId = ++requestSequence;
  state.loading = true;
  try {
    const res: any = await useCouponApi().getList({
      ...buildQuery(),
      page: state.listQuery.page,
      pageSize: state.listQuery.pageSize,
    });
    if (requestId !== requestSequence) return;
    state.listData = res.data?.rows || [];
    state.total = res.data?.rowTotal || 0;
    if (!state.listData.length && state.listQuery.page > 1) {
      state.listQuery.page = Math.max(
        1,
        Math.ceil(state.total / state.listQuery.pageSize)
      );
      await getList();
    }
  } catch {
    // 接口错误由统一拦截器提示。
  } finally {
    if (requestId === requestSequence) state.loading = false;
  }
};
const onSearch = () => {
  state.listQuery.page = 1;
  getList();
};
const onSizeChange = () => {
  state.listQuery.page = 1;
  getList();
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
const onAdd = () => couponDialogRef.value.openDialog('add');
const onEdit = (row: any) => couponDialogRef.value.openDialog('edit', row);
const onDetail = (row: any) =>
  router.push({ path: '/promotion/couponDetail', query: { id: row.id } });
const onDelete = async (row: any) => {
  if (state.deletingId !== null) return;
  try {
    await ElMessageBox.confirm(`确定删除优惠券「${row.name}」吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    });
  } catch {
    return;
  }
  state.deletingId = row.id;
  try {
    await useCouponApi().deleted({ id: row.id });
    ElNotification({
      title: '成功',
      message: '删除成功',
      type: 'success',
      position: 'top-right',
    });
    if (state.listData.length === 1 && state.listQuery.page > 1)
      state.listQuery.page--;
    await getList();
  } catch {
    /* 统一拦截器提示 */
  } finally {
    state.deletingId = null;
  }
};
const onExport = async () => {
  if (state.exporting) return;
  state.exporting = true;
  try {
    const blob: any = await useCouponApi().exportExcel(buildQuery());
    if (blob.type?.includes('json')) {
      const result = JSON.parse(await blob.text());
      ElMessage.error(result.msg || '导出失败');
      return;
    }
    const url = URL.createObjectURL(
      new Blob([blob], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
    );
    const link = document.createElement('a');
    link.href = url;
    link.download = `优惠券列表_${Date.now()}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch {
    /* 统一拦截器提示 */
  } finally {
    state.exporting = false;
  }
};
onMounted(getList);
onBeforeUnmount(() => {
  requestSequence++;
});
</script>

<style scoped lang="scss">
.coupon-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
  overflow-x: hidden;
  --el-color-primary: #1890ff;
}
.coupon-panel {
  background: #fff;
}
.coupon-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 4px 2px 18px;
  .coupon-input {
    width: 200px;
    :deep(.el-input__wrapper),
    :deep(.el-select__wrapper) {
      min-height: 34px;
      border-radius: 4px;
    }
  }
  .coupon-btn {
    margin-left: 0;
    height: 34px;
    min-width: 76px;
  }
}
.coupon-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  .el-button {
    margin-left: 0;
    padding: 7px 16px;
    border-radius: 3px;
  }
}
.coupon-pagination {
  display: flex;
  justify-content: flex-start;
  padding: 24px 2px 6px;
  overflow-x: auto;
}
@media (max-width: 900px) {
  .coupon-page {
    padding: 10px;
  }
  .coupon-toolbar {
    .coupon-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }
    .coupon-btn {
      flex: 0 1 auto;
    }
  }
  .coupon-pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}
@media (max-width: 560px) {
  .coupon-toolbar {
    .coupon-input {
      flex: 1 1 100%;
    }
    .coupon-btn {
      flex: 1 1 40%;
    }
  }
}
</style>
