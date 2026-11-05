<template>
  <el-dialog
    v-model="state.visible"
    title="添加商品"
    width="800px"
    class="topic-goods-dialog"
    :close-on-click-modal="false"
    destroy-on-close
    @close="closeDialog"
  >
    <div class="topic-goods-toolbar">
      <el-input
        v-model="state.query.goods_sn"
        placeholder="请输入商品编号"
        clearable
        @keyup.enter="onSearch"
      />
      <el-input
        v-model="state.query.name"
        placeholder="请输入商品名称"
        clearable
        @keyup.enter="onSearch"
      />
      <el-button type="primary" :icon="Search" @click="onSearch"
        >查找</el-button
      >
    </div>
    <el-table
      ref="tableRef"
      v-loading="state.loading"
      :data="state.rows"
      row-key="id"
      border
      :header-cell-style="headerCellStyle"
      empty-text="暂无数据"
      @selection-change="onSelectionChange"
    >
      <el-table-column
        type="selection"
        width="48"
        reserve-selection
        align="center"
      />
      <el-table-column
        prop="id"
        label="商品ID"
        min-width="120"
        align="center"
      />
      <el-table-column label="图片" min-width="110" align="center"
        ><template #default="{ row }"
          ><el-image
            v-if="row.image"
            :src="row.image"
            :preview-src-list="[row.image]"
            preview-teleported
            fit="contain"
            class="topic-goods-thumb"
          /><span v-else>—</span></template
        ></el-table-column
      >
      <el-table-column
        prop="name"
        label="商品名称"
        min-width="230"
        align="center"
      />
    </el-table>
    <div class="topic-goods-pagination">
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
    <template #footer
      ><div class="topic-goods-footer">
        <span>已选择 {{ state.selectedRows.length }} 件商品</span
        ><el-button @click="state.visible = false">取消</el-button
        ><el-button type="primary" :disabled="state.loading" @click="onConfirm"
          >确定</el-button
        >
      </div></template
    >
  </el-dialog>
</template>
<script setup lang="ts">
defineOptions({ name: 'TopicGoodsDialog' });
import { nextTick, onBeforeUnmount, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { Search } from '@element-plus/icons-vue';
import { useGoodsApi } from '/@/api/useSystemApi/goods';
const emit = defineEmits(['confirm']);
const tableRef = ref();
const state = reactive({
  visible: false,
  loading: false,
  rows: [] as any[],
  total: 0,
  selectedRows: [] as any[],
  query: { goods_sn: '', name: '', page: 1, pageSize: 10 },
});
const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  height: '40px',
  borderColor: '#e8edf3',
};
let requestSequence = 0;
const getList = async () => {
  if (!state.visible) return;
  const requestId = ++requestSequence;
  state.loading = true;
  try {
    const res: any = await useGoodsApi().getList({
      goods_sn: state.query.goods_sn.trim() || undefined,
      name: state.query.name.trim() || undefined,
      page: state.query.page,
      pageSize: state.query.pageSize,
      sort_order: 'desc',
    });
    if (requestId !== requestSequence || !state.visible) return;
    state.rows = res.data?.rows || [];
    state.total = res.data?.rowTotal || 0;
    if (!state.rows.length && state.query.page > 1) {
      state.query.page = Math.max(
        1,
        Math.ceil(state.total / state.query.pageSize)
      );
      await getList();
    }
  } catch {
    // 统一拦截器提示接口错误。
  } finally {
    if (requestId === requestSequence) state.loading = false;
  }
};
const openDialog = async () => {
  const requestId = ++requestSequence;
  state.query = { goods_sn: '', name: '', page: 1, pageSize: 10 };
  state.rows = [];
  state.total = 0;
  state.selectedRows = [];
  state.loading = false;
  state.visible = true;
  await nextTick();
  if (requestId !== requestSequence || !state.visible) return;
  tableRef.value?.clearSelection();
  await getList();
};
const closeDialog = () => {
  state.visible = false;
  requestSequence++;
  state.loading = false;
};
const onSelectionChange = (rows: any[]) => {
  state.selectedRows = rows;
};
const onSearch = () => {
  state.query.page = 1;
  getList();
};
const onSizeChange = () => {
  state.query.page = 1;
  getList();
};
const onConfirm = () => {
  if (state.loading) return;
  if (!state.selectedRows.length) {
    ElMessage.warning('请选择至少一件商品');
    return;
  }
  emit(
    'confirm',
    state.selectedRows.map((row) => ({
      id: row.id,
      name: row.name,
      image: row.image || '',
      brief: row.brief || '',
      goods_sn: row.goods_sn || '',
    }))
  );
  state.visible = false;
};
onBeforeUnmount(closeDialog);
defineExpose({ openDialog, closeDialog });
</script>
<style scoped lang="scss">
.topic-goods-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  .el-input {
    width: 200px;
  }
  .el-button {
    margin-left: 0;
  }
}
.topic-goods-thumb {
  width: 40px;
  height: 40px;
  vertical-align: middle;
}
.topic-goods-pagination {
  padding-top: 24px;
  overflow-x: auto;
}
.topic-goods-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 10px;
  > span {
    margin-right: auto;
    color: #909399;
    font-size: 13px;
  }
  .el-button {
    margin-left: 0;
  }
}
@media (max-width: 900px) {
  .topic-goods-toolbar .el-input {
    flex: 1 1 calc(50% - 4px);
    width: auto;
    min-width: 0;
  }
  .topic-goods-pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}
@media (max-width: 560px) {
  .topic-goods-toolbar {
    .el-input {
      flex: 1 1 100%;
    }
    .el-button {
      flex: 1 1 40%;
    }
  }
}
</style>
<style lang="scss">
.topic-goods-dialog {
  max-width: 92vw;
  --el-color-primary: #1890ff;
}
@media (max-width: 560px) {
  .topic-goods-dialog .el-dialog__body {
    padding: 12px 8px;
  }
}
</style>
