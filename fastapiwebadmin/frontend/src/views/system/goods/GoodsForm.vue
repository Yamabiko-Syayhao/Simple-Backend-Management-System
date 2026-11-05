<template>
  <div class="goods-edit" v-loading="loading">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
      <el-card shadow="never"
        ><h2>{{ props.mode === 'edit' ? '商品编辑' : '商品上架' }}</h2>
        <el-form-item v-if="form.id" label="商品ID"
          ><el-input :model-value="form.id" disabled
        /></el-form-item>
        <el-form-item label="商品名称" prop="name"
          ><el-input v-model="form.name" maxlength="128"
        /></el-form-item>
        <el-form-item label="商品编号"
          ><el-input v-model="form.goods_sn" maxlength="64"
        /></el-form-item>
        <el-form-item label="市场售价" prop="market_price"
          ><el-input-number
            v-model="form.market_price"
            :min="0"
            :max="9999999999.99"
            :precision="2"
        /></el-form-item>
        <el-form-item v-if="!form.id" label="当前价格"
          ><el-input-number
            v-model="form.retail_price"
            :min="0"
            :max="9999999999.99"
            :precision="2"
        /></el-form-item>
        <el-form-item v-for="(label, key) in flags" :key="key" :label="label[0]"
          ><el-radio-group
            v-model="form[key]"
            :disabled="props.mode === 'create' && key === 'is_on_sale'"
            ><el-radio :value="true">{{ label[1] }}</el-radio
            ><el-radio :value="false">{{ label[2] }}</el-radio></el-radio-group
          ></el-form-item
        >
        <el-form-item label="商品图片"
          ><GoodsImageUpload v-model="form.image"
        /></el-form-item>
        <el-form-item label="分享图"
          ><GoodsImageUpload v-model="form.share_image"
        /></el-form-item>
        <el-form-item label="宣传画廊"
          ><div class="goods-gallery">
            <div v-for="(url, index) in form.gallery" :key="index">
              <el-image
                :src="url"
                :preview-src-list="form.gallery"
                preview-teleported
              /><el-button
                link
                type="danger"
                @click="form.gallery.splice(index, 1)"
                >移除</el-button
              >
            </div>
            <GoodsImageUpload
              model-value=""
              @update:model-value="(url) => url && form.gallery.push(url)"
            /></div
        ></el-form-item>
        <el-form-item label="商品单位"
          ><el-input v-model="form.unit" maxlength="32"
        /></el-form-item>
        <el-form-item label="关键字"
          ><el-tag
            v-for="(word, index) in form.keywords"
            :key="word"
            closable
            @close="form.keywords.splice(index, 1)"
            >{{ word }}</el-tag
          ><el-input
            v-if="keywordVisible"
            ref="keywordRef"
            v-model="keyword"
            class="goods-keyword"
            @keyup.enter="addKeyword"
            @blur="addKeyword"
          /><el-button v-else type="primary" @click="showKeyword"
            >+ 增加</el-button
          ></el-form-item
        >
        <el-form-item label="所属分类"
          ><el-cascader
            v-model="form.category_id"
            :options="categories"
            :props="{
              value: 'id',
              label: 'name',
              emitPath: false,
              checkStrictly: true,
            }"
            clearable
            filterable
        /></el-form-item>
        <el-form-item label="所属品牌商"
          ><el-select v-model="form.brand_id" clearable filterable
            ><el-option
              v-for="brand in brands"
              :key="brand.id"
              :value="brand.id"
              :label="brand.name" /></el-select
        ></el-form-item>
        <el-form-item label="商品简介"
          ><el-input v-model="form.brief" maxlength="500"
        /></el-form-item>
        <el-form-item label="商品详细介绍"
          ><div class="goods-editor">
            <GoodsRichEditor v-model="form.detail" /></div
        ></el-form-item>
      </el-card>
    </el-form>
    <template v-if="form.id">
      <el-card shadow="never"
        ><h2>商品规格</h2>
        <div class="spec-mode">
          <el-radio-group v-model="specMode">
            <el-radio-button label="default">默认标准规格</el-radio-button>
            <el-radio-button label="multi">多规格支持</el-radio-button>
          </el-radio-group>
          <el-button
            v-if="specMode === 'multi'"
            type="primary"
            plain
            @click="addSpecification"
            >添加</el-button
          >
        </div>
        <el-table
          v-if="specMode === 'default'"
          :data="defaultSpecifications"
          :header-cell-style="headerStyle"
          ><el-table-column prop="name" label="规格名" min-width="140" /><el-table-column
            label="规格值"
            min-width="140"
            ><template #default="{ row }"
              ><el-tag>{{ row.value }}</el-tag></template
            ></el-table-column
          ><el-table-column label="规格图片" min-width="140"
            ><template #default="{ row }"
              ><el-image
                v-if="row.image"
                :src="row.image"
                class="goods-thumb" /></template></el-table-column
        ></el-table>
        <el-table
          v-else
          :data="multiSpecifications"
          :header-cell-style="headerStyle"
          empty-text="暂无数据"
          ><el-table-column prop="name" label="规格名" min-width="140" /><el-table-column
            label="规格值"
            min-width="140"
            ><template #default="{ row }"
              ><el-tag>{{ row.value }}</el-tag></template
            ></el-table-column
          ><el-table-column label="规格图片" min-width="140"
            ><template #default="{ row }"
              ><el-image
                v-if="row.image"
                :src="row.image"
                class="goods-thumb" /></template></el-table-column
          ><el-table-column label="操作" width="140"
            ><template #default="{ row }"
              ><el-button
                type="primary"
                @click="openChild('specification', row)"
                >设置</el-button
              ></template
            ></el-table-column
        ></el-table>
      </el-card>
      <el-card shadow="never"
        ><h2>商品库存</h2>
        <el-table :data="products" :header-cell-style="headerStyle"
          ><el-table-column
            prop="specification"
            label="货品规格"
            min-width="140"
          /><el-table-column
            prop="price"
            label="货品售价"
            min-width="140"
          /><el-table-column
            prop="quantity"
            label="货品数量"
            min-width="140"
          /><el-table-column label="货品图片" min-width="140"
            ><template #default="{ row }"
              ><el-image
                v-if="row.image"
                :src="row.image"
                class="goods-thumb" /></template></el-table-column
          ><el-table-column label="操作" width="140"
            ><template #default="{ row }"
              ><el-button type="primary" @click="openChild('product', row)"
                >设置</el-button
              ></template
            ></el-table-column
          ></el-table
        ></el-card
      >
      <el-card shadow="never"
        ><h2>商品参数</h2>
        <el-button type="primary" @click="openChild('attribute')"
          >添加</el-button
        ><el-table :data="attributes" :header-cell-style="headerStyle"
          ><el-table-column
            prop="name"
            label="商品参数名称"
            min-width="160"
          /><el-table-column
            prop="value"
            label="商品参数值"
            min-width="260"
          /><el-table-column label="操作" width="190"
            ><template #default="{ row }"
              ><el-button type="primary" @click="openChild('attribute', row)"
                >设置</el-button
              ><el-button type="danger" @click="deleteAttribute(row)"
                >删除</el-button
              ></template
            ></el-table-column
          ></el-table
        ></el-card
      >
      <p class="goods-note">
        规格、库存、参数点击确定后立即保存。{{
          props.mode === 'create'
            ? '当前商品为未售，设置完成后点击“商品上架”。'
            : ''
        }}
      </p>
    </template>
    <el-alert
      v-else
      title="先保存商品（未售），再设置规格、库存和参数，最后点击商品上架。"
      type="info"
      :closable="false"
    />
    <div class="goods-actions">
      <el-button @click="router.push('/goods/list')">取消</el-button
      ><el-button
        type="primary"
        :loading="saving"
        :disabled="loading || failed"
        @click="save"
        >{{
          props.mode === 'edit'
            ? '更新商品'
            : savedGoodsId
            ? '商品上架'
            : '保存商品'
        }}</el-button
      >
    </div>
    <el-dialog
      v-model="dialog"
      :title="titles[kind]"
      width="700px"
      class="goods-child-dialog"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="childRef"
        :model="child"
        :rules="childRules"
        label-width="120px"
      >
        <template v-if="kind === 'product'"
          ><el-form-item label="货品规格列"
            ><el-tag>{{ child.specification }}</el-tag></el-form-item
          ><el-form-item label="货品售价" prop="price"
            ><el-input-number
              v-model="child.price"
              :min="0"
              :max="9999999999.99"
              :precision="2" /></el-form-item
          ><el-form-item label="货品数量" prop="quantity"
            ><el-input-number
              v-model="child.quantity"
              :min="0"
              :max="2147483647"
              :precision="0" /></el-form-item
        ></template>
        <template v-else
          ><el-form-item
            :label="kind === 'attribute' ? '商品参数名称' : '规格名'"
            prop="name"
            ><el-input
              v-model="child.name"
              :maxlength="kind === 'attribute' ? 128 : 64" /></el-form-item
          ><el-form-item
            :label="kind === 'attribute' ? '商品参数值' : '规格值'"
            prop="value"
            ><el-input
              v-model="child.value"
              :maxlength="kind === 'attribute' ? 1000 : 128" /></el-form-item
        ></template>
        <el-form-item
          v-if="kind !== 'attribute'"
          :label="kind === 'product' ? '货品图片' : '规格图片'"
          ><GoodsImageUpload v-model="child.image"
        /></el-form-item> </el-form
      ><template #footer
        ><el-button @click="dialog = false">取消</el-button
        ><el-button type="primary" :loading="childSaving" @click="saveChild"
          >确定</el-button
        ></template
      >
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus';
import { useGoodsApi } from '/@/api/useSystemApi/goods';
import { useBrandApi } from '/@/api/useSystemApi/brand';
import { useCategoryApi } from '/@/api/useSystemApi/category';
import GoodsImageUpload from './GoodsImageUpload.vue';
import GoodsRichEditor from './GoodsRichEditor.vue';
defineOptions({ name: 'GoodsForm' });
const props = defineProps<{ mode: 'create' | 'edit'; goodsId?: number }>();
const api = useGoodsApi(),
  router = useRouter();
