<template>
  <div class="topic-form-page" v-loading="state.loading">
    <el-alert
      v-if="state.errorMessage"
      :title="state.errorMessage"
      type="warning"
      :closable="false"
      show-icon
      class="topic-form-error"
    />
    <el-form
      ref="formRef"
      :model="state.form"
      :rules="rules"
      :disabled="state.loading || state.saving || state.failed"
      label-width="125px"
      class="topic-form"
    >
      <el-form-item label="专题标题" prop="title"
        ><el-input v-model="state.form.title" maxlength="128"
      /></el-form-item>
      <el-form-item label="专题子标题" prop="subtitle"
        ><el-input v-model="state.form.subtitle" maxlength="500"
      /></el-form-item>
      <el-form-item label="专题图片"
        ><TopicImageUpload
          :key="state.formVersion"
          v-model="state.form.image"
          :disabled="state.loading || state.saving || state.failed"
          @busy="state.coverUploading = $event"
      /></el-form-item>
      <el-form-item label="专题内容" prop="content"
        ><div class="topic-form-editor">
          <GoodsRichEditor
            :key="state.formVersion"
            v-model="state.form.content"
          /></div
      ></el-form-item>
      <el-form-item label="商品低价" prop="price"
        ><el-input v-model="state.form.price"
      /></el-form-item>
      <el-form-item label="阅读量" prop="read_count"
        ><el-input v-model="state.form.read_count"
      /></el-form-item>
      <el-form-item label="专题商品"
        ><div class="topic-form-goods">
          <div class="topic-form-goods-toolbar">
            <el-button type="primary" @click="goodsDialogRef?.openDialog()"
              >创建商品</el-button
            >
          </div>
          <el-table
            :data="state.goods"
            border
            :header-cell-style="headerCellStyle"
            empty-text="暂无数据"
          >
            <el-table-column
              prop="id"
              label="商品ID"
              min-width="110"
              align="center"
            />
            <el-table-column label="图片" min-width="100" align="center"
              ><template #default="{ row }"
                ><el-image
                  v-if="row.image"
                  :src="row.image"
                  :preview-src-list="[row.image]"
                  preview-teleported
                  fit="contain"
                  class="topic-form-goods-image"
                /><span v-else>—</span></template
              ></el-table-column
            >
            <el-table-column
              prop="name"
              label="商品名称"
              min-width="150"
              align="center"
            />
            <el-table-column
              prop="brief"
              label="商品介绍"
              min-width="190"
              align="center"
              show-overflow-tooltip
            />
            <el-table-column label="操作" width="90" align="center"
              ><template #default="{ $index }"
                ><el-button
                  type="danger"
                  link
                  @click="state.goods.splice($index, 1)"
                  >删除</el-button
                ></template
              ></el-table-column
            >
          </el-table>
        </div></el-form-item
      >
    </el-form>
    <div class="topic-form-actions">
      <el-button
        :disabled="state.saving"
        @click="router.push('/promotion/topic')"
        >取消</el-button
      ><el-button
        type="primary"
        :loading="state.saving"
        :disabled="state.loading || state.failed || state.coverUploading"
        @click="onSubmit"
        >确定</el-button
      >
    </div>
    <TopicGoodsDialog ref="goodsDialogRef" @confirm="addGoods" />
  </div>
</template>
<script setup lang="ts">
defineOptions({ name: 'TopicForm' });
import { onBeforeUnmount, reactive, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElNotification } from 'element-plus';
import type { FormInstance, FormRules } from 'element-plus';
import GoodsRichEditor from '/@/views/system/goods/GoodsRichEditor.vue';
import TopicImageUpload from './TopicImageUpload.vue';
import TopicGoodsDialog from './TopicGoodsDialog.vue';
import { useTopicApi } from '/@/api/useSystemApi/topic';

const props = defineProps<{ mode: 'create' | 'edit'; topicId?: number }>();
const router = useRouter();
const formRef = ref<FormInstance>();
const goodsDialogRef = ref<InstanceType<typeof TopicGoodsDialog>>();
const blankForm = () => ({
  id: undefined as number | undefined,
  title: '',
  subtitle: '',
  image: '',
  content: '',
  price: 0 as string | number,
  read_count: 0 as string | number,
});
const state = reactive({
  loading: false,
  saving: false,
  failed: false,
  errorMessage: '',
  coverUploading: false,
  formVersion: 0,
  form: blankForm(),
  goods: [] as any[],
});
const headerCellStyle = {
  background: '#f7f9fc',
  color: '#909399',
  height: '40px',
  borderColor: '#e8edf3',
};
const contentDocument = (value: string) =>
  new DOMParser().parseFromString(value || '', 'text/html');
