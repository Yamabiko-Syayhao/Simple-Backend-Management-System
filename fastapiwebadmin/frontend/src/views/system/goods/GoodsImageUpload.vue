<template>
  <div class="goods-upload">
    <el-upload
      :action="uploadUrl"
      :headers="headers"
      accept="image/*"
      :show-file-list="false"
      :before-upload="beforeUpload"
      :on-success="success"
      :on-error="failed"
      :disabled="loading"
      :on-progress="() => (loading = true)"
    >
      <img v-if="modelValue" :src="modelValue" alt="商品图片" /><span v-else>{{
        loading ? '上传中…' : '+'
      }}</span>
    </el-upload>
    <el-button
      v-if="modelValue"
      link
      type="danger"
      @click="$emit('update:modelValue', '')"
      >移除</el-button
    >
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { getApiBaseUrl } from '/@/utils/config';
import { Session } from '/@/utils/storage';
defineProps<{ modelValue: string }>();
const emit = defineEmits(['update:modelValue']);
const loading = ref(false);
const uploadUrl = `${getApiBaseUrl()}/file/upload`;
const headers = { token: Session.get('token') || '' };
function beforeUpload(file: File) {
  if (!file.type.startsWith('image/') || file.size > 10 * 1024 * 1024) {
    ElMessage.error('请选择 10MB 以内的图片');
    return false;
  }
  loading.value = true;
  return true;
}
function success(res: any) {
  loading.value = false;
  if (res.code === 0 && res.data?.url) emit('update:modelValue', res.data.url);
  else ElMessage.error(res.msg || '上传失败');
}
function failed() {
  loading.value = false;
  ElMessage.error('图片上传失败');
}
</script>
<style scoped lang="scss">
.goods-upload {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  margin-right: 8px;
  :deep(.el-upload) {
    width: 120px;
    height: 120px;
    border: 1px dashed #d9dde3;
    border-radius: 4px;
    overflow: hidden;
  }
  img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  span {
    font-size: 30px;
    color: #909399;
  }
}
</style>
