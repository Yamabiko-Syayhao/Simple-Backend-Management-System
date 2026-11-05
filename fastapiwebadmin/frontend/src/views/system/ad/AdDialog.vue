<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="960px"
    class="ad-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="!state.saving"
    :show-close="!state.saving"
    destroy-on-close
    @close="onDialogClose"
  >
    <el-form
      ref="formRef"
      v-loading="state.fetching"
      :model="state.ruleForm"
      :rules="rules"
      :disabled="state.saving || state.fetching || state.loadFailed"
      label-width="110px"
      class="ad-dialog-form"
    >
      <el-form-item label="广告标题" prop="title">
        <el-input
          v-model="state.ruleForm.title"
          maxlength="128"
          placeholder="请输入广告标题"
        />
      </el-form-item>
      <el-form-item label="广告内容" prop="content">
        <el-input
          v-model="state.ruleForm.content"
          maxlength="1000"
          placeholder="请输入广告内容"
        />
      </el-form-item>
      <el-form-item label="广告图片" prop="image">
        <div class="ad-image-field">
          <el-upload
            ref="uploadRef"
            class="ad-uploader"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            :disabled="
              state.uploading ||
              state.saving ||
              state.fetching ||
              state.loadFailed
            "
            accept="image/*"
            :before-upload="beforeUpload"
            :on-success="onUploadSuccess"
            :on-error="onUploadError"
          >
            <img
              v-if="state.ruleForm.image"
              :src="state.ruleForm.image"
              class="ad-uploader-img"
              alt="广告图片"
            />
            <div v-else class="ad-uploader-empty">
              <el-icon :size="30"><Plus /></el-icon>
            </div>
          </el-upload>
          <el-button
            v-if="state.ruleForm.image"
            type="danger"
            link
            :disabled="state.uploading"
            @click="removeImage"
            >移除图片</el-button
          >
          <div class="ad-uploader-tip">
            {{
              state.uploading
                ? '图片上传中，请稍候…'
                : '支持 jpg / jpeg / png / gif / webp / bmp / svg 等图片格式，大小不超过 3MB'
            }}
          </div>
        </div>
      </el-form-item>
      <el-form-item label="广告位置" prop="position">
        <el-select v-model="state.ruleForm.position" class="ad-dialog-select"
          ><el-option :value="1" label="首页"
        /></el-select>
      </el-form-item>
      <el-form-item label="活动链接" prop="link">
        <el-input
          v-model="state.ruleForm.link"
          maxlength="1000"
          placeholder="请输入活动链接（选填）"
        />
      </el-form-item>
      <el-form-item label="是否启用" prop="status">
        <el-select v-model="state.ruleForm.status" class="ad-dialog-select"
          ><el-option :value="1" label="启用" /><el-option
            :value="0"
            label="不启用"
        /></el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="ad-dialog-footer">
        <el-button :disabled="state.saving" @click="state.visible = false"
          >取消</el-button
        >
        <el-button
          type="primary"
          :loading="state.saving"
          :disabled="
            state.fetching ||
            state.uploading ||
            state.loadFailed ||
            !state.ruleForm.image
          "
          @click="onSubmit"
          >确定</el-button
        >
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'AdDialog' });

import { nextTick, reactive, ref } from 'vue';
import { ElMessage, ElNotification } from 'element-plus';
import type {
  FormInstance,
  FormRules,
  UploadFile,
  UploadInstance,
  UploadRawFile,
} from 'element-plus';
import { Plus } from '@element-plus/icons-vue';
import { useAdApi } from '/@/api/useSystemApi/ad';
import { getApiBaseUrl } from '/@/utils/config';
import { Session } from '/@/utils/storage';

