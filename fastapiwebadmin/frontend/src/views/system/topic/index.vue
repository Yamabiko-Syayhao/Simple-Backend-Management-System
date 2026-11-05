<template>
  <div class="topic-page">
    <div class="topic-panel">
      <div class="topic-toolbar">
        <el-input
          v-model="state.query.title"
          class="topic-input"
          placeholder="请输入专题标题"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.query.subtitle"
          class="topic-input"
          placeholder="请输入专题子标题"
          clearable
          @keyup.enter="onSearch"
        />
        <el-select
          v-model="state.query.sort_by"
          class="topic-input"
          @change="onSortChange"
        >
          <el-option value="id" label="按序号排序" />
          <el-option value="time" label="按时间排序" />
          <el-option value="price" label="按价格排序" />
        </el-select>
        <el-button type="primary" :icon="Search" @click="onSearch"
          >查找</el-button
        >
        <el-button
          type="primary"
          :icon="Download"
          :loading="state.exporting"
          @click="onExport"
          >导出</el-button
        >
      </div>
      <div class="topic-create-toolbar">
        <el-button type="primary" :icon="EditPen" @click="onAdd"
          >添加</el-button
        >
        <el-button
          type="danger"
          :icon="Delete"
          :loading="state.deleting"
          @click="onBatchDelete"
          >批量删除</el-button
        >
      </div>
      <el-table
        ref="tableRef"
        v-loading="state.loading"
        :data="state.rows"
        border
        row-key="id"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        empty-text="暂无数据"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="48" align="center" />
        <el-table-column
          prop="title"
          label="专题标题"
          min-width="150"
          align="center"
        />
        <el-table-column
          prop="subtitle"
          label="专题子标题"
          min-width="280"
          align="center"
          show-overflow-tooltip
        >
          <template #default="{ row }"
            ><span class="topic-subtitle">{{ row.subtitle }}</span></template
          >
        </el-table-column>
        <el-table-column label="图片" min-width="100" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              :preview-src-list="[row.image]"
              preview-teleported
              fit="cover"
              class="topic-thumb"
              ><template #error
                ><span class="topic-image-error">加载失败</span></template
              ></el-image
            >
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="专题详情" min-width="110" align="center"
          ><template #default="{ row }"
            ><el-button type="primary" size="small" @click="onPreview(row)"
              >查看</el-button
            ></template
          ></el-table-column
        >
        <el-table-column
          prop="price"
          label="底价"
          min-width="100"
          align="center"
        />
        <el-table-column
          prop="read_count_text"
          label="阅读数量"
          min-width="110"
          align="center"
        />
        <el-table-column label="操作" min-width="180" align="center"
          ><template #default="{ row }"
            ><div class="topic-actions">
              <el-button type="primary" size="small" @click="onEdit(row)"
                >编辑</el-button
              ><el-button
                type="danger"
                size="small"
                :disabled="state.deleting"
                @click="onDelete(row)"
                >删除</el-button
              >
            </div></template
          ></el-table-column
        >
      </el-table>
      <div class="topic-pagination">
        <el-pagination
          v-model:current-page="state.query.page"
          v-model:page-size="state.query.pageSize"
          :page-sizes="[10, 20, 30, 40, 50, 100]"
          :total="state.total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="onSizeChange"
          @current-change="getList"
        />
      </div>
    </div>
    <el-dialog
      v-model="state.previewVisible"
      title="专题详情"
      width="900px"
      class="topic-preview-dialog"
      :close-on-click-modal="false"
      destroy-on-close
      @close="closePreview"
    >
      <div v-loading="state.previewLoading" class="topic-preview-content">
        <div v-if="state.previewHtml" v-html="state.previewHtml" />
        <el-empty
          v-else-if="!state.previewLoading"
          description="暂无专题内容"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'promotionTopic' });
import {
  onActivated,
  onBeforeUnmount,
  onDeactivated,
  onMounted,
  reactive,
  ref,
} from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
import { Delete, Download, EditPen, Search } from '@element-plus/icons-vue';
import DOMPurify from 'dompurify';
import { useTopicApi } from '/@/api/useSystemApi/topic';

const router = useRouter();
const tableRef = ref();
const state = reactive({
  loading: false,
  exporting: false,
  deleting: false,
  rows: [] as any[],
  total: 0,
  selectedIds: [] as number[],
  previewVisible: false,
  previewLoading: false,
  previewHtml: '',
  query: {
    title: '',
    subtitle: '',
    sort_by: 'time',
    sort_order: 'desc',
    page: 1,
    pageSize: 20,
  },
});
const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  fontWeight: '500',
  height: '42px',
  borderColor: '#e8edf3',
};
const cellStyle = { height: '60px', borderColor: '#e8edf3' };
const buildQuery = () => ({
  title: state.query.title.trim() || undefined,
  subtitle: state.query.subtitle.trim() || undefined,
  sort_by: state.query.sort_by,
  sort_order: state.query.sort_order,
});
let listRequestId = 0;
let previewRequestId = 0;
const getList = async () => {
  const requestId = ++listRequestId;
  state.loading = true;
  try {
    const res: any = await useTopicApi().getList({
      ...buildQuery(),
      page: state.query.page,
      pageSize: state.query.pageSize,
    });
    if (requestId !== listRequestId) return;
    state.rows = res.data?.rows || [];
    state.total = res.data?.rowTotal || 0;
    state.selectedIds = [];
    tableRef.value?.clearSelection();
    if (!state.rows.length && state.query.page > 1) {
      state.query.page = Math.max(
        1,
        Math.ceil(state.total / state.query.pageSize)
      );
      await getList();
    }
  } catch {
    // 统一拦截器负责接口错误提示。
  } finally {
    if (requestId === listRequestId) state.loading = false;
  }
};
const onSearch = () => {
  state.query.page = 1;
  getList();
};
const onSizeChange = () => {
  state.query.page = 1;
  getList();
};
const onSortChange = () => {
  state.query.sort_order = state.query.sort_by === 'time' ? 'desc' : 'asc';
  onSearch();
};
const onSelectionChange = (rows: any[]) => {
  state.selectedIds = rows.map((row) => row.id);
};
const onAdd = () => router.push('/promotion/topicCreate');
const onEdit = (row: any) =>
  router.push({ path: '/promotion/topicEdit', query: { id: row.id } });