const hasPendingImages = (value: string) => {
  const document = contentDocument(value);
  return [...document.querySelectorAll('img[src]')].some((image) =>
    /^blob:/i.test(image.getAttribute('src') || '')
  );
};
const hasContent = (value: string) => {
  const document = contentDocument(value);
  document
    .querySelectorAll('script,style,noscript')
    .forEach((node) => node.remove());
  const text = (document.body.textContent || '').replace(
    /[\s\u00a0\u200b]/g,
    ''
  );
  return (
    !!text ||
    !!document.querySelector(
      'img[src],video[src],audio[src],source[src],iframe[src],object[data],embed[src]'
    )
  );
};
const parseReadCount = (value: string | number) => {
  const text = String(value).trim();
  const match = text.match(/^(\d+)(?:\.(\d+))?(k)?$/i);
  if (!match) return Number.NaN;
  const fraction = match[2] || '';
  let count = BigInt(match[1]);
  if (match[3]) {
    if (/[1-9]/.test(fraction.slice(3))) return Number.NaN;
    count = count * BigInt(1000) + BigInt((fraction + '000').slice(0, 3));
  } else if (/[1-9]/.test(fraction)) return Number.NaN;
  return count <= BigInt(Number.MAX_SAFE_INTEGER) ? Number(count) : Number.NaN;
};
const rules: FormRules = {
  title: [
    {
      required: true,
      whitespace: true,
      message: '请输入专题标题',
      trigger: 'blur',
    },
  ],
  subtitle: [
    {
      required: true,
      whitespace: true,
      message: '请输入专题子标题',
      trigger: 'blur',
    },
  ],
  content: [
    {
      required: true,
      validator: (
        _rule: any,
        value: string,
        callback: (error?: Error) => void
      ) => {
        if (!hasContent(value)) callback(new Error('请输入专题内容'));
        else if (hasPendingImages(value))
          callback(new Error('专题图片正在上传，请上传完成后再保存'));
        else callback();
      },
      trigger: 'change',
    },
  ],
  price: [
    {
      required: true,
      validator: (
        _rule: any,
        value: any,
        callback: (error?: Error) => void
      ) => {
        if (
          !/^\d+(\.\d{1,2})?$/.test(String(value)) ||
          !Number.isFinite(Number(value)) ||
          Number(value) > 9999999999.99
        )
          callback(new Error('请输入非负金额，最多两位小数'));
        else callback();
      },
      trigger: 'blur',
    },
  ],
  read_count: [
    {
      validator: (_rule: any, value: any, callback: (error?: Error) => void) =>
        Number.isNaN(parseReadCount(value))
          ? callback(new Error('请输入非负整数阅读量，可使用 76.5k 格式'))
          : callback(),
      trigger: 'blur',
    },
  ],
};

