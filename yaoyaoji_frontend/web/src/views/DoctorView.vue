<template>
  <div class="doctor-view-container">
    <div class="doctor-content">
      <el-row :gutter="24">
        <el-col :span="16">
          <!-- AI 智能诊断 -->
          <el-card class="feature-card ai-predict-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="header-title">
                  <el-icon class="header-icon"><FirstAidKit /></el-icon>
                  <span>智能症状分析</span>
                </div>
                <el-tag effect="dark" type="success" round>DeepSeek AI 驱动</el-tag>
              </div>
            </template>
            
            <div class="ai-input-section">
              <div class="input-wrapper">
                <el-input
                  v-model="symptomDescription"
                  type="textarea"
                  :rows="6"
                  placeholder="请详细描述您的身体不适症状，例如：头痛、发热、38.5度、喉咙痛、持续2天..."
                  maxlength="500"
                  show-word-limit
                  resize="none"
                  class="custom-textarea"
                />
                <div class="input-actions">
                  <el-button @click="symptomDescription = ''; aiSuggestion = null" plain>清空</el-button>
                  <el-button 
                    type="primary" 
                    :icon="Search" 
                    @click="handleAIPredict" 
                    :loading="aiPredicting"
                    :disabled="!symptomDescription.trim()"
                    class="submit-btn"
                  >
                    开始分析
                  </el-button>
                </div>
              </div>

              <!-- 加载状态 -->
              <div v-if="aiPredicting" class="ai-loading-state">
                <div class="loading-animation">
                  <div class="pulse-ring"></div>
                  <el-icon class="loading-icon is-loading"><Loading /></el-icon>
                </div>
                <div class="loading-text">
                  <h4>AI 正在深度分析您的症状...</h4>
                  <el-progress 
                    :percentage="loadingProgress" 
                    :stroke-width="6" 
                    status="success"
                    :show-text="false"
                    class="loading-progress"
                  />
                  <p>正在检索医学知识库，生成个性化建议</p>
                </div>
              </div>
              
              <!-- 分析结果 -->
              <div v-if="aiSuggestion" class="ai-result-container">
                <div class="result-header">
                  <span class="result-title">分析报告</span>
                  <div class="result-actions">
                    <el-button size="small" link>导出报告</el-button>
                  </div>
                </div>
                <div class="ai-markdown-content" v-html="formatAISuggestion(aiSuggestion)"></div>
                <div class="disclaimer">
                  <el-icon><Warning /></el-icon>
                  <span>AI建议仅供参考，不能替代专业医疗诊断。如症状严重或持续不缓解，请及时线下就医。</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <!-- 侧边栏：快速查询 -->
          <div class="sidebar-tools">
            <el-card class="tool-card medicine-search" shadow="hover">
              <div class="tool-header">
                <el-icon class="tool-icon"><Goods /></el-icon>
                <h3>药品百科</h3>
              </div>
              <p class="tool-desc">查询药品功效、用法及禁忌</p>
              <div class="search-box">
                <el-input
                  v-model="searchQuery"
                  placeholder="输入药品名称..."
                  @keyup.enter="handleSearch"
                >
                  <template #append>
                    <el-button :icon="Search" @click="handleSearch" :loading="aiMedicineQuerying" />
                  </template>
                </el-input>
              </div>
            </el-card>

            <el-card class="tool-card disease-search" shadow="hover">
              <div class="tool-header">
                <el-icon class="tool-icon"><Monitor /></el-icon>
                <h3>疾病查询</h3>
              </div>
              <p class="tool-desc">了解疾病症状、病因及治疗</p>
              <div class="search-box">
                <el-input
                  v-model="diseaseQuery"
                  placeholder="输入疾病名称..."
                  @keyup.enter="handleDiseaseSearch"
                >
                  <template #append>
                    <el-button :icon="Search" @click="handleDiseaseSearch" :loading="aiDiseaseQuerying" />
                  </template>
                </el-input>
              </div>
            </el-card>
          </div>
        </el-col>
      </el-row>

      <!-- 查询结果弹窗 -->
      <el-dialog
        v-model="resultDialogVisible"
        :title="resultTitle"
        width="600px"
        class="result-dialog"
        destroy-on-close
      >
        <div class="ai-markdown-content" v-html="formatAISuggestion(resultContent)"></div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Loading, FirstAidKit, Goods, Monitor, Warning } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { aiDoctorAPI, userMedicationAPI } from '@/api'
