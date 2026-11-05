<template>
  <div class="group-rule-page">
    <div class="group-rule-panel">
      <!-- 搜索区 -->
      <div class="group-rule-toolbar">
        <el-input
          v-model="state.listQuery.keyword"
          class="group-rule-input"
          placeholder="请输入商品编号"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="group-rule-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="group-rule-btn" type="primary" :icon="Plus" @click="onAdd">添加</el-button>
        <el-button class="group-rule-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="group-rule-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="团购规则ID" min-width="150" align="center">
          <template #default="{ row }">
            <span class="group-rule-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="goods_id" label="商品ID" min-width="140" align="center">
          <template #default="{ row }">
            <span class="group-rule-cell-text">{{ row.goods_id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="goods_name" label="名称" min-width="200" align="center">
          <template #default="{ row }">
            <span class="group-rule-cell-text group-rule-name">{{ row.goods_name || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="图片" min-width="120" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.goods_image"
              :src="row.goods_image"
              :preview-src-list="[row.goods_image]"
              fit="cover"
              class="group-rule-thumb"
              preview-teleported
            >
              <template #error>
                <div class="group-rule-thumb-error">加载失败</div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column prop="discount" label="团购优惠" min-width="140" align="center">
          <template #default="{ row }">
            <span class="group-rule-cell-text">{{ row.discount }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="people" label="团购要求" min-width="140" align="center">
          <template #default="{ row }">
            <span class="group-rule-cell-text">{{ row.people }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" min-width="140" align="center">
          <template #default="{ row }">
            <span class="group-rule-tag" :class="row.status === 1 ? 'group-rule-tag--off' : 'group-rule-tag--on'">
              {{ row.status_text }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="end_time" label="结束时间" min-width="190" align="center">
          <template #default="{ row }">
            <span class="group-rule-cell-text">{{ row.end_time || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="180" align="center">
          <template #default="{ row }">
            <div class="group-rule-actions">
              <el-button type="primary" size="small" class="group-rule-edit-btn" @click="onEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" class="group-rule-del-btn" @click="onDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="group-rule-pagination">
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

    <GroupRuleDialog ref="groupRuleDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemGroupRule' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Download, Plus, Search } from '@element-plus/icons-vue'
import GroupRuleDialog from '/@/views/system/groupRule/GroupRuleDialog.vue'
import { useGroupRuleApi } from '/@/api/useSystemApi/groupRule'

const groupRuleDialogRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    keyword: '',
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
  if (state.listQuery.keyword) payload.keyword = state.listQuery.keyword
  return payload
}

const getList = () => {
  state.loading = true
  const payload = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    ...buildQuery(),
  }

  useGroupRuleApi()
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
  groupRuleDialogRef.value.openDialog('add')
}

const onEdit = (row: any) => {
  groupRuleDialogRef.value.openDialog('edit', row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除商品「${row.goods_name || row.goods_id}」的团购规则吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      await useGroupRuleApi().deleted({ id: row.id })
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
    const blob: any = await useGroupRuleApi().exportExcel(buildQuery())
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `团购规则_${new Date().getTime()}.xlsx`
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
.group-rule-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.group-rule-panel {
  background: #fff;
}

.group-rule-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .group-rule-input {
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

  .group-rule-btn {
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

.group-rule-table {
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

.group-rule-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.group-rule-name {
  display: inline-block;
  line-height: 1.6;
  white-space: normal;
  word-break: break-all;
}

.group-rule-thumb {
  width: 44px;
  height: 44px;
  border-radius: 3px;
  background: #f5f7fa;
}

.group-rule-thumb-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
}

.group-rule-tag {
  display: inline-block;
  padding: 2px 10px;
  font-size: 13px;
  line-height: 22px;
  border-radius: 3px;
  white-space: nowrap;
}

.group-rule-tag--off {
  color: #1890ff;
  background: #eaf4ff;
  border: 1px solid #cfe6ff;
}

.group-rule-tag--on {
  color: #52c41a;
  background: #f0f9eb;
  border: 1px solid #d9f0cc;
}

.group-rule-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .group-rule-edit-btn {
    border-radius: 3px;
    background: #409eff;
    border-color: #409eff;
    padding: 7px 16px;
  }

  .group-rule-del-btn {
    border-radius: 3px;
    background: #f56c6c;
    border-color: #f56c6c;
    padding: 7px 16px;
  }
}

.group-rule-pagination {
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
  .group-rule-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .group-rule-toolbar {
    flex-wrap: wrap;
    gap: 8px;

    .group-rule-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .group-rule-btn {
      flex: 0 1 auto;
      min-width: 76px;
    }
  }

  .group-rule-pagination {
    overflow-x: auto;

    :deep(.el-pagination) {
      flex-wrap: wrap;
      row-gap: 8px;
      font-size: 13px;
    }
  }
}

@media screen and (max-width: 560px) {
  .group-rule-toolbar {
    .group-rule-input {
      flex: 1 1 100%;
    }

    .group-rule-btn {
      flex: 1 1 30%;
      height: 38px;
    }
  }
}
</style>
