<template>
  <div class="group-activity-page">
    <div class="group-activity-panel">
      <!-- 搜索区 -->
      <div class="group-activity-toolbar">
        <el-input
          v-model="state.listQuery.rule_id"
          class="group-activity-input"
          placeholder="请输入团购规则ID"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="group-activity-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="group-activity-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        row-key="id"
        class="group-activity-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <!-- 展开：该活动的参与成员 -->
        <el-table-column type="expand" width="46">
          <template #default="{ row }">
            <div class="group-activity-members">
              <el-table :data="row.members" size="small" border empty-text="暂无数据">
                <el-table-column prop="order_id" label="订单ID" min-width="220" align="center">
                  <template #default="{ row: member }">
                    <span class="group-activity-cell-text">{{ member.order_id }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="member_id" label="用户ID" min-width="220" align="center">
                  <template #default="{ row: member }">
                    <span class="group-activity-cell-text">{{ member.member_id }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="order_id" label="订单ID" min-width="190" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.order_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="member_id" label="用户ID" min-width="190" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.member_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="participants" label="参与人数" min-width="170" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.participants }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="discount" label="团购折扣" min-width="170" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.discount }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="people" label="团购要求" min-width="170" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.people }}</span>
          </template>
        </el-table-column>

        <el-table-column label="分享图片" min-width="190" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.share_image"
              :src="row.share_image"
              :preview-src-list="[row.share_image]"
              fit="cover"
              class="group-activity-thumb"
              preview-teleported
            >
              <template #error>
                <div class="group-activity-thumb-error">加载失败</div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column prop="start_time" label="开始时间" min-width="200" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.start_time || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="end_time" label="结束时间" min-width="200" align="center">
          <template #default="{ row }">
            <span class="group-activity-cell-text">{{ row.end_time || '' }}</span>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="group-activity-pagination">
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
defineOptions({ name: 'SystemGroupActivity' })

import { onMounted, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search } from '@element-plus/icons-vue'
import { useGroupActivityApi } from '/@/api/useSystemApi/groupActivity'

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    rule_id: '',
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
  const payload: Record<string, any> = {}
  if (state.listQuery.rule_id) payload.rule_id = Number(state.listQuery.rule_id) || undefined
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useGroupActivityApi()
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
    const blob: any = await useGroupActivityApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `团购活动_${new Date().getTime()}.xlsx`
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
.group-activity-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.group-activity-panel {
  background: #fff;
}

.group-activity-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .group-activity-input {
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

  .group-activity-btn {
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

.group-activity-table {
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

.group-activity-members {
  padding: 10px 16px 10px 56px;
  background: #fbfcfd;
}

.group-activity-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.group-activity-thumb {
  width: 44px;
  height: 44px;
  border-radius: 3px;
  background: #f5f7fa;
}

.group-activity-thumb-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
}

.group-activity-pagination {
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
  .group-activity-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .group-activity-toolbar {
    flex-wrap: wrap;
    gap: 8px;

    .group-activity-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .group-activity-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .group-activity-pagination {
    overflow-x: auto;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .group-activity-toolbar {
    .group-activity-input {
      flex: 1 1 100%;
    }

    .group-activity-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }
}
</style>
