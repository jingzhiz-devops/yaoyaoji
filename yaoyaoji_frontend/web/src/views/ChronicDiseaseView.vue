<template>
  <div class="chronic-disease-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>慢性病管理</h1>
      <div class="header-actions">
        <el-button text type="primary" @click="goToStats">
          <el-icon><DataAnalysis /></el-icon>
          统计分析
        </el-button>
        <el-button type="primary" @click="openCreateDialog">
          <el-icon><Plus /></el-icon>
          添加慢性病
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-input
        v-model="searchText"
        placeholder="搜索疾病名称..."
        clearable
        style="width: 200px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>

      <el-select
        v-model="filterStatus"
        placeholder="选择控制状态"
        clearable
        style="width: 150px; margin-left: 10px"
      >
        <el-option label="控制良好" value="good" />
        <el-option label="控制中等" value="fair" />
        <el-option label="控制不良" value="poor" />
      </el-select>

      <el-button @click="handleSearch" style="margin-left: 10px">搜索</el-button>
    </div>

    <!-- 疾病列表 -->
    <div class="disease-list">
      <div
        v-for="disease in diseases"
        :key="disease.id"
        class="disease-card"
        @click="selectDisease(disease)"
      >
        <div class="card-header">
          <div class="disease-title">
            <h3>{{ disease.disease_name }}</h3>
            <el-tag :type="getStatusType(disease.control_status)" effect="light">
              {{ getStatusText(disease.control_status) }}
            </el-tag>
          </div>
          <el-dropdown @command="handleCommand">
            <el-icon style="cursor: pointer"><MoreFilled /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit" :command-value="disease.id">编辑</el-dropdown-item>
                <el-dropdown-item command="delete" :command-value="disease.id">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="card-content">
          <div v-if="disease.icd10_code" class="info-item">
            <span class="label">ICD-10编码:</span>
            <span class="value">{{ disease.icd10_code }}</span>
          </div>
          <div v-if="disease.diagnosis_date" class="info-item">
            <span class="label">诊断日期:</span>
            <span class="value">{{ formatDate(disease.diagnosis_date) }}</span>
          </div>
          <div v-if="disease.diagnosis_hospital" class="info-item">
            <span class="label">诊疗医院:</span>
            <span class="value">{{ disease.diagnosis_hospital }}</span>
          </div>
          <div v-if="disease.current_treatment" class="info-item">
            <span class="label">当前治疗:</span>
            <span class="value">{{ disease.current_treatment }}</span>
          </div>
        </div>

        <div class="card-footer">
          <el-button text type="primary" @click.stop="viewDetails(disease)">
            查看详情
          </el-button>
          <el-button text type="success" @click.stop="showIndicatorDialog(disease)">
            记录指标
          </el-button>
          <el-button text type="warning" @click.stop="showFollowupDialog(disease)">
            安排随访
          </el-button>
        </div>
      </div>

      <el-empty v-if="diseases.length === 0" description="暂无慢性病记录" />
    </div>

    <!-- 创建/编辑慢性病对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingDisease ? '编辑慢性病' : '添加慢性病'"
      width="700px"
    >
      <!-- 中国10大慢性病快捷选择 -->
      <div v-if="!editingDisease" class="disease-templates" style="margin-bottom: 20px">
        <div style="margin-bottom: 10px; font-weight: 500; color: #606266">
          常见慢性病快捷选择：
        </div>
        <el-space wrap>
          <el-tag
            v-for="template in diseaseTemplates"
            :key="template.name"
            class="disease-tag"
            effect="plain"
            @click="selectDiseaseTemplate(template)"
            style="cursor: pointer; padding: 8px 12px"
          >
            {{ template.name }}
          </el-tag>
          <el-tag
            class="disease-tag"
            type="info"
            effect="plain"
            @click="clearDiseaseTemplate"
            style="cursor: pointer; padding: 8px 12px"
          >
            自定义
          </el-tag>
        </el-space>
      </div>

      <el-form ref="diseaseFormRef" :model="diseaseForm" label-width="100px">
        <el-form-item label="疾病名称" prop="disease_name" required>
          <el-input v-model="diseaseForm.disease_name" placeholder="请输入疾病名称" />
        </el-form-item>

        <el-form-item label="ICD-10编码">
          <el-input v-model="diseaseForm.icd10_code" placeholder="可选" />
        </el-form-item>

        <el-form-item label="诊断日期">
          <el-date-picker v-model="diseaseForm.diagnosis_date" type="date" placeholder="选择日期" />
        </el-form-item>

        <el-form-item label="诊疗医院">
          <el-input v-model="diseaseForm.diagnosis_hospital" placeholder="可选" />
        </el-form-item>

        <el-form-item label="主治医生">
          <el-input v-model="diseaseForm.diagnosis_doctor" placeholder="可选" />
        </el-form-item>

        <el-form-item label="当前治疗">
          <el-input
            v-model="diseaseForm.current_treatment"
            type="textarea"
            rows="3"
            placeholder="描述当前治疗方案"
          />
        </el-form-item>

        <el-form-item label="控制状态">
          <el-radio-group v-model="diseaseForm.control_status">
            <el-radio value="good">控制良好</el-radio>
            <el-radio value="fair">控制中等</el-radio>
            <el-radio value="poor">控制不良</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveDisease">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 记录指标对话框 -->
    <el-dialog v-model="showIndicator" title="记录指标" width="600px">
      <div v-if="selectedForIndicator">
        <el-select
          v-model="selectedIndicatorId"
          placeholder="选择指标"
          style="width: 100%; margin-bottom: 10px"
        >
          <el-option
            v-for="indicator in selectedForIndicator.indicators || []"
            :key="indicator.id"
            :label="indicator.indicator_name"
            :value="indicator.id"
          />
        </el-select>

        <el-input
          v-model="indicatorValue"
          type="number"
          placeholder="输入测量值"
          style="margin-bottom: 10px"
        />

        <el-input
          v-model="indicatorNotes"
          type="textarea"
          rows="3"
          placeholder="备注"
        />
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showIndicator = false">取消</el-button>
          <el-button type="primary" @click="handleRecordIndicator">记录</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 安排随访对话框 -->
    <el-dialog v-model="showFollowup" title="安排随访" width="600px">
      <el-form ref="followupFormRef" :model="followupForm" label-width="100px">
        <el-form-item label="随访频率" prop="frequency" required>
          <el-select v-model="followupForm.frequency" placeholder="选择随访频率">
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="每季度" value="quarterly" />
            <el-option label="每半年" value="half-yearly" />
            <el-option label="每年" value="yearly" />
          </el-select>
        </el-form-item>

        <el-form-item label="下次随访日期" prop="next_followup_date" required>
          <el-date-picker
            v-model="followupForm.next_followup_date"
            type="date"
            placeholder="选择日期"
          />
        </el-form-item>

        <el-form-item label="责任医生">
          <el-input v-model="followupForm.responsible_doctor" placeholder="可选" />
        </el-form-item>

        <el-form-item label="提醒天数">
          <el-input-number v-model="followupForm.reminder_days" :min="1" :max="30" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showFollowup = false">取消</el-button>
          <el-button type="primary" @click="handleCreateFollowup">创建随访计划</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, MoreFilled, DataAnalysis } from '@element-plus/icons-vue'
