<template>
  <div class="synrebort-table">
    <el-table
        :data="data"
        :tree-props="treeProps"
        :row-key="rowKey"
        v-bind="mergedTableOptions"
        :load="load"
        :border="border"
        :size="tableSize"
        v-loading="tableLoading"
        row-class-name="synrebort-table-row"
        :lazy="lazy"
        @selection-change="handleSelectionChange"
        @row-click="handleRowClick"
        @cell-click="handleCellClick"
        @sort-change="handleSortChange">
      <template v-for="(col, index) in columns" :key="index">
        <el-table-column
            class-name="index-class"
            v-if="col.columnType === 'index' || col.columnType === 'selection' || col.columnType === 'expand'"
            :sortable="col.sortable"
            :prop="col.key"
            :fixed="col.fixed"
            :align="col.align"
            :label="col.label"
            :type="col.columnType"
            :index="indexMethod"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)"/>
        <el-table-column
            v-else-if="col.columnType === 'image'"
            :sortable="col.sortable"
            :prop="col.key"
            :align="col.align"
            :fixed="col.fixed"
            :label="col.label"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)">
          <template #default="{ row }">
            <el-image
                preview-teleported
                :hide-on-click-modal="true"
                :preview-src-list="[row[col.prop]]"
                :src="row[col.prop]"
                fit="cover"
                class="synrebort-table__thumb"/>
          </template>
        </el-table-column>
        <el-table-column
            v-else-if="col.columnType === 'date'"
            :sortable="col.sortable"
            :prop="col.key"
            :align="col.align"
            :fixed="col.fixed"
            :label="col.label"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)">
          <template #default="{ row }">
            <span>{{ (row[col.prop]).format(col.dateFormat ?? 'YYYY-MM-DD') }}</span>
          </template>
        </el-table-column>
        <el-table-column
            :show-overflow-tooltip="col.show"
            v-else-if="col.slot"
            :sortable="col.sortable"
            :prop="col.key"
            :align="col.align"
            :fixed="col.fixed"
            :label="col.label"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)">
          <template #default="scope">
            <slot :name="col.slot" :row="scope.row" :index="scope.$index"></slot>
          </template>
        </el-table-column>
        <el-table-column
            v-else-if="col.buttons?.length"
            :align="col.align"
            :label="col.label"
            :fixed="col.fixed"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)"
            :class-name="isOperationColumn(col) ? 'synrebort-table-op-cell' : ''">
          <template #default="scope">
            <div class="synrebort-table-actions">
              <el-button
                  v-for="(btn, btnIndex) in col.buttons"
                  :key="btnIndex"
                  link
                  :type="btn.type || 'primary'"
                  @click="handleAction(btn.command, scope)"
              >{{ btn.name }}
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column
            :show-overflow-tooltip="col.show"
            v-else-if="col.render"
            :label="col.label"
            :sortable="col.sortable"
            :prop="col.key"
            :fixed="col.fixed"
            :align="col.align"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)"
            :class-name="isOperationColumn(col) ? 'synrebort-table-op-cell' : ''">
          <template #default="scope">
            <Expand :render="col.render"
                    :row="scope.row"
                    :index="scope.$index"/>
          </template>
        </el-table-column>
        <el-table-column
            :show-overflow-tooltip="col.show"
            v-else
            :label="col.label"
            :sortable="col.sortable"
            :prop="col.key"
            :fixed="col.fixed"
            :align="col.align"
            :width="resolveColumnWidth(col)"
            :min-width="resolveColumnMinWidth(col)">
          <template #default="{row}">
            {{ handleRow(row, col.key, col.lookupCode) }}
          </template>
        </el-table-column>
      </template>
      <template #empty>
        <el-empty description="暂无数据" :image-size="100"/>
      </template>
    </el-table>
    <div
        v-show="showPage && total > 0"
        class="synrebort-table__pagination custom-pagination"
        :class="paginationAlign">
      <el-pagination
          :total="total"
          :page-size="pageSize"
          :page-sizes="pageSizes"
          :layout="layout"
          :current-page="page"
          :background="paginationBackground"
          :size="paginationSize"
          @size-change="pageSizeChange"
          @current-change="currentPageChange"/>
    </div>
  </div>
</template>
<script setup lang="ts">
defineOptions({ name: 'synrebort-table' })
import {computed, defineAsyncComponent, reactive} from 'vue'
import {formatLookup} from '/@/utils/lookup'
import other from '/@/utils/other'
import { isOperationColumn, resolveColumnMinWidth, resolveColumnWidth } from '/@/utils/tableRender'