import { useMedicationStore } from '@/stores/medication'
import { marked } from 'marked'

const medicationStore = useMedicationStore()
const searchQuery = ref('')
const diseaseQuery = ref('')

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

// 结果弹窗
const resultDialogVisible = ref(false)
const resultTitle = ref('')
const resultContent = ref('')

async function handleSearch() {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入药品名称')
    return
  }
  await handleAIMedicineQuery()
}

async function handleDiseaseSearch() {
  if (!diseaseQuery.value.trim()) {
    ElMessage.warning('请输入疾病名称')
    return
  }
  await handleAIDiseaseQuery()
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
    ElMessage.success('分析完成')
  } catch (error: any) {
    handleError(error)
  } finally {
    clearInterval(progressInterval)
    aiPredicting.value = false
    loadingProgress.value = 0
  }
}

// AI 药品查询
async function handleAIMedicineQuery() {
  aiMedicineQuerying.value = true
  try {
    const response: any = await aiDoctorAPI.queryMedicine(searchQuery.value.trim())
    resultTitle.value = `💊 ${searchQuery.value} - 药品百科`
    resultContent.value = response.suggestion
    resultDialogVisible.value = true
  } catch (error: any) {
    handleError(error)
  } finally {
    aiMedicineQuerying.value = false
  }
}

// AI 疾病查询
async function handleAIDiseaseQuery() {
  aiDiseaseQuerying.value = true
  try {
    const response: any = await aiDoctorAPI.queryDisease(diseaseQuery.value.trim())
    resultTitle.value = `🏥 ${diseaseQuery.value} - 疾病百科`
    resultContent.value = response.suggestion
    resultDialogVisible.value = true
  } catch (error: any) {
    handleError(error)
  } finally {
    aiDiseaseQuerying.value = false
  }
}

function handleError(error: any) {
  let errorMsg = 'AI 服务暂时不可用，请稍后重试'
  if (error.response) {
    const status = error.response.status
    const detail = error.response.data?.detail
    if (status === 404) errorMsg = 'AI 服务接口未找到'
    else if (status === 500) errorMsg = '服务器内部错误'
    else errorMsg = detail || `服务器错误: ${status}`
  }
  ElMessage.error(errorMsg)
}

// 格式化 AI 建议 - 支持 Markdown
function formatAISuggestion(text: string): string {
  if (!text) return ''
  // 将【】风格标题转为 markdown 标题
  let processed = text.replace(/【([^】]+)】/g, '## $1')
  return marked.parse(processed, { async: false }) as string
}
</script>

<style scoped>
.doctor-view-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
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

/* Feature Card */
.feature-card {
  border: none;
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all 0.3s;
}

.ai-predict-card {
  border-top: 4px solid var(--color-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
}

.header-icon {
  font-size: 24px;
  color: var(--color-primary);
}

/* AI Input Section */
.ai-input-section {
  padding: 10px 0;
}

.custom-textarea :deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 16px;
  font-size: 15px;
  background-color: #f9fafb;
  border: 1px solid var(--color-border);
  transition: all 0.3s;
}

