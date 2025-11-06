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
          <el-tag type="warning" size="small">功能开发中</el-tag>
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

      <!-- AI 建议结果 -->
      <el-alert
        v-if="aiSuggestion"
        type="success"
        :closable="false"
        style="margin-top: 20px;"
      >
        <template #title>
          <div style="font-size: 16px; font-weight: bold; margin-bottom: 10px;">
            👨‍⚕️ AI 区生建议
          </div>
        </template>
        <div style="line-height: 1.8; white-space: pre-wrap;">{{ aiSuggestion }}</div>
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
        <span>查询药品</span>
      </template>
      <el-form :inline="true">
        <el-form-item label="查询药品">
          <el-input
            v-model="searchQuery"
            placeholder="请输入药品名称（支持模糊，如：芬缓）"
            style="width: 300px"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" :loading="searching">查询</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="medicineResults.length > 0" class="result-card" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>药品搜索结果</span>
          <el-tag type="info">共 {{ medicineResults.length }} 条</el-tag>
        </div>
      </template>
      <el-tag
        v-for="m in medicineResults"
        :key="m.id"
        style="margin-right: 8px; margin-bottom: 8px; cursor: pointer;"
        @click="currentMedicine = m"
      >
        {{ m.name }}<span v-if="m.generic_name">（{{ m.generic_name }}）</span>
      </el-tag>
    </el-card>

    <el-card class="search-card" style="margin-top: 20px;">
      <template #header>
        <span>查询疾病</span>
      </template>
      <el-form :inline="true">
        <el-form-item label="疾病名称">
          <el-input
            v-model="diseaseQuery"
            placeholder="请输入疾病名称（支持模糊）"
            style="width: 280px"
            clearable
            @keyup.enter="handleDiseaseSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleDiseaseSearch" :loading="dSearching">查询</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="药品名称">
          <el-input
            v-model="medicineQueryForDisease"
            placeholder="输入药品名查询相关疾病"
            style="width: 280px"
            clearable
            @keyup.enter="handleDiseaseSearchByMedicine"
          >
            <template #append>
              <el-button :icon="Search" @click="handleDiseaseSearchByMedicine" :loading="dSearching">反查</el-button>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card v-if="diseaseResults.length > 0" class="result-card" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>疾病搜索结果</span>
          <el-tag type="info">共 {{ diseaseResults.length }} 条</el-tag>
        </div>
      </template>
      <el-tag
        v-for="d in diseaseResults"
        :key="d.id || d.name"
        style="margin-right: 8px; margin-bottom: 8px; cursor: pointer;"
        @click="currentDisease = d"
      >
        {{ d.name }}
      </el-tag>
    </el-card>

    <el-card v-if="currentDisease" class="result-card" style="margin-top: 10px;">
      <template #header>
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 18px; font-weight: bold;">疾病详情</span>
          <el-tag type="info">{{ currentDisease.name }}</el-tag>
        </div>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="别名" v-if="parseList(currentDisease.aliases).length">
          <el-tag v-for="a in parseList(currentDisease.aliases)" :key="a" style="margin-right: 6px;">{{ a }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="简介">{{ currentDisease.description }}</el-descriptions-item>
        <el-descriptions-item label="常用药物" v-if="parseList(currentDisease.recommended).length">
          <el-tag type="success" v-for="m in parseList(currentDisease.recommended)" :key="m" style="margin-right: 6px;">{{ m }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="避免搭配" v-if="parseList(currentDisease.avoid).length">
          <el-tag type="danger" v-for="x in parseList(currentDisease.avoid)" :key="x" style="margin-right: 6px;">{{ x }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card

    <!-- 查询结果 -->
    <el-card v-if="currentMedicine" class="result-card" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 20px; font-weight: bold;">{{ currentMedicine.name }}</span>
          <el-tag type="success" v-if="currentMedicine.generic_name">{{ currentMedicine.generic_name }}</el-tag>
        </div>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="药品名称">
          <span style="font-size: 16px; font-weight: bold;">{{ currentMedicine.name }}</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="通用名" v-if="currentMedicine.generic_name">
          {{ currentMedicine.generic_name }}
        </el-descriptions-item>

        <el-descriptions-item label="生产厂家" v-if="currentMedicine.manufacturer">
          {{ currentMedicine.manufacturer }}
        </el-descriptions-item>

        <el-descriptions-item label="主要成分">
          <el-tag type="info" style="margin-right: 5px;" v-for="(ingredient, index) in parseIngredients(currentMedicine)" :key="index">
            {{ ingredient }}
          </el-tag>
          <span v-if="!currentMedicine.ingredients" style="color: #909399;">暂无成分信息</span>
        </el-descriptions-item>

        <el-descriptions-item label="功效与作用">
          <div style="line-height: 1.8;">
            {{ currentMedicine.efficacy || '暂无功效信息' }}
          </div>
        </el-descriptions-item>

        <el-descriptions-item label="禁忌信息">
          <el-alert
            :title="currentMedicine.contraindications || '暂无禁忌信息'"
            type="warning"
            :closable="false"
            show-icon
          />
        </el-descriptions-item>

        <el-descriptions-item label="副作用">
          <div style="line-height: 1.8;">
            {{ currentMedicine.side_effects || '暂无副作用信息' }}
          </div>
        </el-descriptions-item>

        <el-descriptions-item label="不能搭配服用">
          <el-alert
            v-if="conflicts.length > 0"
            type="error"
            :closable="false"
            show-icon
          >
            <template #title>
              <div v-for="conflict in conflicts" :key="conflict.medicine_2" style="margin-bottom: 10px;">
                <strong>{{ conflict.medicine_2 }}</strong>: {{ conflict.warning }}
              </div>
            </template>
          </el-alert>
          <span v-else style="color: #67c23a;">✓ 暂无已知药物冲突</span>
        </el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 20px; text-align: right;">
        <el-button type="primary" @click="addToBox" v-if="!isInBox">添加到药箱</el-button>
        <el-button type="info" disabled v-else>已在药箱中</el-button>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-if="!currentMedicine && !searching" description="请输入药品名称进行查询" />

    <!-- 历史查询记录 -->
    <el-card v-if="searchHistory.length > 0" style="margin-top: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>最近查询</span>
          <el-button size="small" text @click="clearHistory">清空</el-button>
        </div>
      </template>
      <el-tag
        v-for="item in searchHistory"
        :key="item"
        style="margin-right: 10px; margin-bottom: 10px; cursor: pointer;"
        @click="searchQuery = item; handleSearch()"
      >
        {{ item }}
      </el-tag>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { medicineAPI, userMedicationAPI, diseaseAPI } from '@/api'
import { useMedicationStore } from '@/stores/medication'

const medicationStore = useMedicationStore()
const searchQuery = ref('')
const searching = ref(false)
const currentMedicine = ref<any>(null)
const diseaseQuery = ref('')
const medicineQueryForDisease = ref('')
const searchHistory = ref<string[]>([])
const conflicts = ref<any[]>([])
const dSearching = ref(false)
const diseaseResults = ref<any[]>([])
const medicineResults = ref<any[]>([])
const currentDisease = ref<any>(null)

// AI 预测相关状态
const symptomDescription = ref('')
const aiPredicting = ref(false)
const aiSuggestion = ref<string | null>(null)

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

  searching.value = true
  try {
    const data: any = await medicineAPI.list({ search: searchQuery.value })
    medicineResults.value = Array.isArray(data) ? data : []

    // 客户端兜底：若服务端未命中，再全量拉取后前端模糊匹配
    if (medicineResults.value.length === 0) {
      const all: any = await medicineAPI.list()
      const q = searchQuery.value.trim()
      medicineResults.value = (Array.isArray(all) ? all : []).filter((m: any) => {
        const hay = [m.name, m.generic_name, m.manufacturer, m.ingredients, m.efficacy, m.contraindications]
          .filter(Boolean)
          .join(' ')
        return hay.includes(q)
      })
    }

    if (medicineResults.value.length > 0) {
      currentMedicine.value = medicineResults.value[0]
      if (!searchHistory.value.includes(searchQuery.value)) {
        searchHistory.value.unshift(searchQuery.value)
        if (searchHistory.value.length > 5) searchHistory.value.pop()
      }
      await checkConflicts()
    } else {
      ElMessage.warning('未找到该药品信息')
      currentMedicine.value = null
    }
  } catch (error: any) {
    console.error('❌ 药品查询错误:', error)
    ElMessage.error('查询失败：' + (error.response?.data?.detail || error.message))
  } finally {
    searching.value = false
  }
}

async function handleDiseaseSearch() {
  if (!diseaseQuery.value.trim()) return
  dSearching.value = true
  try {
    let data: any = await diseaseAPI.list({ search: diseaseQuery.value })
    diseaseResults.value = Array.isArray(data) ? data : []

    // 客户端兜底：若服务端未命中，再全量拉取后前端模糊匹配（名称/别名/简介）
    if (diseaseResults.value.length === 0) {
      data = await diseaseAPI.list()
      const q = diseaseQuery.value.trim()
      diseaseResults.value = (Array.isArray(data) ? data : []).filter((d: any) => {
        const hay = [d.name, d.aliases, d.description].filter(Boolean).join(' ')
        return hay.includes(q)
      })
    }

    currentDisease.value = diseaseResults.value[0] || null
  } catch (e) {
    console.error('❌ 疾病查询错误:', e)
  } finally {
    dSearching.value = false
  }
}

async function handleDiseaseSearchByMedicine() {
  if (!medicineQueryForDisease.value.trim()) {
    ElMessage.warning('请输入药品名称')
    return
  }
  
  dSearching.value = true
  try {
    let data: any = await diseaseAPI.list({ medicine_name: medicineQueryForDisease.value })
    diseaseResults.value = Array.isArray(data) ? data : []

    // 客户端兜底：若服务端未命中，再全量拉取后在推荐药物字段中模糊匹配
    if (diseaseResults.value.length === 0) {
      data = await diseaseAPI.list()
      const q = medicineQueryForDisease.value.trim()
      diseaseResults.value = (Array.isArray(data) ? data : []).filter((d: any) => {
        const recommended = d.recommended || ''
        return recommended.includes(q)
      })
    }

    if (diseaseResults.value.length > 0) {
      currentDisease.value = diseaseResults.value[0]
      ElMessage.success(`找到 ${diseaseResults.value.length} 个相关疾病`)
    } else {
      ElMessage.warning(`未找到使用「${medicineQueryForDisease.value}」的相关疾病`)
      currentDisease.value = null
    }
  } catch (e) {
    console.error('❌ 药品反查疾病错误:', e)
    ElMessage.error('查询失败')
  } finally {
    dSearching.value = false
  }
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

  try {
    // TODO: 这里后续接入真实的 AI API
    // 暂时使用模拟响应
    await new Promise(resolve => setTimeout(resolve, 1500)) // 模拟网络请求

    // 模拟 AI 响应
    aiSuggestion.value = `根据您描述的症状，AI 初步分析如下：

【可能原因】
1. 普通感冒或流感
2. 上呼吸道感染
3. 疾病或病毒感染

【建议措施】
1. 多休息，保证充足睡眠
2. 多喝温水，保持水分补充
3. 清淡饮食，避免辛辣刺激食物
4. 可适当服用退烧药物（如对乙酰氨基酸）
5. 注意通风，保持室内空气清新

【就医建议】
如果出现以下情况，请立即就医：
- 体温超过39.5°C且持续不退
- 呼吸困难或胸痛
- 症状持续超过3天未好转
- 出现严重头痛、喉哙剧痛等

❗注意：此建议仅供参考，不代替专业医疗诊断。`

    ElMessage.success('已生成 AI 医疗建议')
  } catch (error: any) {
    console.error('❌ AI 预测错误:', error)
    ElMessage.error('AI 预测失败，请稍后重试')
  } finally {
    aiPredicting.value = false
  }
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
</style>
