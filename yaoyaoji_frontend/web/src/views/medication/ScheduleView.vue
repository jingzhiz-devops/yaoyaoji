<template>
  <div class="schedule-view">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>📅 用药提醒</h2>
      <el-button type="primary" @click="dialogVisible = true">创建提醒</el-button>
    </div>

      <div v-if="upcomingReminders.length > 0" class="reminder-banner">
        <div class="reminder-content">
          <span class="reminder-icon">⏰</span>
          <span class="reminder-text">
            5分钟内即将服用：
            <span v-for="item in upcomingReminders" :key="item.key" class="reminder-item">
              {{ item.name }}（{{ item.time.substring(0, 5) }}）
            </span>
          </span>
        </div>
      </div>
    <div class="schedule-list" style="margin-top: 20px">
      <el-table :data="schedules" style="width: 100%">
        <el-table-column prop="medication.custom_name" label="药品名称" width="200">
          <template #default="{ row }">
            {{ row.user_medication?.custom_name || row.user_medication?.medicine?.name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column label="频率" width="120">
          <template #default="{ row }">
            {{ formatFrequency(row.frequency) }}
          </template>
        </el-table-column>
        <el-table-column prop="scheduled_times" label="服药时间" width="200">
          <template #default="{ row }">
            <div v-if="Array.isArray(row.scheduled_times)" style="display: flex; flex-wrap: wrap; gap: 5px;">
              <el-tag v-for="(time, index) in row.scheduled_times" :key="index" size="small" type="info">
                {{ time.substring(0, 5) }}
              </el-tag>
            </div>
            <span v-else>{{ row.scheduled_times }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="dose" label="剂量" width="120" />
        <el-table-column prop="start_date" label="开始日期" width="120" />
        <el-table-column prop="end_date" label="结束日期" width="120" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">U</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">D</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="schedules.length === 0" description="暂无用药提醒，快去创建吧！" />
    </div>

    <!-- 创建/编辑计划对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用药提醒' : '创建用药提醒'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="选择药品">
          <el-select v-model="form.user_medication_id" placeholder="请选择药品" style="width: 100%">
            <el-option
              v-for="med in medications"
              :key="med.id"
              :label="med.custom_name || med.medicine.name"
              :value="med.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="频率">
          <el-select v-model="form.frequency" placeholder="请选择频率" style="width: 100%" @change="handleFrequencyChange">
            <el-option label="每天一次" value="once_daily" />
            <el-option label="每天两次" value="twice_daily" />
            <el-option label="每天三次" value="three_times_daily" />
            <el-option label="每天四次" value="four_times_daily" />
          </el-select>
        </el-form-item>
        <el-form-item label="服药时间">
          <div v-for="(time, index) in form.scheduled_times" :key="index" style="margin-bottom: 10px">
            <el-time-picker
              v-model="form.scheduled_times[index]"
              :placeholder="`选择第${index + 1}次服药时间`"
              format="HH:mm"
              value-format="HH:mm:00"
              style="width: 100%"
            />
          </div>
        </el-form-item>
        <el-form-item label="剂量">
          <el-input v-model="form.dose" placeholder="例如：1片、10ml" />
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker v-model="form.start_date" type="date" placeholder="选择开始日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker v-model="form.end_date" type="date" placeholder="选择结束日期(可选)" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" placeholder="用药备注(可选)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleAPI, userMedicationAPI } from '@/api'
import dayjs from 'dayjs'

const dialogVisible = ref(false)
const schedules = ref<any[]>([])
const medications = ref<any[]>([])
const editingId = ref<number | null>(null)

// 提前5分钟提醒：用于计算5分钟内即将服用的药物
const nowTs = ref(Date.now())
let reminderTimer: any = null

const upcomingReminders = computed(() => {
  const now = new Date(nowTs.value)
  const currentMinutes = now.getHours() * 60 + now.getMinutes()
  const today = new Date(now)
  today.setHours(0, 0, 0, 0)

  const result: Array<{ key: string; name: string; time: string }> = []
  schedules.value.forEach((s: any) => {
    // 仅在计划日期范围内提醒
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
        // 提前5分钟提醒窗口：0 <= delta <= 5
        if (delta >= 0 && delta <= 5) {
          result.push({ key: `${s.id}-${idx}-${t}`, name, time: t })
        }
      })
    }
  })
  return result
})

