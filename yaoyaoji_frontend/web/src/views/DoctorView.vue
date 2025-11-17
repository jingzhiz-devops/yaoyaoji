<template>
  <div class="doctor-view">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>🤖 AI 医生</h2>
    </div>

    <!-- AI 预测卡片 -->
    <el-card class="ai-predict-card">
      <template #header>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>🧠 AI 智能预测</span>
          <el-tag type="success" size="small">已接入DeepSeek</el-tag>
        </div>
      </template>
      <el-form>
        <el-form-item label="症状描述">
          <el-input
            v-model="symptomDescription"
            type="textarea"
            :rows="4"
            placeholder="请详细描述您的身体不适症状，例如：头痛、发热、38.5度、喉哙痛、持续2天..."
            maxlength="500"
            show-word-limit
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :icon="Search" 
            @click="handleAIPredict" 
            :loading="aiPredicting"
            :disabled="!symptomDescription.trim()"
          >
            获取AI医疗建议
          </el-button>
          <el-button @click="symptomDescription = ''; aiSuggestion = null">清空</el-button>
        </el-form-item>
      </el-form>

      <!-- 加载中状态 -->
      <div v-if="aiPredicting" class="ai-loading">
        <el-progress :percentage="loadingProgress" :stroke-width="8" status="success">
          <template #default="{ percentage }">
            <span class="loading-text">🧬 AI 医生分析中... {{ percentage }}%</span>
          </template>
        </el-progress>
        <div class="loading-tips">
          <el-icon class="is-loading" :size="20" color="#409eff" style="margin-right: 8px;">
            <Loading />
          </el-icon>
          <span>正在调用 DeepSeek AI 进行智能分析，请稍候...</span>
        </div>
      </div>
      
      <el-alert
        v-if="aiSuggestion"
        type="success"
        :closable="false"
        class="ai-suggestion-card"
      >
        <template #title>
          <div class="ai-suggestion-header">
            <span class="ai-suggestion-title">👨‍⚕️ AI 医生建议</span>
            <el-tag type="success" size="small">DeepSeek AI</el-tag>
          </div>
        </template>
        <div class="ai-suggestion-content" v-html="formatAISuggestion(aiSuggestion)"></div>
      </el-alert>

      <el-alert
        type="warning"
        :closable="false"
        style="margin-top: 15px;"
      >
        <template #title>
          <div style="font-size: 13px;">
            ⚠️ 温馨提示：AI建议仅供参考，不能替代专业医疗诊断。如症状严重或持续不缓解，请及时就医。
          </div>
        </template>
      </el-alert>
    </el-card>

    <el-card class="search-card">
      <template #header>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>💊 查询药品</span>
          <el-tag type="warning" size="small">AI 智能查询</el-tag>
        </div>
      </template>
      <el-form :inline="true">
        <el-form-item label="药品名称">
          <el-input
            v-model="searchQuery"
            placeholder="请输入药品名称（如：阿莫西林、布洛芬）"
            style="width: 500px"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" :loading="aiMedicineQuerying">
                AI 查询
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI 药品查询结果 -->
    <el-card v-if="aiMedicineResult" class="ai-result-card" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 18px; font-weight: bold;">💊 AI 药品查询结果</span>
          <el-tag type="warning">DeepSeek AI</el-tag>
        </div>
      </template>
      <div class="ai-suggestion-content" v-html="formatAISuggestion(aiMedicineResult)"></div>
    </el-card>

    <el-card class="search-card" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span>🏥 查询疾病</span>
          <el-tag type="warning" size="small">AI 智能查询</el-tag>
        </div>
      </template>
      <el-form :inline="true">
        <el-form-item label="疾病名称">
          <el-input
            v-model="diseaseQuery"
            placeholder="请输入疾病名称（如：感冒、高血压）"
            style="width: 500px"
            clearable
            @keyup.enter="handleDiseaseSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleDiseaseSearch" :loading="aiDiseaseQuerying">
                AI 查询
              </el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- AI 疾病查询结果 -->
    <el-card v-if="aiDiseaseResult" class="ai-result-card" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 18px; font-weight: bold;">🏥 AI 疾病查询结果</span>
          <el-tag type="warning">DeepSeek AI</el-tag>
        </div>
      </template>
      <div class="ai-suggestion-content" v-html="formatAISuggestion(aiDiseaseResult)"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { medicineAPI, userMedicationAPI, diseaseAPI, aiDoctorAPI } from '@/api'