import { chronicDiseaseAPI } from '@/api/chronic-disease'
import type { ChronicDisease } from '@/types'

// 中国10大慢性病模板（带预定义的监控指标）
const diseaseTemplates = [
  {
    name: '高血压',
    icd10_code: 'I10',
    indicators: [
      { indicator_name: '收缩压', normal_range_min: 90, normal_range_max: 140, unit: 'mmHg', check_frequency: 'daily' },
      { indicator_name: '舒张压', normal_range_min: 60, normal_range_max: 90, unit: 'mmHg', check_frequency: 'daily' },
      { indicator_name: '心率', normal_range_min: 60, normal_range_max: 100, unit: '次/分', check_frequency: 'daily' }
    ],
    treatment_tips: '低盐饮食、规律运动、控制体重、按时服药'
  },
  {
    name: '糖尿病',
    icd10_code: 'E11',
    indicators: [
      { indicator_name: '空腹血糖', normal_range_min: 3.9, normal_range_max: 7.0, unit: 'mmol/L', check_frequency: 'daily' },
      { indicator_name: '餐后2小时血糖', normal_range_min: null, normal_range_max: 10.0, unit: 'mmol/L', check_frequency: 'daily' },
      { indicator_name: '糖化血红蛋白', normal_range_min: null, normal_range_max: 7.0, unit: '%', check_frequency: 'monthly' }
    ],
    treatment_tips: '控制饮食、适量运动、定期监测血糖、遵医嘴用药'
  },
  {
    name: '冠心病',
    icd10_code: 'I25',
    indicators: [
      { indicator_name: '心率', normal_range_min: 60, normal_range_max: 100, unit: '次/分', check_frequency: 'daily' },
      { indicator_name: '血压', normal_range_min: 90, normal_range_max: 140, unit: 'mmHg', check_frequency: 'daily' },
      { indicator_name: '总胆固醇', normal_range_min: null, normal_range_max: 5.2, unit: 'mmol/L', check_frequency: 'monthly' }
    ],
    treatment_tips: '避免过度劳累、低脂饮食、戒烟限酒、定期复查'
  },
  {
    name: '高血脂',
    icd10_code: 'E78',
    indicators: [
      { indicator_name: '总胆固醇', normal_range_min: 2.8, normal_range_max: 5.2, unit: 'mmol/L', check_frequency: 'monthly' },
      { indicator_name: '甘油三酯', normal_range_min: null, normal_range_max: 1.7, unit: 'mmol/L', check_frequency: 'monthly' },
      { indicator_name: '低密度脂蛋白', normal_range_min: null, normal_range_max: 3.4, unit: 'mmol/L', check_frequency: 'monthly' },
      { indicator_name: '高密度脂蛋白', normal_range_min: 1.0, normal_range_max: null, unit: 'mmol/L', check_frequency: 'monthly' }
    ],
    treatment_tips: '低脂饮食、增加运动、控制体重、必要时服用降脂药'
  },
  {
    name: '慢性肾病',
    icd10_code: 'N18',
    indicators: [
      { indicator_name: '血背酸酯', normal_range_min: 44, normal_range_max: 133, unit: 'μmol/L', check_frequency: 'monthly' },
      { indicator_name: '尿蛋白', normal_range_min: null, normal_range_max: 150, unit: 'mg/24h', check_frequency: 'monthly' },
      { indicator_name: '血压', normal_range_min: 90, normal_range_max: 130, unit: 'mmHg', check_frequency: 'daily' }
    ],
    treatment_tips: '低盐低蛋白饮食、控制血压、避免肾毒性药物、定期检查'
  },
  {
    name: '甲状腺疾病',
    icd10_code: 'E07',
    indicators: [
      { indicator_name: 'TSH', normal_range_min: 0.27, normal_range_max: 4.2, unit: 'mIU/L', check_frequency: 'monthly' },
      { indicator_name: 'FT3', normal_range_min: 3.1, normal_range_max: 6.8, unit: 'pmol/L', check_frequency: 'monthly' },
      { indicator_name: 'FT4', normal_range_min: 12, normal_range_max: 22, unit: 'pmol/L', check_frequency: 'monthly' }
    ],
    treatment_tips: '遵医嘴服药、定期检查甲功、保持良好作息'
  },
  {
    name: '慢阻肺',
    icd10_code: 'J44',
    indicators: [
      { indicator_name: '血氧饱和度', normal_range_min: 95, normal_range_max: 100, unit: '%', check_frequency: 'daily' },
      { indicator_name: '呼吸频率', normal_range_min: 12, normal_range_max: 20, unit: '次/分', check_frequency: 'daily' }
    ],
    treatment_tips: '戒烟、避免空气污染、呼吸功能锻炼、遵医嘴用药'
  },
  {
    name: '骨质疏松',
    icd10_code: 'M81',
    indicators: [
      { indicator_name: '骨密度T值', normal_range_min: -1.0, normal_range_max: null, unit: 'SD', check_frequency: 'yearly' },
      { indicator_name: '血钙', normal_range_min: 2.1, normal_range_max: 2.7, unit: 'mmol/L', check_frequency: 'monthly' }
    ],
    treatment_tips: '补充钙和维生素D、适量运动、防摔倒、定期检查'
  },
  {
    name: '风湿性关节炎',
    icd10_code: 'M06',
    indicators: [
      { indicator_name: '红细胞沉降率', normal_range_min: null, normal_range_max: 15, unit: 'mm/h', check_frequency: 'monthly' },
      { indicator_name: 'C反应蛋白', normal_range_min: null, normal_range_max: 10, unit: 'mg/L', check_frequency: 'monthly' }
    ],
    treatment_tips: '遵医嘴用药、适度锻炼、保持关节保暖、定期复查'
  },
  {
    name: '脂肪肝',
    icd10_code: 'K76.0',
    indicators: [
      { indicator_name: '谷丙转氨酶', normal_range_min: null, normal_range_max: 40, unit: 'U/L', check_frequency: 'monthly' },
      { indicator_name: '谷草转氨酶', normal_range_min: null, normal_range_max: 40, unit: 'U/L', check_frequency: 'monthly' },
      { indicator_name: '体重指数', normal_range_min: 18.5, normal_range_max: 24, unit: 'kg/m²', check_frequency: 'weekly' }
    ],
    treatment_tips: '控制体重、低脂饮食、适量运动、戒酒、定期检查'
  }
]

