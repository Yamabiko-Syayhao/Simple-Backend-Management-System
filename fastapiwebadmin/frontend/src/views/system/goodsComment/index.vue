<template>
  <div class="comment-page">
    <div class="comment-panel">
      <!-- 搜索区 -->
      <div class="comment-toolbar">
        <el-input
          v-model="state.listQuery.member_id"
          class="comment-input"
          placeholder="请输入用户ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.goods_id"
          class="comment-input"
          placeholder="请输入商品ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="comment-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="comment-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="comment-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <el-table-column prop="member_id" label="用户ID" min-width="140" align="center">
          <template #default="{ row }">
            <span class="comment-cell-text">{{ row.member_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="goods_id" label="商品ID" min-width="160" align="center">
          <template #default="{ row }">
            <span class="comment-cell-text">{{ row.goods_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="score" label="打分" min-width="120" align="center">
          <template #default="{ row }">
            <span class="comment-cell-text">{{ row.score }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="content" label="评论内容" min-width="360" align="center">
          <template #default="{ row }">
            <span class="comment-cell-text comment-content">{{ row.content || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="评论图片" min-width="170" align="center">
          <template #default="{ row }">
            <div v-if="row.image_list && row.image_list.length" class="comment-images">
              <el-image
                v-for="(img, index) in row.image_list"
                :key="index"
                :src="img"
                :preview-src-list="row.image_list"
                :initial-index="index"
                fit="cover"
                class="comment-thumb"
                preview-teleported
              >
                <template #error>
                  <div class="comment-thumb-error">加载失败</div>
                </template>
              </el-image>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="comment_time" label="时间" min-width="190" align="center">
          <template #default="{ row }">
            <span class="comment-cell-text">{{ row.comment_time || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="200" align="center">
          <template #default="{ row }">
            <div class="comment-actions">
              <el-button type="primary" size="small" class="comment-reply-btn" @click="onReply(row)">回复</el-button>
              <el-button type="danger" size="small" class="comment-del-btn" @click="onDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="comment-pagination">
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

    <ReplyDialog ref="replyDialogRef" @success="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemGoodsComment' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import ReplyDialog from '/@/views/system/goodsComment/ReplyDialog.vue'
import { useGoodsCommentApi } from '/@/api/useSystemApi/goodsComment'

const replyDialogRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    member_id: '',
    goods_id: '',
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

const buildQuery = () => {
  const payload: Record<string, any> = {}
  if (state.listQuery.member_id) payload.member_id = Number(state.listQuery.member_id) || undefined
  if (state.listQuery.goods_id) payload.goods_id = Number(state.listQuery.goods_id) || undefined
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useGoodsCommentApi()
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

const onReply = (row: any) => {
  replyDialogRef.value.openDialog(row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除这条评论吗？', '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      await useGoodsCommentApi().deleted({ id: row.id })
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
    const blob: any = await useGoodsCommentApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `商品评论_${new Date().getTime()}.xlsx`
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
.comment-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.comment-panel {
  background: #fff;
}

.comment-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .comment-input {
    width: 220px;

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

  .comment-btn {
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

.comment-table {
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

.comment-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.comment-content {
  display: inline-block;
  line-height: 1.6;
  text-align: left;
  white-space: normal;
  word-break: break-all;
}

.comment-images {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 6px;
}

.comment-thumb {
  width: 44px;
  height: 44px;
  border-radius: 3px;
  background: #f5f7fa;
}

.comment-thumb-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
}

.comment-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .comment-reply-btn {
    border-radius: 3px;
    background: #409eff;
    border-color: #409eff;
    padding: 7px 16px;
  }

  .comment-del-btn {
    border-radius: 3px;
    background: #f56c6c;
    border-color: #f56c6c;
    padding: 7px 16px;
  }
}

.comment-pagination {
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
  .comment-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .comment-toolbar {
    flex-wrap: wrap;
    gap: 8px;

    .comment-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .comment-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .comment-pagination {
    overflow-x: auto;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .comment-toolbar {
    .comment-input {
      flex: 1 1 100%;
    }

    .comment-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }
}
</style>
