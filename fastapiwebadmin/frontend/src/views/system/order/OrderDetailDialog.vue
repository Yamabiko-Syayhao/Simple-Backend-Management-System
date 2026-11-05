<template>
  <el-dialog
    v-model="state.visible"
    title="订单详情"
    width="1000px"
    class="order-detail-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <div v-loading="state.loading" class="order-detail">
      <div class="detail-row">
        <span class="detail-label">订单编号</span>
        <span class="detail-value">{{ state.order.order_no }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">订单状态</span>
        <span class="detail-value">
          <span class="detail-tag">{{ state.order.status_name }}</span>
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">订单用户</span>
        <span class="detail-value">{{ state.order.username }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">用户留言</span>
        <span class="detail-value">{{ state.order.user_message || '' }}</span>
      </div>

      <div class="detail-row">
        <span class="detail-label">收货信息</span>
        <span class="detail-value">
          （收货人）{{ state.order.receiver_name || '' }}
          （手机号）{{ state.order.receiver_phone || '' }}
          （地址）{{ state.order.receiver_region || '' }} {{ state.order.receiver_detail || '' }}
        </span>
      </div>

      <div class="detail-block">
        <div class="detail-block-title">商品信息</div>
        <el-table :data="state.order.items || []" border size="small" empty-text="暂无商品明细">
          <el-table-column prop="goods_name" label="商品名称" min-width="220" align="center" />
          <el-table-column prop="goods_no" label="商品编号" min-width="130" align="center" />
          <el-table-column prop="spec" label="货品规格" min-width="110" align="center" />
          <el-table-column prop="price" label="货品价格" min-width="110" align="center" />
          <el-table-column prop="quantity" label="货品数量" min-width="100" align="center" />
          <el-table-column label="货品图片" min-width="110" align="center">
            <template #default="{ row }">
              <el-image
                v-if="row.image"
                :src="row.image"
                :preview-src-list="[row.image]"
                fit="cover"
                class="detail-item-img"
                preview-teleported
              />
              <span v-else>-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="detail-row">
        <span class="detail-label">费用信息</span>
        <span class="detail-value">
          （实际费用）{{ state.order.pay_amount }}元 =（商品总价）{{ state.order.total_amount }}元
          +（快递费用）0元 -（优惠减免）0元 -（积分减免）0元
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">支付信息</span>
        <span class="detail-value">
          （支付渠道）{{ state.order.pay_channel || '' }} （支付时间）{{ state.order.pay_time || '' }}
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">快递信息</span>
        <span class="detail-value">
          （快递公司）{{ state.order.express_company || '' }}
          （快递单号）{{ state.order.express_no || '' }}
          （发货时间）{{ state.order.deliver_time || '' }}
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">退款信息</span>
        <span class="detail-value">
          （退款金额）{{ state.order.refund_amount ?? '' }} 元
          （退款类型）{{ state.order.refund_type || '' }}
          （退款备注）{{ state.order.refund_note || '' }}
          （退款时间）{{ state.order.refund_time || '' }}
        </span>
      </div>

      <div class="detail-row">
        <span class="detail-label">收货信息</span>
        <span class="detail-value">（确认收货时间）{{ state.order.confirm_time || '' }}</span>
      </div>
    </div>

    <template #footer>
      <div class="order-detail-footer">
        <el-button class="detail-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="detail-print" type="primary" @click="onPrint">打印</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'OrderDetailDialog' })

import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useOrderApi } from '/@/api/useSystemApi/order'

const state = reactive({
  visible: false,
  loading: false,
  order: {} as any,
})

const openDialog = async (orderId: number) => {
  state.visible = true
  state.loading = true
  state.order = {}
  try {
    const res: any = await useOrderApi().getDetail({ id: orderId })
    state.order = res.data || {}
  } finally {
    state.loading = false
  }
}

/** 组装打印用的 HTML，在新窗口里调用浏览器打印 */
const buildPrintHtml = (order: any) => {
  const items = order.items || []
  const itemRows = items
    .map(
      (item: any) => `
        <tr>
          <td>${item.goods_name || ''}</td>
          <td>${item.goods_no || ''}</td>
          <td>${item.spec || ''}</td>
          <td>${item.price ?? ''}</td>
          <td>${item.quantity ?? ''}</td>
        </tr>`
    )
    .join('')

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>订单详情 - ${order.order_no || ''}</title>
<style>
  body { font-family: -apple-system, "Microsoft YaHei", Arial, sans-serif; color: #303133; padding: 32px 40px; font-size: 14px; }
  h3 { margin: 0 0 20px; font-size: 16px; }
  .row { margin-bottom: 14px; line-height: 1.6; }
  .label { color: #606266; margin-right: 12px; }
  table { width: 100%; border-collapse: collapse; margin: 8px 0 16px; }
  th, td { border: 1px solid #dcdfe6; padding: 8px; text-align: center; font-size: 13px; }
  th { background: #f7f9fc; font-weight: 500; }
  .tag { display: inline-block; padding: 1px 8px; border: 1px solid #cfe6ff; background: #eaf4ff; color: #1890ff; border-radius: 3px; font-size: 12px; }
</style>
</head>
<body>
  <h3>订单详情</h3>
  <div class="row"><span class="label">订单编号</span>${order.order_no || ''}</div>
  <div class="row"><span class="label">订单状态</span><span class="tag">${order.status_name || ''}</span></div>
  <div class="row"><span class="label">订单用户</span>${order.username || ''}</div>
  <div class="row"><span class="label">用户留言</span>${order.user_message || ''}</div>
  <div class="row"><span class="label">收货信息</span>（收货人）${order.receiver_name || ''} （手机号）${order.receiver_phone || ''} （地址）${order.receiver_region || ''} ${order.receiver_detail || ''}</div>
  <div class="row"><span class="label">商品信息</span></div>
  <table>
    <thead><tr><th>商品名称</th><th>商品编号</th><th>货品规格</th><th>货品价格</th><th>货品数量</th></tr></thead>
    <tbody>${itemRows}</tbody>
  </table>
  <div class="row"><span class="label">费用信息</span>（实际费用）${order.pay_amount ?? ''}元 =（商品总价）${order.total_amount ?? ''}元 +（快递费用）0元 -（优惠减免）0元 -（积分减免）0元</div>
  <div class="row"><span class="label">支付信息</span>（支付渠道）${order.pay_channel || ''} （支付时间）${order.pay_time || ''}</div>
  <div class="row"><span class="label">快递信息</span>（快递公司）${order.express_company || ''} （快递单号）${order.express_no || ''} （发货时间）${order.deliver_time || ''}</div>
  <div class="row"><span class="label">退款信息</span>（退款金额）${order.refund_amount ?? ''} 元 （退款类型）${order.refund_type || ''} （退款备注）${order.refund_note || ''} （退款时间）${order.refund_time || ''}</div>
  <div class="row"><span class="label">收货信息</span>（确认收货时间）${order.confirm_time || ''}</div>
</body>
</html>`
}

const onPrint = () => {
  const win = window.open('', '_blank', 'width=1000,height=760')
  if (!win) {
    ElMessage.error('打印窗口被浏览器拦截，请允许弹出窗口')
    return
  }
  win.document.write(buildPrintHtml(state.order))
  win.document.close()
  win.focus()
  setTimeout(() => {
    win.print()
  }, 300)
}

defineExpose({ openDialog })
</script>

<style scoped lang="scss">
.order-detail-dialog {
  :deep(.el-dialog__header) {
    padding: 20px 24px 14px;
    border-bottom: 1px solid #eef1f6;
  }

  :deep(.el-dialog__title) {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
  }

  :deep(.el-dialog__body) {
    padding: 22px 28px 6px;
    max-height: 68vh;
    overflow-y: auto;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 18px;
  }
}

.order-detail {
  font-size: 14px;
  color: #3d4d66;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
  line-height: 1.7;

  .detail-label {
    flex: 0 0 92px;
    color: #3d4d66;
    font-weight: 500;
  }

  .detail-value {
    flex: 1;
    color: #3d4d66;
    word-break: break-all;
  }
}

.detail-tag {
  display: inline-block;
  padding: 1px 10px;
  font-size: 13px;
  border-radius: 3px;
  color: #1890ff;
  background: #eaf4ff;
  border: 1px solid #cfe6ff;
}

.detail-block {
  margin-bottom: 16px;

  .detail-block-title {
    margin-bottom: 10px;
    font-weight: 500;
  }
}

.detail-item-img {
  width: 44px;
  height: 44px;
  border-radius: 3px;
}

.order-detail-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .detail-cancel,
  .detail-print {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .detail-print {
    background: #1890ff;
    border-color: #1890ff;

    &:hover {
      background: #40a9ff;
      border-color: #40a9ff;
    }
  }
}

@media screen and (max-width: 768px) {
  :global(.order-detail-dialog) {
    width: 94% !important;
  }

  .detail-row {
    .detail-label {
      flex: 0 0 74px;
    }
  }
}
</style>
