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
                        <div class="symptom-intensity-display">
                          <span class="intensity-face">{{ getIntensityIcon(symptom.intensity) }}</span>
                          <span class="intensity-text-inline">{{ getIntensityDesc(symptom.intensity) }}</span>
                          <el-tag :type="getTagType(symptom.intensity)" size="small">{{ symptom.intensity }}级</el-tag>
                        </div>
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
                        <span class="mini-intensity">{{ getIntensityIcon(symptom.intensity) }} {{ getIntensityDesc(symptom.intensity) }}</span>
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
              <el-form-item label="最低不适程度">
                <el-select v-model="minIntensity" @change="fetchSymptoms" style="width: 120px">
                  <el-option label="全部" :value="0" />
                  <el-option label="1级及以上" :value="1" />
                  <el-option label="2级及以上" :value="2" />
                  <el-option label="3级及以上" :value="3" />
                  <el-option label="4级及以上" :value="4" />
                  <el-option label="5级" :value="5" />
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
              <el-table-column label="不适程度" width="200">
                <template #default="{ row }">
                  <div class="table-intensity">
                    <span class="table-intensity-icon">{{ getIntensityIcon(row.intensity) }}</span>
                    <span class="table-intensity-text">{{ getIntensityDesc(row.intensity) }}</span>
                    <el-tag :type="getTagType(row.intensity)" size="small">{{ row.intensity }}级</el-tag>
                  </div>
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
      width="600px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" label-position="top">
        <!-- 快捷症状 -->
        <el-form-item label="快捷选择">
          <div class="quick-symptoms">
            <div 
              v-for="qs in quickSymptoms"
              :key="qs.text"
              class="quick-symptom-tag"
              :class="{ active: form.symptom_text === qs.text && form.symptom_emoji === qs.emoji }"
              @click="applyQuickSymptom(qs)"
            >
              <span class="qs-emoji">{{ qs.emoji }}</span>
              <span class="qs-text">{{ qs.text }}</span>
            </div>
          </div>
        </el-form-item>

        <!-- 分类表情选择 -->
        <el-form-item label="症状表情">
          <div class="emoji-category-tabs">
            <span 
              v-for="(cat, idx) in emojiCategories"
              :key="cat.label"
              class="emoji-tab"
              :class="{ active: activeEmojiCategory === idx }"
              @click="activeEmojiCategory = idx"
            >{{ cat.label }}</span>
          </div>
          <div class="emoji-picker">
            <div 
              v-for="item in emojiCategories[activeEmojiCategory].emojis"
              :key="item.emoji"
              class="emoji-item"
              :class="{ active: form.symptom_emoji === item.emoji }"
              @click="selectEmoji(item.emoji, item.desc)"
              :title="item.desc"
            >
              <span class="emoji-char">{{ item.emoji }}</span>
              <span class="emoji-label">{{ item.desc }}</span>
            </div>
          </div>
          <el-input v-model="form.symptom_emoji" placeholder="或者输入其他表情符号" style="margin-top: 10px" size="small">
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
        
        <el-form-item label="不适程度">
          <div class="intensity-selector">
            <div 
              v-for="level in 5"
              :key="level"
              class="intensity-level"
              :class="{ active: form.intensity === level, [`level-${level}`]: true }"
              @click="form.intensity = level"
            >
              <span class="intensity-icon">{{ getIntensityIcon(level) }}</span>
              <span class="intensity-label">{{ getIntensityDesc(level) }}</span>
            </div>
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

// 按症状类型分组的表情
const emojiCategories = [
  {
    label: '疼痛类',
    emojis: [
      { emoji: '🤕', desc: '头痛' },
      { emoji: '💥', desc: '偏头痛' },
      { emoji: '😣', desc: '腹痛' },
      { emoji: '🦴', desc: '关节痛' },
      { emoji: '🦷', desc: '牙痛' },
      { emoji: '👁️', desc: '眼痛' },
      { emoji: '🫁', desc: '胸闷' },
    ]
  },
  {
    label: '消化类',
    emojis: [
      { emoji: '🤢', desc: '恶心' },
      { emoji: '🤮', desc: '呕吐' },
      { emoji: '😖', desc: '腹胀' },
      { emoji: '💩', desc: '腹泻' },
      { emoji: '😫', desc: '便秘' },
      { emoji: '🍽️', desc: '食欲不振' },
    ]
  },
  {
    label: '全身类',
    emojis: [
      { emoji: '🤒', desc: '发热' },
      { emoji: '🥶', desc: '发冷/畏寒' },
      { emoji: '🥵', desc: '潮热/出汗' },
      { emoji: '😵‍💫', desc: '头晕' },
      { emoji: '🥱', desc: '乏力/疲劳' },
      { emoji: '😴', desc: '失眠/嗜睡' },
      { emoji: '💪', desc: '肌肉酸痛' },
    ]
  },
  {
    label: '呼吸/五官类',
    emojis: [
      { emoji: '🤧', desc: '打喷嚏/流涕' },
      { emoji: '😷', desc: '咳嗽' },
      { emoji: '😮‍💨', desc: '气短/呼吸困难' },
      { emoji: '👃', desc: '鼻塞' },
      { emoji: '👂', desc: '耳鸣' },
      { emoji: '🗣️', desc: '咽喉痛' },
    ]
  },
  {
    label: '皮肤/过敏类',
    emojis: [
      { emoji: '🫠', desc: '皮疹/红肿' },
      { emoji: '🤡', desc: '面部浮肿' },
      { emoji: '💧', desc: '水肿' },
      { emoji: '🔴', desc: '过敏反应' },
    ]
  },
  {
    label: '情绪/精神类',
    emojis: [
      { emoji: '😰', desc: '焦虑/紧张' },
      { emoji: '😢', desc: '情绪低落' },
      { emoji: '🤯', desc: '烦躁/易怒' },
      { emoji: '😶‍🌫️', desc: '注意力不集中' },
      { emoji: '😊', desc: '感觉好转' },
    ]
  }
]

