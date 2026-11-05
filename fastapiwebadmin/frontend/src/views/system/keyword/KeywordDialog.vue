<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="640px"
    class="keyword-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="state.ruleForm"
      :rules="rules"
      label-width="90px"
      class="keyword-dialog-form"
    >
      <el-form-item label="关键词" prop="keyword">
        <el-input v-model="state.ruleForm.keyword" placeholder="请输入关键词" maxlength="64" />
      </el-form-item>

      <el-form-item label="跳转链接" prop="link">
        <el-input v-model="state.ruleForm.link" placeholder="请输入跳转链接" maxlength="500" />
      </el-form-item>

      <el-form-item label="是否推荐" prop="is_recommend">
        <el-select v-model="state.ruleForm.is_recommend" style="width: 100%">
          <el-option label="推荐" :value="1" />
          <el-option label="普通" :value="0" />
        </el-select>
      </el-form-item>

      <el-form-item label="是否默认" prop="is_default">
        <el-select v-model="state.ruleForm.is_default" style="width: 100%">
          <el-option label="默认" :value="1" />
          <el-option label="非默认" :value="0" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="keyword-dialog-footer">
        <el-button class="keyword-dialog-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="keyword-dialog-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'KeywordDialog' })

import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useKeywordApi } from '/@/api/useSystemApi/keyword'

const emit = defineEmits(['getList'])

const formRef = ref()

const state = reactive({
  visible: false,
  loading: false,
  editType: 'add' as 'add' | 'edit',
  ruleForm: {
    id: undefined as number | undefined,
    keyword: '',
    link: '',
    is_recommend: 0,
    is_default: 0,
  },
})

const rules = {
  keyword: [{ required: true, message: '关键词不能为空', trigger: 'blur' }],
}

const resetForm = () => {
  state.ruleForm = {
    id: undefined,
    keyword: '',
    link: '',
    is_recommend: 0,
    is_default: 0,
  }
  formRef.value?.clearValidate()
}

const openDialog = async (editType: 'add' | 'edit', row?: any) => {
  state.editType = editType
  resetForm()
  state.visible = true

  if (editType === 'edit' && row?.id) {
    const res: any = await useKeywordApi().getDetail({ id: row.id })
    const data = res.data || {}
    state.ruleForm = {
      id: data.id,
      keyword: data.keyword || '',
      link: data.link || '',
      is_recommend: data.is_recommend ?? 0,
      is_default: data.is_default ?? 0,
    }
  }
}

const onSubmit = () => {
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return

    state.loading = true
    try {
      await useKeywordApi().saveOrUpdate({
        id: state.ruleForm.id,
        keyword: state.ruleForm.keyword,
        link: state.ruleForm.link,
        is_recommend: state.ruleForm.is_recommend,
        is_default: state.ruleForm.is_default,
      })
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
.keyword-dialog {
  :deep(.el-dialog__header) {
    padding: 18px 24px 14px;
    border-bottom: 1px solid #eef1f6;
  }

  :deep(.el-dialog__title) {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
  }

  :deep(.el-dialog__body) {
    padding: 26px 30px 8px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 18px;
  }
}

.keyword-dialog-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    color: #3d4d66;
    justify-content: flex-end;
    padding-right: 12px;
  }

  :deep(.el-input__wrapper),
  :deep(.el-select__wrapper) {
    height: 38px;
    border-radius: 4px;
  }
}

.keyword-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .keyword-dialog-cancel {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .keyword-dialog-confirm {
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
  :global(.keyword-dialog) {
    width: 92% !important;
  }
}
</style>
