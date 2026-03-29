<template>
  <div class="schedule-view-container">
    <div class="action-bar">
      <el-button type="primary" size="large" @click="dialogVisible = true" class="add-btn">
        <el-icon><Plus /></el-icon>
        创建提醒
      </el-button>
      <el-button size="large" @click="showFeishuConfig" class="feishu-config-btn">
        <span class="feishu-logo-btn">飞书</span>
        通知设置
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
              <span>{{ item.name }} {{ item.time.substring(0, 5) }}</span>
              <span v-if="item.notes" class="reminder-notes">💡 {{ item.notes }}</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="schedule-list">
      <el-card v-for="row in schedules" :key="row.id" class="schedule-card" shadow="hover" :class="{ 'replenish-reminder': needsReplenishReminder(row) }">
        <div class="schedule-card-content">
          <div class="schedule-info">
            <div class="medicine-name-row">
              <h3>{{ row.user_medication?.custom_name || row.user_medication?.medicine?.name || '未知药品' }}</h3>
            </div>
            <div class="schedule-details">
              <div class="detail-item">
                <el-icon><Calendar /></el-icon>
                <span>{{ row.start_date }} <span v-if="row.end_date">至 {{ row.end_date }}</span></span>
              </div>
              <div class="detail-item">
                <el-icon><Timer /></el-icon>
                <span>{{ formatFrequency(row.frequency) }}</span>
                <el-icon><Dish /></el-icon>
                <span>{{ row.dose }}</span>
              </div>
              <div v-if="row.purchase_date && row.therapy_duration" class="detail-item" style="color: #e6a23c;">
                <span>🛒 {{ row.purchase_date }} 购入，{{ row.therapy_duration }}天疗程</span>
              </div>
              <div class="detail-item times-inline">
                <span class="time-label-inline">服药时间</span>
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
          </div>

          <div class="schedule-actions">
            <el-button circle type="primary" plain @click.stop="handleEdit(row)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button circle type="danger" plain @click.stop="handleDelete(row.id)">
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

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="买入日期">
              <el-date-picker v-model="form.purchase_date" type="date" placeholder="药品买入日期" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="疗程天数">
              <el-input-number v-model="form.therapy_duration" :min="1" :max="365" placeholder="吃药天数" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="提前提醒天数">
              <el-input-number v-model="form.remind_advance_days" :min="1" :max="30" placeholder="提前提醒备药" style="width: 100%" />
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

    <!-- 飞书通知配置对话框 -->
    <el-dialog v-model="feishuDialogVisible" title="飞书通知设置" width="500px" class="custom-dialog">
      <div class="feishu-config-content">
        <div class="feishu-status">
          <span class="status-label">当前状态：</span>
          <span v-if="userStore.user?.feishu_webhook" class="status-value configured">
            ✓ 已配置
          </span>
          <span v-else class="status-value not-configured">
            ✗ 未配置
          </span>
        </div>
        
        <div class="feishu-help">
          <p><strong>如何获取飞书机器人 Webhook？</strong></p>
          <ol>
            <li>在飞书群中点击「设置」→「群机器人」→「添加机器人」</li>
            <li>选择「自定义机器人」，输入机器人名称</li>
            <li>复制生成的 Webhook 地址粘贴到下方</li>
          </ol>
        </div>
        
        <el-form :model="feishuForm" :rules="feishuRules" ref="feishuFormRef" label-position="top">
          <el-form-item label="Webhook 地址" prop="feishu_webhook">
            <el-input 
              v-model="feishuForm.feishu_webhook" 
              placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..." 
              size="large"
              clearable
            />
          </el-form-item>
          <div class="form-tip">配置后，用药提醒将通过机器人发送到对应的飞书群</div>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="feishuDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveFeishuWebhook" :loading="feishuSubmitting">保存配置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleAPI, userMedicationAPI, feishuAPI, authAPI } from '@/api'
import { Plus, AlarmClock, Calendar, Dish, Edit, Delete, Timer } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const userStore = useUserStore()

const dialogVisible = ref(false)
const schedules = ref<any[]>([])
const medications = ref<any[]>([])
const editingId = ref<number | null>(null)

