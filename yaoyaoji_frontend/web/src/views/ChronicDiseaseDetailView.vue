<template>
  <div class="disease-detail-view">
    <div class="detail-header">
      <el-button @click="goBack" text>
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
      <h1>{{ disease?.disease_name || '疾病详情' }}</h1>
      <div class="header-actions">
        <el-tag :type="getStatusType(disease?.control_status || 'fair')" effect="light">
          {{ getStatusText(disease?.control_status || 'fair') }}
        </el-tag>
      </div>
    </div>

    <div v-if="disease" class="detail-container">
      <!-- 基本信息 -->
      <el-card class="box-card" header="基本信息">
        <div class="info-grid">
          <div class="info-item" v-if="disease.icd10_code">
            <span class="label">ICD-10编码</span>
            <span class="value">{{ disease.icd10_code }}</span>
          </div>
          <div class="info-item" v-if="disease.diagnosis_date">
            <span class="label">诊断日期</span>
            <span class="value">{{ formatDate(disease.diagnosis_date) }}</span>
          </div>
          <div class="info-item" v-if="disease.diagnosis_hospital">
            <span class="label">诊疗医院</span>
            <span class="value">{{ disease.diagnosis_hospital }}</span>
          </div>
          <div class="info-item" v-if="disease.diagnosis_doctor">
            <span class="label">主治医生</span>
            <span class="value">{{ disease.diagnosis_doctor }}</span>
          </div>
          <div class="info-item" v-if="disease.current_treatment">
            <span class="label">当前治疗</span>
            <span class="value" style="grid-column: 2">{{ disease.current_treatment }}</span>
          </div>
        </div>
        <div class="card-actions">
          <el-button @click="editDisease">编辑基本信息</el-button>
        </div>
      </el-card>

      <!-- 关键指标 -->
      <el-card class="box-card" header="关键指标监测">
        <div v-if="disease.indicators && disease.indicators.length > 0" class="indicators-list">
          <div v-for="indicator in disease.indicators" :key="indicator.id" class="indicator-item">
            <div class="indicator-header">
              <span class="name">{{ indicator.indicator_name }}</span>
              <span v-if="indicator.unit" class="unit">{{ indicator.unit }}</span>
            </div>
            <div v-if="indicator.normal_range_min || indicator.normal_range_max" class="range">
              正常值范围: {{ indicator.normal_range_min }} - {{ indicator.normal_range_max }}
            </div>
            <div class="frequency">
              检查频率: {{ indicator.check_frequency || '未设定' }}
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无指标设定" />
        <div class="card-actions">
          <el-button @click="addIndicator">添加指标</el-button>
        </div>
      </el-card>

      <!-- 指标记录 -->
      <el-card class="box-card" header="指标记录历史">
        <el-table :data="indicatorRecords" v-if="indicatorRecords.length > 0">
          <el-table-column prop="indicator_id" label="指标名称" width="150">
            <template #default="{ row }">
              {{
                disease.indicators
                  ?.find((i) => i.id === row.indicator_id)
                  ?.indicator_name || '未知'
              }}
            </template>
          </el-table-column>
          <el-table-column prop="value" label="测量值" width="100" />
          <el-table-column prop="measurement_date" label="测量日期" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.measurement_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        </el-table>
        <el-empty v-else description="暂无记录" />
        <div class="card-actions">
          <el-button @click="recordIndicator">记录指标</el-button>
        </div>
      </el-card>

      <!-- 随访计划 -->
      <el-card class="box-card" header="随访计划">
        <div v-if="disease.followup_plans && disease.followup_plans.length > 0" class="plans-list">
          <div v-for="plan in disease.followup_plans" :key="plan.id" class="plan-item">
            <div class="plan-header">
              <span class="frequency">{{ plan.frequency }}</span>
              <el-tag :type="getPlanStatus(plan.next_followup_date)">
                {{ getPlanStatusText(plan.next_followup_date) }}
              </el-tag>
            </div>
            <div class="plan-info">
              <div>下次随访: {{ formatDate(plan.next_followup_date) }}</div>
              <div v-if="plan.responsible_doctor">医生: {{ plan.responsible_doctor }}</div>
              <div v-if="plan.last_followup_date">上次随访: {{ formatDate(plan.last_followup_date) }}</div>
            </div>
            <div class="plan-actions">
              <el-button size="small" @click="editPlan(plan)">编辑</el-button>
              <el-button size="small" @click="recordFollowup(plan)">记录随访</el-button>
              <el-button size="small" type="danger" @click="deletePlan(plan)">删除</el-button>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无随访计划" />
        <div class="card-actions">
          <el-button @click="createPlan">创建随访计划</el-button>
        </div>
      </el-card>

      <!-- 随访记录 -->
      <el-card class="box-card" header="随访记录">
        <el-table :data="followupRecords" v-if="followupRecords.length > 0">
          <el-table-column prop="followup_date" label="随访日期" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.followup_date) }}
            </template>
          </el-table-column>
          <el-table-column prop="symptoms_assessment" label="症状评估" show-overflow-tooltip />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button size="small" @click="viewFollowupDetail(row)">查看详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无随访记录" />
      </el-card>
    </div>

    <el-empty v-else description="疾病信息加载失败或不存在" />

    <!-- 编辑基本信息对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑基本信息" width="600px">
      <el-form ref="editFormRef" :model="editForm" label-width="100px">
        <el-form-item label="疾病名称" prop="disease_name" required>
          <el-input v-model="editForm.disease_name" />
        </el-form-item>
        <el-form-item label="ICD-10编码">
          <el-input v-model="editForm.icd10_code" />
        </el-form-item>
        <el-form-item label="诊断日期">
          <el-date-picker v-model="editForm.diagnosis_date" type="date" />
        </el-form-item>
        <el-form-item label="诊疗医院">
          <el-input v-model="editForm.diagnosis_hospital" />
        </el-form-item>
        <el-form-item label="主治医生">
          <el-input v-model="editForm.diagnosis_doctor" />
        </el-form-item>
        <el-form-item label="当前治疗">
          <el-input v-model="editForm.current_treatment" type="textarea" rows="3" />
        </el-form-item>
        <el-form-item label="控制状态">
          <el-radio-group v-model="editForm.control_status">
            <el-radio value="good">控制良好</el-radio>
            <el-radio value="fair">控制中等</el-radio>
            <el-radio value="poor">控制不良</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEdit">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加指标对话框 -->
    <el-dialog v-model="indicatorDialogVisible" title="添加指标" width="600px">
      <el-form ref="indicatorFormRef" :model="newIndicator" label-width="100px">
        <el-form-item label="指标名称" prop="indicator_name" required>
          <el-input v-model="newIndicator.indicator_name" />
        </el-form-item>
        <el-form-item label="最小值">
          <el-input-number v-model="newIndicator.normal_range_min" />
        </el-form-item>
        <el-form-item label="最大值">
          <el-input-number v-model="newIndicator.normal_range_max" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="newIndicator.unit" />
        </el-form-item>
        <el-form-item label="检查频率">
          <el-input v-model="newIndicator.check_frequency" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="indicatorDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveIndicator">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { chronicDiseaseAPI } from '@/api/chronic-disease'
