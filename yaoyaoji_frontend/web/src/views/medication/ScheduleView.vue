<template>
  <div class="schedule-view-container">
    <div class="action-bar">
      <el-button type="primary" size="large" @click="dialogVisible = true" class="add-btn">
        <el-icon><Plus /></el-icon>
        创建提醒
      </el-button>
    </div>

    <div v-if="upcomingReminders.length > 0" class="reminder-banner">
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon class="swing-icon"><AlarmClock /></el-icon>
        </div>
        <div class="banner-text">
          <span class="banner-title">即将服药提醒</span>
          <div class="banner-items">
            <span v-for="item in upcomingReminders" :key="item.key" class="reminder-tag">
              {{ item.name }} {{ item.time.substring(0, 5) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="schedule-list">
      <el-card v-for="row in schedules" :key="row.id" class="schedule-card" shadow="hover">
        <div class="schedule-card-content">
          <div class="schedule-info">
            <div class="medicine-name-row">
              <h3>{{ row.user_medication?.custom_name || row.user_medication?.medicine?.name || '未知药品' }}</h3>
              <el-tag size="small" effect="plain">{{ formatFrequency(row.frequency) }}</el-tag>
            </div>
            <div class="schedule-details">
              <div class="detail-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ row.start_date }} <span v-if="row.end_date">至 {{ row.end_date }}</span></span>
              </div>
              <div class="detail-item">
                <el-icon><Dish /></el-icon>
                <span>{{ row.dose }}</span>
              </div>
            </div>
          </div>
          
          <div class="schedule-times">
            <div class="time-label">服药时间</div>
            <div class="time-tags">
              <el-tag 
                v-for="(time, index) in row.scheduled_times" 
                :key="index" 
                effect="light"
                :type="getTimeStatus(time)"
              >
                {{ time.substring(0, 5) }}
              </el-tag>
            </div>
          </div>

          <div class="schedule-actions">
            <el-button circle type="primary" plain @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button circle type="danger" plain @click="handleDelete(row.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </el-card>

      <el-empty v-if="schedules.length === 0" description="暂无用药提醒，快去创建吧！" :image-size="200">
        <el-button type="primary" @click="dialogVisible = true">立即创建</el-button>
      </el-empty>
    </div>

    <!-- 创建/编辑计划对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingId ? '编辑用药提醒' : '创建用药提醒'" 
      width="600px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-width="100px" label-position="top">
        <el-form-item label="选择药品" required>
          <el-select v-model="form.user_medication_id" placeholder="请选择药品" style="width: 100%" size="large">
            <el-option
              v-for="med in medications"
              :key="med.id"
              :label="med.custom_name || med.medicine.name"
              :value="med.id"
            />
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="服药频率" required>
              <el-select v-model="form.frequency" placeholder="请选择频率" style="width: 100%" @change="handleFrequencyChange">
                <el-option label="每天一次" value="once_daily" />
                <el-option label="每天两次" value="twice_daily" />
                <el-option label="每天三次" value="three_times_daily" />
                <el-option label="每天四次" value="four_times_daily" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单次剂量" required>
              <el-input v-model="form.dose" placeholder="例如：1片、10ml" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="服药时间" required>
          <div class="time-picker-grid">
            <div v-for="(time, index) in form.scheduled_times" :key="index" class="time-picker-item">
              <span class="time-index">第 {{ index + 1 }} 次</span>
              <el-time-picker
                v-model="form.scheduled_times[index]"
                placeholder="选择时间"
                format="HH:mm"
                value-format="HH:mm:00"
                style="width: 100%"
              />
            </div>
          </div>
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" required>
              <el-date-picker v-model="form.start_date" type="date" placeholder="选择开始日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.end_date" type="date" placeholder="可选，留空则长期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="例如：饭后服用、忌辛辣等(可选)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleAPI, userMedicationAPI } from '@/api'
import { Plus, AlarmClock, Calendar, Dish, Edit, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const dialogVisible = ref(false)
const schedules = ref<any[]>([])
const medications = ref<any[]>([])
const editingId = ref<number | null>(null)

// 提前5分钟提醒
const nowTs = ref(Date.now())
let reminderTimer: any = null

const upcomingReminders = computed(() => {
  const now = new Date(nowTs.value)
  const currentMinutes = now.getHours() * 60 + now.getMinutes()
  const today = new Date(now)
  today.setHours(0, 0, 0, 0)

  const result: Array<{ key: string; name: string; time: string }> = []
  schedules.value.forEach((s: any) => {
    const start = new Date(s.start_date)
    start.setHours(0, 0, 0, 0)
    const end = s.end_date ? new Date(s.end_date) : null
    if (end) end.setHours(0, 0, 0, 0)
    const activeToday = start <= today && (!end || end >= today)
    if (!activeToday) return

    const name = s.user_medication?.custom_name || s.user_medication?.medicine?.name || '未知'
    if (Array.isArray(s.scheduled_times)) {
      s.scheduled_times.forEach((t: string, idx: number) => {
        const [h, m] = t.split(':').map(Number)
        const minutes = h * 60 + m
        const delta = minutes - currentMinutes
        if (delta >= 0 && delta <= 5) {
          result.push({ key: `${s.id}-${idx}-${t}`, name, time: t })
        }
      })
    }
  })
  return result
})

// 语音提醒
const announcedKeys = new Set<string>()
function speakGentle(text: string, repeats = 3) {
  if ('speechSynthesis' in window) {
    const voices = window.speechSynthesis.getVoices()
    const zhVoice = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('zh')) || null
    for (let i = 0; i < repeats; i++) {
      const utter = new SpeechSynthesisUtterance(text)
      utter.lang = 'zh-CN'
      utter.rate = 0.95
      utter.pitch = 1.15
      utter.volume = 0.9
      if (zhVoice) utter.voice = zhVoice
      window.speechSynthesis.speak(utter)
    }
  }
}

watch(upcomingReminders, (list) => {
  list.forEach(item => {
    if (!announcedKeys.has(item.key)) {
      speakGentle(`主人，现在是北京时间 ${dayjs().format('HH:mm')}，该吃 ${item.name} 啦`, 3)
      announcedKeys.add(item.key)
      setTimeout(() => announcedKeys.delete(item.key), 5 * 60 * 1000)
    }
  })
})

const form = reactive({
  user_medication_id: null,
  frequency: '',
  scheduled_times: [] as string[],
  dose: '',
  start_date: new Date(),
  end_date: null,
  notes: ''
})

onMounted(async () => {
  await fetchSchedules()
  await fetchMedications()
  reminderTimer = setInterval(() => {
    nowTs.value = Date.now()
  }, 15000)
})

onUnmounted(() => {
  if (reminderTimer) clearInterval(reminderTimer)
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
  }
})