import { useMedicationStore } from '@/stores/medication'

const medicationStore = useMedicationStore()
const searchQuery = ref('')
const searching = ref(false)
const currentMedicine = ref<any>(null)
const diseaseQuery = ref('')
const searchHistory = ref<string[]>([])
const conflicts = ref<any[]>([])

// AI 预测相关状态
const symptomDescription = ref('')
const aiPredicting = ref(false)
const aiSuggestion = ref<string | null>(null)
const loadingProgress = ref(0)

// AI 药品查询状态
const aiMedicineQuerying = ref(false)
const aiMedicineResult = ref<string | null>(null)

// AI 疾病查询状态
const aiDiseaseQuerying = ref(false)
const aiDiseaseResult = ref<string | null>(null)

// 检查是否已在药箱中
const isInBox = computed(() => {
  if (!currentMedicine.value) return false
  return medicationStore.myMedications.some(
    med => med.medicine.id === currentMedicine.value.id
  )
})

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入药品名称')
    return
  }

  // 直接使用 AI 查询
  await handleAIMedicineQuery()
}

async function handleDiseaseSearch() {
  if (!diseaseQuery.value.trim()) {
    ElMessage.warning('请输入疾病名称')
    return
  }
  
  // 直接使用 AI 查询
  await handleAIDiseaseQuery()
}

async function checkConflicts() {
  // TODO: 接入后端冲突检测服务
  conflicts.value = []
}

function parseList(val: any): string[] {
  if (!val) return []
  if (Array.isArray(val)) return val
  if (typeof val === 'string') {
    return val.split(/[,，、;；\s]+/).filter(i => i.trim())
  }
  return []
}

function parseIngredients(medicine: any): string[] {
  if (!medicine.ingredients) return []
  if (typeof medicine.ingredients === 'string') {
    return medicine.ingredients.split(/[,，、]/).filter(i => i.trim())
  }
  return []
}

async function addToBox() {
  if (!currentMedicine.value) return
  
  try {
    await userMedicationAPI.add({
      medicine_id: currentMedicine.value.id,
      custom_name: currentMedicine.value.name
    })
    await medicationStore.fetchMyMedications()
    ElMessage.success('已添加到药箱')
  } catch (error: any) {
    ElMessage.error('添加失败：' + (error.response?.data?.detail || error.message))
  }
}

function clearHistory() {
  searchHistory.value = []
  ElMessage.success('已清空历史记录')
}

// AI 预测函数
async function handleAIPredict() {
  if (!symptomDescription.value.trim()) {
    ElMessage.warning('请输入症状描述')
    return
  }

  aiPredicting.value = true
  aiSuggestion.value = null
  loadingProgress.value = 0

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 90) {
      loadingProgress.value += Math.random() * 15
      if (loadingProgress.value > 90) loadingProgress.value = 90
    }
  }, 300)

  try {
    const response: any = await aiDoctorAPI.predict(symptomDescription.value.trim())
    loadingProgress.value = 100
    await new Promise(resolve => setTimeout(resolve, 300))
    
    aiSuggestion.value = response.suggestion
    ElMessage.success('✅ 已生成 AI 医疗建议')
  } catch (error: any) {
    let errorMsg = 'AI 服务暂时不可用，请稍后重试'
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      if (status === 404) {
        errorMsg = '❌ AI 服务接口未找到'
      } else if (status === 500) {
        errorMsg = '❌ 服务器内部错误：' + (detail || '请检查后端日志')
      } else {
        errorMsg = detail || `服务器错误: ${status}`
      }
    } else if (error.request) {
      errorMsg = '❌ 无法连接到服务器，请检查：\n1. 后端服务是否启动\n2. 网络连接是否正常\n3. 防火墙设置'
      ElMessage({ message: errorMsg, type: 'error', duration: 5000, showClose: true })
      return
    }
    ElMessage.error(errorMsg)
  } finally {
    clearInterval(progressInterval)
    aiPredicting.value = false
    loadingProgress.value = 0
  }
}

