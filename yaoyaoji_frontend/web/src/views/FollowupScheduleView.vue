<template>
  <div class="followup-schedule-view">
    <div class="page-header">
      <h1>随访日程管理</h1>
      <el-select
        v-model="filterStatus"
        placeholder="筛选状态"
        clearable
        style="width: 150px"
      >
        <el-option label="待进行" value="pending" />
        <el-option label="已完成" value="completed" />
        <el-option label="已过期" value="overdue" />
      </el-select>
    </div>

    <!-- 按时间线展示随访计划 -->
    <div class="timeline-container">
      <div v-if="sortedPlans.length > 0">
        <div
          v-for="plan in sortedPlans"
          :key="plan.id"
          class="timeline-item"
          :class="getPlanClass(plan)"
        >
          <div class="timeline-marker">
            <div class="marker-dot"></div>
            <div class="marker-line"></div>
          </div>

          <div class="timeline-content">
            <div class="plan-header">
              <div class="disease-info">
                <h3>{{ getDiseaseNameById(plan.disease_id) }}</h3>
                <span class="frequency">{{ plan.frequency }}</span>
              </div>
              <el-tag :type="getPlanStatusType(plan.next_followup_date)">
                {{ getPlanStatusText(plan.next_followup_date) }}
              </el-tag>
            </div>

            <div class="plan-details">
              <div class="detail-item">
                <span class="label">下次随访:</span>
                <span class="value">{{ formatDate(plan.next_followup_date) }}</span>
              </div>
              <div v-if="plan.last_followup_date" class="detail-item">
                <span class="label">上次随访:</span>
                <span class="value">{{ formatDate(plan.last_followup_date) }}</span>
              </div>
              <div v-if="plan.responsible_doctor" class="detail-item">
                <span class="label">责任医生:</span>
                <span class="value">{{ plan.responsible_doctor }}</span>
              </div>
            </div>

            <div class="plan-actions">
              <el-button size="small" @click="editFollowupPlan(plan)">编辑</el-button>
              <el-button size="small" type="primary" @click="recordFollowup(plan)">
                记录随访
              </el-button>
              <el-button size="small" type="danger" @click="deletePlan(plan)">删除</el-button>
            </div>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无随访计划" />
    </div>

    <!-- 记录随访对话框 -->
    <el-dialog v-model="followupDialogVisible" title="记录随访" width="700px">
      <el-form ref="followupRecordFormRef" :model="followupRecord" label-width="100px">
        <el-form-item label="随访日期" prop="followup_date" required>
          <el-date-picker
            v-model="followupRecord.followup_date"
            type="datetime"
            placeholder="选择日期时间"
          />
        </el-form-item>

        <el-form-item label="症状评估" prop="symptoms_assessment">
          <el-input
            v-model="followupRecord.symptoms_assessment"
            type="textarea"
            rows="3"
            placeholder="描述患者当前症状和身体状况"
          />
        </el-form-item>

        <el-form-item label="指标检查">
          <div v-if="selectedPlanForFollowup" class="indicators-check">
            <div
              v-for="indicator in getIndicatorsForDisease(selectedPlanForFollowup.disease_id)"
              :key="indicator.id"
              class="indicator-check-item"
            >
              <span class="indicator-name">{{ indicator.indicator_name }}</span>
              <el-input
                v-model="followupRecord.indicator_check"
                type="number"
                placeholder="输入测量值"
                style="width: 150px"
              />
            </div>
          </div>
        </el-form-item>

        <el-form-item label="用药评估" prop="medication_evaluation">
          <el-input
            v-model="followupRecord.medication_evaluation"
            type="textarea"
            rows="3"
            placeholder="评估用药效果和依从性"
          />
        </el-form-item>

        <el-form-item label="生活指导" prop="lifestyle_guidance">
          <el-input
            v-model="followupRecord.lifestyle_guidance"
            type="textarea"
            rows="3"
            placeholder="提供生活方式和饮食建议"
          />
        </el-form-item>

        <el-form-item label="医生备注" prop="doctor_notes">
          <el-input
            v-model="followupRecord.doctor_notes"
            type="textarea"
            rows="3"
            placeholder="医生临床备注"
          />
        </el-form-item>

        <el-form-item label="下一步计划" prop="next_plan">
          <el-input
            v-model="followupRecord.next_plan"
            type="textarea"
            rows="2"
            placeholder="下一步治疗或随访计划"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="followupDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveFollowupRecord">保存</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑随访计划对话框 -->
    <el-dialog v-model="editPlanDialogVisible" title="编辑随访计划" width="600px">
      <el-form ref="editPlanFormRef" :model="editPlan" label-width="100px">
        <el-form-item label="随访频率" prop="frequency" required>
          <el-select v-model="editPlan.frequency" placeholder="选择随访频率">
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="每季度" value="quarterly" />
            <el-option label="每半年" value="half-yearly" />
            <el-option label="每年" value="yearly" />
          </el-select>
        </el-form-item>

        <el-form-item label="下次随访日期" prop="next_followup_date" required>
          <el-date-picker
            v-model="editPlan.next_followup_date"
            type="date"
            placeholder="选择日期"
          />
        </el-form-item>

        <el-form-item label="责任医生">
          <el-input v-model="editPlan.responsible_doctor" placeholder="可选" />
        </el-form-item>

        <el-form-item label="提醒天数">
          <el-input-number v-model="editPlan.reminder_days" :min="1" :max="30" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editPlanDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveEditPlan">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { chronicDiseaseAPI } from '@/api/chronic-disease'
