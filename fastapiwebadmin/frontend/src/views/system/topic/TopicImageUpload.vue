<template>
  <div class="topic-cover">
    <el-upload
      ref="uploadRef"
      class="topic-cover-uploader"
      :action="uploadUrl"
      :headers="headers"
      accept="image/*"
      :show-file-list="false"
      :disabled="disabled || uploading"
      :before-upload="beforeUpload"
      :on-success="onSuccess"
      :on-error="onError"
    >
      <img v-if="modelValue" :src="modelValue" alt="专题封面" />
      <span v-else>{{ uploading ? '上传中…' : '+' }}</span>
    </el-upload>
    <el-button
      v-if="modelValue"
      type="danger"
      link
      :disabled="disabled || uploading"
      @click="$emit('update:modelValue', '')"
      >移除</el-button
    >
  </div>
</template>
<script setup lang="ts">
import { onBeforeUnmount, reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import type { UploadFile, UploadInstance, UploadRawFile } from 'element-plus';
import { getApiBaseUrl } from '/@/utils/config';
import { Session } from '/@/utils/storage';
const props = defineProps<{ modelValue: string; disabled?: boolean }>();
const emit = defineEmits(['update:modelValue', 'busy']);
const uploadRef = ref<UploadInstance>();
const uploading = ref(false);
const uploadUrl = `${getApiBaseUrl()}/file/upload`;
const headers = reactive({ token: Session.get('token') || '' });
let activeUid: number | undefined;
let alive = true;
const beforeUpload = (file: UploadRawFile) => {
  if (props.disabled || uploading.value) return false;
  const extension = file.name.split('.').pop()?.toLowerCase() || '';
  const isImage =
    file.type.startsWith('image/') ||
    (!file.type &&
      ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(extension));
  if (!isImage || !file.size || file.size > 10 * 1024 * 1024) {
    ElMessage.error('请选择 10MB 以内的图片');
    return false;
  }
  headers.token = Session.get('token') || '';
  activeUid = file.uid;
  uploading.value = true;
  emit('busy', true);
  return true;
};
const onSuccess = (result: any, file: UploadFile) => {
  if (!alive || file.uid !== activeUid) return;
  uploading.value = false;
  activeUid = undefined;
  emit('busy', false);
  if (result?.code === 0 && result.data?.url) {
    emit('update:modelValue', result.data.url);
    ElMessage.success('图片上传成功');
  } else ElMessage.error(result?.msg || '图片上传失败');
};
const onError = (error: Error & { status?: number }, file: UploadFile) => {
  if (!alive || file.uid !== activeUid) return;
  uploading.value = false;
  activeUid = undefined;
  emit('busy', false);
  ElMessage.error(
    error.status
      ? `图片上传失败（HTTP ${error.status}）`
      : '图片上传失败，请检查后端服务'
  );
};
onBeforeUnmount(() => {
  alive = false;
  activeUid = undefined;
  uploadRef.value?.abort();
  emit('busy', false);
});
</script>
<style scoped lang="scss">
.topic-cover {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.topic-cover-uploader {
  :deep(.el-upload) {
    width: 145px;
    height: 145px;
    border: 1px dashed #d9dde3;
    border-radius: 5px;
    overflow: hidden;
    &:hover {
      border-color: #1890ff;
    }
  }
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  span {
    color: #909399;
    font-size: 30px;
  }
}
</style>