const remove = async (ids: number[], batch: boolean) => {
  if (state.deleting) return;
  state.deleting = true;
  try {
    try {
      await ElMessageBox.confirm(
        batch
          ? `确定删除选中的 ${ids.length} 条专题及其商品关联吗？`
          : '确定删除此专题及其商品关联吗？',
        '提示',
        { type: 'warning', confirmButtonText: '确定', cancelButtonText: '取消' }
      );
    } catch {
      return;
    }
    if (batch) await useTopicApi().batchDeleted({ ids });
    else await useTopicApi().deleted({ id: ids[0] });
    ElNotification({
      title: '成功',
      message: '删除成功',
      type: 'success',
      position: 'top-right',
    });
    await getList();
  } catch {
    // 统一拦截器负责接口错误提示。
  } finally {
    state.deleting = false;
  }
};
const onDelete = (row: any) => remove([row.id], false);
const onBatchDelete = () => {
  if (state.deleting) return;
  if (!state.selectedIds.length) {
    ElMessage.warning('请选择至少一条记录');
    return;
  }
  remove([...state.selectedIds], true);
};
const onPreview = async (row: any) => {
  const requestId = ++previewRequestId;
  state.previewVisible = true;
  state.previewLoading = true;
  state.previewHtml = '';
  try {
    const res: any = await useTopicApi().getDetail({ id: row.id });
    if (requestId !== previewRequestId || !state.previewVisible) return;
    state.previewHtml = DOMPurify.sanitize(res.data?.content || '');
  } catch {
    // 统一拦截器负责接口错误提示。
  } finally {
    if (requestId === previewRequestId) state.previewLoading = false;
  }
};
const closePreview = () => {
  previewRequestId++;
};
const onExport = async () => {
  if (state.exporting) return;
  state.exporting = true;
  try {
    const blob: any = await useTopicApi().exportExcel(buildQuery());
    if (blob.type?.includes('json')) {
      const result = JSON.parse(await blob.text());
      ElMessage.error(result.msg || '导出失败');
      return;
    }
    const url = URL.createObjectURL(
      new Blob([blob], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
    );
    const link = document.createElement('a');
    link.href = url;
    link.download = `专题列表_${Date.now()}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch {
    // 统一拦截器负责接口错误提示。
  } finally {
    state.exporting = false;
  }
};
let activated = false;
onMounted(getList);
onActivated(() => {
  if (activated) getList();
  activated = true;
});
onDeactivated(() => {
  listRequestId++;
  previewRequestId++;
});
onBeforeUnmount(() => {
  listRequestId++;
  previewRequestId++;
});
</script>

<style scoped lang="scss">
.topic-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
  overflow-x: hidden;
  --el-color-primary: #1890ff;
}
.topic-panel {
  background: #fff;
}
.topic-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 2px 18px;
  .topic-input {
    width: 200px;
    :deep(.el-input__wrapper),
    :deep(.el-select__wrapper) {
      min-height: 32px;
      border-radius: 4px;
    }
  }
  .el-button {
    margin-left: 0;
    height: 32px;
  }
}
.topic-create-toolbar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-bottom: 12px;
  .el-button {
    margin-left: 0;
  }
}
.topic-subtitle {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.7;
}
.topic-thumb {
  width: 40px;
  height: 40px;
  vertical-align: middle;
}
.topic-image-error {
  color: #b9c0cc;
  font-size: 11px;
}
.topic-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  .el-button {
    margin-left: 0;
    padding: 7px 16px;
  }
}
.topic-pagination {
  padding: 24px 2px 6px;
  overflow-x: auto;
}
.topic-preview-content {
  min-height: 160px;
  overflow-wrap: anywhere;
  overflow-x: auto;
  :deep(img),
  :deep(video),
  :deep(iframe) {
    max-width: 100%;
  }
  :deep(table) {
    border-collapse: collapse;
    max-width: 100%;
  }
}
@media (max-width: 900px) {
  .topic-toolbar .topic-input {
    flex: 1 1 calc(50% - 4px);
    width: auto;
    min-width: 0;
  }
  .topic-pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}
@media (max-width: 560px) {
  .topic-page {
    padding: 10px;
  }
  .topic-toolbar {
    .topic-input {
      flex: 1 1 100%;
    }
    .el-button {
      flex: 1 1 40%;
    }
  }
  .topic-create-toolbar .el-button {
    flex: 1 1 40%;
  }
}
</style>
<style lang="scss">
.topic-preview-dialog {
  max-width: 92vw;
}
</style>