const blank = () => ({
  id: undefined,
  name: '',
  goods_sn: '',
  market_price: 0,
  retail_price: 0,
  is_new: false,
  is_hot: false,
  is_on_sale: false,
  image: '',
  share_image: '',
  gallery: [],
  unit: '件',
  keywords: [],
  category_id: undefined,
  brand_id: undefined,
  brief: '',
  detail: '',
});
const savedGoodsId = ref<number>();
const form = ref<any>(blank()),
  formRef = ref(),
  loading = ref(false),
  failed = ref(false),
  saving = ref(false);
const specifications = ref<any[]>([]),
  products = ref<any[]>([]),
  attributes = ref<any[]>([]),
  categories = ref<any[]>([]),
  brands = ref<any[]>([]);
// 商品规格：默认标准规格 / 多规格支持
// 新建商品时后端会自动写入一条「规格 / 标准」，视为默认规格；
// 默认模式下只读展示，多规格模式下列出除此之外的规格并允许添加。
const DEFAULT_SPEC = { name: '规格', value: '标准' };
const isDefaultSpec = (row: any) =>
  row?.name === DEFAULT_SPEC.name && row?.value === DEFAULT_SPEC.value;
const specMode = ref<'default' | 'multi'>('default');
const defaultSpecifications = computed(() =>
  specifications.value.filter(isDefaultSpec)
);
const multiSpecifications = computed(() =>
  specifications.value.filter((row) => !isDefaultSpec(row))
);
let specModeInited = false;
function syncSpecMode() {
  // 只在首次加载时推断模式，避免用户手动切换后又被刷新重置
  if (specModeInited) return;
  specModeInited = true;
  specMode.value = multiSpecifications.value.length ? 'multi' : 'default';
}
function addSpecification() {
  // 不传 row → 弹窗提交时不带 id，后端按新增处理
  openChild('specification');
}
const rules = {
  name: [
    {
      required: true,
      whitespace: true,
      message: '请输入商品名称',
      trigger: 'blur',
    },
  ],
};
const headerStyle = { background: '#f7f9fc', color: '#909399' };
const flags = {
  is_new: ['是否新品', '新品', '非新品'],
  is_hot: ['是否热卖', '热卖', '普通'],
  is_on_sale: ['是否在售', '在售', '未售'],
};
const keyword = ref(''),
  keywordVisible = ref(false),
  keywordRef = ref();