async function fetchSchedules() {
  try {
    const data: any = await scheduleAPI.list()
    schedules.value = data
  } catch (error: any) {
    console.error('获取用药提醒失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取用药提醒失败')
  }
}

async function fetchMedications() {
  try {
    const data: any = await userMedicationAPI.list()
    medications.value = data
  } catch (error: any) {
    console.error('获取药品列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取药品列表失败')
  }
}

async function handleSubmit() {
  if (!form.user_medication_id || !form.frequency || !form.dose || form.scheduled_times.length === 0) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  const expectedCount = getExpectedTimeCount(form.frequency)
  if (form.scheduled_times.length !== expectedCount) {
    ElMessage.warning(`频率"${formatFrequency(form.frequency)}"需要${expectedCount}个时间点`)
    return
  }

  try {
    const data = {
      user_medication_id: form.user_medication_id,
      frequency: form.frequency,
      scheduled_times: form.scheduled_times,
      dose: form.dose,
      start_date: dayjs(form.start_date).format('YYYY-MM-DD'),
      end_date: form.end_date ? dayjs(form.end_date).format('YYYY-MM-DD') : null,
      notes: form.notes || null
    }

    if (editingId.value) {
      await scheduleAPI.update(editingId.value, data)
      ElMessage.success('修改成功')
    } else {
      await scheduleAPI.create(data)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    await fetchSchedules()
    resetForm()
  } catch (error: any) {
    console.error('操作失败:', error)
    ElMessage.error(error.response?.data?.detail || error.message || '操作失败')
  }
}

function handleEdit(row: any) {
  editingId.value = row.id
  form.user_medication_id = row.user_medication_id
  form.frequency = row.frequency
  form.scheduled_times = [...row.scheduled_times]
  form.dose = row.dose
  form.start_date = new Date(row.start_date)
  form.end_date = row.end_date ? new Date(row.end_date) : null
  form.notes = row.notes || ''
  dialogVisible.value = true
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个提醒吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    await scheduleAPI.delete(id)
    ElMessage.success('删除成功')
    await fetchSchedules()
  } catch (error) {
    // Cancelled
  }
}