import type { ChronicDisease, FollowupPlan } from '@/types'

const diseases = ref<ChronicDisease[]>([])
const allPlans = ref<FollowupPlan[]>([])
const filterStatus = ref('')

const followupDialogVisible = ref(false)
const editPlanDialogVisible = ref(false)

const selectedPlanForFollowup = ref<FollowupPlan | null>(null)
const selectedPlanForEdit = ref<FollowupPlan | null>(null)

const followupRecord = ref({
  followup_date: '',
  symptoms_assessment: '',
  indicator_check: '',
  medication_evaluation: '',
  lifestyle_guidance: '',
  doctor_notes: '',
  next_plan: ''
})

const editPlan = ref({
  frequency: '',
  next_followup_date: '',
  responsible_doctor: '',
  reminder_days: 7
})

const followupRecordFormRef = ref()
const editPlanFormRef = ref()

// 加载所有疾病和随访计划
const loadData = async () => {
  try {
    const response = await chronicDiseaseAPI.list({ limit: 100 })
    diseases.value = response.data

    // 收集所有随访计划
    allPlans.value = []
    for (const disease of diseases.value) {
      const plansResponse = await chronicDiseaseAPI.followupPlans.list(disease.id)
      allPlans.value.push(...plansResponse.data)
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

// 排序的随访计划
const sortedPlans = computed(() => {
  let filtered = [...allPlans.value]

  // 根据状态筛选
  if (filterStatus.value === 'pending') {
    filtered = filtered.filter(
      (p) => new Date(p.next_followup_date) >= new Date()
    )
  } else if (filterStatus.value === 'overdue') {
    filtered = filtered.filter(
      (p) => new Date(p.next_followup_date) < new Date()
    )
  }

  // 按日期排序
  return filtered.sort(
    (a, b) => new Date(a.next_followup_date).getTime() - new Date(b.next_followup_date).getTime()
  )
})

// 获取疾病名称
const getDiseaseNameById = (diseaseId: number): string => {
  return diseases.value.find((d) => d.id === diseaseId)?.disease_name || '未知疾病'
}

// 获取疾病的指标
const getIndicatorsForDisease = (diseaseId: number) => {
  const disease = diseases.value.find((d) => d.id === diseaseId)
  return disease?.indicators || []
}

// 获取随访计划类名
const getPlanClass = (plan: FollowupPlan): string => {
  const days = Math.floor(
    (new Date(plan.next_followup_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  )
  if (days < 0) return 'overdue'
  if (days < 7) return 'urgent'
  return 'normal'
}

// 获取随访计划状态类型
const getPlanStatusType = (
  nextDate: string
): 'success' | 'warning' | 'danger' | 'info' => {
  const days = Math.floor(
    (new Date(nextDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  )
  if (days < 0) return 'danger'
  if (days < 7) return 'warning'
  return 'success'
}

// 获取随访计划状态文本
const getPlanStatusText = (nextDate: string): string => {
  const days = Math.floor(
    (new Date(nextDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)
  )
  if (days < 0) return `已过期 ${Math.abs(days)} 天`
  if (days === 0) return '今天随访'
  if (days < 7) return `${days} 天后随访`
  return `${days} 天后随访`
}

// 记录随访
const recordFollowup = (plan: FollowupPlan) => {
  selectedPlanForFollowup.value = plan
  followupRecord.value = {
    followup_date: new Date().toISOString(),
    symptoms_assessment: '',
    indicator_check: '',
    medication_evaluation: '',
    lifestyle_guidance: '',
    doctor_notes: '',
    next_plan: ''
  }
  followupDialogVisible.value = true
}

// 保存随访记录
const saveFollowupRecord = async () => {
  if (!selectedPlanForFollowup.value) return

  try {
    await chronicDiseaseAPI.followupRecords.create(
      selectedPlanForFollowup.value.disease_id,
      selectedPlanForFollowup.value.id,
      {
        followup_date: followupRecord.value.followup_date,
        symptoms_assessment: followupRecord.value.symptoms_assessment || undefined,
        indicator_check: followupRecord.value.indicator_check
          ? { check: followupRecord.value.indicator_check }
          : undefined,
        medication_evaluation: followupRecord.value.medication_evaluation || undefined,
        lifestyle_guidance: followupRecord.value.lifestyle_guidance || undefined,
        doctor_notes: followupRecord.value.doctor_notes || undefined,
        next_plan: followupRecord.value.next_plan || undefined
      }
    )
    ElMessage.success('随访记录保存成功')
    followupDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 编辑随访计划
const editFollowupPlan = (plan: FollowupPlan) => {
  selectedPlanForEdit.value = plan
  editPlan.value = {
    frequency: plan.frequency,
    next_followup_date: plan.next_followup_date,
    responsible_doctor: plan.responsible_doctor || '',
    reminder_days: plan.reminder_days
  }
  editPlanDialogVisible.value = true
}

// 保存编辑的随访计划
const saveEditPlan = async () => {
  if (!selectedPlanForEdit.value) return

  try {
    await chronicDiseaseAPI.followupPlans.update(
      selectedPlanForEdit.value.disease_id,
      selectedPlanForEdit.value.id,
      editPlan.value
    )
    ElMessage.success('更新成功')
    editPlanDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 删除随访计划
const deleteFollowupPlan = (plan: FollowupPlan) => {
  ElMessageBox.confirm('确认删除该随访计划？', 'Warning', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(async () => {
    try {
      await chronicDiseaseAPI.followupPlans.delete(plan.disease_id, plan.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

const formatDate = (date: string): string => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}

const deletePlan = (plan: FollowupPlan) => {
  deleteFollowupPlan(plan)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.followup-schedule-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;

  h1 {
    margin: 0;
    font-size: 28px;
  }
}

.timeline-container {
  position: relative;
  padding: 20px;

  &::before {
    content: '';
    position: absolute;
    left: 30px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #dcdfe6;
  }
}

.timeline-item {
  position: relative;
  margin-bottom: 30px;
  padding-left: 80px;
  opacity: 0.7;
  transition: opacity 0.3s;

  &:hover {
    opacity: 1;
  }

  &.normal {
    opacity: 1;
  }

  &.urgent {
    opacity: 1;

    .timeline-marker {
      .marker-dot {
        background: #e6a23c;
        box-shadow: 0 0 0 8px rgba(230, 162, 60, 0.1);
      }
    }
  }

  &.overdue {
    opacity: 1;

    .timeline-marker {
      .marker-dot {
        background: #f56c6c;
        box-shadow: 0 0 0 8px rgba(245, 108, 108, 0.1);
      }
    }
  }

  .timeline-marker {
    position: absolute;
    left: -70px;
    top: 0;
    width: 60px;
    height: 60px;
    display: flex;
    flex-direction: column;
    align-items: center;

    .marker-dot {
      width: 16px;
      height: 16px;
      background: #67c23a;
      border-radius: 50%;
      box-shadow: 0 0 0 8px rgba(103, 194, 58, 0.1);
    }

    .marker-line {
      width: 2px;
      flex: 1;
      background: #dcdfe6;
    }
  }

  .timeline-content {
    background: white;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    padding: 20px;

    .plan-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 15px;

      .disease-info {
        h3 {
          margin: 0 0 5px 0;
          font-size: 18px;
        }

        .frequency {
          color: #909399;
          font-size: 14px;
        }
      }
    }

    .plan-details {
      margin-bottom: 15px;
      padding-top: 15px;
      border-top: 1px solid #ebeef5;

      .detail-item {
        display: flex;
        margin-bottom: 8px;
        font-size: 14px;

        .label {
          color: #606266;
          min-width: 80px;
        }

        .value {
          color: #303133;
        }
      }
    }

    .plan-actions {
      display: flex;
      gap: 10px;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.indicators-check {
  display: flex;
  flex-direction: column;
  gap: 10px;

  .indicator-check-item {
    display: flex;
    gap: 10px;
    align-items: center;

    .indicator-name {
      min-width: 100px;
    }
  }
}
</style>