import type { ChronicDisease, IndicatorRecord, FollowupRecord } from '@/types'

const route = useRoute()
const router = useRouter()

const disease = ref<ChronicDisease | null>(null)
const indicatorRecords = ref<IndicatorRecord[]>([])
const followupRecords = ref<FollowupRecord[]>([])
const loading = ref(false)

const editDialogVisible = ref(false)
const indicatorDialogVisible = ref(false)

const editForm = ref({
  disease_name: '',
  icd10_code: '',
  diagnosis_date: '',
  diagnosis_hospital: '',
  diagnosis_doctor: '',
  current_treatment: '',
  control_status: 'fair'
})

const newIndicator = ref({
  indicator_name: '',
  normal_range_min: undefined,
  normal_range_max: undefined,
  unit: '',
  check_frequency: ''
})

const diseaseId = ref<number>(parseInt(route.params.id as string))

const loadDiseaseDetail = async () => {
  loading.value = true
  try {
    const response = await chronicDiseaseAPI.get(diseaseId.value)
    disease.value = response.data

    const recordsResponse = await chronicDiseaseAPI.indicatorRecords.list(diseaseId.value)
    indicatorRecords.value = recordsResponse.data
  } catch (error) {
    ElMessage.error('加载疾病详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const editDisease = () => {
  if (disease.value) {
    editForm.value = {
      disease_name: disease.value.disease_name,
      icd10_code: disease.value.icd10_code || '',
      diagnosis_date: disease.value.diagnosis_date || '',
      diagnosis_hospital: disease.value.diagnosis_hospital || '',
      diagnosis_doctor: disease.value.diagnosis_doctor || '',
      current_treatment: disease.value.current_treatment || '',
      control_status: disease.value.control_status
    }
    editDialogVisible.value = true
  }
}

const saveEdit = async () => {
  try {
    await chronicDiseaseAPI.update(diseaseId.value, editForm.value)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadDiseaseDetail()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

const addIndicator = () => {
  newIndicator.value = {
    indicator_name: '',
    normal_range_min: undefined,
    normal_range_max: undefined,
    unit: '',
    check_frequency: ''
  }
  indicatorDialogVisible.value = true
}

const saveIndicator = async () => {
  try {
    await chronicDiseaseAPI.indicators.add(diseaseId.value, newIndicator.value)
    ElMessage.success('指标添加成功')
    indicatorDialogVisible.value = false
    loadDiseaseDetail()
  } catch (error) {
    ElMessage.error('添加失败')
  }
}

const recordIndicator = () => {
  router.push({
    name: 'chronicDiseaseDetail',
    params: { id: diseaseId.value },
    query: { tab: 'indicator' }
  })
}

const createPlan = () => {
  router.push({
    name: 'chronicDiseaseDetail',
    params: { id: diseaseId.value },
    query: { tab: 'followup' }
  })
}

const editPlan = (plan: any) => {
  // TODO: 引导到随访作编辑模态
}

const recordFollowup = (plan: any) => {
  // TODO: 引导到随访记录模态
}

const deletePlan = (plan: any) => {
  ElMessageBox.confirm('确认删除该随访计划？', 'Warning', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(async () => {
    try {
      await chronicDiseaseAPI.followupPlans.delete(diseaseId.value, plan.id)
      ElMessage.success('删除成功')
      loadDiseaseDetail()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const viewFollowupDetail = (record: FollowupRecord) => {
  // TODO: 展示随访记录详情
}

const getStatusType = (status: string): 'success' | 'warning' | 'danger' | 'info' => {
  const statusMap = {
    good: 'success' as const,
    fair: 'warning' as const,
    poor: 'danger' as const
  }
  return statusMap[status as keyof typeof statusMap] || 'info'
}

const getStatusText = (status: string): string => {
  const statusMap = {
    good: '控制良好',
    fair: '控制中等',
    poor: '控制不良'
  }
  return statusMap[status as keyof typeof statusMap] || status
}

const getPlanStatus = (nextDate: string): 'success' | 'warning' | 'danger' => {
  const days = Math.floor(
    (new Date(nextDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  )
  if (days < 0) return 'danger'
  if (days < 7) return 'warning'
  return 'success'
}

const getPlanStatusText = (nextDate: string): string => {
  const days = Math.floor(
    (new Date(nextDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  )
  if (days < 0) return `已过期 ${Math.abs(days)} 天`
  if (days === 0) return '今天随访'
  if (days < 7) return `${days} 天后随访`
  return `${days} 天后随访`
}

const formatDate = (date: string): string => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateTime: string): string => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

onMounted(() => {
  loadDiseaseDetail()
})
</script>

<style scoped lang="scss">
.disease-detail-view {
  padding: 20px;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;

  h1 {
    margin: 0;
    font-size: 28px;
    flex: 1;
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.box-card {
  :deep(.el-card__header) {
    padding: 15px 20px;
    border-bottom: 1px solid #ebeef5;
    background: #f5f7fa;
  }

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;

  .info-item {
    display: flex;
    flex-direction: column;

    .label {
      color: #909399;
      font-size: 14px;
      margin-bottom: 5px;
    }

    .value {
      color: #303133;
      font-size: 16px;
      font-weight: 500;
    }
  }
}

.indicators-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;

  .indicator-item {
    padding: 15px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background: #fafafa;

    .indicator-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .name {
        font-weight: 600;
        color: #303133;
      }

      .unit {
        color: #909399;
        font-size: 14px;
      }
    }

    .range,
    .frequency {
      color: #606266;
      font-size: 14px;
      margin-top: 5px;
    }
  }
}

.plans-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;

  .plan-item {
    padding: 15px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    background: #fafafa;

    .plan-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      .frequency {
        font-weight: 600;
        color: #303133;
      }
    }

    .plan-info {
      color: #606266;
      font-size: 14px;
      margin-bottom: 10px;

      div {
        margin: 5px 0;
      }
    }

    .plan-actions {
      display: flex;
      gap: 10px;
    }
  }
}

.card-actions {
  display: flex;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
