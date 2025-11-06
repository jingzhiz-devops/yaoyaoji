<template>
  <div class="symptom-view">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>📝 症状记录</h2>
      <el-button type="primary" @click="dialogVisible = true">记录症状</el-button>
    </div>

    <el-tabs v-model="activeTab" style="margin-top: 20px">
      <el-tab-pane label="今日症状" name="today">
        <el-timeline v-if="todaySymptoms.length > 0">
          <el-timeline-item
            v-for="symptom in todaySymptoms"
            :key="symptom.id"
            :timestamp="symptom.recorded_at"
            placement="top"
          >
            <el-card>
              <div class="symptom-item">
                <div>
                  <span class="symptom-emoji">{{ symptom.symptom_emoji || '📝' }}</span>
                  <span class="symptom-text">{{ symptom.symptom_text }}</span>
                </div>
                <div style="display: flex; align-items: center; gap: 15px;">
                  <el-rate v-model="symptom.intensity" disabled show-score />
                  <el-button type="primary" size="small" @click="handleEdit(symptom)">U</el-button>
                  <el-button type="danger" size="small" @click="handleDelete(symptom.id)">D</el-button>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
        <el-empty v-else description="今日暂无症状记录" />
      </el-tab-pane>

      <el-tab-pane label="症状时间轴" name="timeline">
        <el-form :inline="true" style="margin-bottom: 20px">
          <el-form-item label="查看天数">
            <el-select v-model="timelineDays" @change="fetchTimeline" style="width: 120px">
              <el-option label="最近7天" :value="7" />
              <el-option label="最近14天" :value="14" />
              <el-option label="最近30天" :value="30" />
            </el-select>
          </el-form-item>
        </el-form>

        <div v-if="timeline.length > 0">
          <el-card v-for="day in timeline" :key="day.date" style="margin-bottom: 10px">
            <template #header>
              <div>{{ day.date }} ({{ day.count }}条记录)</div>
            </template>
            <el-tag
              v-for="symptom in day.symptoms"
              :key="symptom.id"
              style="margin-right: 10px; margin-bottom: 5px"
              :type="getTagType(symptom.intensity)"
            >
              {{ symptom.symptom_emoji }} {{ symptom.symptom_text }} ({{ symptom.intensity }}⭐)
            </el-tag>
          </el-card>
        </div>
        <el-empty v-else description="暂无时间轴数据" />
      </el-tab-pane>

      <el-tab-pane label="历史记录" name="history">
        <el-form :inline="true" style="margin-bottom: 20px">
          <el-form-item label="日期范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              @change="fetchSymptoms"
            />
          </el-form-item>
          <el-form-item label="最低强度">
            <el-select v-model="minIntensity" @change="fetchSymptoms" style="width: 120px">
              <el-option label="全部" :value="0" />
              <el-option label="1星及以上" :value="1" />
              <el-option label="2星及以上" :value="2" />
              <el-option label="3星及以上" :value="3" />
              <el-option label="4星及以上" :value="4" />
              <el-option label="5星" :value="5" />
            </el-select>
          </el-form-item>
        </el-form>

        <el-table :data="symptoms" style="width: 100%">
          <el-table-column label="表情" width="80">
            <template #default="{ row }">
              <span style="font-size: 24px">{{ row.symptom_emoji || '📝' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="symptom_text" label="症状描述" />
          <el-table-column label="强度" width="200">
            <template #default="{ row }">
              <el-rate v-model="row.intensity" disabled show-score />
            </template>
          </el-table-column>
          <el-table-column prop="recorded_at" label="记录时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="handleEdit(row)">U</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row.id)">D</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="symptoms.length === 0" description="暂无历史记录" />
      </el-tab-pane>
    </el-tabs>

    <!-- 记录/编辑症状对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑症状' : '记录症状'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="症状表情">
          <el-input v-model="form.symptom_emoji" placeholder="输入一个表情符号(可选)" />
          <div style="margin-top: 10px">
            <el-button
              v-for="emoji in commonEmojis"
              :key="emoji"
              size="small"
              @click="form.symptom_emoji = emoji"
            >
              {{ emoji }}
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="症状描述">
          <el-input v-model="form.symptom_text" type="textarea" placeholder="描述你的症状" />
        </el-form-item>
        <el-form-item label="症状强度">
          <el-rate v-model="form.intensity" show-score />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { symptomAPI } from '@/api'
import dayjs from 'dayjs'

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const activeTab = ref('today')
const todaySymptoms = ref<any[]>([])
const symptoms = ref<any[]>([])
const timeline = ref<any[]>([])
const dateRange = ref<[Date, Date]>()
const minIntensity = ref(0)
const timelineDays = ref(7)

const commonEmojis = ['😊', '😷', '🤒', '🤕', '😴', '😖', '🤢', '🤧', '💊', '🏥']

const form = reactive({
  symptom_emoji: '',
  symptom_text: '',
  intensity: 3
})

onMounted(async () => {
  await fetchTodaySymptoms()
  await fetchSymptoms()
  await fetchTimeline()
})

async function fetchTodaySymptoms() {
  try {
    const data: any = await symptomAPI.today()
    // 添加格式化的时间
    todaySymptoms.value = data.map((symptom: any) => ({
      ...symptom,
      recorded_at: dayjs(symptom.recorded_time).format('HH:mm')
    }))
  } catch (error) {
    console.error('获取今日症状失败', error)
  }
}

async function fetchSymptoms() {
  try {
    const params: any = {}
    if (dateRange.value) {
      params.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    }
    if (minIntensity.value > 0) {
      params.min_intensity = minIntensity.value
    }
    const data: any = await symptomAPI.list(params)
    // 添加格式化的时间
    symptoms.value = data.map((symptom: any) => ({
      ...symptom,
      recorded_at: dayjs(symptom.recorded_time).format('YYYY-MM-DD HH:mm')
    }))
  } catch (error) {
    console.error('获取症状记录失败', error)
  }
}

async function fetchTimeline() {
  try {
    const data: any = await symptomAPI.timeline(timelineDays.value)
    // 将症状记录按日期分组
    const grouped = new Map<string, any[]>()
    
    data.forEach((symptom: any) => {
      const date = dayjs(symptom.recorded_time).format('YYYY-MM-DD')
      if (!grouped.has(date)) {
        grouped.set(date, [])
      }
      grouped.get(date)!.push({
        ...symptom,
        recorded_at: dayjs(symptom.recorded_time).format('HH:mm')
      })
    })
    
    // 转换为数组格式，按日期降序排列
    timeline.value = Array.from(grouped.entries())
      .map(([date, symptoms]) => ({
        date,
        count: symptoms.length,
        symptoms
      }))
      .sort((a, b) => b.date.localeCompare(a.date))
  } catch (error) {
    console.error('获取症状时间轴失败', error)
  }
}

async function handleSubmit() {
  if (!form.symptom_text) {
    ElMessage.warning('请描述症状')
    return
  }

  try {
    if (editingId.value) {
      // 编辑模式
      await symptomAPI.update(editingId.value, {
        symptom_emoji: form.symptom_emoji || undefined,
        symptom_text: form.symptom_text,
        intensity: form.intensity
      })
      ElMessage.success('修改成功')
    } else {
      // 创建模式
      await symptomAPI.create({
        symptom_emoji: form.symptom_emoji || undefined,
        symptom_text: form.symptom_text,
        intensity: form.intensity
      })
      ElMessage.success('记录成功')
    }
    dialogVisible.value = false
    await fetchTodaySymptoms()
    await fetchSymptoms()
    await fetchTimeline()
    resetForm()
  } catch (error) {
    ElMessage.error(editingId.value ? '修改失败' : '记录失败')
  }
}

function handleEdit(symptom: any) {
  editingId.value = symptom.id
  form.symptom_emoji = symptom.symptom_emoji || ''
  form.symptom_text = symptom.symptom_text
  form.intensity = symptom.intensity
  dialogVisible.value = true
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
    type: 'warning'
  })

  try {
    await symptomAPI.delete(id)
    ElMessage.success('删除成功')
    await fetchTodaySymptoms()
    await fetchSymptoms()
    await fetchTimeline()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function getTagType(intensity: number) {
  if (intensity >= 4) return 'danger'
  if (intensity >= 3) return 'warning'
  return 'success'
}

function resetForm() {
  editingId.value = null
  form.symptom_emoji = ''
  form.symptom_text = ''
  form.intensity = 3
}
</script>

<style scoped>
.symptom-view {
  width: 100%;
  height: 100%;
}

.symptom-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.symptom-emoji {
  font-size: 24px;
  margin-right: 10px;
}

.symptom-text {
  font-size: 16px;
}
</style>
