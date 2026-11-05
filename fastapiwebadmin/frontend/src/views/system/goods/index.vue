<template>
  <div class="goods-page">
    <div class="goods-panel">
      <div class="goods-toolbar">
        <el-input
          v-model="query.goods_id"
          placeholder="请输入商品ID"
          clearable
          @keyup.enter="search"
        />
        <el-input
          v-model="query.goods_sn"
          placeholder="请输入商品编号"
          clearable
          @keyup.enter="search"
        />
        <el-input
          v-model="query.name"
          placeholder="请输入商品名称"
          clearable
          @keyup.enter="search"
        />
        <el-button type="primary" @click="search">查找</el-button
        ><el-button type="primary" @click="createGoods">添加</el-button>
        <el-button type="primary" @click="exportExcel">导出</el-button>
        <el-button
          type="danger"
          :disabled="!selected.length || deleting"
          :loading="deleting"
          @click="remove(selected)"
          >批量删除</el-button
        >
      </div>
      <el-table
        v-loading="loading"
        :data="rows"
        border
        row-key="id"
        :header-cell-style="headerCellStyle"
        :cell-style="cellStyle"
        :default-sort="{ prop: 'id', order: 'descending' }"
        @selection-change="selected = $event.map((r: any) => r.id)"
        @sort-change="sort"
      >
        <el-table-column type="expand" width="48"
          ><template #default="{ row }">
            <el-descriptions
              class="goods-expand"
              :column="1"
              label-width="100px"
            >
              <el-descriptions-item label="商品编号">{{
                row.goods_sn
              }}</el-descriptions-item>
              <el-descriptions-item label="宣传画廊"
                ><el-image
                  v-for="url in row.gallery"
                  :key="url"
                  :src="url"
                  :preview-src-list="row.gallery"
                  preview-teleported
                  class="goods-thumb"
              /></el-descriptions-item>
              <el-descriptions-item
                v-for="(label, key) in expanded"
                :key="key"
                :label="label"
                >{{
                  key === 'keywords'
                    ? (row.keywords || []).join('，')
                    : row[key]
                }}</el-descriptions-item
              >
            </el-descriptions>
          </template></el-table-column
        >
        <el-table-column type="selection" width="48" />
        <el-table-column
          prop="id"
          label="商品ID"
          width="110"
          sortable="custom"
        />
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column
          v-for="(label, key) in { image: '图片', share_image: '分享图' }"
          :key="key"
          :label="label"
          width="96"
          ><template #default="{ row }"
            ><el-image
              v-if="row[key]"
              :src="row[key]"
              :preview-src-list="[row[key]]"
              preview-teleported
              class="goods-thumb"
            /><span v-else>—</span></template
          ></el-table-column
        >
        <el-table-column label="详情" width="96"
          ><template #default="{ row }"
            ><el-button type="primary" @click="preview(row.id)"
              >查看</el-button
            ></template
          ></el-table-column
        >
        <el-table-column
          prop="market_price"
          label="市场售价"
          width="100"
        /><el-table-column prop="retail_price" label="当前价格" width="100" />
        <el-table-column
          v-for="(label, key) in {
            is_new: '是否新品',
            is_hot: '是否热品',
            is_on_sale: '是否在售',
          }"
          :key="key"
          :label="label"
          width="100"
          ><template #default="{ row }"
            ><el-tag :type="row[key] ? 'success' : 'primary'">{{
              row[key + '_text']
            }}</el-tag></template
          ></el-table-column
        >
        <el-table-column label="操作" min-width="180"
          ><template #default="{ row }"
            ><el-button type="primary" @click="edit(row.id)">编辑</el-button
            ><el-button
              type="danger"
              :disabled="deleting"
              @click="remove([row.id])"
              >删除</el-button
            ></template
          ></el-table-column
        >
      </el-table>
      <div class="goods-pagination">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[10, 20, 30, 40, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="getList"
          @size-change="search"
        />
      </div>
      <el-dialog
        v-model="visible"
        title="商品详细介绍"
        width="850px"
        class="goods-preview"
        :close-on-click-modal="false"
        destroy-on-close
        ><div class="goods-detail" v-html="html"
      /></el-dialog>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, reactive, onMounted, onActivated } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
