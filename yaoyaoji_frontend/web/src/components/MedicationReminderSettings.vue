<template>
  <div class="medication-reminder-settings">
    <div class="header-row">
      <el-button type="primary" @click="showAdd = true">
        <el-icon><Plus /></el-icon>
        添加提醒
      </el-button>
    </div>

    <div v-if="reminders.length > 0" class="reminder-list">
      <div v-for="r in reminders" :key="r.id" class="reminder-item">
        <div class="reminder-info">
          <span class="time">⏰ {{ r.reminder_time }}</span>
          <span class="days">{{ formatDays(r.reminder_days) }}</span>
          <el-tag :type="r.status === 'active' ? 'success' : r.status === 'paused' ? 'warning' : 'info'" size="small">
            {{ statusText(r.status) }}
          </el-tag>
        </div>
        <div class="reminder-actions">
          <el-button v-if="r.status === 'active'" size="small" text @click="toggleStatus(r, 'paused')">暂停</el-button>
          <el-button v-if="r.status === 'paused'" size="small" text type="success" @click="toggleStatus(r, 'active')">恢复</el-button>
          <el-button size="small" text type="danger" @click="deleteReminder(r)">删除</el-button>
        </div>
      </div>
    </div>
    <el-empty v-else description="暂无用药提醒" />

    <el-dialog v-model="showAdd" title="添加用药提醒" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="提醒时间" required>
          <el-time-picker v-model="form.reminder_time" placeholder="选择时间" format="HH:mm" value-format="HH:mm:ss" />
        </el-form-item>
        <el-form-item label="提醒日期" required>
          <el-checkbox-group v-model="form.reminder_days">
            <el-checkbox v-for="(label, idx) in dayLabels" :key="idx" :value="idx">{{ label }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="提前提醒">
          <el-input-number v-model="form.advance_minutes" :min="0" :max="60" /> 分钟
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { medicationReminderAPI } from '@/api/chronic-disease'
import type { MedicationReminder } from '@/types'

const props = defineProps<{
  diseaseId: number
  userMedicationId?: number
}>()

const reminders = ref<MedicationReminder[]>([])
const showAdd = ref(false)
const saving = ref(false)
const dayLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

const form = ref({
  reminder_time: '',
  reminder_days: [1, 2, 3, 4, 5] as number[],
  advance_minutes: 0
})

const loadData = async () => {
  try {
    const res = await medicationReminderAPI.list({ disease_id: props.diseaseId })
    reminders.value = (res as any) || []
  } catch { /* empty */ }
}

const handleSave = async () => {
  if (!form.value.reminder_time || form.value.reminder_days.length === 0) {
    ElMessage.warning('请填写完整信息')
    return
  }
  saving.value = true
  try {
    await medicationReminderAPI.create({
      disease_id: props.diseaseId,
      user_medication_id: props.userMedicationId || undefined,
      reminder_time: form.value.reminder_time,
      reminder_days: form.value.reminder_days,
      advance_minutes: form.value.advance_minutes
    })
    ElMessage.success('提醒创建成功')
    showAdd.value = false
    form.value = { reminder_time: '', reminder_days: [1, 2, 3, 4, 5], advance_minutes: 0 }
    loadData()
  } catch (err: any) {
    const msg = err?.response?.data?.detail || '创建失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (r: MedicationReminder, status: string) => {
  try {
    await medicationReminderAPI.update(r.id, { status })
    ElMessage.success('操作成功')
    loadData()
  } catch {
    ElMessage.error('操作失败')
  }
}

const deleteReminder = async (r: MedicationReminder) => {
  try {
    await medicationReminderAPI.delete(r.id)
    ElMessage.success('删除成功')
    loadData()
  } catch {
    ElMessage.error('删除失败')
  }
}

const formatDays = (days: number[]) => days.map(d => dayLabels[d]).join('、')
const statusText = (s: string) => ({ active: '活跃', paused: '已暂停', completed: '已完成' }[s] || s)

onMounted(loadData)
</script>

<style scoped lang="scss">
.header-row { margin-bottom: 16px; }
.reminder-list { display: flex; flex-direction: column; gap: 12px; }
.reminder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  .reminder-info { display: flex; align-items: center; gap: 12px;
    .time { font-weight: 600; font-size: 16px; }
    .days { color: #909399; font-size: 13px; }
  }
}
</style>
