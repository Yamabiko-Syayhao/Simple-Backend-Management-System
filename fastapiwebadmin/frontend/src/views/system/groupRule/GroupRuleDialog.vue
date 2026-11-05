<template>
  <el-dialog
    v-model="state.visible"
    :title="state.editType === 'add' ? '创建' : '编辑'"
    width="640px"
    class="group-rule-dialog"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="state.ruleForm"
      :rules="rules"
      label-width="110px"
      class="group-rule-form"
    >
      <el-form-item label="商品ID" prop="goods_id">
        <el-input-number
          v-model="state.ruleForm.goods_id"
          :controls="false"
          :min="1"
          :precision="0"
          placeholder=""
          class="group-rule-number"
        />
      </el-form-item>

      <el-form-item label="团购折扣" prop="discount">
        <el-input v-model="state.ruleForm.discount" placeholder="" class="group-rule-number" />
      </el-form-item>

      <el-form-item label="团购人数要求" prop="people">
        <el-input-number
          v-model="state.ruleForm.people"
          :controls="false"
          :min="1"
          :precision="0"
          placeholder=""
          class="group-rule-number"
        />
      </el-form-item>

      <el-form-item label="过期时间" prop="end_time">
        <el-date-picker
          v-model="state.ruleForm.end_time"
          type="datetime"
          placeholder="选择日期"
          value-format="YYYY-MM-DD HH:mm:ss"
          class="group-rule-number"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="group-rule-footer">
        <el-button class="group-rule-cancel" @click="state.visible = false">取消</el-button>
        <el-button class="group-rule-confirm" type="primary" :loading="state.loading" @click="onSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
defineOptions({ name: 'GroupRuleDialog' })

import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useGroupRuleApi } from '/@/api/useSystemApi/groupRule'

const emit = defineEmits(['getList'])

const formRef = ref()

const state = reactive({
  visible: false,
  loading: false,
  editType: 'add' as 'add' | 'edit',
  ruleForm: {
    id: undefined as number | undefined,
    goods_id: undefined as number | undefined,
    discount: '',
    people: 2 as number | undefined,
    end_time: '',
  },
})

const validateDiscount = (_rule: any, value: string, callback: (error?: Error) => void) => {
  const text = String(value ?? '').trim()
  if (!text) {
    callback(new Error('请输入团购折扣'))
    return
  }
  const num = Number(text)
  if (Number.isNaN(num) || num < 0) {
    callback(new Error('团购折扣必须为不小于 0 的数字'))
    return
  }
  callback()
}

const rules = {
  goods_id: [{ required: true, message: '请输入商品ID', trigger: 'blur' }],
  discount: [{ required: true, validator: validateDiscount, trigger: 'blur' }],
  people: [{ required: true, message: '请输入团购人数要求', trigger: 'blur' }],
  end_time: [{ required: true, message: '请选择过期时间', trigger: 'change' }],
}

const resetForm = () => {
  state.ruleForm = {
    id: undefined,
    goods_id: undefined,
    discount: '',
    people: 2,
    end_time: '',
  }
  formRef.value?.clearValidate()
}

const openDialog = async (editType: 'add' | 'edit', row?: any) => {
  state.editType = editType
  resetForm()
  state.visible = true

  if (editType === 'edit' && row?.id) {
    const res: any = await useGroupRuleApi().getDetail({ id: row.id })
    const data = res.data || {}
    state.ruleForm = {
      id: data.id,
      goods_id: data.goods_id,
      discount: String(data.discount ?? ''),
      people: data.people ?? 1,
      end_time: data.end_time || '',
    }
  }
}

const onSubmit = () => {
  formRef.value?.validate(async (valid: boolean) => {
    if (!valid) return

    state.loading = true
    try {
      await useGroupRuleApi().saveOrUpdate({
        id: state.ruleForm.id,
        goods_id: state.ruleForm.goods_id,
        discount: Number(state.ruleForm.discount),
        people: state.ruleForm.people,
        end_time: state.ruleForm.end_time,
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
.group-rule-dialog {
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

.group-rule-form {
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
  :deep(.el-date-editor.el-input__wrapper) {
    height: 38px;
    border-radius: 4px;
  }
}

.group-rule-number {
  width: 100% !important;

  :deep(.el-input__inner) {
    text-align: left;
  }
}

.group-rule-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  .group-rule-cancel {
    width: 76px;
    height: 36px;
    border-radius: 4px;
  }

  .group-rule-confirm {
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
  :global(.group-rule-dialog) {
    width: 92% !important;
  }
}
</style>
