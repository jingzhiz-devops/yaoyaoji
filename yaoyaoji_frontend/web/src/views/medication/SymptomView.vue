<template>
  <div class="symptom-view-container">
    <div class="content-wrapper">
      <el-tabs v-model="activeTab" class="custom-tabs">
        <el-tab-pane label="今日症状" name="today">
          <template #label>
            <div class="tab-header-with-button">
              <span>今日症状</span>
              <el-button v-if="activeTab === 'today'" type="primary" size="small" @click.stop="handleAdd" class="tab-add-btn">
                <el-icon><Plus /></el-icon>
                记录症状
              </el-button>
            </div>
          </template>
          <div class="tab-content">
            <el-timeline v-if="todaySymptoms.length > 0">
              <el-timeline-item
                v-for="symptom in todaySymptoms"
                :key="symptom.id"
                :timestamp="symptom.recorded_at"
                placement="top"
                :type="getTagType(symptom.intensity)"
                size="large"
                :icon="getTimelineIcon(symptom.intensity)"
              >
                <el-card class="symptom-card" shadow="hover">
                  <div class="symptom-item">
                    <div class="symptom-main">
                      <div class="symptom-emoji-wrapper">
                        <span class="symptom-emoji">{{ symptom.symptom_emoji || '📝' }}</span>
                      </div>
                      <div class="symptom-info">
                        <h4 class="symptom-text">{{ symptom.symptom_text }}</h4>
                        <el-rate 
                          v-model="symptom.intensity" 
                          disabled 
                          show-score 
                          text-color="#ff9900"
                          score-template="{value} 分"
                        />
                      </div>
                    </div>
                    <div class="symptom-actions">
                      <el-button circle size="small" type="primary" plain @click="handleEdit(symptom)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                      <el-button circle size="small" type="danger" plain @click="handleDelete(symptom.id)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </el-card>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="今日暂无症状记录，身体很健康哦！" :image-size="200" />
          </div>
        </el-tab-pane>

        <el-tab-pane name="timeline">
          <template #label>
            <div class="tab-header-with-button">
              <span>症状时间轴</span>
              <el-button v-if="activeTab === 'timeline'" type="primary" size="small" @click.stop="handleAdd" class="tab-add-btn">
                <el-icon><Plus /></el-icon>
                记录症状
              </el-button>
            </div>
          </template>
          <div class="filter-bar">
            <span class="filter-label">查看范围：</span>
            <el-radio-group v-model="timelineDays" @change="fetchTimeline" size="small">
              <el-radio-button :label="7">最近7天</el-radio-button>
              <el-radio-button :label="14">最近14天</el-radio-button>
              <el-radio-button :label="30">最近30天</el-radio-button>
            </el-radio-group>
          </div>

          <div class="tab-content">
            <div v-if="timeline.length > 0" class="timeline-container">
              <div v-for="day in timeline" :key="day.date" class="timeline-day-group">
                <div class="date-header">
                  <span class="date-text">{{ day.date }}</span>
                  <span class="count-badge">{{ day.count }}条记录</span>
                </div>
                <div class="day-symptoms">
                  <div 
                    v-for="symptom in day.symptoms"
                    :key="symptom.id"
                    class="mini-symptom-card"
                    :class="`intensity-${symptom.intensity}`"
                  >
                    <div class="mini-emoji">{{ symptom.symptom_emoji || '📝' }}</div>
                    <div class="mini-content">
                      <div class="mini-text">{{ symptom.symptom_text }}</div>
                      <div class="mini-meta">
                        <span class="mini-time">{{ symptom.recorded_at }}</span>
                        <span class="mini-intensity">{{ symptom.intensity }}分</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无时间轴数据" :image-size="200" />
          </div>
        </el-tab-pane>

        <el-tab-pane name="history">
          <template #label>
            <div class="tab-header-with-button">
              <span>历史记录</span>
              <el-button v-if="activeTab === 'history'" type="primary" size="small" @click.stop="handleAdd" class="tab-add-btn">
                <el-icon><Plus /></el-icon>
                记录症状
              </el-button>
            </div>
          </template>
          <div class="filter-bar">
            <el-form :inline="true">
              <el-form-item label="日期范围">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  @change="fetchSymptoms"
                  size="default"
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
          </div>

          <div class="tab-content">
            <el-table :data="symptoms" style="width: 100%" stripe class="custom-table">
              <el-table-column label="表情" width="80" align="center">
                <template #default="{ row }">
                  <span style="font-size: 24px">{{ row.symptom_emoji || '📝' }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="symptom_text" label="症状描述" />
              <el-table-column label="强度" width="200">
                <template #default="{ row }">
                  <el-rate v-model="row.intensity" disabled show-score text-color="#ff9900" />
                </template>
              </el-table-column>
              <el-table-column prop="recorded_at" label="记录时间" width="180" />
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                  <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty v-if="symptoms.length === 0" description="暂无历史记录" :image-size="200" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 记录/编辑症状对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingId ? '编辑症状' : '记录症状'" 
      width="500px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" label-position="top">
        <el-form-item label="症状表情">
          <div class="emoji-picker">
            <div 
              v-for="emoji in commonEmojis"
              :key="emoji"
              class="emoji-item"
              :class="{ active: form.symptom_emoji === emoji }"
              @click="form.symptom_emoji = emoji"
            >
              {{ emoji }}
            </div>
          </div>
          <el-input v-model="form.symptom_emoji" placeholder="或者输入其他表情符号" style="margin-top: 10px">
            <template #prepend>当前选择</template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="症状描述" required>
          <el-input 
            v-model="form.symptom_text" 
            type="textarea" 
            :rows="3"
            placeholder="请详细描述您的症状感受，例如：头痛持续，伴有恶心..." 
          />
        </el-form-item>
        
        <el-form-item label="症状强度 (1-5分)">
          <div class="intensity-slider">
            <el-rate 
              v-model="form.intensity" 
              show-score 
              :colors="['#99A9BF', '#F7BA2A', '#FF9900']"
              score-template="{value} 分"
            />
            <span class="intensity-desc">{{ getIntensityDesc(form.intensity) }}</span>
          </div>
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { symptomAPI } from '@/api'
import { Plus, Edit, Delete, Warning, CircleCheck, InfoFilled } from '@element-plus/icons-vue'
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

const commonEmojis = ['😊', '😷', '🤒', '🤕', '😴', '😖', '🤢', '🤧', '💊', '🏥', '🤮', '🥶', '🥵', '😵', '🤯']

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

function handleAdd() {
  resetForm()
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.symptom_text) {
    ElMessage.warning('请描述症状')
    return
  }

  try {
    if (editingId.value) {
      await symptomAPI.update(editingId.value, {
        symptom_emoji: form.symptom_emoji || undefined,
        symptom_text: form.symptom_text,
        intensity: form.intensity
      })
      ElMessage.success('修改成功')
    } else {
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
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })

    await symptomAPI.delete(id)
    ElMessage.success('删除成功')
    await fetchTodaySymptoms()
    await fetchSymptoms()
    await fetchTimeline()
  } catch (error) {
    // Cancelled
  }
}

