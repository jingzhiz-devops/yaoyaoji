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
        <el-button @click="showExport = true" text type="primary">导出数据</el-button>
      </div>
    </div>

    <div v-if="disease" class="detail-container">
      <!-- 功能标签页 -->
      <el-tabs v-model="activeTab" type="border-card">
        <!-- 指标监测 -->
        <el-tab-pane label="📊 指标监测" name="indicators">
          <div class="indicator-layout">
            <!-- 左侧：历史记录 + 记录表单 -->
            <div class="indicator-left">
              <h4 class="section-title">历史记录</h4>
              <el-table :data="indicatorRecords" v-if="indicatorRecords.length > 0" stripe size="small" max-height="360">
                <el-table-column label="指标" min-width="100">
                  <template #default="{ row }">
                    {{ disease.indicators?.find(i => i.id === row.indicator_id)?.indicator_name || '未知' }}
                  </template>
                </el-table-column>
                <el-table-column label="测量值" min-width="80">
                  <template #default="{ row }">
                    <span :class="getValueClass(row)">{{ row.value }}</span>
                    <span class="unit-text">{{ getIndicatorUnit(row.indicator_id) }}</span>
                  </template>
                </el-table-column>
                <el-table-column label="测量日期" min-width="140">
                  <template #default="{ row }">{{ formatDateTime(row.measurement_date) }}</template>
                </el-table-column>
                <el-table-column prop="notes" label="备注" min-width="80" show-overflow-tooltip></el-table-column>
              </el-table>
              <el-empty v-else description="暂无记录" :image-size="80" />

              <el-divider />
              <h4 class="section-title">记录指标</h4>
              <IndicatorRecordForm
                v-if="disease.indicators?.length"
                :disease-id="diseaseId"
                :indicators="disease.indicators"
                @submitted="loadDiseaseDetail"
              />
            </div>

            <!-- 右侧：推荐值/正常范围 -->
            <div class="indicator-right">
              <h4 class="section-title">参考范围</h4>
              <div v-if="disease.indicators && disease.indicators.length > 0" class="reference-list">
                <div v-for="indicator in disease.indicators" :key="indicator.id" class="reference-card">
                  <div class="ref-name">{{ indicator.indicator_name }}</div>
                  <div class="ref-range" v-if="indicator.normal_range_min != null || indicator.normal_range_max != null">
                    <span class="ref-value">{{ indicator.normal_range_min ?? '-' }} ~ {{ indicator.normal_range_max ?? '-' }}</span>
                    <span class="ref-unit">{{ indicator.unit }}</span>
                  </div>
                  <div class="ref-range" v-else>
                    <span class="ref-value no-data">未设置</span>
                  </div>
                  <div class="ref-latest" v-if="getLatestValue(indicator.id)">
                    最近: <span :class="getLatestValueClass(indicator)">{{ getLatestValue(indicator.id) }}</span> {{ indicator.unit }}
                  </div>
                  <div v-if="indicator.check_frequency" class="ref-freq">
                    建议频率: {{ formatCheckFrequency(indicator.check_frequency) }}
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无指标设定" :image-size="60" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 疾病常识 -->
        <el-tab-pane label="📚 疾病常识" name="knowledge">
          <div class="knowledge-content">
            <div v-if="diseaseKnowledge" class="knowledge-sections">
              <el-card class="knowledge-card" v-for="(section, index) in diseaseKnowledge" :key="index" shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span class="section-icon">{{ section.icon }}</span>
                    <span class="section-title">{{ section.title }}</span>
                  </div>
                </template>
                <div class="section-content" v-html="section.content"></div>
              </el-card>
            </div>
            <el-empty v-else description="暂无疾病常识" />
          </div>
        </el-tab-pane>

        <!-- 饮食建议 -->
        <el-tab-pane label="🍽️ 饮食建议" name="diet">
          <DietRecommendations :disease-id="diseaseId" />
        </el-tab-pane>

        <!-- 运动建议 -->
        <el-tab-pane label="🏃 运动建议" name="exercise">
          <ExerciseRecommendations :disease-id="diseaseId" />
        </el-tab-pane>

        <!-- 并发症管理 -->
        <el-tab-pane label="⚠️ 并发症" name="complications">
          <ComplicationManager :disease-id="diseaseId" />
        </el-tab-pane>

        <!-- 用药提醒 -->
        <el-tab-pane label="💊 用药提醒" name="reminders">
          <ScheduleView />
        </el-tab-pane>

        <!-- 随访计划 -->
        <el-tab-pane label="📋 随访计划" name="followup">
          <div v-if="disease.followup_plans && disease.followup_plans.length > 0" class="plans-list">
            <div v-for="plan in disease.followup_plans" :key="plan.id" class="plan-item">
              <div class="plan-header">
                <span class="frequency">{{ formatFrequency(plan.frequency) }}</span>
                <el-tag :type="getPlanStatus(plan.next_followup_date)">
                  {{ getPlanStatusText(plan.next_followup_date) }}
                </el-tag>
              </div>
              <div class="plan-info">
                <div>下次随访: {{ formatDate(plan.next_followup_date) }}</div>
                <div v-if="plan.last_followup_date">上次随访: {{ formatDate(plan.last_followup_date) }}</div>
                <div v-if="plan.responsible_doctor">医生: {{ plan.responsible_doctor }}</div>
                <div>提前 {{ plan.reminder_days }} 天提醒</div>
              </div>
              <div class="plan-actions">
                <el-button size="small" type="primary" @click="editPlan(plan)">编辑</el-button>
                <el-button size="small" type="danger" @click="deletePlan(plan)">删除</el-button>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无随访计划" />
          <div class="card-actions">
            <el-button type="primary" @click="openCreatePlan">创建随访计划</el-button>
          </div>
        </el-tab-pane>

        <!-- 基本信息 -->
        <el-tab-pane label="📝 基本信息" name="basic">
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
              <span class="value">{{ disease.current_treatment }}</span>
            </div>
            <div class="info-item">
              <span class="label">控制状态</span>
              <span class="value">
                <el-tag :type="getStatusType(disease.control_status)" size="small">
                  {{ getStatusText(disease.control_status) }}
                </el-tag>
              </span>
            </div>
          </div>
          <div class="card-actions">
            <el-button type="primary" @click="editDisease">编辑基本信息</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-empty v-else description="疾病信息加载失败或不存在" />

    <!-- 编辑基本信息对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑基本信息" width="600px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="疾病名称" required>
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
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 随访计划对话框 -->
    <el-dialog v-model="planDialogVisible" :title="editingPlanId ? '编辑随访计划' : '创建随访计划'" width="600px">
      <el-form :model="planForm" label-width="100px">
        <el-form-item label="随访频率" required>
          <el-select v-model="planForm.frequency" placeholder="请选择频率" style="width: 100%">
            <el-option label="每周" value="weekly" />
            <el-option label="每月" value="monthly" />
            <el-option label="每季度" value="quarterly" />
            <el-option label="每半年" value="half_yearly" />
            <el-option label="每年" value="yearly" />
          </el-select>
        </el-form-item>
        <el-form-item label="下次随访日期" required>
          <el-date-picker v-model="planForm.next_followup_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="负责医生">
          <el-input v-model="planForm.responsible_doctor" placeholder="请输入医生姓名" />
        </el-form-item>
        <el-form-item label="提前提醒天数">
          <el-input-number v-model="planForm.reminder_days" :min="1" :max="30" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlan">确定</el-button>
      </template>
    </el-dialog>

    <!-- 导出对话框 -->
    <ExportDialog v-model="showExport" :disease-ids="[diseaseId]" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { chronicDiseaseAPI } from '@/api/chronic-disease'
