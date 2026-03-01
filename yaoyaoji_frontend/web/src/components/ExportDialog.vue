<template>
  <el-dialog v-model="visible" title="导出数据" width="500px" @close="$emit('update:modelValue', false)">
    <el-form :model="form" label-width="100px">
      <el-form-item label="导出格式">
        <el-radio-group v-model="form.format">
          <el-radio value="csv">CSV</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="日期范围">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>
      <el-form-item label="导出内容">
        <el-checkbox v-model="form.include_indicators">包含指标记录</el-checkbox>
        <el-checkbox v-model="form.include_complications">包含并发症</el-checkbox>
      </el-form-item>
    </el-form>

    <div v-if="exportStatus" class="export-status">
      <el-result v-if="exportStatus === 'completed'" icon="success" title="导出完成">
        <template #extra>
          <el-button type="primary" @click="handleDownload">下载文件</el-button>
        </template>
      </el-result>
      <div v-else-if="exportStatus === 'processing'" style="text-align: center; padding: 20px">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <p>正在导出...</p>
      </div>
    </div>

    <template #footer>
      <el-button @click="$emit('update:modelValue', false)">关闭</el-button>
      <el-button type="primary" :loading="exporting" :disabled="!!exportStatus" @click="handleExport">开始导出</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { exportAPI } from '@/api/chronic-disease'

const props = defineProps<{
  modelValue: boolean
  diseaseIds: number[]
}>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})

const exporting = ref(false)
const exportStatus = ref('')
const downloadUrl = ref('')

const form = ref({
  format: 'csv',
  dateRange: null as string[] | null,
  include_indicators: true,
  include_complications: false
})

const handleExport = async () => {
  if (props.diseaseIds.length === 0) {
    ElMessage.warning('请选择要导出的慢性病记录')
    return
  }
  exporting.value = true
  exportStatus.value = 'processing'
  try {
    const res = await exportAPI.create({
      disease_ids: props.diseaseIds,
      format: form.value.format,
      start_date: form.value.dateRange?.[0],
      end_date: form.value.dateRange?.[1],
      include_indicators: form.value.include_indicators,
      include_complications: form.value.include_complications
    }) as any
    exportStatus.value = res.status || 'completed'
    downloadUrl.value = res.download_url || ''
    if (exportStatus.value === 'completed') {
      ElMessage.success('导出完成')
    }
  } catch {
    ElMessage.error('导出失败')
    exportStatus.value = ''
  } finally {
    exporting.value = false
  }
}

const handleDownload = () => {
  if (downloadUrl.value) {
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
    window.open(`${baseUrl.replace('/api', '')}${downloadUrl.value}`, '_blank')
  }
}
</script>

<style scoped>
.export-status { margin-top: 16px; }
</style>
