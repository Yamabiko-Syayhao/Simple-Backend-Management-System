<template>
  <div class="feedback-page">
    <div class="feedback-panel">
      <!-- 搜索区 -->
      <div class="feedback-toolbar">
        <el-input
          v-model="state.listQuery.username"
          class="feedback-input"
          placeholder="请输入用户名"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.feedback_id"
          class="feedback-input"
          placeholder="请输入反馈ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="feedback-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="feedback-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="feedback-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="反馈ID" min-width="140" align="center">
          <template #default="{ row }">
            <span class="feedback-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="username" label="用户名" min-width="160" align="center">
          <template #default="{ row }">
            <span class="feedback-cell-text">{{ row.username || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="mobile" label="手机号码" min-width="180" align="center">
          <template #default="{ row }">
            <span class="feedback-cell-text">{{ row.mobile || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="feedback_type" label="反馈类型" min-width="160" align="center">
          <template #default="{ row }">
            <span class="feedback-cell-text">{{ row.feedback_type || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="content" label="反馈内容" min-width="220" align="center">
          <template #default="{ row }">
            <span class="feedback-cell-text feedback-content">{{ row.content || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="反馈图片" min-width="180" align="center">
          <template #default="{ row }">
            <div v-if="row.image_list && row.image_list.length" class="feedback-images">
              <el-image
                v-for="(img, index) in row.image_list"
                :key="index"
                :src="img"
                :preview-src-list="row.image_list"
                :initial-index="index"
                fit="cover"
                class="feedback-image"
                preview-teleported
              />
            </div>
            <span v-else class="feedback-cell-text">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="creation_date" label="时间" min-width="200" align="center">
          <template #default="{ row }">
            <span class="feedback-cell-text">{{ row.creation_date || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="feedback-pagination">
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
defineOptions({ name: 'SystemFeedback' })

import { onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { useFeedbackApi } from '/@/api/useSystemApi/feedback'

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    username: '',
    feedback_id: '',
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
  height: '52px',
  borderColor: '#e8edf3',
}

const buildQuery = () => {
  const payload: Record<string, any> = {}
  if (state.listQuery.username) {
    payload.username = state.listQuery.username
  }
  if (state.listQuery.feedback_id) {
    payload.feedback_id = Number(state.listQuery.feedback_id) || undefined
  }
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useFeedbackApi()
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

const onExport = async () => {
  state.exporting = true
  try {
    const blob: any = await useFeedbackApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `意见反馈_${new Date().getTime()}.xlsx`
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
.feedback-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.feedback-panel {
  background: #fff;
}

.feedback-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .feedback-input {
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

  .feedback-btn {
    height: 40px;
    min-width: 88px;
    margin-left: 4px;
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

.feedback-table {
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

.feedback-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.feedback-content {
  display: inline-block;
  line-height: 1.5;
  word-break: break-all;
  white-space: normal;
}

.feedback-images {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
}

.feedback-image {
  width: 40px;
  height: 40px;
  border-radius: 3px;
}

.feedback-pagination {
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
  .feedback-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .feedback-toolbar {
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 12px;

    .feedback-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .feedback-btn {
      flex: 0 1 auto;
      margin-left: 0;
      min-width: 76px;
    }
  }

  .feedback-pagination {
    overflow-x: auto;
    padding-bottom: 10px;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }

    :deep(.el-pagination__jump) {
      margin-left: 0;
    }
  }
}

@media screen and (max-width: 560px) {
  .feedback-toolbar {
    .feedback-input {
      flex: 1 1 100%;
    }

    .feedback-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }

  .feedback-pagination {
    :deep(.el-pagination__sizes) {
      margin-right: 4px;
    }

    :deep(.el-pagination__jump) {
      margin-left: 4px;
    }
  }
}
</style>
