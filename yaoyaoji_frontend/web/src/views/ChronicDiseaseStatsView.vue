<template>
  <div class="chronic-disease-stats">
    <div class="stats-header">
      <h1>慢性病统计与分析</h1>
    </div>

    <!-- 关键指标卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #f0f9ff">
            <el-icon style="color: #409eff; font-size: 32px"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">总慢性病数</div>
            <div class="stat-value">{{ totalDiseases }}</div>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #f0f9ff">
            <el-icon style="color: #67c23a; font-size: 32px"><SuccessFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">控制良好</div>
            <div class="stat-value" style="color: #67c23a">{{ goodControlCount }}</div>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fef0f0">
            <el-icon style="color: #f56c6c; font-size: 32px"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">控制不良</div>
            <div class="stat-value" style="color: #f56c6c">{{ poorControlCount }}</div>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fef0f0">
            <el-icon style="color: #e6a23c; font-size: 32px"><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">待进行随访</div>
            <div class="stat-value" style="color: #e6a23c">{{ pendingFollowup }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 控制状态分布 -->
    <el-card class="status-card" header="控制状态分布">
      <div class="status-distribution">
        <div v-for="status in statusDistribution" :key="status.name" class="distribution-item">
          <div class="distribution-bar">
            <div
              class="distribution-fill"
              :style="{ width: status.percentage + '%', backgroundColor: status.color }"
            ></div>
          </div>
          <div class="distribution-info">
            <span class="status-name">{{ status.name }}</span>
            <span class="status-count">{{ status.count }} 个</span>
            <span class="status-percentage">{{ status.percentage }}%</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 近期随访计划 -->
    <el-card class="recent-card" header="7天内随访计划">
      <el-table :data="upcomingFollowups" v-if="upcomingFollowups.length > 0">
        <el-table-column prop="disease_name" label="疾病名称" width="150" />
        <el-table-column prop="frequency" label="随访频率" width="100" />
        <el-table-column prop="next_followup_date" label="随访日期" width="150">
          <template #default="{ row }">
            {{ formatDate(row.next_followup_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="responsible_doctor" label="医生" width="100" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToFollowupSchedule">进行随访</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="近7天暂无随访计划" />
    </el-card>

    <!-- 最近的指标记录 -->
    <el-card class="recent-card" header="最近指标记录">
      <el-table :data="recentIndicators" v-if="recentIndicators.length > 0">
        <el-table-column prop="disease_name" label="疾病" width="150" />
        <el-table-column prop="indicator_name" label="指标" width="150" />
        <el-table-column prop="value" label="数值" width="100" />
        <el-table-column prop="measurement_date" label="记录时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.measurement_date) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无指标记录" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, SuccessFilled, Warning, Clock } from '@element-plus/icons-vue'
import { chronicDiseaseAPI } from '@/api/chronic-disease'
import type { ChronicDisease, FollowupPlan } from '@/types'

const router = useRouter()

const diseases = ref<ChronicDisease[]>([])
const allFollowupPlans = ref<(FollowupPlan & { disease_name: string })[]>([])

// 加载数据
const loadData = async () => {
  try {
    const response = await chronicDiseaseAPI.list({ limit: 100 })
    diseases.value = response.data

    // 收集所有随访计划
    allFollowupPlans.value = []
    for (const disease of diseases.value) {
      const plansResponse = await chronicDiseaseAPI.followupPlans.list(disease.id)
      const plansWithDiseaseName = plansResponse.data.map((plan) => ({
        ...plan,
        disease_name: disease.disease_name
      }))
      allFollowupPlans.value.push(...plansWithDiseaseName)
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

// 总慢性病数
const totalDiseases = computed(() => diseases.value.length)

// 控制良好的数量
const goodControlCount = computed(
  () => diseases.value.filter((d) => d.control_status === 'good').length
)

// 控制不良的数量
const poorControlCount = computed(
  () => diseases.value.filter((d) => d.control_status === 'poor').length
)

// 待进行随访
const pendingFollowup = computed(() => {
  return allFollowupPlans.value.filter(
    (p) => new Date(p.next_followup_date) < new Date()
  ).length
})

// 控制状态分布
const statusDistribution = computed(() => {
  const total = diseases.value.length
  if (total === 0) return []

  const good = diseases.value.filter((d) => d.control_status === 'good').length
  const fair = diseases.value.filter((d) => d.control_status === 'fair').length
  const poor = diseases.value.filter((d) => d.control_status === 'poor').length

  return [
    {
      name: '控制良好',
      count: good,
      percentage: Math.round((good / total) * 100),
      color: '#67c23a'
    },
    {
      name: '控制中等',
      count: fair,
      percentage: Math.round((fair / total) * 100),
      color: '#e6a23c'
    },
    {
      name: '控制不良',
      count: poor,
      percentage: Math.round((poor / total) * 100),
      color: '#f56c6c'
    }
  ]
})

// 近7天的随访计划
const upcomingFollowups = computed(() => {
  const now = new Date()
  const sevenDaysLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

  return allFollowupPlans.value
    .filter(
      (p) =>
        new Date(p.next_followup_date) >= now &&
        new Date(p.next_followup_date) <= sevenDaysLater
    )
    .sort(
      (a, b) =>
        new Date(a.next_followup_date).getTime() -
        new Date(b.next_followup_date).getTime()
    )
})

// 最近的指标记录
const recentIndicators = computed(() => {
  const records: any[] = []

  for (const disease of diseases.value) {
    if (disease.indicators) {
      // TODO: 这里需要从API获取指标记录
      // 目前这是一个占位符
    }
  }

  return records.slice(0, 10)
})

const formatDate = (date: string): string => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateTime: string): string => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

const goToFollowupSchedule = () => {
  router.push('/followup-schedule')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.chronic-disease-stats {
  padding: 20px;
}

.stats-header {
  margin-bottom: 30px;

  h1 {
    margin: 0;
    font-size: 28px;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  }

  .stat-content {
    display: flex;
    align-items: center;
    gap: 20px;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .stat-info {
    flex: 1;

    .stat-label {
      color: #909399;
      font-size: 14px;
      margin-bottom: 8px;
    }

    .stat-value {
      color: #303133;
      font-size: 28px;
      font-weight: 600;
    }
  }
}

.status-card,
.recent-card {
  margin-bottom: 20px;
}

.status-distribution {
  display: flex;
  flex-direction: column;
  gap: 20px;

  .distribution-item {
    display: flex;
    align-items: center;
    gap: 15px;

    .distribution-bar {
      flex: 1;
      height: 30px;
      background: #f5f7fa;
      border-radius: 4px;
      overflow: hidden;

      .distribution-fill {
        height: 100%;
        transition: width 0.3s;
      }
    }

    .distribution-info {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 120px;

      .status-name {
        color: #303133;
        font-weight: 500;
      }

      .status-count {
        color: #909399;
        font-size: 14px;
      }

      .status-percentage {
        color: #606266;
        font-size: 14px;
        min-width: 40px;
        text-align: right;
      }
    }
  }
}
</style>