// 飞书配置相关
const feishuDialogVisible = ref(false)
const feishuFormRef = ref()
const feishuSubmitting = ref(false)
const feishuForm = ref({
  feishu_webhook: ''
})
const feishuRules = {
  feishu_webhook: [
    { 
      pattern: /^https:\/\/open\.feishu\.cn\/open-apis\/bot\//, 
      message: '请输入正确的飞书Webhook地址', 
      trigger: 'blur' 
    }
  ]
}

// 提前5分钟提醒
const nowTs = ref(Date.now())
let reminderTimer: any = null

const upcomingReminders = computed(() => {
  const now = new Date(nowTs.value)
  const currentMinutes = now.getHours() * 60 + now.getMinutes()
  const today = new Date(now)
  today.setHours(0, 0, 0, 0)

  const result: Array<{ key: string; name: string; time: string; notes?: string }> = []
  schedules.value.forEach((s: any) => {
    const start = new Date(s.start_date)
    start.setHours(0, 0, 0, 0)
    const end = s.end_date ? new Date(s.end_date) : null
    if (end) end.setHours(0, 0, 0, 0)
    const activeToday = start <= today && (!end || end >= today)
    if (!activeToday) return

    const name = s.user_medication?.custom_name || s.user_medication?.medicine?.name || '未知'
    const medicationNotes = s.user_medication?.notes || ''
    if (Array.isArray(s.scheduled_times)) {
      s.scheduled_times.forEach((t: string, idx: number) => {
        const [h, m] = t.split(':').map(Number)
        const minutes = h * 60 + m
        const delta = minutes - currentMinutes
        if (delta >= 0 && delta <= 5) {
          result.push({ key: `${s.id}-${idx}-${t}`, name, time: t, notes: medicationNotes })
        }
      })
    }
    
    // 添加备药提醒（疗程结束前 N 天）
    if (s.purchase_date && s.therapy_duration && s.remind_advance_days) {
      const purchaseDate = new Date(s.purchase_date)
      const endOfTherapy = new Date(purchaseDate)
      endOfTherapy.setDate(endOfTherapy.getDate() + s.therapy_duration)
      const reminderDate = new Date(endOfTherapy)
      reminderDate.setDate(reminderDate.getDate() - s.remind_advance_days)
      reminderDate.setHours(0, 0, 0, 0)
      
      // 应用到每一次服药时间
      if (reminderDate <= today && today < endOfTherapy) {
        const firstTime = s.scheduled_times[0]
        const [h, m] = firstTime.split(':').map(Number)
        const minutes = h * 60 + m
        const delta = minutes - currentMinutes
        // 每天的第一次服药时间提醒备药
        if (delta >= 0 && delta <= 5) {
          result.push({ key: `${s.id}-reminder-${firstTime}`, name: `🚨备${name}`, time: firstTime, notes: medicationNotes })
        }
      }
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
      let speechText = `主人，现在是北京时间 ${dayjs().format('HH:mm')}，该吃 ${item.name} 啦`
      if (item.notes) {
        speechText += `。温馨提示：${item.notes}`
      }
      speakGentle(speechText, 3)
      announcedKeys.add(item.key)
      setTimeout(() => announcedKeys.delete(item.key), 5 * 60 * 1000)
      
      // 同时发送飞书通知
      feishuAPI.sendReminder({
        medicine_name: item.name,
        reminder_time: item.time.substring(0, 5),
        notes: item.notes || ''
      }).catch((err: any) => {
        console.warn('飞书通知发送失败:', err)
      })
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
  purchase_date: null,
  therapy_duration: null,
  remind_advance_days: 5,
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

// 显示飞书配置对话框
function showFeishuConfig() {
  feishuForm.value = {
    feishu_webhook: userStore.user?.feishu_webhook || ''
  }
  feishuDialogVisible.value = true
}

// 保存飞书 Webhook
async function handleSaveFeishuWebhook() {
  await feishuFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      feishuSubmitting.value = true
      try {
        const webhook = feishuForm.value.feishu_webhook?.trim() || ''
        await authAPI.updateProfile({ feishu_webhook: webhook || undefined })
        await userStore.fetchUserInfo()
        ElMessage.success('飞书通知配置成功')
        feishuDialogVisible.value = false
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '配置失败')
      } finally {
        feishuSubmitting.value = false
      }
    }
  })
}

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
      purchase_date: form.purchase_date ? dayjs(form.purchase_date).format('YYYY-MM-DD') : null,
      therapy_duration: form.therapy_duration || null,
      remind_advance_days: form.remind_advance_days || 5,
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
  form.purchase_date = row.purchase_date ? new Date(row.purchase_date) : null
  form.therapy_duration = row.therapy_duration || null
  form.remind_advance_days = row.remind_advance_days || 5
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
  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close') {
      console.error('删除失败:', error)
      
      // 更详细的错误信息
      let errorMessage = '删除失败'
      if (error.response) {
        // 服务器返回了响应
        errorMessage += `：${error.response.data?.detail || error.response.data?.message || error.response.statusText || '服务器错误'}`
      } else if (error.request) {
        // 请求已发出但没有收到响应（网络错误）
        errorMessage += '：网络错误，请检查后端服务是否正常运行'
      } else {
        // 其他错误
        errorMessage += `：${error.message || '未知错误'}`
      }
      
      ElMessage.error(errorMessage)
    }
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
  form.purchase_date = null
  form.therapy_duration = null
  form.remind_advance_days = 5
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

