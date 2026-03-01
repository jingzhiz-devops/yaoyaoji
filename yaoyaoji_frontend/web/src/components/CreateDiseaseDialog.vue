<template>
  <el-dialog v-model="visible" title="添加慢性病" width="750px" @close="$emit('update:modelValue', false)">
    <div class="create-disease-dialog">
      <!-- 步骤1: 选择疾病类型 -->
      <div v-if="step === 1">
        <p style="margin-bottom: 16px; color: #606266">选择要管理的慢性病类型：</p>
        <DiseaseTypeSelector v-model="selectedType" />
      </div>

      <!-- 步骤2: 填写基本信息 -->
      <div v-if="step === 2">
        <el-form ref="formRef" :model="form" label-width="100px">
          <el-form-item label="疾病类型">
            <el-tag>{{ getTypeName(selectedType) }}</el-tag>
          </el-form-item>
          <el-form-item label="诊断日期">
            <el-date-picker v-model="form.diagnosis_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
          </el-form-item>
          <el-form-item label="诊疗医院">
            <el-input v-model="form.diagnosis_hospital" placeholder="可选" />
          </el-form-item>
          <el-form-item label="主治医生">
            <el-input v-model="form.diagnosis_doctor" placeholder="可选" />
          </el-form-item>
          <el-form-item label="治疗方案">
            <el-input v-model="form.current_treatment" type="textarea" rows="3" placeholder="描述当前治疗方案" />
          </el-form-item>
        </el-form>
      </div>
    </div>

    <template #footer>
      <el-button v-if="step === 2" @click="step = 1">上一步</el-button>
      <el-button @click="$emit('update:modelValue', false)">取消</el-button>
      <el-button v-if="step === 1" type="primary" :disabled="!selectedType" @click="step = 2">下一步</el-button>
      <el-button v-if="step === 2" type="primary" :loading="loading" @click="handleCreate">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import DiseaseTypeSelector from './DiseaseTypeSelector.vue'
import { createFromTemplate } from '@/api/chronic-disease'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'created': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const step = ref(1)
const selectedType = ref('')
const loading = ref(false)
const form = ref({
  diagnosis_date: '',
  diagnosis_hospital: '',
  diagnosis_doctor: '',
  current_treatment: ''
})

const getTypeName = (type: string) => {
  const map: Record<string, string> = { hypertension: '高血压', hyperlipidemia: '高血脂', diabetes: '糖尿病' }
  return map[type] || type
}

const handleCreate = async () => {
  loading.value = true
  try {
    await createFromTemplate({
      disease_type: selectedType.value,
      diagnosis_date: form.value.diagnosis_date || undefined,
      diagnosis_hospital: form.value.diagnosis_hospital || undefined,
      diagnosis_doctor: form.value.diagnosis_doctor || undefined,
      current_treatment: form.value.current_treatment || undefined
    })
    ElMessage.success('慢性病记录创建成功，已自动配置监控指标')
    emit('created')
    emit('update:modelValue', false)
    // Reset
    step.value = 1
    selectedType.value = ''
    form.value = { diagnosis_date: '', diagnosis_hospital: '', diagnosis_doctor: '', current_treatment: '' }
  } catch (error: any) {
    const msg = error?.response?.data?.detail || error?.message || '创建失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.create-disease-dialog { min-height: 200px; }
</style>
