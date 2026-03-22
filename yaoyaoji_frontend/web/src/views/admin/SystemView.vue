<template>
  <div class="system-container">
    <h2 class="page-title">系统设置</h2>

    <el-row :gutter="20">
      <!-- 系统健康状态 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>系统健康状态</span>
              <el-button size="small" @click="loadHealth" :loading="healthLoading">刷新</el-button>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统状态">
              <el-tag :type="health.status === 'running' ? 'success' : 'danger'">
                {{ health.status === 'running' ? '运行中' : '异常' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据库状态">
              <el-tag :type="health.database === 'healthy' ? 'success' : 'danger'">
                {{ health.database === 'healthy' ? '正常' : '异常' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="检查时间">
              {{ health.timestamp ? formatDate(health.timestamp) : '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 数据库统计 -->
      <el-col :xs="24" :md="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>数据库统计</span>
              <el-button size="small" @click="loadDbStats" :loading="statsLoading">刷新</el-button>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户数">{{ dbStats.users }}</el-descriptions-item>
            <el-descriptions-item label="药品数">{{ dbStats.medicines }}</el-descriptions-item>
            <el-descriptions-item label="疾病数">{{ dbStats.diseases }}</el-descriptions-item>
            <el-descriptions-item label="用户药箱数">{{ dbStats.user_medications }}</el-descriptions-item>
            <el-descriptions-item label="用药计划数">{{ dbStats.medication_schedules }}</el-descriptions-item>
            <el-descriptions-item label="用药记录数">{{ dbStats.medication_records }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemHealth, getDbStats } from '@/api/admin'
import type { SystemHealth, DbStats } from '@/types/admin'

const healthLoading = ref(false)
const statsLoading = ref(false)

const health = reactive<SystemHealth>({
  status: '',
  database: '',
  timestamp: ''
})

const dbStats = reactive<DbStats>({
  users: 0,
  medicines: 0,
  diseases: 0,
  user_medications: 0,
  medication_schedules: 0,
  medication_records: 0
})

async function loadHealth() {
  healthLoading.value = true
  try {
    const res = await getSystemHealth()
    Object.assign(health, res)
  } catch (error) {
    ElMessage.error('获取系统状态失败')
  } finally {
    healthLoading.value = false
  }
}

async function loadDbStats() {
  statsLoading.value = true
  try {
    const res = await getDbStats()
    Object.assign(dbStats, res)
  } catch (error) {
    ElMessage.error('获取数据库统计失败')
  } finally {
    statsLoading.value = false
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadHealth()
  loadDbStats()
})
</script>

<style scoped>
.system-container {
  max-width: 1200px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-col {
  margin-bottom: 20px;
}
</style>
