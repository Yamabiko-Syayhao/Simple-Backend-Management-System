<template>
  <div class="footprint-page">
    <div class="footprint-panel">
      <!-- 搜索区 -->
      <div class="footprint-toolbar">
        <el-input
          v-model="state.listQuery.member_id"
          class="footprint-input"
          placeholder="请输入用户ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.goods_id"
          class="footprint-input"
          placeholder="请输入商品ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="footprint-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="footprint-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="footprint-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
        :default-sort="{ prop: 'id', order: 'descending' }"
        @sort-change="onSortChange"
      >
        <el-table-column prop="id" label="足迹ID" min-width="200" sortable="custom">
          <template #default="{ row }">
            <span class="footprint-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="member_id" label="用户ID" min-width="340" align="center">
          <template #default="{ row }">
            <span class="footprint-cell-text">{{ row.member_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="goods_id" label="商品ID" min-width="340" align="center">
          <template #default="{ row }">
            <span class="footprint-cell-text">{{ row.goods_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="creation_date" label="添加时间" min-width="340" align="center">
          <template #default="{ row }">
            <span class="footprint-cell-text">{{ row.creation_date || '-' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="footprint-pagination">
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
defineOptions({ name: 'SystemFootprint' })

import { onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { useFootprintApi } from '/@/api/useSystemApi/footprint'

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
  height: '42px',
  borderColor: '#e8edf3',
}

const buildQuery = () => {
  const payload: Record<string, any> = {
    sort_order: state.listQuery.sortOrder,
  }
  if (state.listQuery.member_id) {
    payload.member_id = Number(state.listQuery.member_id) || undefined
  }
  if (state.listQuery.goods_id) {
    payload.goods_id = Number(state.listQuery.goods_id) || undefined
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

  useFootprintApi()
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

const onExport = async () => {
  state.exporting = true
  try {
    const blob: any = await useFootprintApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `会员足迹_${new Date().getTime()}.xlsx`
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
.footprint-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.footprint-panel {
  background: #fff;
}

.footprint-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .footprint-input {
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

  .footprint-btn {
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

.footprint-table {
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

.footprint-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.footprint-pagination {
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
  .footprint-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .footprint-toolbar {
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 12px;

    .footprint-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .footprint-btn {
      flex: 0 1 auto;
      margin-left: 0;
      min-width: 76px;
    }
  }

  .footprint-pagination {
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
  .footprint-toolbar {
    .footprint-input {
      flex: 1 1 100%;
    }

    .footprint-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }

  .footprint-pagination {
    :deep(.el-pagination__sizes) {
      margin-right: 4px;
    }

    :deep(.el-pagination__jump) {
      margin-left: 4px;
    }
  }
}
</style>