// 快捷症状模板 - 点击直接填充表情+描述
const quickSymptoms = [
  { emoji: '🤒', text: '发热', intensity: 3 },
  { emoji: '🤕', text: '头痛', intensity: 3 },
  { emoji: '😵‍💫', text: '头晕', intensity: 2 },
  { emoji: '🤮', text: '呕吐', intensity: 4 },
  { emoji: '😴', text: '失眠', intensity: 3 },
  { emoji: '🤧', text: '流涕/鼻塞', intensity: 2 },
  { emoji: '😷', text: '咳嗽', intensity: 2 },
  { emoji: '🤢', text: '恶心', intensity: 3 },
  { emoji: '😣', text: '腹痛', intensity: 3 },
  { emoji: '🥱', text: '乏力', intensity: 2 },
]

const activeEmojiCategory = ref(0)

const form = reactive({
  symptom_emoji: '',
  symptom_text: '',
  intensity: 3
})

function applyQuickSymptom(qs: { emoji: string; text: string; intensity: number }) {
  form.symptom_emoji = qs.emoji
  form.symptom_text = qs.text
  form.intensity = qs.intensity
}

function selectEmoji(emoji: string, desc: string) {
  form.symptom_emoji = emoji
  // 如果描述为空，自动填入症状名称
  if (!form.symptom_text) {
    form.symptom_text = desc
  }
}

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
    1: '轻微',
    2: '有点不适',
    3: '明显不适',
    4: '很难受',
    5: '非常痛苦'
  }
  return map[intensity] || ''
}

function getIntensityIcon(intensity: number) {
  const map: Record<number, string> = {
    1: '😌',
    2: '😐',
    3: '😟',
    4: '😣',
    5: '😫'
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
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
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
  background: rgba(255, 255, 255, 0.85);
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
.emoji-category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.emoji-tab {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  cursor: pointer;
  background: #f3f4f6;
  color: var(--color-text-secondary);
  transition: all 0.2s;
  user-select: none;
}

.emoji-tab:hover {
  background: #e5e7eb;
}

.emoji-tab.active {
  background: var(--color-primary);
  color: white;
}

.emoji-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.emoji-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  cursor: pointer;
  padding: 6px 8px;
  border-radius: 8px;
  transition: all 0.2s;
  min-width: 56px;
}

.emoji-item:hover {
  background: white;
  transform: scale(1.05);
  box-shadow: var(--shadow-sm);
}

.emoji-item.active {
  background: var(--color-primary-light);
  box-shadow: 0 0 0 2px var(--color-primary);
}

.emoji-char {
  font-size: 24px;
  line-height: 1.2;
}

.emoji-label {
  font-size: 10px;
  color: var(--color-text-light);
  white-space: nowrap;
}

.emoji-item.active .emoji-label {
  color: var(--color-primary);
  font-weight: 500;
}

/* Quick Symptoms */
.quick-symptoms {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-symptom-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 16px;
  background: #f3f4f6;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
  border: 1px solid transparent;
}

.quick-symptom-tag:hover {
  background: #e5e7eb;
  transform: translateY(-1px);
}

.quick-symptom-tag.active {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.qs-emoji {
  font-size: 16px;
}

.qs-text {
  font-size: 13px;
  color: var(--color-text-main);
}

/* Intensity Selector */
.intensity-selector {
  display: flex;
  gap: 8px;
  width: 100%;
}

.intensity-level {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  background: #f9fafb;
  user-select: none;
}

.intensity-level:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.intensity-level.active.level-1 {
  border-color: #67c23a;
  background: #f0f9eb;
}

.intensity-level.active.level-2 {
  border-color: #a0d911;
  background: #fcffe6;
}

.intensity-level.active.level-3 {
  border-color: #e6a23c;
  background: #fdf6ec;
}

.intensity-level.active.level-4 {
  border-color: #f56c6c;
  background: #fef0f0;
}

.intensity-level.active.level-5 {
  border-color: #d32029;
  background: #fff1f0;
}

.intensity-icon {
  font-size: 28px;
  line-height: 1;
}

.intensity-label {
  font-size: 11px;
  color: var(--color-text-secondary);
  text-align: center;
  white-space: nowrap;
}

.intensity-level.active .intensity-label {
  font-weight: 600;
}

/* Symptom intensity display in cards */
.symptom-intensity-display {
  display: flex;
  align-items: center;
  gap: 6px;
}

.intensity-face {
  font-size: 18px;
}

.intensity-text-inline {
  font-size: 13px;
  color: var(--color-text-secondary);
}

/* Table intensity display */
.table-intensity {
  display: flex;
  align-items: center;
  gap: 6px;
}

.table-intensity-icon {
  font-size: 18px;
}

.table-intensity-text {
  font-size: 13px;
  color: var(--color-text-secondary);
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