// 状态管理
const diseases = ref<ChronicDisease[]>([])
const loading = ref(false)
const searchText = ref('')
const filterStatus = ref('')

// 对话框状态
const showCreateDialog = ref(false)
const showIndicator = ref(false)
const showFollowup = ref(false)

// 表单数据
const diseaseForm = ref({
  disease_name: '',
  icd10_code: '',
  diagnosis_date: '',
  diagnosis_hospital: '',
  diagnosis_doctor: '',
  current_treatment: '',
  control_status: 'fair'
})

const followupForm = ref({
  frequency: 'monthly',
  next_followup_date: '',
  responsible_doctor: '',
  reminder_days: 7
})

const router = useRouter()
const editingDisease = ref<ChronicDisease | null>(null)
const selectedForIndicator = ref<ChronicDisease | null>(null)
const selectedIndicatorId = ref<number | null>(null)
const indicatorValue = ref('')
const indicatorNotes = ref('')

const diseaseFormRef = ref()
const followupFormRef = ref()

// 选中的疾病模板
const selectedTemplate = ref<any>(null)

// 选择疾病模板
const selectDiseaseTemplate = (template: any) => {
  selectedTemplate.value = template
  diseaseForm.value.disease_name = template.name
  diseaseForm.value.icd10_code = template.icd10_code
  diseaseForm.value.current_treatment = template.treatment_tips
  ElMessage.success(`已选择 ${template.name}，保存后将自动添加监控指标`)
}