import DOMPurify from 'dompurify';
import { useGoodsApi } from '/@/api/useSystemApi/goods';
defineOptions({ name: 'goodsList' });
const api = useGoodsApi(),
  router = useRouter();
const query = reactive({
  goods_id: '',
  goods_sn: '',
  name: '',
  page: 1,
  pageSize: 20,
  sort_order: 'desc',
});
const rows = ref<any[]>([]),
  selected = ref<number[]>([]),
  total = ref(0),
  loading = ref(false),
  deleting = ref(false),
  visible = ref(false),
  html = ref('');
const expanded = {
  brief: '商品介绍',
  unit: '商品单位',
  keywords: '关键字',
  category_id: '类目ID',
  brand_id: '品牌商ID',
};
const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  textAlign: 'center',
};
const cellStyle = { textAlign: 'center' };
function payload() {
  return {
    ...query,
    goods_id: query.goods_id ? Number(query.goods_id) : undefined,
  };
}
let sequence = 0;
async function getList() {
  const current = ++sequence;
  loading.value = true;
  try {
    const res: any = await api.getList(payload());
    if (current !== sequence) return;
    rows.value = res.data?.rows || [];
    total.value = res.data?.rowTotal || 0;
    selected.value = [];
    if (!rows.value.length && query.page > 1) {
      query.page--;
      await getList();
    }
  } finally {
    if (current === sequence) loading.value = false;
  }
}
function search() {
  if (query.goods_id && !/^\d+$/.test(query.goods_id)) {
    ElMessage.error('商品ID必须为数字');
    return;
  }
  query.page = 1;
  getList();
}
function sort({ order }: any) {
  query.sort_order = order === 'ascending' ? 'asc' : 'desc';
  search();
}
function createGoods() {
  router.push('/goods/create');
}
function edit(id: number) {
  router.push({ path: '/goods/edit', query: { id } });
}
async function preview(id: number) {
  const res: any = await api.getDetail({ id });
  html.value = DOMPurify.sanitize(res.data.detail || '<p>暂无详细介绍</p>');
  visible.value = true;
}
async function remove(ids: number[]) {
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${ids.length} 个商品及其规格、库存、参数？`,
      '提示',
      { type: 'warning' }
    );
  } catch {
    return;
  }
  deleting.value = true;
  try {
    if (ids.length === 1) await api.deleted({ id: ids[0] });
    else await api.batchDeleted({ ids });
    ElNotification({
      title: '成功',
      message: '删除成功',
      type: 'success',
      position: 'top-right',
    });
    await getList();
  } finally {
    deleting.value = false;
  }
}
async function exportExcel() {
  const blob: any = await api.exportExcel(payload());
  if (blob.type.includes('json')) {
    ElMessage.error(JSON.parse(await blob.text()).msg || '导出失败');
    return;
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '商品列表.xlsx';
  a.click();
  URL.revokeObjectURL(url);
}
onMounted(getList);
onActivated(getList);
</script>
<style scoped lang="scss">
.goods-page {
  padding: 20px;
  overflow-x: hidden;
  --el-color-primary: #1890ff;
}
.goods-panel {
  padding: 20px;
  background: white;
  border: 1px solid #e8edf3;
  border-radius: 4px;
}
.goods-toolbar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  .el-input {
    width: 160px;
  }
  .el-button {
    margin-left: 0;
  }
}
.goods-thumb {
  width: 40px;
  height: 40px;
  margin: 4px;
}
.goods-expand {
  padding: 16px 50px;
}
.goods-pagination {
  margin-top: 20px;
  overflow-x: auto;
}
.goods-detail {
  overflow-wrap: anywhere;
  :deep(img) {
    max-width: 100%;
  }
  :deep(table) {
    max-width: 100%;
  }
}
@media (max-width: 900px) {
  .goods-toolbar .el-input {
    flex: 1 1 calc(50% - 4px);
  }
  .goods-pagination :deep(.el-pagination) {
    flex-wrap: wrap;
    row-gap: 8px;
  }
}
@media (max-width: 560px) {
  .goods-page,
  .goods-panel {
    padding: 10px;
  }
  .goods-toolbar .el-input {
    flex: 1 1 100%;
  }
  .goods-toolbar .el-button {
    flex: 1 1 40%;
  }
}
</style>
<style>
.goods-preview {
  max-width: 92vw;
}
</style>