const Expand = defineAsyncComponent(() => import("./expand.vue"))

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  columns: {
    type: Array,
    default: () => []
  },
  options: {
    type: Object,
    default: () => ({})
  },
  rowKey: {
    type: String,
    default() {
      return ""
    }
  },
  border: {
    type: Boolean,
    default() {
      return true
    }
  },
  treeProps: {
    type: Object,
    default() {
      return {}
    }
  },
  showPage: {
    type: Boolean,
    default: () => true
  },
  lazy: {
    type: Boolean,
    default: () => false
  },
  load: {
    type: Function,
    default: () => {}
  },
  showPlaceholder: {
    type: Boolean,
    default: () => false
  },
  placeholder: {
    type: String,
    default: () => "-"
  },
  page: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 10
  },
  total: {
    type: Number,
    default: 0
  },
  pageSizes: {
    type: Array,
    default() {
      return [10, 20, 30, 50, 100]
    }
  },
  layout: {
    type: String,
    default: 'total, sizes, prev, pager, next, jumper'
  },
  paginationAlign: {
    type: String,
    default: 'center',
    validator: (v: string) => ['left', 'center', 'right'].includes(v)
  },
  paginationBackground: {
    type: Boolean,
    default: true
  },
  paginationSize: {
    type: String as () => 'small' | 'default' | 'large',
    default: 'default'
  },
  tableSize: {
    type: String as () => 'small' | 'default' | 'large',
    default: undefined
  },
  actionButtonSize: {
    type: String as () => 'small' | 'default' | 'large',
    default: 'default'
  },
  loading: {
    type: Boolean,
    default: () => false
  }
})

const state = reactive({
  tableLoading: false,
})

const tableLoading = computed(() => props.loading || state.tableLoading)

const resolvedTableSize = computed(() => {
  return props.tableSize || other.globalComponentSize() || 'default'
})

const mergedTableOptions = computed(() => ({
  stripe: true,
  tooltipEffect: 'dark',
  showHeader: true,
  ...props.options,
}))

const tableSize = computed(() => props.options?.size ?? resolvedTableSize.value)

const emit = defineEmits([
  "update:pageSize",
  "update:page",
  "update:loading",
  "pagination-change",
  "current-change",
  "command",
  "selection-change",
  "row-click",
  "cell-click",
  "sort-change",
])

const indexMethod = (index: number) => {
  if (!props.showPage) return index + 1
  return index + (props.page - 1) * props.pageSize + 1
}

const pageSizeChange = (pageSize: number) => {
  emit('update:pageSize', pageSize)
  emit('pagination-change', {page: props.page, limit: pageSize})
}

const currentPageChange = (currentPage: number) => {
  emit('current-change', currentPage)
  emit('update:page', currentPage)
  emit('pagination-change', {page: currentPage, limit: props.pageSize})
}

const handleAction = (command: any, scope: any) => {
  emit('command', command, scope.row)
}

const handleSelectionChange = (val: any) => {
  emit('selection-change', val)
}

const handleRowClick = (row: any, column: any, event: Event) => {
  emit('row-click', row, column, event)
}

const handleCellClick = (row: any, column: any, cell: any, event: Event) => {
  emit('cell-click', row, column, cell, event)
}

const handleSortChange = ({column, prop, order}: any) => {
  emit('sort-change', {column, prop, order})
}

const handleRow = (row: any, key: string, lookupCode: string) => {
  if (props.showPlaceholder && (!row[key] || row[key] === '' || row[key] === null)) {
    return props.placeholder
  }
  return lookupCode ? formatLookup(lookupCode, row[key]) : row[key]
}

const openLoading = () => {
  if (props.loading) {
    emit('update:loading', true)
  } else {
    state.tableLoading = true
  }
}

const closeLoading = () => {
  if (props.loading) {
    emit('update:loading', false)
  } else {
    state.tableLoading = false
  }
}

defineExpose({
  openLoading,
  closeLoading
})
</script>
<style lang="scss" scoped>
@use "./style";

:deep(.el-image__inner) {
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    transform: scale(1.08);
  }
}

.synrebort-table__thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
}

:deep(.el-table__placeholder) {
  display: none;
}

:deep(.synrebort-table-row) {
  .el-table__cell {
    padding-top: 10px;
    padding-bottom: 10px;
  }
}
</style>