// AI 药品查询
async function handleAIMedicineQuery() {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入药品名称')
    return
  }

  aiMedicineQuerying.value = true
  aiMedicineResult.value = null

  try {
    const response: any = await aiDoctorAPI.queryMedicine(searchQuery.value.trim())
    aiMedicineResult.value = response.suggestion
    ElMessage.success('✅ 已生成 AI 药品查询结果')
  } catch (error: any) {
    let errorMsg = 'AI 服务暂时不可用，请稍后重试'
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      if (status === 404) errorMsg = '❌ AI 服务接口未找到'
      else if (status === 500) errorMsg = '❌ 服务器内部错误：' + (detail || '请检查后端日志')
      else errorMsg = detail || `服务器错误: ${status}`
    }
    ElMessage.error(errorMsg)
  } finally {
    aiMedicineQuerying.value = false
  }
}

// AI 疾病查询
async function handleAIDiseaseQuery() {
  if (!diseaseQuery.value.trim()) {
    ElMessage.warning('请输入疾病名称')
    return
  }

  aiDiseaseQuerying.value = true
  aiDiseaseResult.value = null

  try {
    const response: any = await aiDoctorAPI.queryDisease(diseaseQuery.value.trim())
    aiDiseaseResult.value = response.suggestion
    ElMessage.success('✅ 已生成 AI 疾病查询结果')
  } catch (error: any) {
    let errorMsg = 'AI 服务暂时不可用，请稍后重试'
    if (error.response) {
      const status = error.response.status
      const detail = error.response.data?.detail
      if (status === 404) errorMsg = '❌ AI 服务接口未找到'
      else if (status === 500) errorMsg = '❌ 服务器内部错误：' + (detail || '请检查后端日志')
      else errorMsg = detail || `服务器错误: ${status}`
    }
    ElMessage.error(errorMsg)
  } finally {
    aiDiseaseQuerying.value = false
  }
}

// 格式化 AI 建议
function formatAISuggestion(text: string): string {
  if (!text) return ''
  let formatted = text.replace(/【([^】]+)】/g, '<h3 class="ai-section-title">$1</h3>')
  formatted = formatted.replace(/\n/g, '<br>')
  formatted = formatted.replace(/^(\d+\.)\s/gm, '<strong class="ai-number">$1</strong> ')
  formatted = formatted.replace(/(⚠️|❌|✅|💡|⚡)\s*([^：：<]+)/g, '<span class="ai-highlight">$1 $2</span>')
  return formatted
}
</script>

<style scoped>
.doctor-view {
  width: 100%;
  height: 100%;
}

.ai-predict-card {
  margin-bottom: 20px;
  border: 2px solid #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
  transition: all 0.3s ease;
}

.ai-predict-card:hover {
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
  transform: translateY(-2px);
}

.ai-predict-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
  font-size: 16px;
}

.search-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.search-card :deep(.el-form-item__label) {
  color: white;
  font-weight: bold;
}

.result-card {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* AI 加载状态 */
.ai-loading {
  margin-top: 20px;
  padding: 30px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4f8 100%);
  border-radius: 12px;
  border: 2px solid #409eff;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(64, 158, 255, 0);
  }
}

.ai-loading .loading-text {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
}

.ai-loading .loading-tips {
  margin-top: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: #606266;
}

/* AI 建议卡片样式 */
.ai-suggestion-card {
  margin-top: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.15);
  animation: fadeIn 0.5s ease-in;
}

.ai-suggestion-card :deep(.el-alert__content) {
  width: 100%;
}

.ai-suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
}

.ai-suggestion-title {
  font-size: 18px;
  font-weight: bold;
  color: #67c23a;
}

.ai-suggestion-content {
  line-height: 2;
  color: #333;
  font-size: 15px;
  background: linear-gradient(135deg, #f9fdf6 0%, #ffffff 100%);
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #67c23a;
}

/* AI 结果卡片 */
.ai-result-card {
  animation: fadeIn 0.5s ease-in;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(230, 162, 60, 0.15);
}

.ai-result-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  font-weight: bold;
}

/* AI 建议内容样式 */
.ai-suggestion-content :deep(.ai-section-title) {
  font-size: 16px;
  font-weight: bold;
  color: #409eff;
  margin: 15px 0 10px 0;
  padding-left: 10px;
  border-left: 3px solid #409eff;
  background: linear-gradient(90deg, rgba(64, 158, 255, 0.1) 0%, transparent 100%);
  padding: 8px 0 8px 10px;
}

.ai-suggestion-content :deep(.ai-number) {
  color: #e6a23c;
  font-weight: bold;
  margin-right: 5px;
}

.ai-suggestion-content :deep(.ai-highlight) {
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.15) 0%, transparent 100%);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  color: #d97706;
  display: inline-block;
  margin: 2px 0;
}
</style>
