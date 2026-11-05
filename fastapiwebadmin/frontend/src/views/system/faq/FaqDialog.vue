<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="720px"
    class="faq-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="state.ruleForm"
      :rules="rules"
      label-width="70px"
      class="faq-dialog-form"
    >
      <el-form-item label="问题" prop="question">
        <el-input v-model="state.ruleForm.question" placeholder="请输入问题" maxlength="500" />
      </el-form-item>

      <el-form-item label="回复" prop="answer">
        <el-input
          v-model="state.ruleForm.answer"
          type="textarea"
          :rows="8"
          placeholder="请输入内容"
          maxlength="2000"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="faq-dialog-footer">
        <el-button class="faq-dialog-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="faq-dialog-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'FaqDialog' })

import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useFaqApi } from '/@/api/useSystemApi/faq'

const emit = defineEmits(['getList'])

const formRef = ref()

const state = reactive({
  visible: false,
  loading: false,
  editType: 'add' as 'add' | 'edit',
  ruleForm: {
    id: undefined as number | undefined,
    question: '',
    answer: '',
  },
})

const rules = {
  question: [{ required: true, message: '问题不能为空', trigger: 'blur' }],
  answer: [{ required: true, message: '回复不能为空', trigger: 'blur' }],
}

const resetForm = () => {
  state.ruleForm = {
    id: undefined,
    question: '',
    answer: '',
  }
  formRef.value?.clearValidate()
}

const openDialog = async (editType: 'add' | 'edit', row?: any) => {
  state.editType = editType
  resetForm()
  state.visible = true

  if (editType === 'edit' && row?.id) {
    const res: any = await useFaqApi().getDetail({ id: row.id })
    const data = res.data || {}
    state.ruleForm = {
      id: data.id,
      question: data.question || '',
      answer: data.answer || '',
    }
  }
}

const onSubmit = () => {
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return

    state.loading = true
    try {
      await useFaqApi().saveOrUpdate({
        id: state.ruleForm.id,
        question: state.ruleForm.question,
        answer: state.ruleForm.answer,
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
.faq-dialog {
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
    padding: 26px 34px 8px;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 24px 18px;
  }
}

.faq-dialog-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
  }

  :deep(.el-form-item__label) {
    font-size: 14px;
    color: #3d4d66;
    justify-content: flex-end;
    padding-right: 12px;
  }

  :deep(.el-input__wrapper) {
    height: 38px;
    border-radius: 4px;
  }

  :deep(.el-textarea__inner) {
    border-radius: 4px;
    font-size: 14px;
    line-height: 1.6;
  }
}

.faq-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .faq-dialog-cancel {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .faq-dialog-confirm {
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
  :global(.faq-dialog) {
    width: 92% !important;
  }
}
</style>
