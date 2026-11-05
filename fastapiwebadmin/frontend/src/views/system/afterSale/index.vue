<template>
  <div class="after-sale-page">
    <div class="after-sale-panel">
      <!-- 搜索区 -->
      <div class="as-toolbar">
        <el-input
          v-model="state.listQuery.after_sale_no"
          class="as-input"
          placeholder="请输入售后编号"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.order_id"
          class="as-input"
          placeholder="请输入订单ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="as-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="as-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 批量操作 -->
      <div class="as-actions">
        <el-button class="as-batch-pass" type="success" :icon="CircleCheck" @click="onBatch('pass')">批量通过</el-button>
        <el-button class="as-batch-reject" type="danger" :icon="CircleClose" @click="onBatch('reject')">批量拒绝</el-button>
      </div>

      <!-- 状态页签 -->
      <el-tabs v-model="state.activeTab" class="as-tabs" @tab-change="onTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="待审核" name="pending" />
        <el-tab-pane label="待退款" name="refund" />
      </el-tabs>

      <!-- 列表 -->
      <el-table
        ref="tableRef"
        v-loading="state.loading"
        :data="state.listData"
        class="as-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />

        <el-table-column prop="after_sale_no" label="售后编号" min-width="170" align="center">
          <template #default="{ row }">
            <span class="as-cell-text">{{ row.after_sale_no }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="order_id" label="订单ID" min-width="120" align="center">
          <template #default="{ row }">
            <span class="as-cell-text">{{ row.order_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="member_id" label="用户ID" min-width="110" align="center">
          <template #default="{ row }">
            <span class="as-cell-text">{{ row.member_id ?? '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="type" label="售后类型" min-width="130" align="center">
          <template #default="{ row }">
            <span class="as-cell-text">{{ row.type || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="reason" label="退款原因" min-width="220" align="center">
          <template #default="{ row }">
            <span class="as-cell-text as-reason">{{ row.reason || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="退款价格" min-width="120" align="center">
          <template #default="{ row }">
            <span class="as-cell-text">{{ row.refund_amount ?? '' }} 元</span>
          </template>
        </el-table-column>

        <el-table-column prop="apply_time" label="申请时间" min-width="160" align="center">
          <template #default="{ row }">
            <span class="as-cell-text">{{ row.apply_time || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="170" align="center">
          <template #default="{ row }">
            <div v-if="row.status === 1" class="as-row-actions">
              <el-button size="small" type="success" class="as-row-btn" @click="onAuditOne(row, 'pass')">通过</el-button>
              <el-button size="small" type="danger" class="as-row-btn" @click="onAuditOne(row, 'reject')">拒绝</el-button>
            </div>
            <span v-else class="as-cell-text">{{ row.status_name }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="as-pagination">
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
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemAfterSale' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import { CircleCheck, CircleClose, Download, Search } from '@element-plus/icons-vue'
import { useAfterSaleApi } from '/@/api/useSystemApi/afterSale'

const tableRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  selection: [] as any[],
  activeTab: 'all',
  listQuery: {
    page: 1,
    pageSize: 20,
    after_sale_no: '',
    order_id: '',
  },
})

const headerCellStyle = {
  background: '#f7f9fc',
  color: '#5a6a85',
  fontWeight: '500',
  height: '52px',
  borderColor: '#e8edf3',
}

const cellStyle = {
  height: '60px',
  borderColor: '#e8edf3',
}

const tabStatus = () => {
  if (state.activeTab === 'pending') return 1
  if (state.activeTab === 'refund') return 2
  return undefined
}

const buildQuery = () => {
  const payload: Record<string, any> = {}
  if (state.listQuery.after_sale_no) payload.after_sale_no = state.listQuery.after_sale_no
  if (state.listQuery.order_id) payload.order_id = Number(state.listQuery.order_id) || undefined
  const status = tabStatus()
  if (status !== undefined) payload.status = status
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useAfterSaleApi()
    .getList(payload)
    .then((res: any) => {
      state.listData = res.data?.rows || []
      state.total = res.data?.rowTotal || 0
    })
    .finally(() => {
      state.loading = false
    })
}

const onSearch = () => {
  state.listQuery.page = 1
  getList()
}

const onSizeChange = () => {
  state.listQuery.page = 1
  getList()
}

const onTabChange = () => {
  state.listQuery.page = 1
  getList()
}

const onSelectionChange = (rows: any[]) => {
  state.selection = rows
}

const doAudit = async (ids: number[], action: 'pass' | 'reject') => {
  try {
    await useAfterSaleApi().audit({ ids, action })
    ElNotification({
      title: '成功',
      message: action === 'pass' ? '已通过审核' : '已拒绝申请',
      type: 'success',
      duration: 2500,
      position: 'top-right',
    })
    tableRef.value?.clearSelection()
    getList()
  } catch (err: any) {
    ElNotification({
      title: '失败',
      message: err?.msg || '操作失败',
      type: 'error',
      duration: 3000,
      position: 'top-right',
    })
  }
}

const onBatch = (action: 'pass' | 'reject') => {
  if (!state.selection.length) {
    ElMessage.error('请选择至少一条记录')
    return
  }
  const ids = state.selection.map((item) => item.id)
  doAudit(ids, action)
}

const onAuditOne = (row: any, action: 'pass' | 'reject') => {
  doAudit([row.id], action)
}

const onExport = async () => {
  state.exporting = true
  try {
    const blob: any = await useAfterSaleApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `售后管理_${new Date().getTime()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
  } finally {
    state.exporting = false
  }
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.after-sale-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.after-sale-panel {
  background: #fff;
}

.as-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 14px;

  .as-input {
    width: 200px;

    :deep(.el-input__wrapper) {
      height: 40px;
      border-radius: 4px;
      box-shadow: 0 0 0 1px #dcdfe6 inset;
    }

    :deep(.el-input__inner) {
      font-size: 14px;

      &::placeholder {
        color: #b9c0cc;
      }
    }
  }

  .as-btn {
    height: 40px;
    min-width: 88px;
    border-radius: 4px;
    background: #1890ff;
    border-color: #1890ff;
    font-size: 14px;

    &:hover {
      background: #40a9ff;
      border-color: #40a9ff;
    }
  }
}

.as-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 0 2px 6px;

  .as-batch-pass,
  .as-batch-reject {
    height: 36px;
    min-width: 102px;
    border-radius: 4px;
    font-size: 14px;
  }

  .as-batch-pass {
    background: #2fc96b;
    border-color: #2fc96b;

    &:hover {
      background: #4ad27f;
      border-color: #4ad27f;
    }
  }

  .as-batch-reject {
    background: #f4143c;
    border-color: #f4143c;

    &:hover {
      background: #f7456b;
      border-color: #f7456b;
    }
  }
}

.as-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 12px;
  }

  :deep(.el-tabs__item) {
    font-size: 14px;
    color: #5a6a85;
  }

  :deep(.el-tabs__item.is-active) {
    color: #1890ff;
  }

  :deep(.el-tabs__active-bar) {
    background-color: #1890ff;
  }

  :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: #e8edf3;
  }
}

.as-table {
  width: 100%;

  :deep(.el-table__header th) {
    border-right: 1px solid #e8edf3;
  }

  :deep(.el-table__body td) {
    border-right: 1px solid #e8edf3;
  }

  :deep(.el-table__inner-wrapper::before) {
    display: none;
  }
}

.as-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.as-reason {
  display: inline-block;
  line-height: 1.6;
  text-align: left;
  white-space: normal;
  word-break: break-all;
}

.as-row-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .as-row-btn {
    margin-left: 0;
    border-radius: 3px;
    padding: 6px 12px;
  }
}

.as-pagination {
  display: flex;
  justify-content: flex-start;
  padding: 18px 2px 6px;

  :deep(.el-pagination) {
    --el-pagination-button-bg-color: #ffffff;
    --el-pagination-hover-color: #1890ff;
    font-weight: 400;
    color: #5a6a85;
  }

  :deep(.el-pagination.is-background .el-pager li.is-active) {
    background: #1890ff;
    color: #fff;
  }

  :deep(.el-pagination__sizes .el-select .el-input__wrapper) {
    box-shadow: 0 0 0 1px #dcdfe6 inset;
    border-radius: 3px;
  }

  :deep(.el-pagination__jump .el-input__wrapper) {
    box-shadow: 0 0 0 1px #dcdfe6 inset;
    border-radius: 3px;
  }
}

/* ============================ 响应式 ============================ */
@media screen and (max-width: 900px) {
  .after-sale-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .as-toolbar {
    flex-wrap: wrap;
    gap: 8px;

    .as-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .as-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .as-pagination {
    overflow-x: auto;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .as-actions {
    justify-content: flex-start;
  }

  .as-toolbar {
    .as-input {
      flex: 1 1 100%;
    }

    .as-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }
}
</style>
