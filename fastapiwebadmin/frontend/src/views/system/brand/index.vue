<template>
  <div class="brand-page">
    <div class="brand-panel">
      <!-- 搜索区 -->
      <div class="brand-toolbar">
        <el-input
          v-model="state.listQuery.brand_id"
          class="brand-input"
          placeholder="请输入品牌商ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.name"
          class="brand-input"
          placeholder="请输入品牌商名称"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="brand-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="brand-btn" type="primary" :icon="Plus" @click="onAdd">添加</el-button>
        <el-button class="brand-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="brand-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="品牌商ID" min-width="130" align="center">
          <template #default="{ row }">
            <span class="brand-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="品牌商名称" min-width="180" align="center">
          <template #default="{ row }">
            <span class="brand-cell-text">{{ row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="品牌商图片" min-width="140" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              :preview-src-list="[row.image]"
              fit="cover"
              class="brand-thumb"
              preview-teleported
            />
            <div v-else class="brand-thumb brand-thumb--empty">
              <el-icon :size="18"><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="介绍" min-width="460" align="center">
          <template #default="{ row }">
            <span class="brand-cell-text brand-desc">{{ row.description || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="floor_price" label="底价" min-width="110" align="center">
          <template #default="{ row }">
            <span class="brand-cell-text">{{ row.floor_price ?? '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="170" align="center">
          <template #default="{ row }">
            <div class="brand-actions">
              <el-button type="primary" size="small" class="brand-edit-btn" @click="onEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" class="brand-del-btn" @click="onDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="brand-pagination">
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

    <BrandDialog ref="brandDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemBrand' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Download, Picture, Plus, Search } from '@element-plus/icons-vue'
import BrandDialog from '/@/views/system/brand/BrandDialog.vue'
import { useBrandApi } from '/@/api/useSystemApi/brand'

const brandDialogRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    brand_id: '',
    name: '',
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
  const payload: Record<string, any> = {}
  if (state.listQuery.brand_id) {
    payload.brand_id = Number(state.listQuery.brand_id) || undefined
  }
  if (state.listQuery.name) {
    payload.name = state.listQuery.name
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

  useBrandApi()
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

const onAdd = () => {
  brandDialogRef.value.openDialog('add')
}

const onEdit = (row: any) => {
  brandDialogRef.value.openDialog('edit', row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除品牌商「${row.name}」吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      await useBrandApi().deleted({ id: row.id })
      ElNotification({
        title: '成功',
        message: '删除成功',
        type: 'success',
        duration: 2500,
        position: 'top-right',
      })
      // 删除后当前页可能空了，回退一页
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
    const blob: any = await useBrandApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `品牌制造商_${new Date().getTime()}.xlsx`
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
.brand-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.brand-panel {
  background: #fff;
}

.brand-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .brand-input {
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

  .brand-btn {
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

.brand-table {
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

.brand-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.brand-desc {
  display: inline-block;
  line-height: 1.6;
  text-align: left;
  word-break: break-all;
  white-space: normal;
}

.brand-thumb {
  width: 56px;
  height: 56px;
  border-radius: 4px;
  display: block;
  margin: 0 auto;
}

.brand-thumb--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f2f4f7;
  color: #b9c0cc;
}

.brand-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .brand-edit-btn {
    border-radius: 3px;
    background: #409eff;
    border-color: #409eff;
    padding: 7px 16px;
  }

  .brand-del-btn {
    border-radius: 3px;
    background: #f56c6c;
    border-color: #f56c6c;
    padding: 7px 16px;
  }
}

.brand-pagination {
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
  .brand-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .brand-toolbar {
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 12px;

    .brand-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .brand-btn {
      flex: 0 1 auto;
      margin-left: 0;
      min-width: 76px;
    }
  }

  .brand-pagination {
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
  .brand-toolbar {
    .brand-input {
      flex: 1 1 100%;
    }

    .brand-btn {
      flex: 1 1 30%;
      height: 38px;
    }
  }

  .brand-pagination {
    :deep(.el-pagination__sizes) {
      margin-right: 4px;
    }

    :deep(.el-pagination__jump) {
      margin-left: 4px;
    }
  }
}
</style>
