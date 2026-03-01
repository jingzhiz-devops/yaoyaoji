<template>
  <div class="indicator-record-form">
    <div v-for="(record, index) in records" :key="index" class="record-row">
      <el-select v-model="record.indicator_id" placeholder="选择指标" style="width: 160px">
        <el-option
          v-for="ind in indicators"
          :key="ind.id"
          :label="`${ind.indicator_name} (${ind.unit || ''})`"
          :value="ind.id"
        />
      </el-select>

      <el-input-number
        v-model="record.value"
        :precision="1"
        placeholder="测量值"
        style="width: 140px"
      />

      <el-date-picker
        v-model="record.measurement_date"
        type="datetime"
        placeholder="测量时间"
        value-format="YYYY-MM-DDTHH:mm:ss"
        style="width: 200px"
      />

      <el-input v-model="record.notes" placeholder="备注" style="width: 140px" />

      <!-- 范围提示 -->
      <el-tag v-if="getWarning(record)" :type="getWarning(record)!.type" size="small">
        {{ getWarning(record)!.text }}
      </el-tag>

      <el-button v-if="records.length > 1" type="danger" text @click="records.splice(index, 1)">
        <el-icon><Delete /></el-icon>
      </el-button>
    </div>

    <div class="form-actions">
      <el-button @click="addRecord">
        <el-icon><Plus /></el-icon>
        添加更多记录
      </el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">提交记录</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import { batchRecordIndicators } from '@/api/chronic-disease'
import type { DiseaseIndicator } from '@/types'

const props = defineProps<{
  diseaseId: number
  indicators: DiseaseIndicator[]
}>()

const emit = defineEmits<{ submitted: [] }>()

interface RecordItem {
  indicator_id: number | null
  value: number | null
  measurement_date: string
  notes: string
}

const loading = ref(false)
const records = ref<RecordItem[]>([
  { indicator_id: null, value: null, measurement_date: new Date().toISOString().slice(0, 19), notes: '' }
])

const addRecord = () => {
  records.value.push({
    indicator_id: null,
    value: null,
    measurement_date: new Date().toISOString().slice(0, 19),
    notes: ''
  })
}

const getWarning = (record: RecordItem) => {
  if (!record.indicator_id || record.value === null) return null
  const ind = props.indicators.find(i => i.id === record.indicator_id)
  if (!ind) return null

  if (ind.normal_range_max !== undefined && ind.normal_range_max !== null && record.value > ind.normal_range_max) {
    return { type: 'danger' as const, text: `超出上限 ${ind.normal_range_max}${ind.unit || ''}` }
  }
  if (ind.normal_range_min !== undefined && ind.normal_range_min !== null && record.value < ind.normal_range_min) {
    return { type: 'warning' as const, text: `低于下限 ${ind.normal_range_min}${ind.unit || ''}` }
  }
  return { type: 'success' as const, text: '正常' }
}

const handleSubmit = async () => {
  const valid = records.value.filter(r => r.indicator_id && r.value !== null)
  if (valid.length === 0) {
    ElMessage.warning('请至少填写一条记录')
    return
  }

  loading.value = true
  try {
    const result = await batchRecordIndicators(
      props.diseaseId,
      valid.map(r => ({
        indicator_id: r.indicator_id!,
        value: r.value!,
        measurement_date: r.measurement_date,
        notes: r.notes || undefined
      }))
    )
    const alertCount = (result as any)?.alerts?.length || 0
    ElMessage.success(`成功记录 ${valid.length} 条数据${alertCount > 0 ? `，产生 ${alertCount} 条预警` : ''}`)
    emit('submitted')
    records.value = [{ indicator_id: null, value: null, measurement_date: new Date().toISOString().slice(0, 19), notes: '' }]
  } catch (error) {
    ElMessage.error('记录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.record-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}
</style>