// 清空模板选择（自定义）
const clearDiseaseTemplate = () => {
  selectedTemplate.value = null
  resetForm()
  ElMessage.info('已切换为自定义模式')
}

// 打开创建对话框
const openCreateDialog = () => {
  console.log('点击了添加慢性病按钮') // 调试日志
  resetForm()
  selectedTemplate.value = null
  editingDisease.value = null
  showCreateDialog.value = true
  console.log('对话框状态:', showCreateDialog.value) // 调试日志
}

// 加载慢性病列表
const loadDiseases = async () => {
  loading.value = true
  try {
    const response = await chronicDiseaseAPI.list({
      search: searchText.value || undefined,
      control_status: filterStatus.value || undefined
    })
    diseases.value = response.data
  } catch (error) {
    ElMessage.error('加载慢性病列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  loadDiseases()
}

// 查看详情
const viewDetails = (disease: ChronicDisease) => {
  router.push(`/chronic-disease/${disease.id}`)
}

// 显示指标记录对话框
const showIndicatorDialog = (disease: ChronicDisease) => {
  selectedForIndicator.value = disease
  selectedIndicatorId.value = null
  indicatorValue.value = ''
  indicatorNotes.value = ''
  showIndicator.value = true
}

// 显示随访对话框
const showFollowupDialog = (disease: ChronicDisease) => {
  const nextDate = new Date()
  nextDate.setMonth(nextDate.getMonth() + 1)
  followupForm.value = {
    frequency: 'monthly',
    next_followup_date: nextDate.toISOString().split('T')[0],
    responsible_doctor: '',
    reminder_days: 7
  }
  selectedForIndicator.value = disease
  showFollowup.value = true
}

// 选中疾病
const selectDisease = (disease: ChronicDisease) => {
  console.log('选中疾病:', disease)
}

// 保存慢性病
const handleSaveDisease = async () => {
  try {
    let diseaseId: number
    
    if (editingDisease.value) {
      await chronicDiseaseAPI.update(editingDisease.value.id, diseaseForm.value)
      diseaseId = editingDisease.value.id
      ElMessage.success('更新成功')
    } else {
      const response = await chronicDiseaseAPI.create(diseaseForm.value)
      diseaseId = response.data.id
      ElMessage.success('添加成功')
      
      // 如果选择了疾病模板，自动添加监控指标
      if (selectedTemplate.value && selectedTemplate.value.indicators) {
        for (const indicator of selectedTemplate.value.indicators) {
          try {
            await chronicDiseaseAPI.indicators.add(diseaseId, indicator)
          } catch (error) {
            console.error('添加指标失败:', indicator.indicator_name)
          }
        }
        ElMessage.success(`已自动添加 ${selectedTemplate.value.indicators.length} 个监控指标`)
      }
    }
    
    showCreateDialog.value = false
    editingDisease.value = null
    selectedTemplate.value = null
    resetForm()
    loadDiseases()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 记录指标
const handleRecordIndicator = async () => {
  if (!selectedForIndicator.value || !selectedIndicatorId.value || !indicatorValue.value) {
    ElMessage.warning('请填写完整信息')
    return
  }

  try {
    await chronicDiseaseAPI.indicatorRecords.create(selectedForIndicator.value.id, {
      indicator_id: selectedIndicatorId.value,
      value: parseFloat(indicatorValue.value),
      measurement_date: new Date().toISOString(),
      notes: indicatorNotes.value || undefined
    })
    ElMessage.success('记录成功')
    showIndicator.value = false
    loadDiseases()
  } catch (error) {
    ElMessage.error('记录失败')
  }
}

// 创建随访计划
const handleCreateFollowup = async () => {
  if (!selectedForIndicator.value || !followupForm.value.next_followup_date) {
    ElMessage.warning('请填写必要信息')
    return
  }

  try {
    await chronicDiseaseAPI.followupPlans.create(selectedForIndicator.value.id, followupForm.value)
    ElMessage.success('随访计划创建成功')
    showFollowup.value = false
    loadDiseases()
  } catch (error) {
    ElMessage.error('创建失败')
  }
}

// 处理下拉菜单命令
const handleCommand = (command: string, value?: number) => {
  if (command === 'edit' && value) {
    const disease = diseases.value.find(d => d.id === value)
    if (disease) {
      editingDisease.value = disease
      diseaseForm.value = {
        disease_name: disease.disease_name,
        icd10_code: disease.icd10_code || '',
        diagnosis_date: disease.diagnosis_date || '',
        diagnosis_hospital: disease.diagnosis_hospital || '',
        diagnosis_doctor: disease.diagnosis_doctor || '',
        current_treatment: disease.current_treatment || '',
        control_status: disease.control_status
      }
      showCreateDialog.value = true
    }
  } else if (command === 'delete' && value) {
    handleDeleteDisease(value)
  }
}

// 删除慢性病
const handleDeleteDisease = (diseaseId: number) => {
  ElMessageBox.confirm('确认删除该慢性病记录？', 'Warning', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(async () => {
    try {
      await chronicDiseaseAPI.delete(diseaseId)
      ElMessage.success('删除成功')
      loadDiseases()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

// 重置表单
const resetForm = () => {
  diseaseForm.value = {
    disease_name: '',
    icd10_code: '',
    diagnosis_date: '',
    diagnosis_hospital: '',
    diagnosis_doctor: '',
    current_treatment: '',
    control_status: 'fair'
  }
  editingDisease.value = null
}

// 获取状态类型
const getStatusType = (status: string): 'success' | 'warning' | 'danger' | 'info' => {
  const statusMap = {
    good: 'success' as const,
    fair: 'warning' as const,
    poor: 'danger' as const
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

// 获取状态文本
const getStatusText = (status: string): string => {
  const statusMap = {
    good: '控制良好',
    fair: '控制中等',
    poor: '控制不良'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

// 格式化日期
const formatDate = (date: string): string => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const goToStats = () => {
  router.push('/chronic-disease-stats')
}

// 组件挂载
onMounted(() => {
  loadDiseases()
})
</script>

<style scoped lang="scss">
.chronic-disease-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h1 {
    margin: 0;
    font-size: 28px;
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.filter-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}

.disease-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 20px;
}

.disease-card {
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    border-color: #409eff;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;

    .disease-title {
      display: flex;
      align-items: center;
      gap: 10px;

      h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
      }
    }
  }

  .card-content {
    margin-bottom: 15px;

    .info-item {
      display: flex;
      margin-bottom: 8px;
      font-size: 14px;

      .label {
        color: #606266;
        min-width: 80px;
      }

      .value {
        color: #303133;
        flex: 1;
      }
    }
  }

  .card-footer {
    display: flex;
    gap: 10px;
    padding-top: 15px;
    border-top: 1px solid #ebeef5;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.disease-templates {
  .disease-tag {
    transition: all 0.3s;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
    }
  }
}
</style>
