<template>
  <el-dialog
    v-model="state.visible"
    :title="dialogTitle"
    width="840px"
    class="order-action-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <!-- 收款 -->
    <div v-if="state.mode === 'collect'" class="action-body">
      <div class="action-tip">
        确认当前订单（订单编号 {{ state.row.order_no }}）已经完成线下收款？
      </div>

      <div class="action-field">
        <span class="action-label">订单金额</span>
        <el-input :model-value="state.row.total_amount" disabled class="action-input" />
      </div>

      <div class="action-field">
        <span class="action-label">付款金额</span>
        <el-input v-model="state.payAmount" class="action-input" />
      </div>

      <el-table :data="state.row.items || []" size="small" class="action-table" empty-text="暂无商品明细">
        <el-table-column prop="goods_name" label="商品" min-width="220" />
        <el-table-column prop="spec" label="规格" min-width="150" align="center" />
        <el-table-column prop="quantity" label="下单数量" min-width="120" align="center" />
      </el-table>
    </div>

    <!-- 发货 -->
    <div v-else-if="state.mode === 'deliver'" class="action-body action-body--deliver">
      <div class="action-field">
        <span class="action-label">快递公司</span>
        <el-select v-model="state.expressCompany" placeholder="请选择" class="action-input">
          <el-option v-for="item in EXPRESS_COMPANIES" :key="item" :label="item" :value="item" />
        </el-select>
      </div>

      <div class="action-field">
        <span class="action-label">快递编号</span>
        <el-input v-model="state.expressNo" placeholder="请输入快递编号" class="action-input" />
      </div>
    </div>

    <!-- 退款 -->
    <div v-else class="action-body">
      <div class="action-field">
        <span class="action-label">退款金额</span>
        <el-input :model-value="state.row.pay_amount" disabled class="action-input" />
      </div>
    </div>

    <template #footer>
      <div class="action-footer">
        <el-button class="action-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="action-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'OrderActionDialog' })

import { computed, reactive } from 'vue'
import { ElNotification } from 'element-plus'
import { useOrderApi } from '/@/api/useSystemApi/order'

const emit = defineEmits(['success'])

const EXPRESS_COMPANIES = [
  '中通快递',
  '圆通速递',
  '韵达速递',
  '邮政快递包裹',
  'EMS',
  '德邦快递',
  '快捷快递',
  '京东物流',
  '顺丰速运',
]

const state = reactive({
  visible: false,
  loading: false,
  mode: 'collect' as 'collect' | 'deliver' | 'refund',
  row: {} as any,
  payAmount: '',
  expressCompany: '',
  expressNo: '',
})

const dialogTitle = computed(() => {
  if (state.mode === 'collect') return '订单收款'
  if (state.mode === 'deliver') return '发货'
  return '退款'
})

const openDialog = (mode: 'collect' | 'deliver' | 'refund', row: any) => {
  state.mode = mode
  state.row = row || {}
  state.payAmount = String(row?.pay_amount ?? '')
  state.expressCompany = ''
  state.expressNo = ''
  state.loading = false
  state.visible = true
}

const notifyFail = (msg: string) => {
  ElNotification({
    title: '失败',
    message: msg || '操作失败',
    type: 'error',
    duration: 3000,
    position: 'top-right',
  })
}

const onSubmit = async () => {
  state.loading = true
  try {
    if (state.mode === 'collect') {
      await useOrderApi().collect({
        id: state.row.id,
        pay_amount: state.payAmount ? Number(state.payAmount) : null,
      })
    } else if (state.mode === 'deliver') {
      await useOrderApi().deliver({
        id: state.row.id,
        express_company: state.expressCompany,
        express_no: state.expressNo,
      })
    } else {
      await useOrderApi().refund({
        id: state.row.id,
        refund_amount: state.row.pay_amount,
      })
    }
    state.visible = false
    emit('success')
  } catch (err: any) {
    // 后端返回业务错误：这里用右上角「失败」通知，而不是全局 toast
    notifyFail(err?.msg || '操作失败')
  } finally {
    state.loading = false
  }
}

defineExpose({ openDialog })
</script>

<style scoped lang="scss">
.order-action-dialog {
  :deep(.el-dialog__header) {
    padding: 18px 24px 14px;
    border-bottom: 1px solid #eef1f6;
  }

  :deep(.el-dialog__title) {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
  }

  :deep(.el-dialog__body) {
    padding: 24px 28px 8px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 18px;
  }
}

.action-body {
  font-size: 14px;
  color: #3d4d66;
}

.action-body--deliver {
  padding: 10px 0 30px;
}

.action-tip {
  margin-bottom: 22px;
  color: #3d4d66;
}

.action-field {
  display: flex;
  align-items: center;
  margin-bottom: 18px;

  .action-label {
    flex: 0 0 90px;
    font-weight: 500;
  }

  .action-input {
    width: 220px;
  }

  :deep(.el-input__wrapper),
  :deep(.el-select__wrapper) {
    height: 38px;
    border-radius: 4px;
  }
}

.action-table {
  margin-top: 10px;

  :deep(thead th) {
    background: #fafbfc;
    color: #5a6a85;
    font-weight: 500;
  }
}

.action-footer {
  display: flex;
  justify-content: center;
  gap: 16px;

  .action-cancel,
  .action-confirm {
    width: 90px;
    height: 36px;
    border-radius: 4px;
  }

  .action-confirm {
    background: #1890ff;
    border-color: #1890ff;

    &:hover {
      background: #40a9ff;
      border-color: #40a9ff;
    }
  }
}

@media screen and (max-width: 768px) {
  :global(.order-action-dialog) {
    width: 92% !important;
  }
}
</style>
