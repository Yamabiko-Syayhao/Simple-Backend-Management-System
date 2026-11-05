<template>
  <div class="category-page">
    <div class="category-panel">
      <!-- 只有一个「添加」按钮（对齐设计稿） -->
      <div class="category-toolbar">
        <el-button class="category-btn" type="primary" :icon="Plus" @click="onAdd">添加</el-button>
      </div>

      <!-- 树形列表 -->
      <el-table
        v-loading="state.loading"
        :data="state.listData"
        row-key="id"
        class="category-table"
        border
        :tree-props="{ children: 'children' }"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="类目ID" min-width="150">
          <template #default="{ row }">
            <span class="category-cell-text">{{ row.id }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="类目名" min-width="140" align="center">
          <template #default="{ row }">
            <span class="category-cell-text">{{ row.name }}</span>
          </template>
        </el-table-column>

        <el-table-column label="类目图标" min-width="140" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.icon"
              :src="row.icon"
              :preview-src-list="[row.icon]"
              fit="contain"
              class="category-icon"
              preview-teleported
            />
            <div v-else class="category-icon category-icon--empty">
              <el-icon :size="18"><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="类目图片" min-width="160" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              :preview-src-list="[row.image]"
              fit="cover"
              class="category-image"
              preview-teleported
            />
            <div v-else class="category-image category-icon--empty">
              <el-icon :size="18"><Picture /></el-icon>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="keywords" label="关键字" min-width="140" align="center">
          <template #default="{ row }">
            <span class="category-cell-text">{{ row.keywords || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="description" label="简介" min-width="240" align="center">
          <template #default="{ row }">
            <span class="category-cell-text category-desc">{{ row.description || '' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="级别" min-width="140" align="center">
          <template #default="{ row }">
            <span class="category-tag" :class="row.level === 1 ? 'category-tag--first' : 'category-tag--second'">
              {{ row.level === 1 ? '一级类目' : '二级类目' }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" min-width="180" align="center">
          <template #default="{ row }">
            <div class="category-actions">
              <el-button type="primary" size="small" class="category-edit-btn" @click="onEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" class="category-del-btn" @click="onDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <CategoryDialog ref="categoryDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemCategory' })

import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import { Picture, Plus } from '@element-plus/icons-vue'
import CategoryDialog from '/@/views/system/category/CategoryDialog.vue'
import { useCategoryApi } from '/@/api/useSystemApi/category'

const categoryDialogRef = ref()

const state = reactive({
  loading: false,
  listData: [] as any[],
})

const headerCellStyle = {
  background: '#f7f9fc',
  color: '#5a6a85',
  fontWeight: '500',
  height: '56px',
  borderColor: '#e8edf3',
}

const cellStyle = {
  height: '76px',
  borderColor: '#e8edf3',
}

/** 把后端返回的平铺列表组装成两级树 */
const buildTree = (rows: any[]) => {
  const roots = rows
    .filter((item) => item.level === 1)
    .map((item) => ({ ...item, children: [] as any[] }))
  const rootMap = new Map(roots.map((item) => [item.id, item]))

  rows
    .filter((item) => item.level === 2)
    .sort((a, b) => a.id - b.id)
    .forEach((child) => {
      const parent = rootMap.get(child.parent_id)
      if (parent) parent.children.push(child)
      else roots.push({ ...child, children: [] })
    })

  // 没有子节点的去掉 children，避免表格出现空箭头
  roots.forEach((item) => {
    if (item.children.length === 0) delete item.children
  })
  return roots
}

const getList = () => {
  state.loading = true
  useCategoryApi()
    .getList()
    .then((res: any) => {
      state.listData = buildTree(res.data?.rows || [])
    })
    .finally(() => {
      state.loading = false
    })
}

const onAdd = () => {
  categoryDialogRef.value.openDialog('add')
}

const onEdit = (row: any) => {
  categoryDialogRef.value.openDialog('edit', row)
}

const onDelete = (row: any) => {
  ElMessageBox.confirm(`确定要删除类目「${row.name}」吗？`, '提示', {
    type: 'warning',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(async () => {
      try {
        await useCategoryApi().deleted({ id: row.id })
        ElNotification({
          title: '成功',
          message: '删除成功',
          type: 'success',
          duration: 2500,
          position: 'top-right',
        })
        getList()
      } catch (e) {
        // 业务错误已在 request 拦截器里提示（例如「该类目下存在子类目」）
      }
    })
    .catch(() => {
      /* 取消删除 */
    })
}

onMounted(() => {
  getList()
})
</script>

<style scoped lang="scss">
.category-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
}

.category-panel {
  background: #fff;
}

.category-toolbar {
  display: flex;
  align-items: center;
  padding: 4px 2px 18px;

  .category-btn {
    height: 38px;
    min-width: 92px;
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

.category-table {
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

.category-cell-text {
  font-size: 14px;
  color: #3d4d66;
}

.category-desc {
  display: inline-block;
  line-height: 1.6;
  text-align: left;
  white-space: normal;
  word-break: break-all;
}

.category-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto;
  display: block;
  background: #fff;
  border-radius: 4px;
}

.category-image {
  width: 80px;
  height: 52px;
  margin: 0 auto;
  display: block;
  border-radius: 4px;
}

.category-icon--empty {
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f2f4f7;
  color: #b9c0cc;
  border-radius: 4px;
}

.category-tag {
  display: inline-block;
  padding: 2px 10px;
  font-size: 13px;
  line-height: 22px;
  border-radius: 3px;
  white-space: nowrap;
}

.category-tag--first {
  color: #1890ff;
  background: #eaf4ff;
  border: 1px solid #cfe6ff;
}

.category-tag--second {
  color: #8b93a6;
  background: #f2f4f7;
  border: 1px solid #e6e8eb;
}

.category-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  .category-edit-btn {
    border-radius: 3px;
    background: #409eff;
    border-color: #409eff;
    padding: 7px 16px;
  }

  .category-del-btn {
    border-radius: 3px;
    background: #f56c6c;
    border-color: #f56c6c;
    padding: 7px 16px;
  }
}

/* ============================ 响应式 ============================ */
@media screen and (max-width: 900px) {
  .category-page {
    padding: 10px;
    overflow-x: hidden;
  }
}
</style>