const emit = defineEmits(['getList']);
const formRef = ref<FormInstance>();
const uploadRef = ref<UploadInstance>();
// 广告上传在服务端同样校验图片类型和 3MB 大小限制。
const uploadUrl = `${getApiBaseUrl()}/ad/upload`;
const uploadHeaders = reactive({ token: Session.get('token') || '' });
const blankForm = () => ({
  id: undefined as number | undefined,
  title: '',
  content: '',
  image: '',
  position: 1,
  link: '',
  status: 1,
});
const state = reactive({
  visible: false,
  saving: false,
  fetching: false,
  uploading: false,
  loadFailed: false,
  editType: 'add' as 'add' | 'edit',
  ruleForm: blankForm(),
});
const rules: FormRules = {
  title: [
    {
      required: true,
      whitespace: true,
      message: '请输入广告标题',
      trigger: 'blur',
    },
  ],
  content: [
    {
      required: true,
      whitespace: true,
      message: '请输入广告内容',
      trigger: 'blur',
    },
  ],
  image: [{ required: true, message: '请上传广告图片', trigger: 'change' }],
};

let dialogRequestId = 0;
let uploadRequestId = 0;
let activeUploadUid: number | undefined;

const openDialog = async (editType: 'add' | 'edit', row?: { id: number }) => {
  const requestId = ++dialogRequestId;
  uploadRef.value?.abort();
  activeUploadUid = undefined;
  state.editType = editType;
  state.ruleForm = blankForm();
  state.saving = false;
  state.fetching = editType === 'edit';
  state.uploading = false;
  state.loadFailed = false;
  uploadHeaders.token = Session.get('token') || '';
  state.visible = true;
  await nextTick();
  formRef.value?.clearValidate();
  if (requestId !== dialogRequestId || editType !== 'edit') return;
  if (!row?.id) {
    state.fetching = false;
    state.loadFailed = true;
    ElMessage.error('广告记录不存在，请刷新列表');
    return;
  }
  try {
    const res: any = await useAdApi().getDetail({ id: row.id });
    if (requestId !== dialogRequestId || !state.visible) return;
    const data = res.data || {};
    if (!data.id) {
      state.loadFailed = true;
      ElMessage.error('广告记录不存在，请刷新列表');
      return;
    }
    state.ruleForm = {
      id: data.id,
      title: data.title || '',
      content: data.content || '',
      image: data.image || '',
      position: data.position ?? 1,
      link: data.link || '',
      status: data.status ?? 1,
    };
  } catch {
    if (requestId === dialogRequestId) state.loadFailed = true;
  } finally {
    if (requestId === dialogRequestId) state.fetching = false;
  }
};

const onDialogClose = () => {
  dialogRequestId += 1;
  uploadRef.value?.abort();
  activeUploadUid = undefined;
  state.uploading = false;
};

const beforeUpload = (file: UploadRawFile) => {
  const extension = file.name.split('.').pop()?.toLowerCase() || '';
  const isImage =
    file.type.startsWith('image/') ||
    (!file.type &&
      ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(extension));
  if (!isImage) {
    ElMessage.error('只能上传图片文件');
    return false;
  }
  if (!file.size || file.size > 3 * 1024 * 1024) {
    ElMessage.error('图片大小须大于 0 且不能超过 3MB');
    return false;
  }
  uploadRequestId = dialogRequestId;
  activeUploadUid = file.uid;
  state.uploading = true;
  return true;
};

const onUploadSuccess = (res: any, file: UploadFile) => {
  if (
    !state.visible ||
    uploadRequestId !== dialogRequestId ||
    file.uid !== activeUploadUid
  )
    return;
  state.uploading = false;
  activeUploadUid = undefined;
  if (res?.code === 0 && res.data?.url) {
    state.ruleForm.image = res.data.url;
    formRef.value?.validateField('image').catch(() => {});
    ElMessage.success('图片上传成功');
  } else {
    ElMessage.error(res?.msg || '图片上传失败');
  }
};

