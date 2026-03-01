<template>
  <div class="complication-manager">
    <div class="header-row">
      <el-select v-model="filterSeverity" placeholder="按严重程度筛选" clearable style="width: 160px">
        <el-option label="轻度" value="mild" />
        <el-option label="中度" value="moderate" />
        <el-option label="重度" value="severe" />
      </el-select>
      <el-button type="primary" @click="showAdd = true">
        <el-icon><Plus /></el-icon>
        记录并发症
      </el-button>
    </div>

    <!-- 时间线 -->
    <el-timeline v-if="complications.length > 0" style="margin-top: 20px">
      <el-timeline-item
        v-for="c in complications"
        :key="c.id"
        :timestamp="c.discovered_date"
        :type="getSeverityColor(c.severity)"
        :hollow="c.is_resolved"
      >
        <div class="complication-item">
          <div class="item-header">
            <span class="type">{{ c.complication_type }}</span>
            <el-tag :type="getSeverityTag(c.severity)" size="small">{{ getSeverityText(c.severity) }}</el-tag>
            <el-tag v-if="c.is_resolved" type="success" size="small">已解决</el-tag>
          </div>
          <p v-if="c.symptoms" class="symptoms">症状：{{ c.symptoms }}</p>
          <p v-if="c.treatment" class="treatment">治疗：{{ c.treatment }}</p>
          <div class="item-actions">
            <el-button size="small" text @click="editComplication(c)">编辑</el-button>
            <el-button v-if="!c.is_resolved" size="small" text type="success" @click="resolveComplication(c)">标记已解决</el-button>
          </div>
        </div>
      </el-timeline-item>
    </el-timeline>
    <el-empty v-else description="暂无并发症记录" />

    <!-- 添加对话框 -->
    <el-dialog v-model="showAdd" title="记录并发症" width="500px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="并发症类型" required>
          <el-input v-model="form.complication_type" placeholder="如：糖尿病视网膜病变" />
        </el-form-item>
        <el-form-item label="严重程度" required>
          <el-radio-group v-model="form.severity">
            <el-radio value="mild">轻度</el-radio>
            <el-radio value="moderate">中度</el-radio>
            <el-radio value="severe">重度</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="发现日期" required>
          <el-date-picker v-model="form.discovered_date" type="date" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="症状描述">
          <el-input v-model="form.symptoms" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="治疗方案">
          <el-input v-model="form.treatment" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAdd = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { complicationAPI } from '@/api/chronic-disease'
import type { ComplicationRecord } from '@/types'

const props = defineProps<{ diseaseId: number }>()

const complications = ref<ComplicationRecord[]>([])
const filterSeverity = ref('')
const showAdd = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)

const form = ref({
  complication_type: '',
  severity: 'mild',
  discovered_date: '',
  symptoms: '',
  treatment: ''
})

const loadData = async () => {
  try {
    const res = await complicationAPI.list(props.diseaseId, {
      severity: filterSeverity.value || undefined
    })
    complications.value = (res as any) || []
  } catch { /* empty */ }
}

watch(filterSeverity, loadData)

const handleSave = async () => {
  if (!form.value.complication_type || !form.value.discovered_date) {
    ElMessage.warning('请填写必要信息')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await complicationAPI.update(editingId.value, form.value)
    } else {
      await complicationAPI.create(props.diseaseId, form.value)
    }
    ElMessage.success('保存成功')
    showAdd.value = false
    editingId.value = null
    resetForm()
    loadData()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const editComplication = (c: ComplicationRecord) => {
  editingId.value = c.id
  form.value = {
    complication_type: c.complication_type,
    severity: c.severity,
    discovered_date: c.discovered_date,
    symptoms: c.symptoms || '',
    treatment: c.treatment || ''
  }
  showAdd.value = true
}

const resolveComplication = async (c: ComplicationRecord) => {
  try {
    await complicationAPI.update(c.id, {
      is_resolved: true,
      resolved_date: new Date().toISOString().split('T')[0]
    })
    ElMessage.success('已标记为已解决')
    loadData()
  } catch {
    ElMessage.error('操作失败')
  }
}

const resetForm = () => {
  form.value = { complication_type: '', severity: 'mild', discovered_date: '', symptoms: '', treatment: '' }
}

const getSeverityColor = (s: string) => ({ mild: 'primary', moderate: 'warning', severe: 'danger' }[s] || 'primary') as any
const getSeverityTag = (s: string) => ({ mild: 'info', moderate: 'warning', severe: 'danger' }[s] || 'info') as any
const getSeverityText = (s: string) => ({ mild: '轻度', moderate: '中度', severe: '重度' }[s] || s)

onMounted(loadData)
</script>

<style scoped lang="scss">
.header-row { display: flex; justify-content: space-between; align-items: center; }
.complication-item {
  .item-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
    .type { font-weight: 600; font-size: 15px; }
  }
  .symptoms, .treatment { margin: 4px 0; color: #606266; font-size: 14px; }
  .item-actions { margin-top: 8px; }
}
</style>
