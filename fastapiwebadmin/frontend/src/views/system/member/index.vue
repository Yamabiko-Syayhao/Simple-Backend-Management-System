<template>
  <div class="member-page">
    <div class="member-panel">
      <!-- 搜索区 -->
      <div class="member-toolbar">
        <el-input
          v-model="state.listQuery.username"
          class="member-input"
          placeholder="请输入用户名"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.member_id"
          class="member-input"
          placeholder="请输入用户id"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.mobile"
          class="member-input"
          placeholder="请输入手机号"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button class="member-btn" type="primary" :icon="Search" @click="onSearch">查找</el-button>
        <el-button class="member-btn" type="primary" :icon="Download" :loading="state.exporting" @click="onExport">导出</el-button>
      </div>

      <!-- 列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="member-table"
        border
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
        :default-sort="{ prop: 'id', order: 'descending' }"
        @sort-change="onSortChange"
      >
        <el-table-column prop="id" label="用户ID" width="150" sortable="custom">
          <template #default="{ row }">
            <span class="member-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="nickname" label="用户昵称" width="130">
          <template #default="{ row }">
            <span class="member-cell-text">{{ row.nickname || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="用户头像" width="130" align="center">
          <template #default="{ row }">
            <el-avatar :size="42" :src="row.avatar || ''" class="member-avatar">
              <el-icon :size="22"><UserFilled /></el-icon>
            </el-avatar>
          </template>
        </el-table-column>

        <el-table-column prop="mobile" label="手机号码" width="180">
          <template #default="{ row }">
            <span class="member-cell-text member-mobile">{{ row.mobile || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="性别" width="90" align="center">
          <template #default="{ row }">
            <span class="member-tag member-tag-blue">{{ row.gender_name }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="birthday" label="生日" width="120" align="center">
          <template #default="{ row }">
            <span class="member-cell-text">{{ row.birthday || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="用户等级" width="160" align="center">
          <template #default="{ row }">
            <span class="member-tag member-tag-blue">{{ row.level_name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <span
              class="member-tag"
              :class="row.status === 1 ? 'member-tag-blue' : (row.status === 2 ? 'member-tag-red' : 'member-tag-gray')"
            >{{ row.status_name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button class="member-detail-btn" type="primary" size="small" @click="onOpenDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="member-pagination">
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

    <MemberDialog ref="memberDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemMember' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Search, UserFilled } from '@element-plus/icons-vue'
import MemberDialog from '/@/views/system/member/MemberDialog.vue'
import { useMemberApi } from '/@/api/useSystemApi/member'

const memberDialogRef = ref()

const state = reactive({
  loading: false,
  exporting: false,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    username: '',
    member_id: '',
    mobile: '',
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
  height: '74px',
  borderColor: '#e8edf3',
}

const getList = () => {
  state.loading = true
  const payload: Record<string, any> = {
    page: state.listQuery.page,
    pageSize: state.listQuery.pageSize,
    sort_order: state.listQuery.sortOrder,
  }
  if (state.listQuery.username) payload.username = state.listQuery.username
  if (state.listQuery.mobile) payload.mobile = state.listQuery.mobile
  if (state.listQuery.member_id) payload.member_id = Number(state.listQuery.member_id) || undefined

  useMemberApi()
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
    const payload: Record<string, any> = {}
    payload.sort_order = state.listQuery.sortOrder
    if (state.listQuery.username) payload.username = state.listQuery.username
    if (state.listQuery.mobile) payload.mobile = state.listQuery.mobile
    if (state.listQuery.member_id) payload.member_id = Number(state.listQuery.member_id) || undefined

    const blob: any = await useMemberApi().exportExcel(payload)
    const url = window.URL.createObjectURL(new Blob([blob], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }))
    const link = document.createElement('a')
    link.href = url
    link.download = `会员列表_${new Date().getTime()}.xlsx`
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

const onOpenDetail = (row: any) => {
  memberDialogRef.value.openDialog('edit', row)
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.member-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.member-panel {
  background: #fff;
}

.member-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 2px 18px;

  .member-input {
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

  .member-btn {
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

.member-table {
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

.member-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.member-mobile {
  display: inline-block;
  max-width: 150px;
  line-height: 1.5;
  word-break: break-all;
  white-space: normal;
}

.member-avatar {
  background: #dfe3e9;
  color: #fff;
}

.member-tag {
  display: inline-block;
  padding: 3px 10px;
  font-size: 13px;
  line-height: 20px;
  border-radius: 3px;
  white-space: nowrap;
}

.member-tag-blue {
  color: #1890ff;
  background: #eaf4ff;
  border: 1px solid #cfe6ff;
}

.member-tag-gray {
  color: #909aa8;
  background: #f4f5f7;
  border: 1px solid #e6e8eb;
}

.member-tag-red {
  color: #f5222d;
  background: #fff1f0;
  border: 1px solid #ffccc7;
}

.member-detail-btn {
  border-radius: 3px;
  background: #1890ff;
  border-color: #1890ff;
  padding: 7px 18px;
  font-size: 13px;

  &:hover {
    background: #40a9ff;
    border-color: #40a9ff;
  }
}

.member-pagination {
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
  .member-page {
    padding: 10px;
    overflow-x: hidden;
  }

  .member-toolbar {
    flex-wrap: wrap;
    gap: 8px;
    padding-bottom: 12px;

    .member-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }

    .member-btn {
      flex: 0 1 auto;
      margin-left: 0;
      min-width: 76px;
    }
  }

  .member-pagination {
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
  .member-toolbar {
    .member-input {
      flex: 1 1 100%;
    }

    .member-btn {
      flex: 1 1 40%;
      height: 38px;
    }
  }

  .member-pagination {
    :deep(.el-pagination__sizes) {
      margin-right: 4px;
    }

    :deep(.el-pagination__jump) {
      margin-left: 4px;
    }
  }
}
</style>