function getTagType(intensity: number) {
  if (intensity >= 4) return 'danger'
  if (intensity >= 3) return 'warning'
  return 'success'
}

function getTimelineIcon(intensity: number) {
  if (intensity >= 4) return Warning
  if (intensity >= 3) return InfoFilled
  return CircleCheck
}

function getIntensityDesc(intensity: number) {
  const map: Record<number, string> = {
    1: '轻微不适',
    2: '有些不舒服',
    3: '明显不适',
    4: '很难受',
    5: '非常痛苦'
  }
  return map[intensity] || ''
}

function resetForm() {
  editingId.value = null
  form.symptom_emoji = ''
  form.symptom_text = ''
  form.intensity = 3
}
</script>

<style scoped>
.symptom-view-container {
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

.content-wrapper {
  background: white;
  border-radius: var(--radius-md);
  padding: 24px;
  box-shadow: var(--shadow-card);
}

/* Tabs */
.tab-header-with-button {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tab-add-btn {
  margin-left: 8px;
}

.tab-content {
  padding-top: 20px;
}

/* Timeline Item */
.symptom-card {
  border: none;
  background: #f9fafb;
}

.symptom-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.symptom-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.symptom-emoji-wrapper {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.symptom-emoji {
  font-size: 24px;
}

.symptom-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.symptom-text {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
}

.symptom-actions {
  display: flex;
  gap: 8px;
}

/* Timeline View */
.filter-bar {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.timeline-day-group {
  border-left: 2px solid var(--color-border);
  padding-left: 24px;
  position: relative;
}

.timeline-day-group::before {
  content: '';
  position: absolute;
  left: -6px;
  top: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-primary);
  border: 2px solid white;
  box-shadow: 0 0 0 2px var(--color-primary-light);
}

.date-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.date-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
}

.count-badge {
  font-size: 12px;
  color: var(--color-text-light);
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 10px;
}

.day-symptoms {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.mini-symptom-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
  transition: all 0.2s;
}

.mini-symptom-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.mini-symptom-card.intensity-4,
.mini-symptom-card.intensity-5 {
  border-left: 4px solid var(--color-danger);
}

.mini-symptom-card.intensity-3 {
  border-left: 4px solid var(--color-warning);
}

.mini-symptom-card.intensity-1,
.mini-symptom-card.intensity-2 {
  border-left: 4px solid var(--color-success);
}

.mini-emoji {
  font-size: 20px;
}

.mini-content {
  flex: 1;
}

.mini-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-main);
  margin-bottom: 4px;
}

.mini-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-text-light);
}

/* Emoji Picker */
.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.emoji-item {
  font-size: 24px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.emoji-item:hover {
  background: white;
  transform: scale(1.2);
  box-shadow: var(--shadow-sm);
}

.emoji-item.active {
  background: var(--color-primary-light);
  color: white;
}

.intensity-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.intensity-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  font-weight: 500;
}
</style>
