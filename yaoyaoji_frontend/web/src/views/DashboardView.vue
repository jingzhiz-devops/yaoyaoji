<template>
  <div class="dashboard">
    <div class="welcome-section">
      <h1 class="welcome-title">
        <span class="gradient-text">欢迎回来，{{ username }}</span>
      </h1>
    </div>

    <!-- 用药统计 -->
    <el-row :gutter="20" style="margin-top: 30px">
      <el-col :span="6">
        <el-card class="stat-card stat-card-primary">
          <div class="stat-content">
            <div class="stat-icon">💊</div>
            <div class="stat-info">
              <div class="stat-title">我的药品</div>
              <div class="stat-value">{{ medicationStore.myMedications.length }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card-warning">
          <div class="stat-content">
            <div class="stat-icon">⏰</div>
            <div class="stat-info">
              <div class="stat-title">今日待服药</div>
              <div class="stat-value">{{ todayPendingCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card-success">
          <div class="stat-content">
            <div class="stat-icon">✅</div>
            <div class="stat-info" style="width: 100%;">
              <div class="stat-title">服药天数</div>
              <div class="medication-days-container">
                <div v-if="medicationScheduleDays.length > 0">
                  <div v-for="item in medicationScheduleDays" :key="item.id" class="medication-day-item">
                    {{ item.name }} <span style="color: #ffffff; font-weight: bold;">{{ item.days }}</span> 天
                  </div>
                </div>
                <div v-else style="color: rgba(255, 255, 255, 0.7); font-size: 14px;">暂无计划</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card stat-card-info">
          <div class="stat-content">
            <div class="stat-icon">📝</div>
            <div class="stat-info">
              <div class="stat-title">症状记录</div>
              <div class="stat-value">{{ symptomCount }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 今日用药 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card header="今日用药">
          <div v-if="todaySchedules.length > 0" style="max-height: 200px; overflow-y: auto;">
            <div v-for="schedule in todaySchedules" :key="schedule.id" style="margin-bottom: 10px; padding: 10px; border-radius: 4px; background: #f5f7fa;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <strong>{{ schedule.user_medication?.custom_name || schedule.user_medication?.medicine?.name }}</strong>
                  <div style="font-size: 12px; color: #909399; margin-top: 5px;">
                    <span v-for="(time, index) in schedule.scheduled_times" :key="index">
                      <el-tag 
                        size="small" 
                        :type="getTimeStatus(time)" 
                        style="margin-right: 5px;"
                      >
                        {{ time.substring(0, 5) }}
                      </el-tag>
                    </span>
                    | {{ schedule.dose }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="今日暂无用药提醒" />
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card header="家人用药">
          <div v-if="familyMembers.length > 0" style="max-height: 200px; overflow-y: auto;">
            <div v-for="member in familyMembers" :key="member.user_id" style="margin-bottom: 10px; padding: 10px; border-radius: 4px; background: #f0f9ff;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <strong style="font-size: 15px;">{{ member.username }}</strong>
                    <el-tag v-if="member.relation" size="small" type="primary">{{ member.relation }}</el-tag>
                  </div>
                  <div style="font-size: 12px; color: #909399; margin-top: 5px;">
                    <span v-if="member.medication_count > 0">
                      💊 用药 {{ member.medication_count }} 种 | 今日 {{ member.today_schedules }} 个提醒
                    </span>
                    <span v-else style="color: #c0c4cc;">暂无用药记录</span>
                  </div>
                </div>
                <el-button 
                  type="primary" 
                  size="small" 
                  @click="handleSwitchToMember(member)"
                  style="margin-left: 10px;"
                >
                  切换
                </el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无家庭成员" :image-size="80" />
        </el-card>
      </el-col>
    </el-row>

    <el-divider style="margin: 30px 0" />

    <!-- 健康档案概览 -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>🩺 基本健康信息</span>
              <el-button text type="primary" @click="$router.push('/health-profile')">详情</el-button>
            </div>
          </template>
          <div v-if="healthProfile" class="health-info">
            <div v-if="healthProfile.real_name" class="info-row">
              <span class="label">👤 姓名</span>
              <span class="value">{{ healthProfile.real_name }}</span>
            </div>
            <div class="info-row">
              <span class="label">🩸 血型</span>
              <span class="value">{{ healthProfile.blood_type || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">📏 身高</span>
              <span class="value">{{ healthProfile.height || '-' }} cm</span>
            </div>
            <div class="info-row">
              <span class="label">⚖️ 体重</span>
              <span class="value">{{ healthProfile.weight || '-' }} kg</span>
            </div>
            <div class="info-row">
              <span class="label">📊 BMI</span>
              <span class="value" :class="getBMIClass(bmi)">{{ bmi }}</span>
            </div>
            <div v-if="healthProfile.systolic_pressure && healthProfile.diastolic_pressure" class="info-row">
              <span class="label">💓 血压</span>
              <span class="value">{{ healthProfile.systolic_pressure }}/{{ healthProfile.diastolic_pressure }} mmHg</span>
            </div>
            <div v-if="healthProfile.heart_rate" class="info-row">
              <span class="label">💗 心率</span>
              <span class="value">{{ healthProfile.heart_rate }} 次/分</span>
            </div>
            <div v-if="healthProfile.blood_glucose" class="info-row">
              <span class="label">🍬 血糖</span>
              <span class="value">{{ healthProfile.blood_glucose }} mmol/L</span>
            </div>
            <div v-if="healthProfile.temperature" class="info-row">
              <span class="label">🌡️ 体温</span>
              <span class="value">{{ healthProfile.temperature }} ℃</span>
            </div>
            <div v-if="healthProfile.chronic_diseases" class="info-row chronic">
              <span class="label">🏥 慢性病</span>
              <el-tag v-for="disease in healthProfile.chronic_diseases.split(',')"
                      :key="disease"
                      size="small"
                      type="warning"
                      style="margin: 2px">
                {{ disease.trim() }}
              </el-tag>
            </div>
          </div>
          <el-empty v-else description="暂无健康信息" :image-size="60" />
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>⚠️ 过敏史</span>
              <el-button text type="primary" @click="$router.push('/health-profile?tab=allergy')">详情</el-button>
            </div>
          </template>
          <div v-if="allergies.length > 0" class="allergy-list">
            <div v-for="item in allergies.slice(0, 3)" :key="item.id" class="allergy-item">
              <div class="allergy-header">
                <el-tag :type="getSeverityType(item.severity)" size="small">
                  {{ item.allergen }}
                </el-tag>
                <span class="allergy-type">{{ getAllergenTypeText(item.allergen_type) }}</span>
              </div>
              <div class="allergy-reaction">{{ item.reaction || '无反应描述' }}</div>
            </div>
            <div v-if="allergies.length > 3" class="more-hint">
              还有 {{ allergies.length - 3 }} 条记录...
            </div>
          </div>
          <el-empty v-else description="暂无过敏记录" :image-size="60" />
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>🧬 家族病史</span>
              <el-button text type="primary" @click="$router.push('/health-profile?tab=family-history')">详情</el-button>
            </div>
          </template>
          <div v-if="familyHistories.length > 0" class="family-history-list">
            <div v-for="item in familyHistories.slice(0, 3)" :key="item.id" class="history-item">
              <div class="history-header">
                <el-tag type="info" size="small">{{ item.relative }}</el-tag>
                <span class="disease-name">{{ item.disease }}</span>
              </div>
              <div class="history-detail">
                发病年龄：{{ item.onset_age || '未知' }} 岁
              </div>
            </div>
            <div v-if="familyHistories.length > 3" class="more-hint">
              还有 {{ familyHistories.length - 3 }} 条记录...
            </div>
          </div>
          <el-empty v-else description="暂无家族病史" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 手术记录和体检报告 -->
    <el-row :gutter="20" style="margin-top: 20px; margin-bottom: 20px">
      <el-col :span="12">
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>🏥 手术记录</span>
              <el-button text type="primary" @click="$router.push('/health-profile?tab=surgery')">详情</el-button>
            </div>
          </template>
          <div v-if="surgeries.length > 0" class="surgery-list">
            <el-timeline>
              <el-timeline-item
                v-for="item in surgeries.slice(0, 3)"
                :key="item.id"
                :timestamp="item.surgery_date"
                placement="top"
              >
                <el-card>
                  <h4>{{ item.surgery_name }}</h4>
                  <p v-if="item.hospital" class="detail-text">医院：{{ item.hospital }}</p>
                  <p v-if="item.doctor" class="detail-text">医生：{{ item.doctor }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <div v-if="surgeries.length > 3" class="more-hint">
              还有 {{ surgeries.length - 3 }} 条记录...
            </div>
          </div>
          <el-empty v-else description="暂无手术记录" :image-size="60" />
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="health-card">
          <template #header>
            <div class="card-header">
              <span>📋 体检报告</span>
              <el-button text type="primary" @click="$router.push('/health-profile?tab=checkup')">详情</el-button>
            </div>
          </template>
          <div v-if="checkups.length > 0" class="checkup-list">
            <el-timeline>
              <el-timeline-item
                v-for="item in checkups.slice(0, 3)"
                :key="item.id"
                :timestamp="item.checkup_date"
                placement="top"
              >
                <el-card>
                  <h4>{{ item.checkup_type || '常规体检' }}</h4>
                  <p v-if="item.hospital" class="detail-text">医院：{{ item.hospital }}</p>
                  <p v-if="item.summary" class="detail-text summary">{{ item.summary }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <div v-if="checkups.length > 3" class="more-hint">
              还有 {{ checkups.length - 3 }} 条记录...
            </div>
          </div>
          <el-empty v-else description="暂无体检报告" :image-size="60" />
        </el-card>
      </el-col>
    </el-row>


  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMedicationStore } from '@/stores/medication'
import { useUserStore } from '@/stores/user'
import { scheduleAPI, symptomAPI, recordAPI, healthProfileAPI, familyAPI } from '@/api'

const medicationStore = useMedicationStore()
const userStore = useUserStore()
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

const username = computed(() => userStore.user?.username || '用户')

// 计算BMI
const bmi = computed(() => {
  if (healthProfile.value?.height && healthProfile.value?.weight) {
    const h = healthProfile.value.height / 100
    const bmiValue = healthProfile.value.weight / (h * h)
    return bmiValue.toFixed(1)
  }
  return '-'
})

// 计算今日待服药数量（根据当前时间判断）
const todayPendingCount = computed(() => {
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes() // 当前时间（分钟数）
  
  let count = 0
  todaySchedules.value.forEach(schedule => {
    if (Array.isArray(schedule.scheduled_times)) {
      schedule.scheduled_times.forEach((time: string) => {
        // 解析时间字符串 "HH:mm:ss"
        const [hours, minutes] = time.split(':').map(Number)
        const scheduleTime = hours * 60 + minutes
        
        // 如果计划时间大于等于当前时间，则计入待服药
        if (scheduleTime >= currentTime) {
          count++
        }
      })
    }
  })
  
  return count
})

onMounted(async () => {
  // 确保用户信息已加载
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
    fetchFamilyMembers()
  ])
})

async function fetchTodaySchedules() {
  try {
    const data: any = await scheduleAPI.list(true)
    // 筛选出今天有服药时间的计划
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

// 获取症状记录数量
async function fetchSymptomCount() {
  try {
    const data: any = await symptomAPI.list()
    symptomCount.value = Array.isArray(data) ? data.length : 0
  } catch (error) {
    console.error('获取症状记录失败:', error)
  }
}

// 获取已服药天数（根据历史记录统计）
// 获取用药计划天数（根据计划开始时间计算）
async function fetchMedicationScheduleDays() {
  try {
    const data: any = await scheduleAPI.list(true) // 只获取活跃的计划
    const today = new Date()
    today.setHours(0, 0, 0, 0) // 重置到当天0点
    
    medicationScheduleDays.value = data.map((schedule: any) => {
      const startDate = new Date(schedule.start_date)
      startDate.setHours(0, 0, 0, 0) // 重置到当天0点
      
      // 计算天数差（今天 - 开始日期 + 1）
      const diffTime = today.getTime() - startDate.getTime()
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1
      
      return {
        id: schedule.id,
        name: schedule.user_medication?.custom_name || schedule.user_medication?.medicine?.name || '未知药品',
        days: Math.max(0, diffDays) // 确保不为负数
      }
    }).filter((item: any) => item.days > 0) // 只显示天数大于0的
    
  } catch (error) {
    console.error('获取用药计划天数失败:', error)
  }
}

// 获取健康档案数据
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

// 获取家庭成员用药信息
async function fetchFamilyMembers() {
  try {
    const data: any = await familyAPI.getMembersMedication()
    familyMembers.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('获取家庭成员用药信息失败:', error)
    familyMembers.value = []
  }
}

// 获取时间状态（用于标签颜色）
function getTimeStatus(timeStr: string): string {
  const now = new Date()
  const currentTime = now.getHours() * 60 + now.getMinutes()
  
  const [hours, minutes] = timeStr.split(':').map(Number)
  const scheduleTime = hours * 60 + minutes
  
  if (scheduleTime < currentTime) {
    return 'info' // 已过期（灰色）
  } else if (scheduleTime < currentTime + 30) {
    return 'warning' // 即将到时（30分钟内，黄色）
  } else {
    return 'success' // 还未到时（绿色）
  }
}

// 获取BMI分级颜色
function getBMIClass(bmiValue: string): string {
  if (bmiValue === '-') return ''
  const bmi = parseFloat(bmiValue)
  if (bmi < 18.5) return 'underweight'
  if (bmi < 24) return 'normal'
  if (bmi < 28) return 'overweight'
  return 'obese'
}

// 获取严重程度类型
function getSeverityType(severity: string | null): string {
  switch (severity) {
    case '轻微': return 'success'
    case '中度': return 'warning'
    case '严重': return 'danger'
    default: return 'info'
  }
}

// 获取过敏原类型文本
function getAllergenTypeText(type: string | null): string {
  const typeMap: Record<string, string> = {
    '药物': '💊',
    '食物': '🍎',
    '环境': '🌳',
    '其他': '❓'
  }
  return typeMap[type || ''] || '❓'
}

// 切换到家庭成员账号
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
    
    // 调用后端切换接口
    const res: any = await familyAPI.switchAccount(member.user_id)
    
    // 更新token
    userStore.token = res.access_token
    localStorage.setItem('token', res.access_token)
    
    // 存储原管理员ID（用于后续切换回来）
    const currentUserId = userStore.user?.id
    if (currentUserId) {
      sessionStorage.setItem('admin_user_id', currentUserId.toString())
    }
    
    ElMessage.success(`已切换到 ${member.real_name || member.username} 的账号`)
    
    // 重新加载页面
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

<style scoped lang="scss">
.dashboard {
  width: 100%;
  height: 100%;
}

.welcome-section {
  text-align: center;
  padding: 40px 20px 20px;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-radius: 20px;
  margin-bottom: 30px;
  animation: fadeInDown 0.8s ease-out;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.welcome-title {
  margin: 0;
  font-size: 42px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer 3s ease-in-out infinite;
  background-size: 200% auto;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% center; }
  50% { background-position: 100% center; }
}

.welcome-subtitle {
  font-size: 24px;
  color: #606266;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-weight: 500;
}

.brand-name {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
  font-size: 28px;
}

.divider {
  color: #dcdfe6;
  font-weight: 300;
}

.slogan {
  color: #909399;
  font-size: 18px;
  font-weight: 400;
  letter-spacing: 0.5px;
}

.stat-card {
  text-align: center;
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.stat-card-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stat-card-warning {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.stat-card-success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.stat-card-info {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: white;
}

.stat-content {
  display: flex;
  align-items: flex-start;
  padding: 10px;
  gap: 15px;
  min-height: 80px;
  max-height: 80px;
}

.stat-icon {
  font-size: 48px;
  opacity: 0.9;
}

.stat-info {
  flex: 1;
  text-align: left;
}

.stat-title {
  font-size: 14px;
  opacity: 0.95;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
}

.el-button {
  margin: 5px;
}

// 健康档案卡片样式
.health-card {
  border-radius: 12px;
  transition: all 0.3s ease;
  height: 100%;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    font-size: 16px;
  }
}

.health-info {
  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    
    &:last-child {
      border-bottom: none;
    }
    
    &.chronic {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .label {
      color: #909399;
      font-size: 14px;
    }
    
    .value {
      font-weight: 600;
      font-size: 16px;
      color: #303133;
      
      &.normal {
        color: #67c23a;
      }
      
      &.underweight,
      &.overweight {
        color: #e6a23c;
      }
      
      &.obese {
        color: #f56c6c;
      }
    }
  }
}

.allergy-list,
.family-history-list {
  .allergy-item,
  .history-item {
    padding: 10px;
    margin-bottom: 10px;
    background: #f5f7fa;
    border-radius: 8px;
    border-left: 3px solid #409eff;
    
    &:last-of-type {
      margin-bottom: 0;
    }
  }
  
  .allergy-header,
  .history-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
  }
  
  .allergy-type {
    font-size: 18px;
  }
  
  .allergy-reaction,
  .history-detail {
    font-size: 13px;
    color: #606266;
    margin-top: 5px;
  }
  
  .disease-name {
    font-weight: 600;
    color: #303133;
  }
}

.surgery-list,
.checkup-list {
  :deep(.el-timeline) {
    padding-left: 0;
  }
  
  :deep(.el-timeline-item__wrapper) {
    padding-left: 20px;
  }
  
  :deep(.el-card) {
    margin-bottom: 0;
    
    h4 {
      margin: 0 0 8px 0;
      color: #303133;
      font-size: 15px;
    }
    
    .detail-text {
      margin: 4px 0;
      font-size: 13px;
      color: #606266;
      
      &.summary {
        color: #909399;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
    }
  }
}

.more-hint {
  text-align: center;
  padding: 10px;
  color: #909399;
  font-size: 13px;
  margin-top: 10px;
}

// 服药天数容器样式
.medication-days-container {
  max-height: 55px;
  overflow-y: auto;
  text-align: left;
  font-size: 13px;
  line-height: 1.4;
  padding-right: 5px;
  
  // 滚动条样式
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 2px;
    
    &:hover {
      background: rgba(255, 255, 255, 0.5);
    }
  }
}

.medication-day-item {
  margin-bottom: 4px;
  padding: 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
