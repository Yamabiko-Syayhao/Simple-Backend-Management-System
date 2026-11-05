<template>
  <div class="ad-page">
    <div class="ad-panel">
      <div class="ad-toolbar">
        <el-input
          v-model="state.listQuery.title"
          class="ad-input"
          placeholder="请输入广告标题"
          clearable
          @keyup.enter="onSearch"
        />
        <el-input
          v-model="state.listQuery.content"
          class="ad-input"
          placeholder="请输入广告内容"
          clearable
          @keyup.enter="onSearch"
        />
        <el-button
          class="ad-btn"
          type="primary"
          :icon="Search"
          @click="onSearch"
          >查找</el-button
        >
        <el-button class="ad-btn" type="primary" :icon="Plus" @click="onAdd"
          >添加</el-button
        >
        <el-button
          class="ad-btn"
          type="primary"
          :icon="Download"
          :loading="state.exporting"
          @click="onExport"
          >导出</el-button
        >
      </div>

      <el-table
        v-loading="state.loading"
        :data="state.listData"
        class="ad-table"
        border
        row-key="id"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        :default-sort="{ prop: 'id', order: 'descending' }"
        empty-text="暂无数据"
        @sort-change="onSortChange"
      >
        <el-table-column
          prop="id"
          label="广告ID"
          min-width="120"
          align="center"
          sortable="custom"
        />
        <el-table-column
          prop="title"
          label="广告标题"
          min-width="140"
          align="center"
        >
          <template #default="{ row }"
            ><span class="ad-cell-text">{{ row.title }}</span></template
          >
        </el-table-column>
        <el-table-column
          prop="content"
          label="广告内容"
          min-width="160"
          align="center"
        >
          <template #default="{ row }"
            ><span class="ad-cell-text">{{ row.content }}</span></template
          >
        </el-table-column>
        <el-table-column label="广告图片" min-width="125" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="row.image"
              :preview-src-list="[row.image]"
              preview-teleported
              fit="contain"
              class="ad-thumb"
            >
              <template #error
                ><span class="ad-image-error">加载失败</span></template
              >
            </el-image>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="position"
          label="广告位置"
          min-width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tooltip :content="row.position_name" placement="top"
              ><span>{{ row.position }}</span></el-tooltip
            >
          </template>
        </el-table-column>
        <el-table-column
          prop="link"
          label="活动链接"
          min-width="150"
          align="center"
        >
          <template #default="{ row }"
            ><span class="ad-cell-text">{{ row.link || '' }}</span></template
          >
        </el-table-column>
        <el-table-column label="是否启用" min-width="120" align="center">
          <template #default="{ row }"
            ><el-tag
              :type="row.status === 1 ? 'success' : 'info'"
              size="small"
              >{{ row.status_name }}</el-tag
            ></template
          >
        </el-table-column>
        <el-table-column label="操作" min-width="190" align="center">
          <template #default="{ row }">
            <div class="ad-actions">
              <el-button
                class="ad-edit-btn"
                type="primary"
                size="small"
                @click="onEdit(row)"
                >编辑</el-button
              >
              <el-button
                class="ad-del-btn"
                type="danger"
                size="small"
                :loading="state.deletingId === row.id"
                :disabled="state.deletingId !== null"
                @click="onDelete(row)"
                >删除</el-button
              >
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="ad-pagination">
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
    <AdDialog ref="adDialogRef" @getList="getList" />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'promotionAd' });

import { onBeforeUnmount, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
import { Download, Plus, Search } from '@element-plus/icons-vue';
import AdDialog from '/@/views/system/ad/AdDialog.vue';
import { useAdApi } from '/@/api/useSystemApi/ad';

const adDialogRef = ref();
const state = reactive({
  loading: false,
  exporting: false,
  deletingId: null as number | null,
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    title: '',
    content: '',
    sortOrder: 'desc',
  },
});

const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  fontWeight: '500',
  height: '48px',
  borderColor: '#e8edf3',
};
const cellStyle = { height: '60px', borderColor: '#e8edf3' };

const buildQuery = () => ({
  title: state.listQuery.title.trim() || undefined,
  content: state.listQuery.content.trim() || undefined,
  sort_order: state.listQuery.sortOrder,
});

