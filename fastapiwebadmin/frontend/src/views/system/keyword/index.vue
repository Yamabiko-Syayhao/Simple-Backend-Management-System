<template>
  <div class="keyword-page">
    <div class="keyword-panel">
      <!-- 搜索区 -->
      <div class="keyword-toolbar">
        <el-input
          v-model="state.listQuery.keyword"
          class="keyword-input"
          placeholder="请输入关键字"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.link"
          class="keyword-input"
          placeholder="请输入跳转链接"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="keyword-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="keyword-btn" type="primary" :icon="Plus" @click="onAdd">添加</el-button>
        <el-button class="keyword-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="keyword-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
        :default-sort="{ prop: 'id', order: 'descending' }"
        @sort-change="onSortChange"
      >
        <el-table-column prop="id" label="关键词ID" min-width="160" sortable="custom" align="center">
          <template #default="{ row }">
            <span class="keyword-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="keyword" label="关键词" min-width="220" align="center">
          <template #default="{ row }">
            <span class="keyword-cell-text">{{ row.keyword }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="link" label="跳转链接" min-width="460" align="center">
          <template #default="{ row }">
            <span class="keyword-cell-text keyword-link">{{ row.link || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="是否推荐" min-width="150" align="center">
          <template #default="{ row }">
            <span class="keyword-tag" :class="row.is_recommend === 1 ? 'keyword-tag--yes' : 'keyword-tag--no'">
              {{ row.is_recommend_text }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="是否默认" min-width="150" align="center">
          <template #default="{ row }">
            <span class="keyword-tag" :class="row.is_default === 1 ? 'keyword-tag--yes' : 'keyword-tag--no'">
              {{ row.is_default_text }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="200" align="center">
          <template #default="{ row }">
            <div class="keyword-actions">
              <el-button type="primary" size="small" class="keyword-edit-btn" @click="onEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" class="keyword-del-btn" @click="onDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="keyword-pagination">
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

    <KeywordDialog ref="keywordDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemKeyword' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Download, Plus, Search } from '@element-plus/icons-vue'
import KeywordDialog from '/@/views/system/keyword/KeywordDialog.vue'
import { useKeywordApi } from '/@/api/useSystemApi/keyword'

const keywordDialogRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    keyword: '',
    link: '',
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
  height: '56px',
  borderColor: '#e8edf3',
}

const buildQuery = () => {
  const payload: Record<string, any> = {
    sort_order: state.listQuery.sortOrder,
  }
  if (state.listQuery.keyword) payload.keyword = state.listQuery.keyword
  if (state.listQuery.link) payload.link = state.listQuery.link
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useKeywordApi()
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
  keywordDialogRef.value.openDialog('add')
}

const onEdit = (row: any) => {
  keywordDialogRef.value.openDialog('edit', row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除关键词「${row.keyword}」吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      await useKeywordApi().deleted({ id: row.id })
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
    const blob: any = await useKeywordApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `关键词_${new Date().getTime()}.xlsx`
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
.keyword-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.keyword-panel {
  background: #fff;
}

.keyword-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .keyword-input {
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

  .keyword-btn {
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

.keyword-table {
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

.keyword-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.keyword-link {
  display: inline-block;
  line-height: 1.6;
  word-break: break-all;
  white-space: normal;
}

.keyword-tag {
  display: inline-block;
  padding: 2px 10px;
  font-size: 13px;
  line-height: 22px;
  border-radius: 3px;
  white-space: nowrap;
}

.keyword-tag--yes {
  color: #52c41a;
  background: #f0f9eb;
  border: 1px solid #d9f0cc;
}

.keyword-tag--no {
  color: #5b8ff9;
  background: #eef4ff;
  border: 1px solid #d9e5ff;
}

.keyword-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .keyword-edit-btn {
    border-radius: 3px;
    background: #409eff;
    border-color: #409eff;
    padding: 7px 16px;
  }

  .keyword-del-btn {
    border-radius: 3px;
    background: #f56c6c;
    border-color: #f56c6c;
    padding: 7px 16px;
  }
}

.keyword-pagination {
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
  .keyword-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .keyword-toolbar {
    flex-wrap: wrap;
    gap: 8px;

    .keyword-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .keyword-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .keyword-pagination {
    overflow-x: auto;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .keyword-toolbar {
    .keyword-input {
      flex: 1 1 100%;
    }

    .keyword-btn {
      flex: 1 1 30%;
      height: 38px;
    }
  }
}
</style>