async function showKeyword() {
  keywordVisible.value = true;
  await nextTick();
  keywordRef.value?.focus();
}
function addKeyword() {
  const word = keyword.value.trim();
  if (word && !form.value.keywords.includes(word))
    form.value.keywords.push(word);
  keyword.value = '';
  keywordVisible.value = false;
}
function children(data: any, infer = true) {
  specifications.value = data.specifications || [];
  products.value = data.products || [];
  attributes.value = data.attributes || [];
  if (infer) syncSpecMode();
}
let generation = 0;
async function load() {
  const current = ++generation;
  loading.value = true;
  failed.value = false;
  form.value = blank();
  savedGoodsId.value = undefined;
  specModeInited = false;
  specMode.value = 'default';
  // 清空时不要参与模式推断，等真实数据回来再判断
  children({}, false);
  keyword.value = '';
  keywordVisible.value = false;
  dialog.value = false;
  // 编辑页必须带有效 ID，不能退化为新增模式。
  if (
    props.mode === 'edit' &&
    (!Number.isSafeInteger(props.goodsId) || props.goodsId! <= 0)
  ) {
    failed.value = true;
    loading.value = false;
    ElMessage.error('缺少有效商品ID，请从商品列表进入编辑');
    return;
  }
  const goodsId = props.goodsId;
  try {
    const [categoryRes, brandRows] = await Promise.all([
      useCategoryApi().getList(),
      loadBrands(),
    ]);
    if (current !== generation) return;
    const all = (categoryRes as any).data?.rows || [];
    categories.value = all
      .filter((x: any) => !x.parent_id)
      .map((x: any) => ({
        ...x,
        children: all.filter((c: any) => c.parent_id === x.id),
      }));
    categories.value.forEach((x) => {
      if (!x.children.length) delete x.children;
    });
    brands.value = brandRows;
    if (props.mode === 'edit') {
      const res: any = await api.getDetail({ id: goodsId });
      if (current !== generation) return;
      form.value = {
        ...blank(),
        ...res.data,
        category_id: res.data.category_id || undefined,
        brand_id: res.data.brand_id || undefined,
        goods_sn: res.data.goods_sn || '',
      };
      children(res.data);
    }
  } catch {
    if (current === generation) failed.value = true;
  } finally {
    if (current === generation) loading.value = false;
  }
}
async function loadBrands() {
  const result: any[] = [];
  for (let page = 1; ; page++) {
    const res: any = await useBrandApi().getList({ page, pageSize: 1000 });
    const rows = res.data?.rows || [];
    result.push(...rows);
    if (!rows.length || result.length >= res.data.rowTotal) break;
  }
  return result;
}
function notify(message: string) {
  ElNotification({
    title: '成功',
    message,
    type: 'success',
    position: 'top-right',
  });
}
async function save() {
  if (loading.value || failed.value || saving.value) return;
  if (
    props.mode === 'edit' &&
    (!form.value.id || form.value.id !== props.goodsId)
  )
    return;
  if (!(await formRef.value.validate().catch(() => false))) return;
  addKeyword();
  saving.value = true;
  try {
    const isFirstSave = props.mode === 'create' && !savedGoodsId.value;
    const res: any = await api.saveOrUpdate({
      ...form.value,
      // 新增阶段只接受本页首次保存后由服务端返回的 ID。
      id: props.mode === 'create' ? savedGoodsId.value : props.goodsId,
      is_on_sale:
        props.mode === 'create' ? !isFirstSave : form.value.is_on_sale,
      category_id: form.value.category_id || 0,
      brand_id: form.value.brand_id || 0,
    });
    if (isFirstSave) {
      savedGoodsId.value = res.data.id;
      form.value.id = res.data.id;
      form.value.is_on_sale = false;
      await refreshChildren();
      notify('商品已保存为未售，请设置规格、库存和参数后再上架');
    } else if (props.mode === 'create') {
      notify('商品上架成功');
      await router.push('/goods/list');
    } else {
      notify('商品保存成功');
    }
  } finally {
    saving.value = false;
  }
}
const dialog = ref(false),
  kind = ref('attribute'),
  child = ref<any>({}),
  childRef = ref(),
  childSaving = ref(false);