const onUploadError = (err: Error & { status?: number }, file: UploadFile) => {
  if (
    !state.visible ||
    uploadRequestId !== dialogRequestId ||
    file.uid !== activeUploadUid
  )
    return;
  state.uploading = false;
  activeUploadUid = undefined;
  ElMessage.error(
    err?.status
      ? `图片上传失败（HTTP ${err.status}）`
      : '图片上传失败，请检查后端服务'
  );
};

const removeImage = () => {
  state.ruleForm.image = '';
  formRef.value?.validateField('image').catch(() => {});
};

const onSubmit = async () => {
  if (state.saving || state.uploading || state.fetching || state.loadFailed)
    return;
  state.saving = true;
  try {
    const valid = await formRef.value?.validate().catch(() => false);
    if (!valid) return;
    const payload = {
      id: state.ruleForm.id,
      title: state.ruleForm.title.trim(),
      content: state.ruleForm.content.trim(),
      image: state.ruleForm.image,
      position: state.ruleForm.position,
      link: state.ruleForm.link.trim(),
      status: state.ruleForm.status,
    };
    await useAdApi().saveOrUpdate(payload);
    ElNotification({
      title: '成功',
      message: state.editType === 'add' ? '创建成功' : '保存成功',
      type: 'success',
      position: 'top-right',
    });
    state.visible = false;
    emit('getList');
  } catch {
    // 接口错误由全局拦截器提示。
  } finally {
    state.saving = false;
  }
};

defineExpose({ openDialog });
</script>

<style scoped lang="scss">
.ad-dialog-form {
  padding: 12px 32px 24px;
  :deep(.el-form-item) {
    margin-bottom: 24px;
  }
  :deep(.el-form-item__label) {
    justify-content: flex-end;
    font-weight: 600;
    color: #606266;
    padding-right: 20px;
  }
  :deep(.el-form-item__content) {
    max-width: 420px;
  }
  :deep(.el-input) {
    width: 300px;
    max-width: 100%;
  }
  :deep(.el-input__wrapper) {
    height: 32px;
    border-radius: 4px;
  }
  .ad-dialog-select {
    width: 208px;
    max-width: 100%;
  }
}
.ad-image-field {
  width: 100%;
}
.ad-uploader {
  display: inline-block;
  :deep(.el-upload) {
    width: 122px;
    height: 122px;
    border: 1px dashed #d9dde3;
    border-radius: 5px;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  :deep(.el-upload:hover) {
    border-color: #1890ff;
  }
}
.ad-uploader-img {
  width: 122px;
  height: 122px;
  object-fit: contain;
  display: block;
}
.ad-uploader-empty {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  color: #909399;
}
.ad-uploader-tip {
  margin-top: 14px;
  color: #909399;
  font-size: 12px;
  line-height: 1.6;
}
.ad-image-field > .el-button {
  display: block;
}
.ad-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  .el-button {
    margin-left: 0;
  }
}
</style>

<style lang="scss">
.ad-dialog {
  max-width: calc(100vw - 40px);
  --el-color-primary: #1890ff;
  .el-dialog__header {
    padding: 6px 4px 16px;
  }
  .el-dialog__body {
    padding: 16px 20px 6px;
  }
  .el-dialog__footer {
    padding: 6px 4px 4px;
  }
}
@media screen and (max-width: 900px) {
  .ad-dialog {
    width: 92% !important;
    .ad-dialog-form {
      padding: 8px 8px 20px;
    }
    .el-form-item__label {
      width: 90px !important;
      padding-right: 12px;
    }
    .el-form-item__content {
      min-width: 0;
      margin-left: 0 !important;
    }
  }
}
@media screen and (max-width: 560px) {
  .ad-dialog {
    .el-dialog__body {
      padding: 12px 4px 4px;
    }
    .ad-dialog-form {
      padding: 4px 0 14px;
    }
    .el-form-item__label {
      width: 78px !important;
      padding-right: 8px;
    }
    .el-form-item__content {
      margin-left: 0 !important;
    }
    .ad-dialog-footer .el-button {
      flex: 1 1 40%;
    }
  }
}
</style>