import IndicatorRecordForm from '@/components/IndicatorRecordForm.vue'
import DietRecommendations from '@/components/DietRecommendations.vue'
import ExerciseRecommendations from '@/components/ExerciseRecommendations.vue'
import ComplicationManager from '@/components/ComplicationManager.vue'
import ScheduleView from '@/views/medication/ScheduleView.vue'
import ExportDialog from '@/components/ExportDialog.vue'
import type { ChronicDisease, IndicatorRecord } from '@/types'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()

const disease = ref<ChronicDisease | null>(null)
const indicatorRecords = ref<IndicatorRecord[]>([])
const activeTab = ref('indicators')
const editDialogVisible = ref(false)
const showExport = ref(false)

// 随访计划
const planDialogVisible = ref(false)
const editingPlanId = ref<number | null>(null)
const planForm = reactive({
  frequency: '',
  next_followup_date: '',
  responsible_doctor: '',
  reminder_days: 7
})

const editForm = ref({
  disease_name: '',
  icd10_code: '',
  diagnosis_date: '',
  diagnosis_hospital: '',
  diagnosis_doctor: '',
  current_treatment: '',
  control_status: 'fair'
})

const diseaseId = ref<number>(parseInt(route.params.id as string))

// 疾病常识数据（根据疾病类型动态加载）
const diseaseKnowledge = ref<Array<{ icon: string; title: string; content: string }> | null>(null)