const titles: Record<string, string> = {
  specification: '设置规格',
  product: '编辑货品',
  attribute: '编辑商品参数',
};
const childRules = {
  name: [
    {
      required: true,
      whitespace: true,
      message: '请输入名称',
      trigger: 'blur',
    },
  ],
  value: [
    { required: true, whitespace: true, message: '请输入值', trigger: 'blur' },
  ],
  price: [{ required: true, message: '请输入售价' }],
  quantity: [{ required: true, message: '请输入库存数量' }],
};
function openChild(type: string, row?: any) {
  kind.value = type;
  child.value = {
    name: '',
    value: '',
    image: '',
    price: 0,
    quantity: 0,
    ...row,
    goods_id: form.value.id,
  };
  dialog.value = true;
}
async function refreshChildren() {
  const res: any = await api.getDetail({ id: form.value.id });
  children(res.data);
  form.value.retail_price = res.data.retail_price;
}
async function saveChild() {
  if (!(await childRef.value.validate().catch(() => false))) return;
  childSaving.value = true;
  try {
    await api.saveChild(kind.value, child.value);
    notify('保存成功');
    dialog.value = false;
    await refreshChildren();
  } finally {
    childSaving.value = false;
  }
}
async function deleteAttribute(row: any) {
  try {
    await ElMessageBox.confirm('确定删除该商品参数？', '提示', {
      type: 'warning',
    });
  } catch {
    return;
  }
  await api.deleteAttribute({ id: row.id, goods_id: form.value.id });
  notify('删除成功');
  await refreshChildren();
}
watch(() => [props.mode, props.goodsId], load, { immediate: true });
onBeforeUnmount(() => {
  generation++;
});
</script>
<style scoped lang="scss">
.goods-edit {
  padding: 20px;
  overflow-x: hidden;
  --el-color-primary: #1890ff;
  .el-card {
    margin-bottom: 12px;
    border-color: #e8edf3;
  }
  h2 {
    font-size: 20px;
    margin: 10px 0 24px;
  }
  .spec-mode {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }
  .el-tag {
    margin-right: 8px;
  }
  .el-select,
  .el-cascader {
    width: 260px;
    max-width: 100%;
  }
}
.goods-editor {
  width: 100%;
  min-width: 0;
}
.goods-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  > div {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .el-image {
    width: 120px;
    height: 120px;
    border: 1px solid #e8edf3;
  }
}
.goods-keyword {
  width: 130px;
}
.goods-thumb {
  width: 50px;
  height: 50px;
}
.goods-actions {
  text-align: center;
  padding: 16px;
}
.goods-note {
  color: #909399;
  font-size: 12px;
}
@media (max-width: 900px) {
  .goods-edit {
    padding: 12px;
    :deep(.el-form-item__label) {
      width: 100px !important;
    }
    :deep(.el-form-item__content) {
      margin-left: 0 !important;
    }
  }
}
@media (max-width: 560px) {
  .goods-edit {
    padding: 6px;
    :deep(.el-card__body) {
      padding: 12px;
    }
    :deep(.el-form-item) {
      display: block;
    }
    :deep(.el-form-item__label) {
      justify-content: flex-start;
    }
  }
  .goods-actions .el-button {
    width: 40%;
  }
}
</style>
<style>
.goods-child-dialog {
  max-width: 92vw;
}
@media (max-width: 560px) {
  .goods-child-dialog .el-form-item__label {
    width: 90px !important;
  }
  .goods-child-dialog .el-form-item__content {
    margin-left: 0 !important;
  }
}
</style>