.custom-textarea :deep(.el-textarea__inner:focus) {
  background-color: white;
  box-shadow: 0 0 0 1px var(--color-primary);
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.submit-btn {
  padding-left: 24px;
  padding-right: 24px;
  font-weight: 600;
}

/* Loading State */
.ai-loading-state {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 40px;
  background: #f9fafb;
  border-radius: 12px;
}

.loading-animation {
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.loading-icon {
  font-size: 32px;
  color: var(--color-primary);
  z-index: 2;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: var(--color-primary);
  opacity: 0.2;
  animation: pulse 2s infinite;
}

.loading-text h4 {
  margin: 0 0 12px 0;
  color: var(--color-text-main);
}

.loading-text p {
  margin: 12px 0 0 0;
  font-size: 13px;
  color: var(--color-text-light);
}

.loading-progress {
  width: 300px;
  margin: 0 auto;
}

/* Result Container */
.ai-result-container {
  margin-top: 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  animation: slideUp 0.5s ease;
}

.result-header {
  background: #f0f9ff;
  padding: 16px 24px;
  border-bottom: 1px solid #e0f2fe;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-title {
  font-weight: 600;
  color: #0369a1;
  font-size: 16px;
}

.ai-markdown-content {
  padding: 24px;
  font-size: 15px;
  line-height: 1.5;
  color: #374151;
}

.disclaimer {
  background: #fff7ed;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #c2410c;
  font-size: 13px;
  border-top: 1px solid #ffedd5;
}

/* Sidebar Tools */
.sidebar-tools {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.tool-card {
  border: none;
  border-radius: var(--radius-md);
  transition: transform 0.3s;
}

.tool-card:hover {
  transform: translateY(-4px);
}

.medicine-search {
  background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
}

.disease-search {
  background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.tool-icon {
  font-size: 24px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
}

.tool-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.tool-desc {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #666;
}

.search-box :deep(.el-input-group__append) {
  background-color: rgba(255, 255, 255, 0.5);
  border-color: transparent;
}

.search-box :deep(.el-input__wrapper) {
  background-color: rgba(255, 255, 255, 0.8);
  box-shadow: none;
}

/* Markdown Styles */
.ai-markdown-content :deep(h1),
.ai-markdown-content :deep(h2),
.ai-markdown-content :deep(h3) {
  color: #0e7490;
  margin: 24px 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-markdown-content :deep(h1)::before,
.ai-markdown-content :deep(h2)::before,
.ai-markdown-content :deep(h3)::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 18px;
  background: #0e7490;
  border-radius: 2px;
  flex-shrink: 0;
}

.ai-markdown-content :deep(h1) { font-size: 20px; }
.ai-markdown-content :deep(h2) { font-size: 17px; }
.ai-markdown-content :deep(h3) { font-size: 15px; border-bottom: none; }

.ai-markdown-content :deep(h4),
.ai-markdown-content :deep(h5) {
  color: #374151;
  margin: 16px 0 8px 0;
  font-size: 15px;
}

.ai-markdown-content :deep(p) {
  margin: 8px 0;
  line-height: 1.8;
}

.ai-markdown-content :deep(ul),
.ai-markdown-content :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.ai-markdown-content :deep(li) {
  margin: 6px 0;
  line-height: 1.7;
}

.ai-markdown-content :deep(li)::marker {
  color: #0e7490;
  font-weight: 600;
}

.ai-markdown-content :deep(strong) {
  color: #1e293b;
  font-weight: 600;
}

.ai-markdown-content :deep(em) {
  color: #6b7280;
  font-style: italic;
}

.ai-markdown-content :deep(blockquote) {
  margin: 12px 0;
  padding: 12px 16px;
  border-left: 4px solid #0e7490;
  background: #f0f9ff;
  border-radius: 0 8px 8px 0;
  color: #334155;
}

.ai-markdown-content :deep(blockquote p) {
  margin: 4px 0;
}

.ai-markdown-content :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.9em;
  color: #be185d;
}

.ai-markdown-content :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
}

.ai-markdown-content :deep(pre code) {
  background: none;
  color: inherit;
  padding: 0;
}

.ai-markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 14px;
}

.ai-markdown-content :deep(th) {
  background: #f0f9ff;
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: #0e7490;
  border: 1px solid #e0f2fe;
}

.ai-markdown-content :deep(td) {
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
}

.ai-markdown-content :deep(tr:nth-child(even)) {
  background: #f9fafb;
}

.ai-markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #e5e7eb;
  margin: 20px 0;
}

@keyframes pulse {
  0% { transform: scale(0.8); opacity: 0.5; }
  100% { transform: scale(1.5); opacity: 0; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