let loadSequence = 0;
const load = async () => {
  const requestId = ++loadSequence;
  state.formVersion++;
  state.loading = false;
  state.saving = false;
  state.failed = false;
  state.errorMessage = '';
  state.coverUploading = false;
  state.form = blankForm();
  state.goods = [];
  goodsDialogRef.value?.closeDialog();
  formRef.value?.clearValidate();
  if (props.mode === 'create') return;
  const id = props.topicId;
  if (!id || !Number.isSafeInteger(id) || id <= 0) {
    state.failed = true;
    state.errorMessage = '缺少有效专题ID，请从专题管理进入编辑。';
    return;
  }
  state.loading = true;
  try {
    const res: any = await useTopicApi().getDetail({ id });
    if (
      requestId !== loadSequence ||
      props.topicId !== id ||
      props.mode !== 'edit'
    )
      return;
    const data = res.data;
    if (!data?.id || Number(data.id) !== id) {
      state.failed = true;
      state.errorMessage = '专题不存在，请返回列表重试。';
      return;
    }
    state.form = {
      id: data.id,
      title: data.title || '',
      subtitle: data.subtitle || '',
      image: data.image || '',
      content: data.content || '',
      price: data.price ?? 0,
      read_count: data.read_count ?? 0,
    };
    state.goods = data.goods || [];
  } catch {
    if (requestId === loadSequence) {
      state.failed = true;
      state.errorMessage = '专题加载失败，请返回列表重试。';
    }
  } finally {
    if (requestId === loadSequence) state.loading = false;
  }
};
const addGoods = (rows: any[]) => {
  if (state.saving || state.loading || state.failed) return;
  const ids = new Set(state.goods.map((row) => row.id));
  rows.forEach((row) => {
    if (!ids.has(row.id)) {
      state.goods.push({ ...row });
      ids.add(row.id);
    }
  });
};
const onSubmit = async () => {
  if (state.loading || state.saving || state.failed) return;
  if (state.coverUploading) {
    ElMessage.warning('封面图片正在上传，请稍候');
    return;
  }
  if (
    props.mode === 'edit' &&
    (!props.topicId || state.form.id !== props.topicId)
  )
    return;
  if (hasPendingImages(state.form.content)) {
    ElMessage.warning('专题图片正在上传，请上传完成后再保存');
    return;
  }
  const requestId = loadSequence;
  state.saving = true;
  try {
    if (!(await formRef.value?.validate().catch(() => false))) return;
    if (requestId !== loadSequence) return;
    await useTopicApi().saveOrUpdate({
      id: props.mode === 'edit' ? props.topicId : undefined,
      title: state.form.title.trim(),
      subtitle: state.form.subtitle.trim(),
      image: state.form.image,
      content: state.form.content,
      price: Number(state.form.price),
      read_count: parseReadCount(state.form.read_count),
      goods_ids: [...new Set(state.goods.map((row) => row.id))],
    });
    if (requestId !== loadSequence) return;
    ElNotification({
      title: '成功',
      message: props.mode === 'create' ? '创建成功' : '修改成功',
      type: 'success',
      position: 'top-right',
    });
    await router.push('/promotion/topic');
  } catch {
    // 统一拦截器负责接口错误提示。
  } finally {
    if (requestId === loadSequence) state.saving = false;
  }
};
watch(() => [props.mode, props.topicId], load, { immediate: true });
onBeforeUnmount(() => {
  loadSequence++;
});
</script>
<style scoped lang="scss">
.topic-form-page {
  padding: 20px;
  min-height: calc(100vh - 100px);
  box-sizing: border-box;
  overflow-x: hidden;
  background: #fff;
  --el-color-primary: #1890ff;
}
.topic-form-error {
  max-width: 840px;
  margin-bottom: 20px;
}
.topic-form {
  width: 840px;
  max-width: 100%;
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }
  :deep(.el-form-item__label) {
    color: #606266;
    font-weight: 600;
    padding-right: 20px;
  }
  :deep(.el-form-item__content) {
    min-width: 0;
  }
  :deep(.el-input__wrapper) {
    min-height: 32px;
    border-radius: 4px;
  }
}
.topic-form-editor {
  width: 100%;
  min-width: 0;
}
.topic-form-goods {
  width: 100%;
  min-width: 0;
}
.topic-form-goods-toolbar {
  display: flex;
  justify-content: flex-end;
  padding-bottom: 8px;
}
.topic-form-goods-image {
  width: 40px;
  height: 40px;
  vertical-align: middle;
}
.topic-form-actions {
  display: flex;
  gap: 10px;
  padding-top: 6px;
  .el-button {
    margin-left: 0;
  }
}
@media (max-width: 900px) {
  .topic-form-page {
    padding: 14px;
  }
  .topic-form :deep(.el-form-item__label) {
    width: 110px !important;
    padding-right: 12px;
  }
}
@media (max-width: 560px) {
  .topic-form-page {
    padding: 10px;
  }
  .topic-form {
    :deep(.el-form-item) {
      display: block;
    }
    :deep(.el-form-item__label) {
      justify-content: flex-start;
      padding-bottom: 6px;
    }
    :deep(.el-form-item__content) {
      margin-left: 0 !important;
    }
  }
  .topic-form-actions .el-button {
    flex: 1 1 40%;
  }
}
</style>