// 检查是否需要备药提醒
function needsReplenishReminder(schedule: any): boolean {
  const advanceDays = schedule.remind_advance_days || 5

  // 优先用 end_date 判断
  if (schedule.end_date) {
    const endDate = new Date(schedule.end_date)
    endDate.setHours(0, 0, 0, 0)
    const reminderDate = new Date(endDate)
    reminderDate.setDate(reminderDate.getDate() - advanceDays)
    reminderDate.setHours(0, 0, 0, 0)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return reminderDate <= today && today < endDate
  }

  // 没有 end_date 时，用 purchase_date + therapy_duration 兜底
  if (!schedule.purchase_date || !schedule.therapy_duration) {
    return false
  }
  const purchaseDate = new Date(schedule.purchase_date)
  const endOfTherapy = new Date(purchaseDate)
  endOfTherapy.setDate(endOfTherapy.getDate() + schedule.therapy_duration)
  const reminderDate = new Date(endOfTherapy)
  reminderDate.setDate(reminderDate.getDate() - advanceDays)
  reminderDate.setHours(0, 0, 0, 0)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return reminderDate <= today && today < endOfTherapy
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
  display: flex;
  flex-direction: column;
  gap: 4px;
  background-color: white;
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 13px;
  color: #C2410C;
  font-weight: 500;
}

.reminder-notes {
  display: block;
  font-size: 12px;
  color: #1F2937;
  font-weight: 400;
  padding-top: 2px;
  border-top: 1px solid #E5E7EB;
  margin-top: 2px;
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

/* 需要备药提醒的卡片 */
.schedule-card.replenish-reminder {
  border-left: 4px solid #e6a23c;
  background-color: #fef9f0;
}

.schedule-card-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.schedule-info {
  flex: 1;
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
  flex-wrap: nowrap;
  white-space: nowrap;
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
  padding-left: 5em;
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

.times-inline {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
}

.time-label-inline {
  font-size: 12px;
  color: var(--color-text-light);
  white-space: nowrap;
}

.schedule-actions {
  display: flex;
  gap: 8px;
  position: relative;
  z-index: 10;
  flex-shrink: 0;
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

/* 飞书配置按钮 */
.feishu-config-btn {
  background: linear-gradient(135deg, #3370ff 0%, #5e8dff 100%);
  border: none;
  color: white;
}

.feishu-config-btn:hover {
  background: linear-gradient(135deg, #2860e1 0%, #4d7de8 100%);
  color: white;
}

.feishu-logo-btn {
  font-weight: bold;
  margin-right: 4px;
}

/* 飞书配置对话框 */
.feishu-config-content {
  padding: 0 8px;
}

.feishu-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.status-label {
  color: var(--color-text-secondary);
}

.status-value {
  font-weight: 600;
}

.status-value.configured {
  color: #67c23a;
}

.status-value.not-configured {
  color: #f56c6c;
}

.feishu-help {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.feishu-help p {
  margin: 0 0 8px 0;
  color: var(--color-text-main);
}

.feishu-help ol {
  margin: 0;
  padding-left: 20px;
  color: var(--color-text-secondary);
  font-size: 13px;
  line-height: 1.8;
}

.form-tip {
  font-size: 12px;
  color: var(--color-text-light);
  margin-top: 4px;
}
</style>
