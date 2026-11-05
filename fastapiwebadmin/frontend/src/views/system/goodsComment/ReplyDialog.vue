<template>
  <el-dialog
    v-model="state.visible"
    title="回复"
    width="640px"
    class="comment-reply-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form label-width="100px">
      <el-form-item label="回复内容">
        <el-input
          v-model="state.content"
          type="textarea"
          :rows="5"
          placeholder="请输入回复内容"
          maxlength="500"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="comment-reply-footer">
        <el-button class="comment-reply-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="comment-reply-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'GoodsCommentReplyDialog' })

import { reactive } from 'vue'
import { ElNotification } from 'element-plus'
import { useGoodsCommentApi } from '/@/api/useSystemApi/goodsComment'

const emit = defineEmits(['success'])

const state = reactive({
  visible: false,
  loading: false,
  content: '',
  commentId: 0,
})

const openDialog = (row: any) => {
  state.commentId = row?.id
  state.content = ''
  state.loading = false
  state.visible = true
}

const onSubmit = async () => {
  const content = state.content.trim()
  if (!content) {
    ElNotification({
      title: '失败',
      message: '回复内容不能为空',
      type: 'error',
      duration: 3000,
      position: 'top-right',
    })
    return
  }

  state.loading = true
  try {
    await useGoodsCommentApi().reply({ comment_id: state.commentId, content })
    ElNotification({
      title: '成功',
      message: '回复成功',
      type: 'success',
      duration: 2500,
      position: 'top-right',
    })
    state.visible = false
    emit('success')
  } catch (err: any) {
    // 已回复过的评论由后端返回「订单商品已回复！」
    ElNotification({
      title: '失败',
      message: err?.msg || '回复失败',
      type: 'error',
      duration: 3000,
      position: 'top-right',
    })
  } finally {
    state.loading = false
  }
}

defineExpose({ openDialog })
</script>

<style scoped lang="scss">
.comment-reply-dialog {
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
    padding: 26px 30px 8px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 18px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    color: #3d4d66;
  }

  :deep(.el-textarea__inner) {
    border-radius: 4px;
    font-size: 14px;
    line-height: 1.6;
  }
}

.comment-reply-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .comment-reply-cancel {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .comment-reply-confirm {
    width: 76px;
    height: 36px;
    border-radius: 4px;
    background: #1890ff;
    border-color: #1890ff;

    &:hover {
      background: #40a9ff;
      border-color: #40a9ff;
    }
  }
}

@media screen and (max-width: 768px) {
  :global(.comment-reply-dialog) {
    width: 92% !important;
  }
}
</style>
