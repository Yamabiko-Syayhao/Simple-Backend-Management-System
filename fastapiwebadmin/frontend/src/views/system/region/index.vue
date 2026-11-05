<template>
  <div class="region-page">
    <div class="region-panel">
      <el-table
        ref="tableRef"
        v-loading="state.loading"
        :data="state.listData"
        row-key="id"
        class="region-table"
        border
        :tree-props="{ children: 'children' }"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <el-table-column prop="name" label="区域名称" min-width="380">
          <template #default="{ row }">
            <span class="region-name">{{ row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="level_name" label="区域类型" min-width="280" align="center">
          <template #default="{ row }">
            <span class="region-cell-text">{{ row.level_name }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="code" label="区域编码" min-width="280" align="center">
          <template #default="{ row }">
            <span class="region-cell-text">{{ row.code }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemRegion' })

import { onMounted, reactive, ref } from 'vue'
import { useRegionApi } from '/@/api/useSystemApi/region'

const tableRef = ref()

const state = reactive({
  loading: false,
  listData: [] as any[],
})

const headerCellStyle = {
  background: '#fafbfc',
  color: '#3d4d66',
  fontWeight: '500',
  height: '44px',
  borderColor: '#e8edf3',
}

const cellStyle = {
  height: '36px',
  borderColor: '#e8edf3',
  padding: '0 12px',
}

const getList = () => {
  state.loading = true
  useRegionApi()
    .getTree()
    .then((res: any) => {
      state.listData = res.data || []
      // 默认展开第一个省及其下级，和设计稿一致
      const first = state.listData[0]
      if (first) {
        tableRef.value?.toggleRowExpansion(first, true)
        const child = (first.children || [])[0]
        if (child) tableRef.value?.toggleRowExpansion(child, true)
      }
    })
    .finally(() => {
      state.loading = false
    })
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.region-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.region-panel {
  background: #fff;
}

.region-table {
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

  :deep(.el-table__expand-icon) {
    color: #909aa8;
  }
}

.region-name {
  font-size: 14px;
  color: #3d4d66;
}

.region-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

/* ============================ 响应式 ============================ */
@media screen and (max-width: 900px) {
  .region-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .region-table {
    :deep(.el-table__body-wrapper) {
      overflow-x: auto;
    }
  }
}
</style>
