<template>
  <div class="dashboard-container">
    <h2 class="page-title">仪表盘</h2>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon users"><el-icon><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_users }}</div>
            <div class="stat-label">用户总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon active"><el-icon><UserFilled /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.active_users }}</div>
            <div class="stat-label">活跃用户</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card stat-card-clickable" shadow="hover" @click="showOnlineUsers">
          <div class="stat-icon online"><el-icon><Connection /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.online_users }}</div>
            <div class="stat-label">在线用户</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon medicines"><el-icon><FirstAidKit /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_medicines }}</div>
            <div class="stat-label">药品总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon diseases"><el-icon><Document /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_diseases }}</div>
            <div class="stat-label">疾病总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="8" :md="4">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon schedules"><el-icon><Calendar /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.total_schedules }}</div>
            <div class="stat-label">用药计划</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增用户统计 -->
    <el-row :gutter="20" class="new-users-row">
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>
            <span>今日新增用户</span>
          </template>
          <div class="big-number">{{ stats.new_users_today }}</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12">
        <el-card shadow="hover">
          <template #header>
            <span>本周新增用户</span>
          </template>
          <div class="big-number">{{ stats.new_users_this_week }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户增长趋势图 -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <span>最近 30 天用户增长趋势</span>
      </template>
      <div ref="chartRef" class="chart-container"></div>
    </el-card>

    <!-- 在线用户对话框 -->
    <el-dialog v-model="onlineDialogVisible" title="在线用户" width="480px">
      <div v-if="onlineUsersLoading" style="text-align: center; padding: 20px;">
        <el-icon class="is-loading"><Connection /></el-icon> 加载中...
      </div>
      <div v-else-if="onlineUsers.length === 0" style="text-align: center; padding: 20px; color: #909399;">
        当前没有在线用户
      </div>
      <div v-else class="online-user-list">
        <div v-for="u in onlineUsers" :key="u.id" class="online-user-item">
          <el-avatar :size="36" :src="u.avatar || undefined">
            {{ (u.real_name || u.username).charAt(0) }}
          </el-avatar>
          <div class="online-user-info">
            <div class="online-user-name">
              {{ u.real_name || u.username }}
              <el-tag v-if="u.is_admin" size="small" type="danger" style="margin-left: 6px;">管理员</el-tag>
            </div>
            <div class="online-user-meta">@{{ u.username }} · 在线 {{ formatDuration(u.connected_at) }}</div>
          </div>
          <div class="online-status-dot"></div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats, getOnlineUsers } from '@/api/admin'
import type { AdminDashboardStats, OnlineUser } from '@/types/admin'
import { User, UserFilled, FirstAidKit, Document, Calendar, Connection } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const stats = ref<AdminDashboardStats>({
  total_users: 0,
  active_users: 0,
  online_users: 0,
  total_medicines: 0,
  total_diseases: 0,
  total_schedules: 0,
  new_users_today: 0,
  new_users_this_week: 0,
  user_growth_trend: []
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const onlineDialogVisible = ref(false)
const onlineUsers = ref<OnlineUser[]>([])
const onlineUsersLoading = ref(false)

async function showOnlineUsers() {
  onlineDialogVisible.value = true
  onlineUsersLoading.value = true
  try {
    onlineUsers.value = await getOnlineUsers()
  } catch {
    ElMessage.error('获取在线用户失败')
  } finally {
    onlineUsersLoading.value = false
  }
}

function formatDuration(connectedAt: string | null): string {
  if (!connectedAt) return ''
  const diff = Date.now() - new Date(connectedAt).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return '刚刚上线'
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} 小时`
  return `${Math.floor(hours / 24)} 天`
}

async function loadStats() {
  try {
    stats.value = await getDashboardStats()
    renderChart()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

function renderChart() {
  if (!chartRef.value) return
  
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  const dates = stats.value.user_growth_trend.map(item => item.date)
  const counts = stats.value.user_growth_trend.map(item => item.count)

  chartInstance.setOption({
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>新增用户: {c}'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [{
      data: counts,
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(42, 157, 143, 0.5)' },
          { offset: 1, color: 'rgba(42, 157, 143, 0.05)' }
        ])
      },
      lineStyle: {
        color: '#2A9D8F',
        width: 2
      },
      itemStyle: {
        color: '#2A9D8F'
      }
    }]
  })
}

function handleResize() {
  chartInstance?.resize()
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 16px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  width: 100%;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.users { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.active { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
.stat-icon.online { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.stat-icon.medicines { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); }
.stat-icon.diseases { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.schedules { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.new-users-row {
  margin-bottom: 20px;
}

.big-number {
  font-size: 48px;
  font-weight: 700;
  color: #2A9D8F;
  text-align: center;
  padding: 20px 0;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 350px;
}

.stat-card-clickable {
  cursor: pointer;
}

.online-user-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.online-user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #f9fafb;
}

.online-user-info {
  flex: 1;
  min-width: 0;
}

.online-user-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
}

.online-user-meta {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.online-status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #67c23a;
  flex-shrink: 0;
}
</style>
