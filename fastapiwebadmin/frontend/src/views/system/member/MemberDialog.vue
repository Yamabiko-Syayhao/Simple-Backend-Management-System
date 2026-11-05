<template>
  <el-dialog
    v-model="state.visible"
    title="用户编辑"
    width="640px"
    class="member-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="state.ruleForm"
      :rules="rules"
      label-width="100px"
      class="member-dialog-form"
    >
      <el-form-item label="用户名" prop="username">
        <el-input v-model="state.ruleForm.username" :disabled="state.editType === 'edit'" placeholder="请输入用户名" />
      </el-form-item>

      <el-form-item label="用户昵称" prop="nickname">
        <el-input v-model="state.ruleForm.nickname" placeholder="请输入用户昵称" />
      </el-form-item>

      <el-form-item label="用户手机" prop="mobile">
        <el-input v-model="state.ruleForm.mobile" placeholder="请输入用户手机" />
      </el-form-item>

      <el-form-item label="用户性别" prop="gender">
        <el-select v-model="state.ruleForm.gender" placeholder="请选择用户性别" style="width: 100%">
          <el-option label="未知" :value="0" />
          <el-option label="男" :value="1" />
          <el-option label="女" :value="2" />
        </el-select>
      </el-form-item>

      <el-form-item label="用户等级" prop="level">
        <el-select v-model="state.ruleForm.level" placeholder="请选择用户等级" style="width: 100%">
          <el-option label="普通用户" :value="0" />
          <el-option label="高级VIP用户" :value="1" />
        </el-select>
      </el-form-item>

      <el-form-item label="状态" prop="status">
        <el-select v-model="state.ruleForm.status" placeholder="请选择状态" style="width: 100%">
          <el-option label="可用" :value="1" />
          <el-option label="禁用" :value="2" />
          <el-option label="注销" :value="0" />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="member-dialog-footer">
        <el-button class="member-dialog-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="member-dialog-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'MemberDialog' })

import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useMemberApi } from '/@/api/useSystemApi/member'

const emit = defineEmits(['getList'])

const formRef = ref()

const state = reactive({
  visible: false,
  loading: false,
  editType: 'edit' as 'add' | 'edit',
  ruleForm: {
    id: undefined as number | undefined,
    username: '',
    nickname: '',
    mobile: '',
    gender: 0,
    level: 0,
    status: 1,
  },
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  mobile: [
    { pattern: /^$|^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
}

const resetForm = () => {
  state.ruleForm = {
    id: undefined,
    username: '',
    nickname: '',
    mobile: '',
    gender: 0,
    level: 0,
    status: 1,
  }
  formRef.value?.clearValidate()
}

const openDialog = async (editType: 'add' | 'edit', row?: any) => {
  state.editType = editType
  resetForm()
  state.visible = true

  if (editType === 'edit' && row?.id) {
    const res: any = await useMemberApi().getDetail({ id: row.id })
    const data = res.data || {}
    state.ruleForm = {
      id: data.id,
      username: data.username || '',
      nickname: data.nickname || '',
      mobile: data.mobile || '',
      gender: data.gender ?? 0,
      level: data.level ?? 0,
      status: data.status ?? 1,
    }
  }
}

const onSubmit = () => {
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return
    state.loading = true
    try {
      const payload: Record<string, any> = {
        ...state.ruleForm,
        mobile: state.ruleForm.mobile || '',
        nickname: state.ruleForm.nickname || '',
      }
      await useMemberApi().saveOrUpdate(payload)
      ElMessage.success('保存成功')
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
.member-dialog {
  :deep(.el-dialog__header) {
    padding: 22px 24px 18px;
    border-bottom: 1px solid #eef1f6;
  }

  :deep(.el-dialog__title) {
    font-size: 18px;
    font-weight: 500;
    color: #303133;
  }

  :deep(.el-dialog__body) {
    padding: 28px 20px 8px;
  }

  :deep(.el-dialog__footer) {
    padding: 12px 24px 22px;
  }
}

.member-dialog-form {
  :deep(.el-form-item) {
    margin-bottom: 20px;
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

  :deep(.el-input.is-disabled .el-input__wrapper) {
    background: #f5f7fa;
    box-shadow: 0 0 0 1px #e4e7ed inset;
  }

  :deep(.el-input.is-disabled .el-input__inner) {
    color: #a8abb2;
    -webkit-text-fill-color: #a8abb2;
  }
}

.member-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .member-dialog-cancel {
    width: 76px;
    height: 38px;
    border-radius: 4px;
  }

  .member-dialog-confirm {
    width: 76px;
    height: 38px;
    border-radius: 4px;
    background: #1890ff;
    border-color: #1890ff;

    &:hover {
      background: #40a9ff;
      border-color: #40a9ff;
    }
  }
}
</style>

<style lang="scss">
/* el-dialog 会被 teleport 到 body，scoped 样式作用不到，这里用全局样式做响应式 */
@media screen and (max-width: 768px) {
  .member-dialog {
    width: 92% !important;
    margin-top: 6vh !important;
    margin-bottom: 6vh !important;
  }

  .member-dialog .el-dialog__header {
    padding: 16px 16px 12px;
  }

  .member-dialog .el-dialog__body {
    padding: 18px 10px 4px;
  }

  .member-dialog .el-dialog__footer {
    padding: 10px 16px 16px;
  }

  .member-dialog .el-form-item {
    margin-bottom: 14px;
  }

  .member-dialog .el-form-item__label {
    width: 78px !important;
    padding-right: 10px;
  }

  .member-dialog .el-form-item__content {
    margin-left: 78px !important;
  }
}
</style>