function resetForm() {
  editingId.value = null
  form.user_medication_id = null
  form.frequency = ''
  form.scheduled_times = []
  form.dose = ''
  form.start_date = new Date()
  form.end_date = null
  form.notes = ''
}

function handleFrequencyChange(frequency: string) {
  const count = getExpectedTimeCount(frequency)
  form.scheduled_times = new Array(count).fill('')
}

function getExpectedTimeCount(frequency: string): number {
  const countMap: Record<string, number> = {
    'once_daily': 1,
    'twice_daily': 2,
    'three_times_daily': 3,
    'four_times_daily': 4
  }
  return countMap[frequency] || 1
}

function formatFrequency(freq: string) {
  const freqMap: Record<string, string> = {
    'once_daily': '每天一次',
    'twice_daily': '每天两次',
    'three_times_daily': '每天三次',
    'four_times_daily': '每天四次'
  }
  return freqMap[freq] || freq
}

function getTimeStatus(timeStr: string): string {
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes()
  const [hours, minutes] = timeStr.split(':').map(Number)
  const scheduleTime = hours * 60 + minutes
  
  if (scheduleTime < currentTime) {
    return 'info'
  } else {
    return 'primary'
  }
}
</script>

<style scoped>
.schedule-view-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-main);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 0;
}

/* Action Bar */
.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 32px;
}

.add-btn {
  box-shadow: var(--shadow-sm);
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 500;
}

/* Reminder Banner */
.reminder-banner {
  background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
  border-radius: var(--radius-md);
  padding: 16px 24px;
  margin-bottom: 32px;
  box-shadow: var(--shadow-sm);
  border: 1px solid #FED7AA;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.banner-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-warning);
  font-size: 20px;
  box-shadow: var(--shadow-sm);
}

.swing-icon {
  animation: swing 1s ease-in-out infinite;
}

.banner-text {
  flex: 1;
}

.banner-title {
  font-weight: 600;
  color: #9A3412;
  margin-right: 12px;
}

.banner-items {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
}

.reminder-tag {
  background-color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  color: #C2410C;
  font-weight: 500;
}

/* Schedule List */
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.schedule-card {
  border: none;
  border-radius: var(--radius-md);
  transition: transform 0.2s;
}

.schedule-card:hover {
  transform: translateX(4px);
}

.schedule-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.schedule-info {
  flex: 2;
}

.medicine-name-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.medicine-name-row h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
}

.schedule-details {
  display: flex;
  gap: 24px;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.schedule-times {
  flex: 2;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.time-label {
  font-size: 12px;
  color: var(--color-text-light);
}

.time-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.schedule-actions {
  display: flex;
  gap: 8px;
}

/* Time Picker Grid */
.time-picker-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.time-picker-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-index {
  font-size: 12px;
  color: var(--color-text-secondary);
}

@keyframes swing {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  50% { transform: rotate(0deg); }
  75% { transform: rotate(-12deg); }
  100% { transform: rotate(0deg); }
}
</style>