const loadDiseaseDetail = async () => {
  try {
    const response = await chronicDiseaseAPI.get(diseaseId.value)
    disease.value = response as any
    const recordsResponse = await chronicDiseaseAPI.indicatorRecords.list(diseaseId.value)
    indicatorRecords.value = (recordsResponse as any) || []
    
    // 加载疾病常识
    loadDiseaseKnowledge()
  } catch {
    ElMessage.error('加载疾病详情失败')
  }
}

const loadDiseaseKnowledge = () => {
  if (!disease.value) return
  
  const diseaseName = disease.value.disease_name
  
  // 根据疾病名称加载对应的常识
  if (diseaseName.includes('糖尿病')) {
    diseaseKnowledge.value = [
      {
        icon: '🩺',
        title: '什么是糖尿病',
        content: `
          <p>糖尿病是一种慢性代谢性疾病，主要特征是血糖水平持续升高。当身体无法有效利用胰岛素或胰岛素分泌不足时，就会导致糖尿病。</p>
          <p><strong>2型糖尿病</strong>是最常见的类型，约占所有糖尿病病例的90%以上，通常与肥胖、缺乏运动和不良饮食习惯有关。</p>
        `
      },
      {
        icon: '🏥',
        title: 'ICD-10 疾病分类编码',
        content: `
          <p>ICD-10（国际疾病分类第10版）是世界卫生组织制定的疾病分类标准。糖尿病的主要分类代码：</p>
          <table style="width: 100%; border-collapse: collapse; margin: 12px 0;">
            <tr style="background: #f5f7fa;">
              <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">代码</th>
              <th style="padding: 8px; border: 1px solid #ddd; text-align: left;">疾病类型</th>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;"><strong>E10</strong></td>
              <td style="padding: 8px; border: 1px solid #ddd;">1型糖尿病（胰岛素依赖型）</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;"><strong style="color: #409eff;">E11</strong></td>
              <td style="padding: 8px; border: 1px solid #ddd;"><strong style="color: #409eff;">2型糖尿病（非胰岛素依赖型）</strong></td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;"><strong>E12</strong></td>
              <td style="padding: 8px; border: 1px solid #ddd;">营养不良相关的糖尿病</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;"><strong>E13</strong></td>
              <td style="padding: 8px; border: 1px solid #ddd;">其他特指的糖尿病</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;"><strong>E14</strong></td>
              <td style="padding: 8px; border: 1px solid #ddd;">未特指的糖尿病</td>
            </tr>
          </table>
          <p style="margin-top: 16px;"><strong>E11 详细分类（按并发症）：</strong></p>
          <ul style="margin-top: 8px;">
            <li><strong>E11.0</strong>：伴有昏迷</li>
            <li><strong>E11.1</strong>：伴有酮症酸中毒</li>
            <li><strong>E11.2</strong>：伴有肾脏并发症（糖尿病肾病）</li>
            <li><strong>E11.3</strong>：伴有眼部并发症（糖尿病视网膜病变）</li>
            <li><strong>E11.4</strong>：伴有神经系统并发症（糖尿病神经病变）</li>
            <li><strong>E11.5</strong>：伴有周围循环并发症（糖尿病足等）</li>
            <li><strong>E11.6</strong>：伴有其他特指的并发症</li>
            <li><strong>E11.9</strong>：无并发症</li>
          </ul>
          <p style="color: #909399; font-size: 13px; margin-top: 12px;">💡 这些编码用于医疗记录、统计分析和医保结算，帮助医生准确记录病情和并发症情况。</p>
        `
      },
      {
        icon: '⚠️',
        title: '常见症状',
        content: `
          <ul>
            <li><strong>三多一少</strong>：多饮、多尿、多食、体重减少</li>
            <li>容易疲劳、乏力</li>
            <li>视力模糊</li>
            <li>伤口愈合缓慢</li>
            <li>皮肤瘙痒、反复感染</li>
            <li>手脚麻木、刺痛感</li>
          </ul>
        `
      },
      {
        icon: '🎯',
        title: '血糖控制目标',
        content: `
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f5f7fa;">
              <th style="padding: 8px; border: 1px solid #ddd;">指标</th>
              <th style="padding: 8px; border: 1px solid #ddd;">目标值</th>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">空腹血糖</td>
              <td style="padding: 8px; border: 1px solid #ddd;">3.9 - 6.1 mmol/L</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">餐后2小时血糖</td>
              <td style="padding: 8px; border: 1px solid #ddd;">3.9 - 7.8 mmol/L</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">糖化血红蛋白</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 6.5%</td>
            </tr>
          </table>
        `
      },
      {
        icon: '💊',
        title: '治疗方法',
        content: `
          <p><strong>五驾马车</strong>综合治疗方案：</p>
          <ol>
            <li><strong>糖尿病教育</strong>：了解疾病知识，学会自我管理</li>
            <li><strong>饮食控制</strong>：合理膳食，控制总热量摄入</li>
            <li><strong>运动疗法</strong>：规律运动，每周至少150分钟中等强度运动</li>
            <li><strong>药物治疗</strong>：遵医嘱服药，不可自行停药</li>
            <li><strong>血糖监测</strong>：定期监测血糖，及时调整治疗方案</li>
          </ol>
        `
      },
      {
        icon: '🚨',
        title: '并发症预防',
        content: `
          <p>糖尿病如果控制不好，可能导致多种并发症：</p>
          <ul>
            <li><strong>心血管疾病</strong>：冠心病、心肌梗死、脑卒中</li>
            <li><strong>糖尿病肾病</strong>：可能发展为尿毒症</li>
            <li><strong>糖尿病视网膜病变</strong>：严重可致失明</li>
            <li><strong>糖尿病足</strong>：足部溃疡、感染，严重需截肢</li>
            <li><strong>神经病变</strong>：手脚麻木、疼痛</li>
          </ul>
          <p style="color: #e6a23c; margin-top: 12px;"><strong>预防关键</strong>：严格控制血糖、血压、血脂，定期体检筛查。</p>
        `
      },
      {
        icon: '📋',
        title: '日常注意事项',
        content: `
          <ul>
            <li>每天监测血糖，记录血糖变化</li>
            <li>按时服药，不可随意增减药量</li>
            <li>保持规律作息，避免熬夜</li>
            <li>戒烟限酒，保持良好生活习惯</li>
            <li>注意足部护理，每天检查足部</li>
            <li>定期复查，每3-6个月检查糖化血红蛋白</li>
            <li>随身携带糖果，预防低血糖</li>
            <li>保持心情愉悦，避免情绪波动</li>
          </ul>
        `
      }
    ]
  } else if (diseaseName.includes('高血压')) {
    diseaseKnowledge.value = [
      {
        icon: '🩺',
        title: '什么是高血压',
        content: `
          <p>高血压是指血压持续高于正常水平的慢性疾病。正常血压应低于120/80 mmHg，当收缩压≥140 mmHg和/或舒张压≥90 mmHg时，即可诊断为高血压。</p>
          <p>高血压被称为"无声的杀手"，因为大多数患者没有明显症状，但长期高血压会损害心、脑、肾等重要器官。</p>
        `
      },
      {
        icon: '🎯',
        title: '血压控制目标',
        content: `
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f5f7fa;">
              <th style="padding: 8px; border: 1px solid #ddd;">人群</th>
              <th style="padding: 8px; border: 1px solid #ddd;">目标值</th>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">一般成人</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 140/90 mmHg</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">糖尿病患者</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 130/80 mmHg</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">老年人(≥65岁)</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 150/90 mmHg</td>
            </tr>
          </table>
        `
      },
      {
        icon: '💊',
        title: '治疗方法',
        content: `
          <p><strong>生活方式干预</strong>：</p>
          <ul>
            <li>限盐：每日食盐摄入量<6克</li>
            <li>减重：BMI控制在18.5-23.9</li>
            <li>戒烟限酒</li>
            <li>规律运动：每周5次，每次30分钟</li>
            <li>减轻精神压力，保持心理平衡</li>
          </ul>
          <p style="margin-top: 12px;"><strong>药物治疗</strong>：遵医嘱规律服药，不可自行停药。</p>
        `
      },
      {
        icon: '📋',
        title: '日常注意事项',
        content: `
          <ul>
            <li>每天测量血压，早晚各一次</li>
            <li>按时服药，不可随意停药</li>
            <li>低盐低脂饮食</li>
            <li>避免情绪激动</li>
            <li>保持大便通畅</li>
            <li>定期复查，监测靶器官损害</li>
          </ul>
        `
      }
    ]
  } else if (diseaseName.includes('高血脂')) {
    diseaseKnowledge.value = [
      {
        icon: '🩺',
        title: '什么是高血脂',
        content: `
          <p>高血脂是指血液中胆固醇和/或甘油三酯水平过高。长期高血脂会导致动脉粥样硬化，增加心脑血管疾病风险。</p>
        `
      },
      {
        icon: '🎯',
        title: '血脂控制目标',
        content: `
          <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f5f7fa;">
              <th style="padding: 8px; border: 1px solid #ddd;">指标</th>
              <th style="padding: 8px; border: 1px solid #ddd;">理想值</th>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">总胆固醇</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 5.2 mmol/L</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">甘油三酯</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 1.7 mmol/L</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">低密度脂蛋白</td>
              <td style="padding: 8px; border: 1px solid #ddd;">< 3.4 mmol/L</td>
            </tr>
            <tr>
              <td style="padding: 8px; border: 1px solid #ddd;">高密度脂蛋白</td>
              <td style="padding: 8px; border: 1px solid #ddd;">> 1.0 mmol/L</td>
            </tr>
          </table>
        `
      },
      {
        icon: '💊',
        title: '治疗方法',
        content: `
          <p><strong>生活方式调整</strong>：</p>
          <ul>
            <li>低脂低胆固醇饮食</li>
            <li>增加膳食纤维摄入</li>
            <li>控制体重</li>
            <li>规律运动</li>
            <li>戒烟限酒</li>
          </ul>
          <p style="margin-top: 12px;"><strong>药物治疗</strong>：他汀类药物等，需遵医嘱服用。</p>
        `
      },
      {
        icon: '📋',
        title: '日常注意事项',
        content: `
          <ul>
            <li>定期检查血脂，每3-6个月复查一次</li>
            <li>避免高脂肪、高胆固醇食物</li>
            <li>多吃蔬菜水果、粗粮</li>
            <li>坚持规律运动</li>
            <li>控制体重，避免肥胖</li>
          </ul>
        `
      }
    ]
  } else {
    diseaseKnowledge.value = null
  }
}

