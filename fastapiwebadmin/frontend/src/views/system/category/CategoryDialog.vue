<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="700px"
    class="category-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="state.ruleForm"
      :rules="rules"
      label-width="110px"
      class="category-dialog-form"
    >
      <el-form-item label="类目名称" prop="name">
        <el-input v-model="state.ruleForm.name" placeholder="请输入类目名称" maxlength="128" />
      </el-form-item>

      <el-form-item label="关键字" prop="keywords">
        <el-input v-model="state.ruleForm.keywords" placeholder="请输入关键字" maxlength="255" />
      </el-form-item>

      <el-form-item label="级别" prop="level">
        <el-select v-model="state.ruleForm.level" placeholder="请选择级别" style="width: 100%">
          <el-option label="一级类目" :value="1" />
          <el-option label="二级类目" :value="2" />
        </el-select>
      </el-form-item>

      <el-form-item v-if="state.ruleForm.level === 2" label="父类目" prop="parent_id">
        <el-select
          v-model="state.ruleForm.parent_id"
          placeholder="请选择"
          style="width: 100%"
        >
          <el-option label="请选择" :value="0" />
          <el-option
            v-for="item in parentSelectOptions"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="类目图标">
        <el-upload
          class="cat-uploader"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          accept="image/*"
          :before-upload="beforeUpload"
          :on-success="(res: any) => onUploadSuccess(res, 'icon')"
          :on-error="onUploadError"
        >
          <img v-if="state.ruleForm.icon" :src="state.ruleForm.icon" class="cat-uploader__img" alt="类目图标" />
          <div v-else class="cat-uploader__empty">
            <el-icon :size="26"><Plus /></el-icon>
          </div>
        </el-upload>
        <div class="cat-uploader__tip">支持 jpg / png / gif / webp / svg 等格式</div>
      </el-form-item>

      <el-form-item label="类目图片">
        <el-upload
          class="cat-uploader"
          :action="uploadUrl"
          :headers="uploadHeaders"
          :show-file-list="false"
          accept="image/*"
          :before-upload="beforeUpload"
          :on-success="(res: any) => onUploadSuccess(res, 'image')"
          :on-error="onUploadError"
        >
          <img v-if="state.ruleForm.image" :src="state.ruleForm.image" class="cat-uploader__img" alt="类目图片" />
          <div v-else class="cat-uploader__empty">
            <el-icon :size="26"><Plus /></el-icon>
          </div>
        </el-upload>
      </el-form-item>

      <el-form-item label="类目简介" prop="description">
        <el-input v-model="state.ruleForm.description" placeholder="请输入类目简介" maxlength="500" />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="category-dialog-footer">
        <el-button class="category-dialog-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="category-dialog-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'CategoryDialog' })

import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useCategoryApi } from '/@/api/useSystemApi/category'
import { getApiBaseUrl } from '/@/utils/config'
import { Session } from '/@/utils/storage'

const emit = defineEmits(['getList'])

const formRef = ref()

// getApiBaseUrl() 已带 /api 前缀
const uploadUrl = `${getApiBaseUrl()}/file/upload`
const uploadHeaders = { token: Session.get('token') || '' }

const state = reactive({
  visible: false,
  loading: false,
  editType: 'add' as 'add' | 'edit',
  parentOptions: [] as any[],
  ruleForm: {
    id: undefined as number | undefined,
    name: '',
    keywords: '',
    level: 2,
    parent_id: 0 as number,
    icon: '',
    image: '',
    description: '',
  },
})

const rules = {
  name: [{ required: true, message: '类目名称不能为空', trigger: 'blur' }],
}

/** 父类目下拉：只列一级类目，并排除自己（避免成为自己的父级） */
const parentSelectOptions = computed(() =>
  state.parentOptions.filter((item: any) => item.id !== state.ruleForm.id)
)

// 切换成一级类目时清空父类目
watch(
  () => state.ruleForm.level,
  (level) => {
    if (level === 1) state.ruleForm.parent_id = 0
  }
)

const resetForm = () => {
  state.ruleForm = {
    id: undefined,
    name: '',
    keywords: '',
    level: 2,
    parent_id: 0,
    icon: '',
    image: '',
    description: '',
  }
  formRef.value?.clearValidate()
}

const loadParentOptions = async () => {
  try {
    const res: any = await useCategoryApi().getList()
    const rows = res.data?.rows || []
    state.parentOptions = rows.filter((item: any) => item.level === 1)
  } catch (e) {
    state.parentOptions = []
  }
}

const openDialog = async (editType: 'add' | 'edit', row?: any) => {
  state.editType = editType
  resetForm()
  state.visible = true
  await loadParentOptions()

  if (editType === 'edit' && row?.id) {
    const res: any = await useCategoryApi().getDetail({ id: row.id })
    const data = res.data || {}
    state.ruleForm = {
      id: data.id,
      name: data.name || '',
      keywords: data.keywords || '',
      level: data.level ?? 1,
      parent_id: data.parent_id ?? 0,
      icon: data.icon || '',
      image: data.image || '',
      description: data.description || '',
    }
  }
}

const beforeUpload = (file: File) => {
  if (!file.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (file.size / 1024 / 1024 >= 10) {
    ElMessage.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

const onUploadSuccess = (res: any, field: 'icon' | 'image') => {
  if (res && res.code === 0 && res.data && res.data.url) {
    state.ruleForm[field] = res.data.url
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

    if (state.ruleForm.level === 2 && !state.ruleForm.parent_id) {
      ElMessage.error('二级类目必须选择父类目')
      return
    }

    state.loading = true
    try {
      const payload: Record<string, any> = {
        id: state.ruleForm.id,
        name: state.ruleForm.name,
        keywords: state.ruleForm.keywords,
        level: state.ruleForm.level,
        parent_id: state.ruleForm.level === 1 ? 0 : state.ruleForm.parent_id,
        icon: state.ruleForm.icon,
        image: state.ruleForm.image,
        description: state.ruleForm.description,
      }
      await useCategoryApi().saveOrUpdate(payload)
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
.category-dialog {
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
    max-height: 70vh;
    overflow-y: auto;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 20px;
  }
}

.category-dialog-form {
  :deep(.el-form-item) {
    margin-bottom: 22px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    color: #3d4d66;
    justify-content: flex-end;
    padding-right: 16px;
  }

  :deep(.el-input__wrapper),
  :deep(.el-select__wrapper) {
    height: 40px;
    border-radius: 4px;
  }

  :deep(.el-form-item__content) {
    max-width: 330px;
  }
}

.cat-uploader {
  :deep(.el-upload) {
    border: 1px dashed #d9dde3;
    border-radius: 6px;
    cursor: pointer;
    overflow: hidden;
    transition: border-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 120px;
    height: 120px;
    background: #fafbfc;

    &:hover {
      border-color: #1890ff;
    }
  }
}

.cat-uploader__img {
  width: 120px;
  height: 120px;
  object-fit: contain;
  display: block;
  background: #fff;
}

.cat-uploader__empty {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #b9c0cc;
}

.cat-uploader__tip {
  width: 100%;
  margin-top: 6px;
  font-size: 12px;
  color: #a8abb2;
}

.category-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .category-dialog-cancel {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .category-dialog-confirm {
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

@media screen and (max-width: 768px) {
  :global(.category-dialog) {
    width: 92% !important;
  }
}
</style>
