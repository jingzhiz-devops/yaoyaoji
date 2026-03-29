<template>
  <div class="dashboard">
    <div class="welcome-section">
      <div class="welcome-text">
        <h1 class="welcome-title">
          {{ greeting }}，{{ username }}
        </h1>
        <p class="welcome-subtitle">祝您身体健康，爱自己，笑口常开！</p>
      </div>
      <!-- 提醒推送区域 -->
      <div class="reminder-widget">
        <div class="reminder-scroll" v-if="reminderItems.length > 0">
          <div 
            v-for="item in reminderItems" 
            :key="item.key" 
            class="reminder-item" 
            :class="item.type"
            @click="handleReminderClick(item)"
          >
            <span class="reminder-icon">{{ item.icon }}</span>
            <div class="reminder-text">
              <span class="reminder-title">{{ item.title }}</span>
              <span class="reminder-desc">{{ item.desc }}</span>
            </div>
            <el-tag :type="item.tagType" size="small" effect="light" round>{{ item.tag }}</el-tag>
          </div>
        </div>
        <div v-else class="reminder-empty">
          <span>✅ 暂无待办提醒</span>
        </div>
      </div>

      <div class="calendar-widget">
        <div class="calendar-date">
          <div class="calendar-day">{{ currentDay }}</div>
          <div class="calendar-month-year">{{ currentMonthYear }}</div>
        </div>
        <div class="calendar-lunar">
          <div class="lunar-date">{{ lunarDateStr }}</div>
          <div class="lunar-festival" v-if="lunarFestival">{{ lunarFestival }}</div>
        </div>
      </div>
      <div class="user-widget">
        <div class="user-avatar-wrapper" @click="$router.push('/user-profile')">
          <img v-if="userStore.user?.avatar" :src="getUserAvatarUrl(userStore.user.avatar)" class="user-avatar-img" />
          <div v-else class="user-avatar-placeholder">
            {{ userStore.user?.username?.charAt(0).toUpperCase() }}
          </div>
        </div>
        <div class="user-info-text" @click="$router.push('/user-profile')">
          <span class="user-name">{{ userStore.user?.username }}</span>
        </div>
        <el-dropdown @command="handleUserCommand" trigger="click">
          <span class="user-role-dropdown">
            <span class="user-role">{{ userRoleText }}</span>
            <el-icon class="user-arrow"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人设置
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="stats-grid">
      <div class="stat-card primary">
        <div class="stat-icon-wrapper">
          <el-icon><Box /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">我的药品</div>
          <div class="stat-value">{{ medicationStore.myMedications.length }}<span class="unit">种</span></div>
        </div>
      </div>
      
      <div class="stat-card warning">
        <div class="stat-icon-wrapper">
          <el-icon><AlarmClock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">今日待服</div>
          <div class="stat-value">{{ todayPendingCount }}<span class="unit">次</span></div>
        </div>
      </div>
      
      <div class="stat-card success">
        <div class="stat-icon-wrapper">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">坚持服药</div>
          <div class="stat-value">
            <span v-if="medicationScheduleDays.length > 0">{{ Math.max(...medicationScheduleDays.map(i => i.days)) }}</span>
            <span v-else>0</span>
            <span class="unit">天</span>
          </div>
        </div>
      </div>
      
      <div class="stat-card info">
        <div class="stat-icon-wrapper">
          <el-icon><Notebook /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-label">症状记录</div>
          <div class="stat-value">{{ symptomCount }}<span class="unit">条</span></div>
        </div>
      </div>
    </div>

    <div class="main-grid">
      <!-- 左侧主要内容 -->
      <div class="left-column">
        <!-- 今日用药 -->
        <div class="content-card">
          <div class="card-header">
            <div class="header-title">
              <el-icon class="header-icon"><Timer /></el-icon>
              <span>今日用药提醒</span>
            </div>
            <el-button text type="primary" @click="$router.push('/schedules')">查看全部</el-button>
          </div>
          
          <div class="schedule-list" v-if="todaySchedules.length > 0">
            <div v-for="schedule in todaySchedules" :key="schedule.id" class="schedule-item">
              <div class="schedule-time-line">
                <div class="time-dot"></div>
                <div class="time-line"></div>
              </div>
              <div class="schedule-content">
                <div class="medicine-info">
                  <h4>{{ schedule.user_medication?.custom_name || schedule.user_medication?.medicine?.name }}</h4>
                  <p>{{ schedule.dose }}<span v-if="schedule.notes" class="schedule-notes">{{ schedule.notes }}</span></p>
                </div>
                <div class="time-tags">
                  <span v-for="(time, index) in schedule.scheduled_times" :key="index">
                    <el-tag 
                      size="small" 
                      :type="getTimeStatus(time)" 
                      effect="light"
                      round
                    >
                      {{ time.substring(0, 5) }}
                    </el-tag>
                  </span>
                </div>
              </div>
              <div class="schedule-actions">
                <el-button 
                  circle 
                  size="small" 
                  type="danger" 
                  plain 
                  @click="handleDeleteSchedule(schedule.id)"
                  title="删除提醒"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="今日暂无用药提醒" :image-size="100" />
        </div>

        <!-- 家人用药 -->
        <div class="content-card">
          <div class="card-header">
            <div class="header-title">
              <el-icon class="header-icon"><UserFilled /></el-icon>
              <span>家人健康概况</span>
            </div>
            <el-button text type="primary" @click="$router.push('/family')">管理家人</el-button>
          </div>
          
          <div class="family-grid" v-if="familyMembers.length > 0">
            <div v-for="member in familyMembers" :key="member.user_id" class="family-card">
              <div class="family-info">
                <el-avatar :size="48" class="family-avatar">
                  {{ member.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="family-text">
                  <div class="name-row">
                    <span class="name">{{ member.username }}</span>
                    <el-tag v-if="member.relation" size="small" effect="plain" round>{{ member.relation }}</el-tag>
                  </div>
                  <div class="status-text">
                    <span v-if="member.medication_count > 0" class="active-status">
                      正在服用 {{ member.medication_count }} 种药物
                    </span>
                    <span v-else class="inactive-status">暂无用药</span>
                  </div>
                </div>
              </div>
              <el-button 
                type="primary" 
                plain 
                size="small" 
                round
                @click="handleSwitchToMember(member)"
              >
                切换视角
              </el-button>
            </div>
          </div>
          <el-empty v-else description="暂无家庭成员" :image-size="80" />
        </div>
      </div>

      <!-- 右侧健康档案 -->
      <div class="right-column">
        <div class="content-card health-profile-card">
          <div class="card-header">
            <div class="header-title">
              <el-icon class="header-icon"><DataLine /></el-icon>
              <span>健康档案摘要</span>
            </div>
            <el-button text type="primary" @click="$router.push('/health-profile')">详情</el-button>
          </div>

          <div v-if="healthProfile" class="health-metrics">
            <div class="metric-item">
              <span class="label">BMI 指数</span>
              <div class="value-row">
                <span class="value" :class="getBMIClass(bmi)">{{ bmi }}</span>
                <span class="status-badge" :class="getBMIClass(bmi)">{{ getBMIStatusText(bmi) }}</span>
              </div>
            </div>
            
            <div class="metric-grid">
              <div class="mini-metric">
                <span class="label">血压</span>
                <span class="value">{{ healthProfile.systolic_pressure || '-' }}/{{ healthProfile.diastolic_pressure || '-' }}</span>
                <span class="unit">mmHg</span>
              </div>
              <div class="mini-metric">
                <span class="label">心率</span>
                <span class="value">{{ healthProfile.heart_rate || '-' }}</span>
                <span class="unit">bpm</span>
              </div>
              <div class="mini-metric">
                <span class="label">血糖</span>
                <span class="value">{{ healthProfile.blood_glucose || '-' }}</span>
                <span class="unit">mmol/L</span>
              </div>
              <div class="mini-metric">
                <span class="label">年龄</span>
                <span class="value">{{ age }}</span>
                <span class="unit">岁</span>
              </div>
              <div class="mini-metric">
                <span class="label">体重</span>
                <span class="value">{{ healthProfile.weight || '-' }}</span>
                <span class="unit">kg</span>
              </div>
              <div class="mini-metric">
                <span class="label">血型</span>
                <span class="value">{{ healthProfile.blood_type || '-' }}</span>
                <span class="unit"></span>
              </div>
            </div>

            <div class="tags-section" v-if="healthProfile.chronic_diseases">
              <span class="section-label">慢性病史</span>
              <div class="tags-wrapper">
                <el-tag 
                  v-for="disease in healthProfile.chronic_diseases.split(',')"
                  :key="disease"
                  size="small"
                  type="warning"
                  effect="light"
                  round
                >
                  {{ disease.trim() }}
                </el-tag>
              </div>
            </div>

            <div class="tags-section" v-if="allergies.length > 0">
              <span class="section-label">过敏史</span>
              <div class="tags-wrapper">
                <el-tag 
                  v-for="allergy in allergies"
                  :key="allergy.id"
                  size="small"
                  type="danger"
                  effect="light"
                  round
                >
                  {{ allergy.allergen }}{{ allergy.reaction ? `(${allergy.reaction})` : '' }}
                </el-tag>
              </div>
            </div>

            <div class="tags-section" v-if="familyHistories.length > 0">
              <span class="section-label">遗传病史</span>
              <div class="tags-wrapper">
                <el-tag 
                  v-for="history in familyHistories"
                  :key="history.id"
                  size="small"
                  type="info"
                  effect="light"
                  round
                >
                  {{ history.relative }}: {{ history.disease }}
                </el-tag>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无健康信息" :image-size="60" />
        </div>

        <!-- 快捷入口/最近记录 -->
        <div class="content-card">
          <div class="card-header">
            <div class="header-title">
              <el-icon class="header-icon"><Files /></el-icon>
              <span>最近记录</span>
            </div>
          </div>
          <div class="recent-list">
            <div class="recent-item" v-for="item in checkups.slice(0, 2)" :key="item.id">
              <div class="recent-icon checkup">
                <el-icon><DocumentChecked /></el-icon>
              </div>
              <div class="recent-info">
                <span class="recent-title">{{ item.checkup_type || '常规体检' }}</span>
                <span class="recent-date">{{ item.checkup_date }}</span>
              </div>
            </div>
            <div class="recent-item" v-for="item in surgeries.slice(0, 2)" :key="item.id">
              <div class="recent-icon surgery">
                <el-icon><KnifeFork /></el-icon>
              </div>
              <div class="recent-info">
                <span class="recent-title">{{ item.surgery_name }}</span>
                <span class="recent-date">{{ item.surgery_date }}</span>
              </div>
            </div>
            <div v-if="checkups.length === 0 && surgeries.length === 0" class="empty-text">
              暂无最近记录
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMedicationStore } from '@/stores/medication'
import { useUserStore } from '@/stores/user'
import { scheduleAPI, symptomAPI, recordAPI, healthProfileAPI, familyAPI } from '@/api'
import { chronicDiseaseAPI, medicationReminderAPI } from '@/api/chronic-disease'
import { 
  Box, AlarmClock, Calendar, Notebook, Timer, UserFilled, 
  DataLine, Files, DocumentChecked, KnifeFork, Delete,
  ArrowDown, User, SwitchButton
} from '@element-plus/icons-vue'
import { Lunar, Solar } from 'lunar-javascript'

const medicationStore = useMedicationStore()
const userStore = useUserStore()
const router = useRouter()
const todaySchedules = ref<any[]>([])
const symptomCount = ref(0)
const medicationScheduleDays = ref<Array<{ id: number; name: string; days: number }>>([])
const familyMembers = ref<any[]>([])

// 健康档案数据
const healthProfile = ref<any>(null)
const allergies = ref<any[]>([])
const familyHistories = ref<any[]>([])
const surgeries = ref<any[]>([])
const checkups = ref<any[]>([])

// 提醒数据
const medicationReminders = ref<any[]>([])
const followupPlans = ref<any[]>([])

interface ReminderItem {
  key: string
  type: 'medication' | 'followup'
  icon: string
  title: string
  desc: string
  tag: string
  tagType: 'success' | 'warning' | 'danger' | 'info'
  link?: string
}

const reminderItems = computed<ReminderItem[]>(() => {
  const items: ReminderItem[] = []
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes()
  const todayDay = now.getDay() // 0=周日

  // 用药提醒：今天需要提醒的
  medicationReminders.value.forEach(r => {
    if (r.status !== 'active') return
    const days: number[] = r.reminder_days || []
    if (!days.includes(todayDay)) return
    const time = r.reminder_time?.substring(0, 5) || ''
    const [h, m] = time.split(':').map(Number)
    const reminderTime = h * 60 + m
    // 显示还没过的和过了不超过60分钟的
    if (currentTime - reminderTime > 60) return
    const isPast = reminderTime <= currentTime
    items.push({
      key: `med-${r.id}`,
      type: 'medication',
      icon: '💊',
      title: `用药提醒`,
      desc: `${time} 服药`,
      tag: isPast ? '请尽快服药' : `${time}`,
      tagType: isPast ? 'danger' : 'warning',
      link: '/schedules'
    })
  })

  // 随访提醒
  followupPlans.value.forEach(plan => {
    if (!plan.next_followup_date) return
    const nextDate = new Date(plan.next_followup_date)
    nextDate.setHours(0, 0, 0, 0)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const diffDays = Math.floor((nextDate.getTime() - today.getTime()) / 86400000)
    const reminderDays = plan.reminder_days || 7

    if (diffDays > reminderDays) return // 还没到提醒窗口
    
    let tag = ''
    let tagType: ReminderItem['tagType'] = 'info'
    if (diffDays < 0) {
      tag = `已过期${Math.abs(diffDays)}天`
      tagType = 'danger'
    } else if (diffDays === 0) {
      tag = '今天'
      tagType = 'danger'
    } else if (diffDays <= 3) {
      tag = `${diffDays}天后`
      tagType = 'warning'
    } else {
      tag = `${diffDays}天后`
      tagType = 'info'
    }

    items.push({
      key: `followup-${plan.id}`,
      type: 'followup',
      icon: '🏥',
      title: `随访计划：${plan.disease_name || '随访'}`,
      desc: plan.responsible_doctor ? `医生: ${plan.responsible_doctor}` : plan.frequency || '',
      tag,
      tagType,
      link: plan.disease_id ? `/chronic-disease/${plan.disease_id}?tab=followup` : '/chronic-disease'
    })
  })

  // 按紧急程度排序：danger > warning > info > success
  const priority: Record<string, number> = { danger: 0, warning: 1, info: 2, success: 3 }
  items.sort((a, b) => (priority[a.tagType] ?? 9) - (priority[b.tagType] ?? 9))
  return items
})

// 日历数据
const now = new Date()
const solar = Solar.fromDate(now)
const lunar = solar.getLunar()

const currentDay = computed(() => now.getDate())
const currentMonthYear = computed(() => {
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
  return `${now.getFullYear()}年${months[now.getMonth()]}`
})

const lunarDateStr = computed(() => {
  return `${lunar.getMonthInChinese()}月${lunar.getDayInChinese()}`
})

const lunarFestival = computed(() => {
  const festivals = lunar.getFestivals()
  const jieQi = lunar.getJieQi()
  if (festivals.length > 0) {
    return festivals[0]
  }
  if (jieQi) {
    return jieQi
  }
  return ''
})

const username = computed(() => userStore.user?.username || '用户')

// 根据用户角色显示文本
function getRoleText(role: string | undefined): string {
  if (!role) return '普通成员'
  
  const roleMap: Record<string, string> = {
    admin: '家庭管理员',
    member: '普通成员',
    parent: '家长',
    child: '儿童',
    elderly: '老人',
    spouse: '配偶'
  }
  return roleMap[role] || role
}

const userRoleText = computed(() => {
  return getRoleText(userStore.user?.relation_to_admin)
})

// 获取用户头像完整URL
function getUserAvatarUrl(avatarPath: string) {
  if (!avatarPath) return ''
  if (avatarPath.startsWith('http')) return avatarPath
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${avatarPath}`
}

// 用户下拉菜单命令
function handleUserCommand(command: string) {
  if (command === 'profile') {
    router.push('/user-profile')
  } else if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}

// 根据时间显示不同的问候语（每分钟更新）
const currentHour = ref(new Date().getHours())
let greetingTimer: ReturnType<typeof setInterval>

const greeting = computed(() => {
  const hour = currentHour.value
  if (hour >= 5 && hour < 8) return '早上好'
  if (hour >= 8 && hour < 12) return '上午好'
  if (hour >= 12 && hour < 14) return '中午好'
  if (hour >= 14 && hour < 18) return '下午好'
  if (hour >= 18 && hour < 22) return '晚上好'
  return '夜深了'
})

// 计算BMI
const bmi = computed(() => {
  if (healthProfile.value?.height && healthProfile.value?.weight) {
    const h = healthProfile.value.height / 100
    const bmiValue = healthProfile.value.weight / (h * h)
    return bmiValue.toFixed(1)
  }
  return '-'
})

// 计算年龄 - 使用User表的birth_date，与家庭管理保持一致
const age = computed(() => {
  // 优先使用User表的birth_date，如果没有则使用HealthProfile表的birth_date作为后备
  const birthDateStr = userStore.user?.birth_date || healthProfile.value?.birth_date
  if (birthDateStr) {
    const birthDate = new Date(birthDateStr)
    const today = new Date()
    let calculatedAge = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      calculatedAge--
    }
    return calculatedAge
  }
  return '-'
})

// 计算今日待服药数量
const todayPendingCount = computed(() => {
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes()
  
  let count = 0
  todaySchedules.value.forEach(schedule => {
    if (Array.isArray(schedule.scheduled_times)) {
      schedule.scheduled_times.forEach((time: string) => {
        const [hours, minutes] = time.split(':').map(Number)
        const scheduleTime = hours * 60 + minutes
        if (scheduleTime >= currentTime) {
          count++
        }
      })
    }
  })
  return count
})

onMounted(async () => {
  greetingTimer = setInterval(() => {
    currentHour.value = new Date().getHours()
  }, 60000)

  if (!userStore.user) {
    await userStore.fetchUserInfo()
  }
  
  await Promise.all([
    medicationStore.fetchMyMedications(),
    fetchTodaySchedules(),
    fetchSymptomCount(),
    fetchMedicationScheduleDays(),
    fetchHealthProfile(),
    fetchAllergies(),
    fetchFamilyHistories(),
    fetchSurgeries(),
    fetchCheckups(),
    fetchFamilyMembers(),
    fetchMedicationReminders(),
    fetchFollowupPlans()
  ])
})

onUnmounted(() => {
  clearInterval(greetingTimer)
})

async function fetchTodaySchedules() {
  try {
    const data: any = await scheduleAPI.list(true)
    const today = new Date()
    todaySchedules.value = data.filter((schedule: any) => {
      const startDate = new Date(schedule.start_date)
      const endDate = schedule.end_date ? new Date(schedule.end_date) : null
      return startDate <= today && (!endDate || endDate >= today)
    })
  } catch (error) {
    console.error('获取今日用药计划失败:', error)
  }
}

async function handleDeleteSchedule(scheduleId: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个用药提醒吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await scheduleAPI.delete(scheduleId)
    ElMessage.success('删除成功')
    // 重新获取今日用药计划
    await fetchTodaySchedules()
    // 重新获取用药计划天数统计
    await fetchMedicationScheduleDays()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败：' + (error.response?.data?.detail || error.message))
    }
  }
}

async function fetchSymptomCount() {
  try {
    const data: any = await symptomAPI.list()
    symptomCount.value = Array.isArray(data) ? data.length : 0
  } catch (error) {
    console.error('获取症状记录失败:', error)
  }
}

async function fetchMedicationScheduleDays() {
  try {
    const data: any = await scheduleAPI.list(true)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    medicationScheduleDays.value = data.map((schedule: any) => {
      const startDate = new Date(schedule.start_date)
      startDate.setHours(0, 0, 0, 0)
      const diffTime = today.getTime() - startDate.getTime()
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1
      
      return {
        id: schedule.id,
        name: schedule.user_medication?.custom_name || schedule.user_medication?.medicine?.name || '未知药品',
        days: Math.max(0, diffDays)
      }
    }).filter((item: any) => item.days > 0)
    
  } catch (error) {
    console.error('获取用药计划天数失败:', error)
  }
}

async function fetchHealthProfile() {
  try {
    healthProfile.value = await healthProfileAPI.get()
  } catch (error) {
    console.error('获取健康档案失败:', error)
  }
}

async function fetchAllergies() {
  try {
    allergies.value = await healthProfileAPI.allergies.list()
  } catch (error) {
    console.error('获取过敏史失败:', error)
  }
}

async function fetchFamilyHistories() {
  try {
    familyHistories.value = await healthProfileAPI.familyHistory.list()
  } catch (error) {
    console.error('获取家族病史失败:', error)
  }
}

async function fetchSurgeries() {
  try {
    surgeries.value = await healthProfileAPI.surgeries.list()
  } catch (error) {
    console.error('获取手术记录失败:', error)
  }
}

async function fetchCheckups() {
  try {
    checkups.value = await healthProfileAPI.checkups.list()
  } catch (error) {
    console.error('获取体检报告失败:', error)
  }
}

async function fetchFamilyMembers() {
  try {
    const data: any = await familyAPI.getMembersMedication()
    familyMembers.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取家庭成员用药信息失败:', error)
    familyMembers.value = []
  }
}

async function fetchMedicationReminders() {
  try {
    const data: any = await medicationReminderAPI.list({ status: 'active' })
    medicationReminders.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取用药提醒失败:', error)
  }
}

async function fetchFollowupPlans() {
  try {
    const diseases: any = await chronicDiseaseAPI.list()
    const diseaseList = Array.isArray(diseases) ? diseases : (diseases?.data || [])
    const allPlans: any[] = []
    for (const disease of diseaseList) {
      try {
        const plans: any = await chronicDiseaseAPI.followupPlans.list(disease.id)
        const planList = Array.isArray(plans) ? plans : (plans?.data || [])
        planList.forEach((p: any) => {
          p.disease_name = disease.disease_name
          p.disease_id = disease.id
        })
        allPlans.push(...planList)
      } catch { /* skip */ }
    }
    followupPlans.value = allPlans
  } catch (error) {
    console.error('获取随访计划失败:', error)
  }
}

function handleReminderClick(item: ReminderItem) {
  if (item.link) router.push(item.link)
}

function getTimeStatus(timeStr: string): string {
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes()
  
  const [hours, minutes] = timeStr.split(':').map(Number)
  const scheduleTime = hours * 60 + minutes
  
  if (scheduleTime < currentTime) {
    return 'info'
  } else if (scheduleTime < currentTime + 30) {
    return 'warning'
  } else {
    return 'success'
  }
}

function getBMIClass(bmiValue: string): string {
  if (bmiValue === '-') return ''
  const bmi = parseFloat(bmiValue)
  if (bmi < 18.5) return 'underweight'
  if (bmi < 24) return 'normal'
  if (bmi < 28) return 'overweight'
  return 'obese'
}

function getBMIStatusText(bmiValue: string): string {
  if (bmiValue === '-') return '未知'
  const bmi = parseFloat(bmiValue)
  if (bmi < 18.5) return '偏瘦'
  if (bmi < 24) return '正常'
  if (bmi < 28) return '超重'
  return '肥胖'
}

async function handleSwitchToMember(member: any) {
  try {
    await ElMessageBox.confirm(
      `确认要切换到 ${member.real_name || member.username} 的账号吗？`,
      '切换账号',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res: any = await familyAPI.switchAccount(member.user_id)
    
    userStore.token = res.access_token
    localStorage.setItem('token', res.access_token)
    
    const currentUserId = userStore.user?.id
    if (currentUserId) {
      sessionStorage.setItem('admin_user_id', currentUserId.toString())
    }
    
    ElMessage.success(`已切换到 ${member.real_name || member.username} 的账号`)
    
    setTimeout(() => {
      window.location.href = '/'
    }, 500)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('切换账号失败：' + (error.response?.data?.detail || error.message))
    }
  }
}
</script>

<style scoped>
.dashboard {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-lg);
  padding: 32px 40px;
  color: white;
  margin-bottom: 32px;
  position: relative;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.welcome-text {
  position: relative;
  z-index: 2;
  flex: 1;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

/* Calendar Widget */
.calendar-widget {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  width: 160px;
  height: 160px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex-shrink: 0;
}

.calendar-date {
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.calendar-day {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
}

.calendar-month-year {
  font-size: 14px;
  opacity: 0.9;
}

.calendar-lunar {
  text-align: center;
}

.lunar-date {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.lunar-festival {
  font-size: 12px;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

/* User Widget */
.user-widget {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  width: 160px;
  height: 160px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
}

.user-avatar-wrapper {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  cursor: pointer;
  border: 2px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 600;
  color: white;
}

.user-widget .user-info-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  cursor: pointer;
}

.user-widget .user-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.user-role-dropdown {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 12px;
  transition: background 0.2s ease;
}

.user-role-dropdown:hover {
  background: rgba(255, 255, 255, 0.15);
}

.user-widget .user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.user-arrow {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  transition: transform 0.2s ease;
}

.user-role-dropdown:hover .user-arrow {
  color: rgba(255, 255, 255, 0.9);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-md);
}

.stat-icon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-card.primary .stat-icon-wrapper {
  background-color: rgba(42, 157, 143, 0.1);
  color: var(--color-primary);
}

.stat-card.warning .stat-icon-wrapper {
  background-color: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}

.stat-card.success .stat-icon-wrapper {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--color-success);
}

.stat-card.info .stat-icon-wrapper {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-main);
  line-height: 1;
}

.stat-value .unit {
  font-size: 12px;
  font-weight: 400;
  color: var(--color-text-light);
  margin-left: 4px;
}

/* Main Grid Layout */
.main-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.left-column, .right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Content Cards */
.content-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-card);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
}

.header-icon {
  color: var(--color-primary);
}

/* Schedule List */
.schedule-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.schedule-item {
  display: flex;
  gap: 12px;
  background-color: var(--color-bg-page);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  position: relative;
}

.schedule-item:hover .schedule-actions {
  opacity: 1;
}

.schedule-time-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 12px;
  flex-shrink: 0;
}

.time-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--color-primary);
  margin-top: 6px;
}

.time-line {
  display: none;
}

.schedule-content {
  flex: 1;
  min-width: 0;
}

.medicine-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.medicine-info p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.schedule-notes {
  margin-left: 6px;
  font-size: 12px;
  color: var(--color-text-placeholder, #aaa);
}

.time-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.schedule-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* Family Grid */
.family-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.family-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: border-color 0.3s;
}

.family-card:hover {
  border-color: var(--color-primary);
}

.family-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.family-avatar {
  background-color: var(--color-secondary-light);
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.family-text {
  flex: 1;
}

.name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.name {
  font-weight: 600;
  font-size: 15px;
}

.status-text {
  font-size: 12px;
}

.active-status {
  color: var(--color-success);
}

.inactive-status {
  color: var(--color-text-light);
}

/* Health Metrics */
.health-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.metric-item .label {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.metric-item .value-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.metric-item .value {
  font-size: 24px;
  font-weight: 700;
}

.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background-color: var(--color-bg-page);
  font-weight: 600;
}

.value.normal, .status-badge.normal { color: var(--color-success); }
.value.underweight, .status-badge.underweight { color: var(--color-warning); }
.value.overweight, .status-badge.overweight { color: var(--color-warning); }
.value.obese, .status-badge.obese { color: var(--color-danger); }

.metric-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

.mini-metric {
  background-color: var(--color-bg-page);
  border-radius: var(--radius-sm);
  padding: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mini-metric .label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.mini-metric .value {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
}

.mini-metric .unit {
  font-size: 10px;
  color: var(--color-text-light);
}

.tags-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.section-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

.tags-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

:deep(.tags-section .el-tag) {
  font-weight: 600;
}

/* Recent List */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-sm);
  background-color: var(--color-bg-page);
}

.recent-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.recent-icon.checkup {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--color-info);
}

.recent-icon.surgery {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--color-danger);
}

.recent-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.recent-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-main);
}

.recent-date {
  font-size: 12px;
  color: var(--color-text-light);
}

.empty-text {
  text-align: center;
  color: var(--color-text-light);
  font-size: 13px;
  padding: 20px 0;
}

/* Reminder Widget */
.reminder-widget {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  flex: 1;
  min-width: 0;
  max-height: 160px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.reminder-scroll {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reminder-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.12);
  cursor: pointer;
  transition: background 0.2s;
}

.reminder-item:hover {
  background: rgba(255, 255, 255, 0.25);
}

.reminder-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.reminder-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.reminder-title {
  font-size: 13px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reminder-desc {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.75);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.reminder-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 60px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.reminder-widget::-webkit-scrollbar {
  width: 4px;
}

.reminder-widget::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}
</style>