let listRequestId = 0;
const getList = async () => {
  const requestId = ++listRequestId;
  state.loading = true;
  try {
    const payload = {
      page: state.listQuery.page,
      pageSize: state.listQuery.pageSize,
      ...buildQuery(),
    };
    const res: any = await useAdApi().getList(payload);
    if (requestId !== listRequestId) return;
    state.listData = res.data?.rows || [];
    state.total = res.data?.rowTotal || 0;
    if (!state.listData.length && state.listQuery.page > 1) {
      state.listQuery.page = Math.max(
        1,
        Math.ceil(state.total / state.listQuery.pageSize)
      );
      await getList();
    }
  } catch {
    // 接口错误由全局拦截器提示。
  } finally {
    if (requestId === listRequestId) state.loading = false;
  }
};

const onSearch = () => {
  state.listQuery.page = 1;
  getList();
};
const onSizeChange = () => {
  state.listQuery.page = 1;
  getList();
};
const onSortChange = ({
  prop,
  order,
}: {
  prop: string;
  order: string | null;
}) => {
  if (prop && prop !== 'id') return;
  state.listQuery.sortOrder = order === 'ascending' ? 'asc' : 'desc';
  onSearch();
};
const onAdd = () => adDialogRef.value.openDialog('add');
const onEdit = (row: any) => adDialogRef.value.openDialog('edit', row);

const onDelete = async (row: any) => {
  if (state.deletingId !== null) return;
  try {
    await ElMessageBox.confirm(`确定要删除广告「${row.title}」吗？`, '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消',
    });
  } catch {
    return;
  }
  state.deletingId = row.id;
  try {
    await useAdApi().deleted({ id: row.id });
    ElNotification({
      title: '成功',
      message: '删除成功',
      type: 'success',
      position: 'top-right',
    });
    if (state.listData.length === 1 && state.listQuery.page > 1)
      state.listQuery.page -= 1;
    await getList();
  } catch {
    // 接口错误由全局拦截器提示。
  } finally {
    state.deletingId = null;
  }
};

const onExport = async () => {
  if (state.exporting) return;
  state.exporting = true;
  try {
    const blob: any = await useAdApi().exportExcel(buildQuery());
    if (blob.type?.includes('json')) {
      const result = JSON.parse(await blob.text());
      ElMessage.error(result.msg || '导出失败');
      return;
    }
    const url = window.URL.createObjectURL(
      new Blob([blob], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
    );
    const link = document.createElement('a');
    link.href = url;
    link.download = `广告列表_${Date.now()}.xlsx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    ElMessage.success('导出成功');
  } catch {
    // 接口错误由全局拦截器提示。
  } finally {
    state.exporting = false;
  }
};

onMounted(getList);
onBeforeUnmount(() => {
  listRequestId += 1;
});
</script>

<style scoped lang="scss">
.ad-page {
  padding: 12px;
  min-height: calc(100vh - 100px);
  background: #fff;
  box-sizing: border-box;
  overflow-x: hidden;
  --el-color-primary: #1890ff;
}
.ad-panel {
  background: #fff;
}
.ad-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 2px 18px;
  .ad-input {
    width: 200px;
    :deep(.el-input__wrapper) {
      height: 34px;
      border-radius: 4px;
    }
    :deep(.el-input__inner::placeholder) {
      color: #b9c0cc;
    }
  }
  .ad-btn {
    margin-left: 0;
    height: 34px;
    min-width: 76px;
  }
}
.ad-table {
  width: 100%;
}
.ad-cell-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
  word-break: break-all;
}
.ad-thumb {
  width: 80px;
  height: 40px;
  display: block;
  margin: 0 auto;
}
.ad-image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background: #f7f9fc;
  color: #b9c0cc;
  font-size: 12px;
}
.ad-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  .el-button {
    margin-left: 0;
    padding: 7px 16px;
    border-radius: 3px;
  }
  .ad-edit-btn {
    background: #1890ff;
    border-color: #1890ff;
  }
  .ad-del-btn {
    background: #ff4949;
    border-color: #ff4949;
  }
}
.ad-pagination {
  display: flex;
  justify-content: flex-start;
  padding: 24px 2px 6px;
  overflow-x: auto;
  :deep(.el-pagination) {
    color: #606266;
    font-weight: 400;
  }
}
@media screen and (max-width: 900px) {
  .ad-page {
    padding: 10px;
  }
  .ad-toolbar {
    .ad-input {
      flex: 1 1 calc(50% - 4px);
      width: auto;
      min-width: 0;
    }
    .ad-btn {
      flex: 0 1 auto;
    }
  }
  .ad-pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}
@media screen and (max-width: 560px) {
  .ad-toolbar {
    .ad-input {
      flex: 1 1 100%;
    }
    .ad-btn {
      flex: 1 1 40%;
    }
  }
}
</style>