const goBack = () => router.back()

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
  } catch {
    ElMessage.error('更新失败')
  }
}

// ===== 随访计划 =====
const resetPlanForm = () => {
  editingPlanId.value = null
  planForm.frequency = ''
  planForm.next_followup_date = ''
  planForm.responsible_doctor = ''
  planForm.reminder_days = 7
}

const openCreatePlan = () => {
  resetPlanForm()
  planDialogVisible.value = true
}

const editPlan = (plan: any) => {
  editingPlanId.value = plan.id
  planForm.frequency = plan.frequency
  planForm.next_followup_date = plan.next_followup_date
  planForm.responsible_doctor = plan.responsible_doctor || ''
  planForm.reminder_days = plan.reminder_days ?? 7
  planDialogVisible.value = true
}

const savePlan = async () => {
  if (!planForm.frequency || !planForm.next_followup_date) {
    ElMessage.warning('请填写频率和下次随访日期')
    return
  }
  const payload = {
    frequency: planForm.frequency,
    next_followup_date: dayjs(planForm.next_followup_date).format('YYYY-MM-DD'),
    responsible_doctor: planForm.responsible_doctor || null,
    reminder_days: planForm.reminder_days
  }
  try {
    if (editingPlanId.value) {
      await chronicDiseaseAPI.followupPlans.update(diseaseId.value, editingPlanId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await chronicDiseaseAPI.followupPlans.create(diseaseId.value, payload)
      ElMessage.success('创建成功')
    }
    planDialogVisible.value = false
    loadDiseaseDetail()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  }
}

const deletePlan = (plan: any) => {
  ElMessageBox.confirm('确认删除该随访计划？', '提示', { type: 'warning' }).then(async () => {
    try {
      await chronicDiseaseAPI.followupPlans.delete(diseaseId.value, plan.id)
      ElMessage.success('删除成功')
      loadDiseaseDetail()
    } catch {
      ElMessage.error('删除失败')
    }
  })
}

const getStatusType = (status: string) => ({ good: 'success', fair: 'warning', poor: 'danger' }[status] || 'info') as any
const getStatusText = (status: string) => ({ good: '控制良好', fair: '控制中等', poor: '控制不良' }[status] || status)
const getPlanStatus = (nextDate: string) => {
  const days = Math.floor((new Date(nextDate).getTime() - Date.now()) / 86400000)
  return days < 0 ? 'danger' : days < 7 ? 'warning' : 'success'
}
const getPlanStatusText = (nextDate: string) => {
  const days = Math.floor((new Date(nextDate).getTime() - Date.now()) / 86400000)
  if (days < 0) return `已过期 ${Math.abs(days)} 天`
  if (days === 0) return '今天随访'
  return `${days} 天后随访`
}
const formatFrequency = (freq: string) => {
  const map: Record<string, string> = { weekly: '每周', monthly: '每月', quarterly: '每季度', half_yearly: '每半年', yearly: '每年' }
  return map[freq] || freq
}
const formatDate = (d: string) => d ? new Date(d).toLocaleDateString('zh-CN') : '-'
const formatDateTime = (d: string) => d ? new Date(d).toLocaleString('zh-CN') : '-'
const formatCheckFrequency = (freq: string) => {
  const map: Record<string, string> = { daily: '每天', weekly: '每周', monthly: '每月', quarterly: '每季度' }
  return map[freq] || freq
}

// 指标相关辅助函数
const getIndicatorUnit = (indicatorId: number) => {
  return disease.value?.indicators?.find(i => i.id === indicatorId)?.unit || ''
}

const getLatestValue = (indicatorId: number): number | null => {
  const record = indicatorRecords.value.find(r => r.indicator_id === indicatorId)
  return record ? record.value : null
}

const getValueClass = (row: any) => {
  const indicator = disease.value?.indicators?.find(i => i.id === row.indicator_id)
  if (!indicator) return ''
  const v = row.value
  if (indicator.normal_range_min != null && v < indicator.normal_range_min) return 'value-low'
  if (indicator.normal_range_max != null && v > indicator.normal_range_max) return 'value-high'
  return 'value-normal'
}

const getLatestValueClass = (indicator: any) => {
  const v = getLatestValue(indicator.id)
  if (v == null) return ''
  if (indicator.normal_range_min != null && v < indicator.normal_range_min) return 'value-low'
  if (indicator.normal_range_max != null && v > indicator.normal_range_max) return 'value-high'
  return 'value-normal'
}

onMounted(loadDiseaseDetail)
</script>

<style scoped lang="scss">
.disease-detail-view { padding: 20px; }
.detail-header {
  display: flex; align-items: center; gap: 20px; margin-bottom: 30px;
  h1 { margin: 0; font-size: 28px; flex: 1; }
  .header-actions { display: flex; gap: 10px; align-items: center; }
}
.detail-container { display: flex; flex-direction: column; gap: 20px; }
.info-grid {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px;
  .info-item { display: flex; flex-direction: column;
    .label { color: #909399; font-size: 14px; margin-bottom: 5px; }
    .value { color: #303133; font-size: 16px; font-weight: 500; }
  }
}
.section-title { margin: 0 0 12px 0; font-size: 15px; color: #303133; }
.indicator-layout {
  display: flex; gap: 24px;
  .indicator-left { flex: 1; min-width: 0; }
  .indicator-right { width: 280px; flex-shrink: 0; }
}
.unit-text { color: #909399; font-size: 12px; margin-left: 4px; }
.value-normal { color: #67c23a; font-weight: 600; }
.value-high { color: #f56c6c; font-weight: 600; }
.value-low { color: #e6a23c; font-weight: 600; }
.reference-list { display: flex; flex-direction: column; gap: 12px; }
.reference-card {
  padding: 14px; border: 1px solid #e4e7ed; border-radius: 8px; background: #f9fafb;
  .ref-name { font-weight: 600; font-size: 15px; color: #303133; margin-bottom: 8px; }
  .ref-range {
    display: flex; align-items: baseline; gap: 6px; margin-bottom: 6px;
    .ref-value { font-size: 20px; font-weight: 700; color: #409eff; }
    .ref-value.no-data { font-size: 14px; color: #c0c4cc; font-weight: 400; }
    .ref-unit { font-size: 13px; color: #909399; }
  }
  .ref-latest { font-size: 13px; color: #606266; margin-bottom: 4px; }
  .ref-freq { font-size: 12px; color: #909399; }
}
.indicators-list {
  display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;
  .indicator-item {
    padding: 12px; border: 1px solid #ebeef5; border-radius: 4px; background: #fafafa;
    .indicator-header { display: flex; justify-content: space-between; align-items: center;
      .name { font-weight: 600; } .unit { color: #909399; font-size: 14px; }
    }
    .range { color: #606266; font-size: 14px; margin-top: 5px; }
  }
}
.plans-list {
  display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px;
  .plan-item {
    padding: 12px; border: 1px solid #ebeef5; border-radius: 4px; background: #fafafa;
    .plan-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
      .frequency { font-weight: 600; }
    }
    .plan-info { color: #606266; font-size: 14px; margin-bottom: 8px; div { margin: 4px 0; } }
    .plan-actions { display: flex; gap: 8px; }
  }
}
.card-actions { display: flex; gap: 10px; padding-top: 15px; border-top: 1px solid #ebeef5; }

// 疾病常识样式
.knowledge-content { padding: 0; }
.knowledge-sections { display: flex; flex-direction: column; gap: 16px; }
.knowledge-card {
  :deep(.el-card__header) { padding: 16px 20px; background: #f5f7fa; }
  .card-header {
    display: flex; align-items: center; gap: 10px;
    .section-icon { font-size: 20px; }
    .section-title { font-size: 16px; font-weight: 600; color: #303133; }
  }
  .section-content {
    line-height: 1.8; color: #606266;
    p { margin: 0 0 12px 0; }
    ul, ol { margin: 8px 0; padding-left: 24px; }
    li { margin: 6px 0; }
    strong { color: #303133; font-weight: 600; }
    table { margin: 12px 0; font-size: 14px; }
  }
}
</style>