// 语音提醒（Web Speech API）：在提醒窗口内播报提示语
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
      // 5分钟后允许再次播报该条提醒
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
  // 定时刷新当前时间，驱动提醒横幅自动更新
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
    const errorMsg = error.response?.data?.detail || '获取用药提醒失败'
    ElMessage.error(errorMsg)
  }
}

async function fetchMedications() {
  try {
    const data: any = await userMedicationAPI.list()
    medications.value = data
  } catch (error: any) {
    console.error('获取药品列表失败:', error)
    const errorMsg = error.response?.data?.detail || '获取药品列表失败'
    ElMessage.error(errorMsg)
  }
}

async function handleSubmit() {
  if (!form.user_medication_id || !form.frequency || !form.dose || form.scheduled_times.length === 0) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  // 验证时间数量与频率匹配
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
    const errorMsg = error.response?.data?.detail || error.message || '操作失败，请检查网络连接'
    ElMessage.error(errorMsg)
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

async function handleCreate() {
  if (!form.user_medication_id || !form.frequency || !form.dose || form.scheduled_times.length === 0) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  // 验证时间数量与频率匹配
  const expectedCount = getExpectedTimeCount(form.frequency)
  if (form.scheduled_times.length !== expectedCount) {
    ElMessage.warning(`频率"${formatFrequency(form.frequency)}"需要${expectedCount}个时间点`)
    return
  }

  try {
    await scheduleAPI.create({
      user_medication_id: form.user_medication_id,
      frequency: form.frequency,
      scheduled_times: form.scheduled_times,
      dose: form.dose,
      start_date: dayjs(form.start_date).format('YYYY-MM-DD'),
      end_date: form.end_date ? dayjs(form.end_date).format('YYYY-MM-DD') : null,
      notes: form.notes || null
    })
    ElMessage.success('创建成功')
    dialogVisible.value = false
    await fetchSchedules()
    resetForm()
  } catch (error: any) {
    console.error('创建用药提醒失败:', error)
    const errorMsg = error.response?.data?.detail || error.message || '创建失败，请检查网络连接'
    ElMessage.error(errorMsg)
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除这个提醒吗？', '提示', {
    type: 'warning'
  })

  try {
    await scheduleAPI.delete(id)
    ElMessage.success('删除成功')
    await fetchSchedules()
  } catch (error: any) {
    console.error('删除失败:', error)
    const errorMsg = error.response?.data?.detail || '删除失败'
    ElMessage.error(errorMsg)
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
  // 根据频率初始化时间数组
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
</script>

<style scoped>
.schedule-view {
  width: 100%;
  height: 100%;
}

.schedule-list {
  margin-top: 20px;
}
.schedule-list {
  margin-top: 20px;
}

/* 显眼提醒横幅样式 */
.reminder-banner {
  background: #fffbe6; /* 温暖的提示色 */
  border: 1px solid #ffe58f;
  border-radius: 10px;
  padding: 12px 16px;
  margin-top: 10px;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.reminder-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reminder-icon {
  font-size: 22px;
  animation: swing 1s ease-in-out infinite;
  display: inline-block;
}

.reminder-text {
  font-size: 14px;
  color: #ad6800;
  font-weight: 600;
}

.reminder-item {
  margin-left: 8px;
  color: #d48806;
}

@keyframes swing {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(12deg); }
  50% { transform: rotate(0deg); }
  75% { transform: rotate(-12deg); }
  100% { transform: rotate(0deg); }
}
</style>
