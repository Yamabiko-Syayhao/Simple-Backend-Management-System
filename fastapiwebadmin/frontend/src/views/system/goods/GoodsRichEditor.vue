<template>
  <Editor
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    tinymce-script-src="/tinymce/tinymce.min.js"
    license-key="gpl"
    :init="config"
  />
</template>
<script setup lang="ts">
import Editor from '@tinymce/tinymce-vue';
import { getApiBaseUrl } from '/@/utils/config';
import { Session } from '/@/utils/storage';
defineProps<{ modelValue: string }>();
defineEmits(['update:modelValue']);
async function upload(file: Blob, name: string) {
  const data = new FormData();
  data.append('file', file, name);
  const response = await fetch(`${getApiBaseUrl()}/file/upload`, {
    method: 'POST',
    headers: { token: Session.get('token') || '' },
    body: data,
  });
  const result = await response.json();
  if (!response.ok || result.code !== 0 || !result.data?.url)
    throw new Error(result.msg || '上传失败');
  return new URL(result.data.url, window.location.origin).href;
}
const config = {
  language: 'zh_CN',
  language_url: '/tinymce/langs/zh_CN.js',
  base_url: '/tinymce',
  suffix: '.min',
  height: 480,
  promotion: false,
  menubar: 'file edit view insert format tools table help',
  plugins:
    'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table help wordcount',
  toolbar:
    'undo redo | blocks | bold italic underline strikethrough | alignleft aligncenter alignright | bullist numlist | link image media table | forecolor backcolor | code preview fullscreen',
  images_upload_handler: (info: any) => upload(info.blob(), info.filename()),
  file_picker_types: 'file image media',
  file_picker_callback: (callback: any, _value: string, meta: any) => {
    const input = document.createElement('input');
    input.type = 'file';
    if (meta.filetype === 'image') input.accept = 'image/*';
    input.onchange = async () => {
      const file = input.files?.[0];
      if (!file) return;
      try {
        callback(await upload(file, file.name), {
          text: file.name,
          title: file.name,
        });
      } catch (error: any) {
        const { ElMessage } = await import('element-plus');
        ElMessage.error(error.message);
      }
    };
    input.click();
  },
};
</script>
