<template>
  <div class="order-page">
    <div class="order-panel">
      <!-- 搜索区 -->
      <div class="order-toolbar">
        <el-input
          v-model="state.listQuery.username"
          class="order-input"
          placeholder="请输入用户昵称"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.receiver_name"
          class="order-input"
          placeholder="请输入收货人名称"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.order_no"
          class="order-input"
          placeholder="请输入订单编号"
          clearable
          @keyup.enter="onSearch"
        />

        <el-date-picker
          v-model="state.dateRange"
          class="order-date"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD HH:mm:ss"
          :shortcuts="dateShortcuts"
          :default-time="defaultTime"
          unlink-panels
        />

        <el-select
          v-model="state.listQuery.status"
          class="order-status"
          placeholder="请选择订单状态"
          clearable
        >
          <el-option
            v-for="item in ORDER_STATUS_OPTIONS"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <el-button class="order-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="order-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        row-key="id"
        class="order-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <!-- 展开显示商品明细（二级目录） -->
        <el-table-column type="expand" width="46">
          <template #default="{ row }">
            <div class="order-items">
              <el-table :data="row.items" size="small" border empty-text="该订单暂无商品明细">
                <el-table-column prop="goods_name" label="商品名称" min-width="240">
                  <template #default="{ row: item }">
                    <span class="order-cell-text">{{ item.goods_name }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="goods_no" label="商品编号" min-width="140" align="center">
                  <template #default="{ row: item }">
                    <span class="order-cell-text">{{ item.goods_no }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="spec" label="货品规格" min-width="120" align="center">
                  <template #default="{ row: item }">
                    <span class="order-cell-text">{{ item.spec || '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="price" label="货品价格" min-width="120" align="center">
                  <template #default="{ row: item }">
                    <span class="order-cell-text">{{ item.price }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="quantity" label="货品数量" min-width="100" align="center">
                  <template #default="{ row: item }">
                    <span class="order-cell-text">{{ item.quantity }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="货品图片" min-width="120" align="center">
                  <template #default="{ row: item }">
                    <el-image
                      v-if="item.image"
                      :src="item.image"
                      :preview-src-list="[item.image]"
                      fit="cover"
                      class="order-item-img"
                      preview-teleported
                    />
                    <span v-else class="order-cell-text">-</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_no" label="订单编号" min-width="160" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.order_no }}</span>
          </template>
        </el-table-column>

        <el-table-column label="用户头像" min-width="90" align="center">
          <template #default="{ row }">
            <el-avatar :size="36" :src="row.avatar || ''" class="order-avatar">
              <el-icon :size="18"><UserFilled /></el-icon>
            </el-avatar>
          </template>
        </el-table-column>

        <el-table-column prop="username" label="下单用户" min-width="110" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.username }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="order_time" label="下单时间" min-width="120" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.order_time || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="订单状态" min-width="130" align="center">
          <template #default="{ row }">
            <span class="order-tag">{{ row.status_name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="订单金额" min-width="100" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.total_amount }} 元</span>
          </template>
        </el-table-column>

        <el-table-column label="实付金额" min-width="100" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.pay_amount }} 元</span>
          </template>
        </el-table-column>

        <el-table-column prop="pay_time" label="支付时间" min-width="120" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.pay_time || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="receiver_name" label="收货人" min-width="90" align="center">
          <template #default="{ row }">
            <span class="order-receiver">{{ row.receiver_name || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="receiver_phone" label="收货电话" min-width="130" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.receiver_phone || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="express_no" label="物流单号" min-width="100" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.express_no || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="express_company" label="物流渠道" min-width="100" align="center">
          <template #default="{ row }">
            <span class="order-cell-text">{{ row.express_company || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="260" align="center">
          <template #default="{ row }">
            <div class="order-actions">
              <el-button size="small" type="primary" class="order-action-btn" @click="onDetail(row)">详情</el-button>
              <el-button size="small" type="danger" class="order-action-btn" @click="onDelete(row)">删除</el-button>
              <el-button size="small" type="success" class="order-action-btn" @click="onAction('collect', row)">收款</el-button>
              <el-button size="small" type="primary" class="order-action-btn" @click="onAction('deliver', row)">发货</el-button>
              <el-button size="small" type="danger" class="order-action-btn" @click="onAction('refund', row)">退款</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="order-pagination">
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

    <OrderDetailDialog ref="detailDialogRef" />
    <OrderActionDialog ref="actionDialogRef" @success="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemOrder' })

import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Download, Search, UserFilled } from '@element-plus/icons-vue'
import OrderDetailDialog from '/@/views/system/order/OrderDetailDialog.vue'
import OrderActionDialog from '/@/views/system/order/OrderActionDialog.vue'
import { useOrderApi } from '/@/api/useSystemApi/order'

const detailDialogRef = ref()
const actionDialogRef = ref()

/** 订单状态字典（与后端 ORDER_STATUS 保持一致） */
const ORDER_STATUS_OPTIONS = [
  { label: '未付款', value: 1 },
  { label: '用户取消', value: 2 },
  { label: '系统取消', value: 3 },
  { label: '已付款', value: 4 },
  { label: '申请退款', value: 5 },
  { label: '已退款', value: 6 },
  { label: '已发货', value: 7 },
  { label: '用户收货', value: 8 },
  { label: '系统收货', value: 9 },
]

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  dateRange: [] as string[],
  listQuery: {
    page: 1,
    pageSize: 20,
    username: '',
    receiver_name: '',
    order_no: '',
    status: '' as number | string,
    start_time: '',
    end_time: '',
  },
})

const defaultTime: [Date, Date] = [
  new Date(2000, 0, 1, 0, 0, 0),
  new Date(2000, 0, 1, 23, 59, 59),
]

const shiftDate = (months: number) => {
  const now = new Date()
  const start = new Date(now.getTime())
  start.setMonth(start.getMonth() - months)
  return [start, now]
}

const dateShortcuts = [
  { text: '最近一周', value: () => [new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), new Date()] },
  { text: '最近一个月', value: () => shiftDate(1) },
  { text: '最近三个月', value: () => shiftDate(3) },
]

const headerCellStyle = {
  background: '#f7f9fc',
  color: '#5a6a85',
  fontWeight: '500',
  height: '52px',
  borderColor: '#e8edf3',
}

const cellStyle = {
  height: '64px',
  borderColor: '#e8edf3',
}

// 日期选择器变化时同步到查询条件
watch(
  () => state.dateRange,
  (range) => {
    if (range && range.length === 2) {
      state.listQuery.start_time = range[0]
      state.listQuery.end_time = range[1]
    } else {
      state.listQuery.start_time = ''
      state.listQuery.end_time = ''
    }
  }
)

const buildQuery = () => {
  const payload: Record<string, any> = {}
  if (state.listQuery.username) payload.username = state.listQuery.username
  if (state.listQuery.receiver_name) payload.receiver_name = state.listQuery.receiver_name
  if (state.listQuery.order_no) payload.order_no = state.listQuery.order_no
  if (state.listQuery.status !== '' && state.listQuery.status !== null && state.listQuery.status !== undefined) {
    payload.status = state.listQuery.status
  }
  if (state.listQuery.start_time) payload.start_time = state.listQuery.start_time
  if (state.listQuery.end_time) payload.end_time = state.listQuery.end_time
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useOrderApi()
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

const onDetail = (row: any) => {
  detailDialogRef.value.openDialog(row.id)
}

const onAction = (mode: 'collect' | 'deliver' | 'refund', row: any) => {
  actionDialogRef.value.openDialog(mode, row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除订单「${row.order_no}」吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      await useOrderApi().deleted({ id: row.id })
      ElNotification({
        title: '成功',
        message: '删除成功',
        type: 'success',
        duration: 2500,
        position: 'top-right',
      })
      if (state.listData.length === 1 && state.listQuery.page > 1) {
        state.listQuery.page -= 1
      }
      getList()
    })
    .catch(() => {
      /* 取消删除 */
    })
}

const onExport = async () => {
  state.exporting = true
  try {
    const blob: any = await useOrderApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `订单列表_${new Date().getTime()}.xlsx`
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
.order-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.order-panel {
  background: #fff;
}

.order-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 4px 2px 18px;

  .order-input {
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

  .order-date {
    width: 380px !important;
  }

  .order-status {
    width: 180px;
  }

  :deep(.el-date-editor),
  :deep(.el-select__wrapper) {
    height: 40px;
    border-radius: 4px;
  }

  .order-btn {
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

.order-table {
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

.order-items {
  padding: 10px 16px 10px 56px;
  background: #fbfcfd;
}

.order-item-img {
  width: 44px;
  height: 44px;
  border-radius: 3px;
}

.order-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.order-receiver {
  font-size: 14px;
  color: #f56c6c;
}

.order-avatar {
  background: #dfe3e9;
  color: #fff;
}

.order-tag {
  display: inline-block;
  padding: 2px 10px;
  font-size: 13px;
  line-height: 22px;
  border-radius: 3px;
  color: #1890ff;
  background: #eaf4ff;
  border: 1px solid #cfe6ff;
  white-space: nowrap;
}

.order-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px;

  .order-action-btn {
    margin-left: 0;
    padding: 6px 10px;
    border-radius: 3px;
    font-size: 12px;
  }
}

.order-pagination {
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
  .order-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .order-toolbar {
    gap: 8px;
    padding-bottom: 12px;

    .order-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .order-date {
      flex: 1 1 100%;
      width: 100% !important;
    }

    .order-status {
      flex: 1 1 calc(50% - 4px);
      width: auto;
    }

    .order-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .order-pagination {
    overflow-x: auto;
    padding-bottom: 10px;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .order-toolbar {
    .order-input,
    .order-status {
      flex: 1 1 100%;
    }

    .order-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }
}
</style>
