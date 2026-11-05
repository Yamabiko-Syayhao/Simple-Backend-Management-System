<template>
  <div class="faq-page">
    <div class="faq-panel">
      <!-- 搜索区 -->
      <div class="faq-toolbar">
        <el-input
          v-model="state.listQuery.question"
          class="faq-input"
          placeholder="请输入问题"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="faq-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="faq-btn" type="primary" :icon="Plus" @click="onAdd">添加</el-button>
        <el-button class="faq-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="faq-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
        :default-sort="{ prop: 'id', order: 'descending' }"
        @sort-change="onSortChange"
      >
        <el-table-column prop="id" label="问题ID" min-width="140" sortable="custom" align="center">
          <template #default="{ row }">
            <span class="faq-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="question" label="问题内容" min-width="280" align="center">
          <template #default="{ row }">
            <span class="faq-cell-text faq-long">{{ row.question }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="answer" label="问题回复" min-width="460" align="center">
          <template #default="{ row }">
            <span class="faq-cell-text faq-long">{{ row.answer }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="180" align="center">
          <template #default="{ row }">
            <div class="faq-actions">
              <el-button type="primary" size="small" class="faq-edit-btn" @click="onEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" class="faq-del-btn" @click="onDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="faq-pagination">
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

    <FaqDialog ref="faqDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemFaq' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Download, Plus, Search } from '@element-plus/icons-vue'
import FaqDialog from '/@/views/system/faq/FaqDialog.vue'
import { useFaqApi } from '/@/api/useSystemApi/faq'

const faqDialogRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    question: '',
    sortOrder: 'desc',
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
  height: '64px',
  borderColor: '#e8edf3',
}

const buildQuery = () => {
  const payload: Record<string, any> = {
    sort_order: state.listQuery.sortOrder,
  }
  if (state.listQuery.question) payload.question = state.listQuery.question
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useFaqApi()
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

const onSortChange = ({ prop, order }: any) => {
  if (prop !== 'id') return
  state.listQuery.sortOrder = order === 'ascending' ? 'asc' : 'desc'
  state.listQuery.page = 1
  getList()
}

const onAdd = () => {
  faqDialogRef.value.openDialog('add')
}

const onEdit = (row: any) => {
  faqDialogRef.value.openDialog('edit', row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除问题「${row.question}」吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      await useFaqApi().deleted({ id: row.id })
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
    const blob: any = await useFaqApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `通用问题_${new Date().getTime()}.xlsx`
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
.faq-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.faq-panel {
  background: #fff;
}

.faq-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .faq-input {
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

  .faq-btn {
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

.faq-table {
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

.faq-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.faq-long {
  display: inline-block;
  line-height: 1.6;
  text-align: left;
  white-space: normal;
  word-break: break-all;
}

.faq-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .faq-edit-btn {
    border-radius: 3px;
    background: #409eff;
    border-color: #409eff;
    padding: 7px 16px;
  }

  .faq-del-btn {
    border-radius: 3px;
    background: #f56c6c;
    border-color: #f56c6c;
    padding: 7px 16px;
  }
}

.faq-pagination {
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
  .faq-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .faq-toolbar {
    flex-wrap: wrap;
    gap: 8px;

    .faq-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .faq-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .faq-pagination {
    overflow-x: auto;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .faq-toolbar {
    .faq-input {
      flex: 1 1 100%;
    }

    .faq-btn {
      flex: 1 1 30%;
      height: 38px;
    }
  }
}
</style>
