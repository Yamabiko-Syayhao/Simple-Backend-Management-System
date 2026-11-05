<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="700px"
    class="brand-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="state.ruleForm"
      :rules="rules"
      label-width="110px"
      class="brand-dialog-form"
    >
      <el-form-item label="品牌商名称" prop="name">
        <el-input v-model="state.ruleForm.name" placeholder="请输入品牌商名称" maxlength="128" />
      </el-form-item>

      <el-form-item label="介绍" prop="description">
        <el-input v-model="state.ruleForm.description" placeholder="请输入介绍" maxlength="500" />
      </el-form-item>

      <el-form-item label="品牌商图片">
        <el-upload
          class="brand-uploader"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          accept="image/*"
          :before-upload="beforeUpload"
          :on-success="onUploadSuccess"
          :on-error="onUploadError"
        >
          <img v-if="state.ruleForm.image" :src="state.ruleForm.image" class="brand-uploader__img" alt="品牌商图片" />
          <div v-else class="brand-uploader__empty">
            <el-icon :size="26"><Plus /></el-icon>
          </div>
        </el-upload>
        <div class="brand-uploader__tip">支持 jpg / jpeg / png / gif / webp / bmp 等图片格式</div>
      </el-form-item>

      <el-form-item label="底价" prop="floor_price">
        <el-input v-model="state.ruleForm.floor_price" placeholder="请输入底价" />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="brand-dialog-footer">
        <el-button class="brand-dialog-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="brand-dialog-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'BrandDialog' })

import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useBrandApi } from '/@/api/useSystemApi/brand'
import { getApiBaseUrl } from '/@/utils/config'
import { Session } from '/@/utils/storage'

const emit = defineEmits(['getList'])

const formRef = ref()

// getApiBaseUrl() 已经带了 /api 前缀，这里只拼路径，避免出现 /api/api/...
const uploadUrl = `${getApiBaseUrl()}/file/upload`
const uploadHeaders = { token: Session.get('token') || '' }

const state = reactive({
  visible: false,
  loading: false,
  editType: 'add' as 'add' | 'edit',
  ruleForm: {
    id: undefined as number | undefined,
    name: '',
    description: '',
    image: '',
    floor_price: '' as string | number,
  },
})

const rules = {
  name: [{ required: true, message: '请输入品牌商名称', trigger: 'blur' }],
  floor_price: [
    {
      validator: (_rule: any, value: any, callback: any) => {
        if (value === '' || value === null || value === undefined) {
          callback()
          return
        }
        if (Number.isNaN(Number(value))) {
          callback(new Error('底价必须是数字'))
          return
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
}

const resetForm = () => {
  state.ruleForm = {
    id: undefined,
    name: '',
    description: '',
    image: '',
    floor_price: '',
  }
  formRef.value?.clearValidate()
}

const openDialog = async (editType: 'add' | 'edit', row?: any) => {
  state.editType = editType
  resetForm()
  state.visible = true

  if (editType === 'edit' && row?.id) {
    const res: any = await useBrandApi().getDetail({ id: row.id })
    const data = res.data || {}
    state.ruleForm = {
      id: data.id,
      name: data.name || '',
      description: data.description || '',
      image: data.image || '',
      floor_price: data.floor_price ?? '',
    }
  }
}

const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

const onUploadSuccess = (res: any) => {
  if (res && res.code === 0 && res.data && res.data.url) {
    state.ruleForm.image = res.data.url
    ElMessage.success('图片上传成功')
  } else {
    ElMessage.error((res && res.msg) || '图片上传失败')
  }
}

const onUploadError = (err: any) => {
  const status = err?.status || err?.statusCode
  ElMessage.error(status ? `图片上传失败（HTTP ${status}）` : '图片上传失败，请检查后端服务')
}

const onSubmit = () => {
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return

    state.loading = true
    try {
      const price = state.ruleForm.floor_price
      const payload: Record<string, any> = {
        id: state.ruleForm.id,
        name: state.ruleForm.name,
        description: state.ruleForm.description,
        image: state.ruleForm.image,
        floor_price: price === '' || price === null ? null : Number(price),
      }
      await useBrandApi().saveOrUpdate(payload)
      ElMessage.success(state.editType === 'add' ? '创建成功' : '保存成功')
      state.visible = false
      emit('getList')
    } finally {
      state.loading = false
    }
  })
}

defineExpose({ openDialog })
</script>

<style scoped lang="scss">
.brand-dialog {
  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    border-bottom: 1px solid #eef1f6;
  }

  :deep(.el-dialog__title) {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
  }

  :deep(.el-dialog__body) {
    padding: 26px 30px 10px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 20px;
  }
}

.brand-dialog-form {
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    color: #3d4d66;
    justify-content: flex-end;
    padding-right: 16px;
  }

  :deep(.el-input__wrapper) {
    height: 40px;
    border-radius: 4px;
  }

  :deep(.el-form-item__content) {
    max-width: 320px;
  }
}

.brand-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9dde3;
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 160px;
    height: 120px;
    background: #fafbfc;

    &:hover {
      border-color: #1890ff;
    }
  }
}

.brand-uploader__img {
  width: 160px;
  height: 120px;
  object-fit: cover;
  display: block;
}

.brand-uploader__empty {
  width: 160px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b9c0cc;
}

.brand-uploader__tip {
  width: 100%;
  margin-top: 6px;
  font-size: 12px;
  line-height: 1.4;
  color: #a8abb2;
}

.brand-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .brand-dialog-cancel {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .brand-dialog-confirm {
    width: 76px;
    height: 36px;
    border-radius: 4px;
    background: #1890ff;
    border-color: #1890ff;

    &:hover {
      background: #40a9ff;
      border-color: #40a9ff;
    }
  }
}

/* el-dialog 被 teleport 到 body，这里用全局样式做窄屏适配 */
@media screen and (max-width: 768px) {
  :global(.brand-dialog) {
    width: 92% !important;
  }
}
</style>
