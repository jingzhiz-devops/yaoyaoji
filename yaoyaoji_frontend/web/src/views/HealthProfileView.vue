<template>
  <div class="health-profile-container">
    <div class="profile-content">
      <el-tabs v-model="activeTab" class="custom-tabs" type="border-card">
        <!-- 基本信息 -->
        <el-tab-pane name="basic">
          <template #label>
            <span class="tab-label"><el-icon><User /></el-icon> 基本信息</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>基本健康信息</h3>
              <el-button type="primary" @click="saveBasicInfo" :loading="saving">保存修改</el-button>
            </div>
            
            <el-form :model="basicInfo" label-width="100px" label-position="top" class="custom-form">
              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="真实姓名">
                    <el-input v-model="basicInfo.real_name" placeholder="请输入真实姓名" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="出生日期">
                    <el-date-picker v-model="basicInfo.birth_date" type="date" placeholder="选择日期" style="width: 100%" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="年龄">
                    <el-input :value="age" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="8">
                  <el-form-item label="血型">
                    <el-select v-model="basicInfo.blood_type" placeholder="请选择血型" clearable style="width: 100%">
                      <el-option label="A型" value="A" />
                      <el-option label="B型" value="B" />
                      <el-option label="AB型" value="AB" />
                      <el-option label="O型" value="O" />
                      <el-option label="未知" value="未知" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="BMI 指数">
                    <el-input :value="bmi" disabled>
                      <template #append>
                        <el-tag size="small" :type="getBMIType(bmi)">{{ getBMIStatus(bmi) }}</el-tag>
                      </template>
                    </el-input>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="身高 (cm)">
                    <el-input-number v-model="basicInfo.height" :min="0" :max="300" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="体重 (kg)">
                    <el-input-number v-model="basicInfo.weight" :min="0" :max="500" style="width: 100%;" />
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="心率 (次/分)">
                    <el-input-number v-model="basicInfo.heart_rate" :min="0" :max="300" style="width: 100%;" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="24">
                <el-col :span="12">
                  <el-form-item label="血压 (mmHg)">
                    <div class="pressure-inputs">
                      <el-input-number 
                        v-model="basicInfo.systolic_pressure" 
                        :min="0" 
                        :max="300" 
                        placeholder="收缩压"
                        style="flex: 1;"
                      />
                      <span class="separator">/</span>
                      <el-input-number 
                        v-model="basicInfo.diastolic_pressure" 
                        :min="0" 
                        :max="200" 
                        placeholder="舒张压"
                        style="flex: 1;"
                      />
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="血糖 (mmol/L)">
                    <el-input v-model="basicInfo.blood_glucose" placeholder="如: 5.6" />
                  </el-form-item>
                </el-col>
                <el-col :span="6">
                  <el-form-item label="体温 (℃)">
                    <el-input v-model="basicInfo.temperature" placeholder="如: 36.5" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item label="慢性疾病">
                <el-input 
                  v-model="basicInfo.chronic_diseases" 
                  type="textarea" 
                  :rows="3"
                  placeholder="如：高血压、糖尿病等，多个用逗号分隔"
                />
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- 过敏史 -->
        <el-tab-pane name="allergies">
          <template #label>
            <span class="tab-label"><el-icon><Warning /></el-icon> 过敏史</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>过敏史记录</h3>
              <el-button type="primary" @click="showAllergyDialog">添加记录</el-button>
            </div>
            
            <el-table :data="allergies" stripe class="custom-table">
              <el-table-column prop="allergen" label="过敏原" width="180" />
              <el-table-column prop="allergen_type" label="类型" width="120">
                <template #default="{ row }">
                  <el-tag effect="plain">{{ row.allergen_type || '未知' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="reaction" label="过敏反应" />
              <el-table-column prop="severity" label="严重程度" width="120">
                <template #default="{ row }">
                  <el-tag :type="getSeverityType(row.severity)">{{ row.severity || '未知' }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" @click="editAllergy(row)">编辑</el-button>
                  <el-button link type="danger" @click="deleteAllergy(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 家族病史 -->
        <el-tab-pane name="family-history">
          <template #label>
            <span class="tab-label"><el-icon><Connection /></el-icon> 家族病史</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>家族病史</h3>
              <el-button type="primary" @click="showFamilyHistoryDialog">添加病史</el-button>
            </div>
            
            <el-table :data="familyHistories" stripe class="custom-table">
              <el-table-column prop="relative" label="亲属关系" width="150" />
              <el-table-column prop="disease" label="疾病" width="200" />
              <el-table-column prop="onset_age" label="发病年龄" width="120">
                <template #default="{ row }">
                  {{ row.onset_age ? `${row.onset_age}岁` : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="notes" label="备注" />
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" @click="editFamilyHistory(row)">编辑</el-button>
                  <el-button link type="danger" @click="deleteFamilyHistory(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 手术记录 -->
        <el-tab-pane name="surgeries">
          <template #label>
            <span class="tab-label"><el-icon><KnifeFork /></el-icon> 手术记录</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>手术记录</h3>
              <el-button type="primary" @click="showSurgeryDialog">添加记录</el-button>
            </div>
            
            <el-table :data="surgeries" stripe class="custom-table">
              <el-table-column prop="surgery_name" label="手术名称" width="200" />
              <el-table-column prop="surgery_date" label="手术日期" width="150" />
              <el-table-column prop="hospital" label="医院" width="200" />
              <el-table-column prop="doctor" label="主刀医生" width="120" />
              <el-table-column prop="notes" label="备注" />
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" @click="editSurgery(row)">编辑</el-button>
                  <el-button link type="danger" @click="deleteSurgery(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 体检报告 -->
        <el-tab-pane name="checkups">
          <template #label>
            <span class="tab-label"><el-icon><DocumentChecked /></el-icon> 体检报告</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>体检报告</h3>
              <el-button type="primary" @click="showCheckupDialog">添加报告</el-button>
            </div>
            
            <el-table :data="checkups" stripe class="custom-table">
              <el-table-column prop="checkup_date" label="体检日期" width="150" />
              <el-table-column prop="checkup_type" label="体检类型" width="180" />
              <el-table-column prop="hospital" label="医院" width="200" />
              <el-table-column prop="summary" label="总结" show-overflow-tooltip />
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" @click="editCheckup(row)">编辑</el-button>
                  <el-button link type="danger" @click="deleteCheckup(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 疫苗接种 -->
        <el-tab-pane name="vaccinations">
          <template #label>
            <span class="tab-label"><el-icon><Aim /></el-icon> 疫苗接种</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>疫苗接种记录</h3>
              <el-button type="primary" @click="showVaccinationDialog">添加记录</el-button>
            </div>
            
            <el-table :data="vaccinations" stripe class="custom-table">
              <el-table-column prop="vaccine_name" label="疫苗名称" width="200" />
              <el-table-column prop="vaccination_date" label="接种日期" width="150" />
              <el-table-column prop="hospital" label="接种地点" width="200" />
              <el-table-column prop="batch_number" label="批次号" width="150" />
              <el-table-column prop="next_dose_date" label="下次接种" width="150" />
              <el-table-column label="操作" width="150" align="center">
                <template #default="{ row }">
                  <el-button link type="primary" @click="editVaccination(row)">编辑</el-button>
                  <el-button link type="danger" @click="deleteVaccination(row.id)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Dialogs (Keeping logic, updating styles) -->
    <el-dialog v-model="allergyDialogVisible" :title="editingAllergy ? '编辑过敏记录' : '添加过敏记录'" width="500px" class="custom-dialog">
      <el-form :model="allergyForm" label-width="80px" label-position="top">
        <el-form-item label="过敏原" required>
          <el-input v-model="allergyForm.allergen" placeholder="如：青霉素、花生" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="allergyForm.allergen_type" placeholder="请选择" style="width: 100%">
                <el-option label="药物" value="药物" />
                <el-option label="食物" value="食物" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="严重程度">
              <el-select v-model="allergyForm.severity" placeholder="请选择" style="width: 100%">
                <el-option label="轻微" value="轻微" />
                <el-option label="中等" value="中等" />
                <el-option label="严重" value="严重" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="过敏反应">
          <el-input v-model="allergyForm.reaction" type="textarea" :rows="2" placeholder="如：皮疹、呼吸困难" />
        </el-form-item>
        <el-form-item label="发现日期">
          <el-date-picker v-model="allergyForm.discovered_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="allergyForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="allergyDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAllergy" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Other dialogs follow similar pattern... -->
    <el-dialog v-model="familyHistoryDialogVisible" :title="editingFamilyHistory ? '编辑家族病史' : '添加家族病史'" width="500px" class="custom-dialog">
      <el-form :model="familyHistoryForm" label-width="80px" label-position="top">
        <el-form-item label="亲属关系" required>
          <el-input v-model="familyHistoryForm.relative" placeholder="如：父亲、母亲" />
        </el-form-item>
        <el-form-item label="疾病" required>
          <el-input v-model="familyHistoryForm.disease" placeholder="如：高血压" />
        </el-form-item>
        <el-form-item label="发病年龄">
          <el-input-number v-model="familyHistoryForm.onset_age" :min="0" :max="150" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="familyHistoryForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="familyHistoryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveFamilyHistory" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="surgeryDialogVisible" :title="editingSurgery ? '编辑手术记录' : '添加手术记录'" width="500px" class="custom-dialog">
      <el-form :model="surgeryForm" label-width="80px" label-position="top">
        <el-form-item label="手术名称" required>
          <el-input v-model="surgeryForm.surgery_name" placeholder="如：阑尾切除术" />
        </el-form-item>
        <el-form-item label="手术日期" required>
          <el-date-picker v-model="surgeryForm.surgery_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="医院">
              <el-input v-model="surgeryForm.hospital" placeholder="医院名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主刀医生">
              <el-input v-model="surgeryForm.doctor" placeholder="医生姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="surgeryForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="surgeryDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveSurgery" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="checkupDialogVisible" :title="editingCheckup ? '编辑体检报告' : '添加体检报告'" width="500px" class="custom-dialog">
      <el-form :model="checkupForm" label-width="80px" label-position="top">
        <el-form-item label="体检日期" required>
          <el-date-picker v-model="checkupForm.checkup_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="体检类型">
          <el-input v-model="checkupForm.checkup_type" placeholder="如：入职体检" />
        </el-form-item>
        <el-form-item label="医院">
          <el-input v-model="checkupForm.hospital" placeholder="医院名称" />
        </el-form-item>
        <el-form-item label="总结">
          <el-input v-model="checkupForm.summary" type="textarea" :rows="3" placeholder="体检总结" />
        </el-form-item>
        <el-form-item label="报告文件">
          <el-input v-model="checkupForm.file_url" placeholder="文件URL（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="checkupDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveCheckup" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="vaccinationDialogVisible" :title="editingVaccination ? '编辑接种记录' : '添加接种记录'" width="500px" class="custom-dialog">
      <el-form :model="vaccinationForm" label-width="80px" label-position="top">
        <el-form-item label="疫苗名称" required>
          <el-input v-model="vaccinationForm.vaccine_name" placeholder="如：流感疫苗" />
        </el-form-item>
        <el-form-item label="接种日期" required>
          <el-date-picker v-model="vaccinationForm.vaccination_date" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="接种地点">
          <el-input v-model="vaccinationForm.hospital" placeholder="医院或社区卫生服务中心" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="批次号">
              <el-input v-model="vaccinationForm.batch_number" placeholder="疫苗批次号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="下次接种">
              <el-date-picker v-model="vaccinationForm.next_dose_date" type="date" placeholder="选择日期" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="vaccinationForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="vaccinationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveVaccination" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { healthProfileAPI } from '@/api'
import { useUserStore } from '@/stores/user'
import { User, Warning, Connection, KnifeFork, DocumentChecked, Aim } from '@element-plus/icons-vue'

const route = useRoute()
const userStore = useUserStore()
const activeTab = ref('basic')
const saving = ref(false)

// 基本信息
const basicInfo = ref({
  real_name: null as string | null,
  birth_date: null as string | null,
  blood_type: null as string | null,
  height: null as number | null,
  weight: null as number | null,
  systolic_pressure: null as number | null,
  diastolic_pressure: null as number | null,
  heart_rate: null as number | null,
  blood_glucose: null as string | null,
  temperature: null as string | null,
  chronic_diseases: null as string | null
})

// 计算年龄
const age = computed(() => {
  if (basicInfo.value.birth_date) {
    const birthDate = new Date(basicInfo.value.birth_date)
    const today = new Date()
    let calculatedAge = today.getFullYear() - birthDate.getFullYear()
    const monthDiff = today.getMonth() - birthDate.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      calculatedAge--
    }
    return calculatedAge
  }
  return '-'
})

// 计算BMI
const bmi = computed(() => {
  if (basicInfo.value.height && basicInfo.value.weight) {
    const h = basicInfo.value.height / 100
    const bmiValue = basicInfo.value.weight / (h * h)
    return bmiValue.toFixed(1)
  }
  return '-'
})

function getBMIType(bmi: string) {
  if (bmi === '-') return 'info'
  const val = parseFloat(bmi)
  if (val < 18.5) return 'warning'
  if (val < 24) return 'success'
  if (val < 28) return 'warning'
  return 'danger'
}

function getBMIStatus(bmi: string) {
  if (bmi === '-') return '未知'
  const val = parseFloat(bmi)
  if (val < 18.5) return '偏瘦'
  if (val < 24) return '正常'
  if (val < 28) return '超重'
  return '肥胖'
}

function getSeverityType(severity: string) {
  if (severity === '严重') return 'danger'
  if (severity === '中等') return 'warning'
  if (severity === '轻微') return 'success'
  return 'info'
}

// 过敏史
const allergies = ref<any[]>([])
const allergyDialogVisible = ref(false)
const editingAllergy = ref<any>(null)
const allergyForm = ref({
  allergen: '',
  allergen_type: null,
  reaction: null,
  severity: null,
  discovered_date: null,
  notes: null
})

// 家族病史
const familyHistories = ref<any[]>([])
const familyHistoryDialogVisible = ref(false)
const editingFamilyHistory = ref<any>(null)
const familyHistoryForm = ref({
  relative: '',
  disease: '',
  onset_age: null,
  notes: null
})

// 手术记录
const surgeries = ref<any[]>([])
const surgeryDialogVisible = ref(false)
const editingSurgery = ref<any>(null)
const surgeryForm = ref({
  surgery_name: '',
  surgery_date: null,
  hospital: null,
  doctor: null,
  notes: null
})

// 体检报告
const checkups = ref<any[]>([])
const checkupDialogVisible = ref(false)
const editingCheckup = ref<any>(null)
const checkupForm = ref({
  checkup_date: null,
  checkup_type: null,
  hospital: null,
  summary: null,
  file_url: null
})

// 疫苗接种
const vaccinations = ref<any[]>([])
const vaccinationDialogVisible = ref(false)
const editingVaccination = ref<any>(null)
const vaccinationForm = ref({
  vaccine_name: '',
  vaccination_date: null,
  hospital: null,
  batch_number: null,
  next_dose_date: null,
  notes: null
})

onMounted(async () => {
  await loadData()
})

// 加载数据
async function loadData() {
  try {
    const profile = await healthProfileAPI.get()
    if (profile) {
      basicInfo.value = {
        real_name: profile.real_name,
        birth_date: profile.birth_date,
        blood_type: profile.blood_type,
        height: profile.height,
        weight: profile.weight,
        systolic_pressure: profile.systolic_pressure,
        diastolic_pressure: profile.diastolic_pressure,
        heart_rate: profile.heart_rate,
        blood_glucose: profile.blood_glucose,
        temperature: profile.temperature,
        chronic_diseases: profile.chronic_diseases
      }
    }
    
    allergies.value = await healthProfileAPI.allergies.list()
    familyHistories.value = await healthProfileAPI.familyHistory.list()
    surgeries.value = await healthProfileAPI.surgeries.list()
    checkups.value = await healthProfileAPI.checkups.list()
    vaccinations.value = await healthProfileAPI.vaccinations.list()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载失败')
  }
}

// 保存基本信息
async function saveBasicInfo() {
  if (saving.value) return
  saving.value = true
  try {
    const submitData = { ...basicInfo.value }
    // 转换日期格式
    if (submitData.birth_date && submitData.birth_date instanceof Date) {
      const d = submitData.birth_date
      submitData.birth_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    await healthProfileAPI.createOrUpdate(submitData)
    // 刷新用户信息，同步更新User表的birth_date
    await userStore.fetchUserInfo()
    ElMessage.success('保存成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

// 过敏史相关
function showAllergyDialog() {
  editingAllergy.value = null
  allergyForm.value = {
    allergen: '',
    allergen_type: null,
    reaction: null,
    severity: null,
    discovered_date: null,
    notes: null
  }
  allergyDialogVisible.value = true
}

function editAllergy(row: any) {
  editingAllergy.value = row
  allergyForm.value = { ...row }
  allergyDialogVisible.value = true
}

async function saveAllergy() {
  if (!allergyForm.value.allergen) {
    ElMessage.warning('请输入过敏原')
    return
  }
  
  saving.value = true
  try {
    const submitData = { ...allergyForm.value }
    if (submitData.discovered_date && submitData.discovered_date instanceof Date) {
      const d = submitData.discovered_date
      submitData.discovered_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    
    if (editingAllergy.value) {
      await healthProfileAPI.allergies.update(editingAllergy.value.id, submitData)
    } else {
      await healthProfileAPI.allergies.create(submitData)
    }
    ElMessage.success('保存成功')
    allergyDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteAllergy(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条过敏记录吗？', '提示', { type: 'warning' })
    await healthProfileAPI.allergies.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

// 家族病史相关
function showFamilyHistoryDialog() {
  editingFamilyHistory.value = null
  familyHistoryForm.value = {
    relative: '',
    disease: '',
    onset_age: null,
    notes: null
  }
  familyHistoryDialogVisible.value = true
}

function editFamilyHistory(row: any) {
  editingFamilyHistory.value = row
  familyHistoryForm.value = { ...row }
  familyHistoryDialogVisible.value = true
}

async function saveFamilyHistory() {
  if (!familyHistoryForm.value.relative || !familyHistoryForm.value.disease) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  saving.value = true
  try {
    if (editingFamilyHistory.value) {
      await healthProfileAPI.familyHistory.update(editingFamilyHistory.value.id, familyHistoryForm.value)
    } else {
      await healthProfileAPI.familyHistory.create(familyHistoryForm.value)
    }
    ElMessage.success('保存成功')
    familyHistoryDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteFamilyHistory(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条家族病史吗？', '提示', { type: 'warning' })
    await healthProfileAPI.familyHistory.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

// 手术记录相关
function showSurgeryDialog() {
  editingSurgery.value = null
  surgeryForm.value = {
    surgery_name: '',
    surgery_date: null,
    hospital: null,
    doctor: null,
    notes: null
  }
  surgeryDialogVisible.value = true
}

function editSurgery(row: any) {
  editingSurgery.value = row
  surgeryForm.value = { ...row }
  surgeryDialogVisible.value = true
}

async function saveSurgery() {
  if (!surgeryForm.value.surgery_name || !surgeryForm.value.surgery_date) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  saving.value = true
  try {
    const submitData = { ...surgeryForm.value }
    if (submitData.surgery_date && submitData.surgery_date instanceof Date) {
      const d = submitData.surgery_date
      submitData.surgery_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    
    if (editingSurgery.value) {
      await healthProfileAPI.surgeries.update(editingSurgery.value.id, submitData)
    } else {
      await healthProfileAPI.surgeries.create(submitData)
    }
    ElMessage.success('保存成功')
    surgeryDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteSurgery(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条手术记录吗？', '提示', { type: 'warning' })
    await healthProfileAPI.surgeries.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

// 体检报告相关
function showCheckupDialog() {
  editingCheckup.value = null
  checkupForm.value = {
    checkup_date: null,
    checkup_type: null,
    hospital: null,
    summary: null,
    file_url: null
  }
  checkupDialogVisible.value = true
}

function editCheckup(row: any) {
  editingCheckup.value = row
  checkupForm.value = { ...row }
  checkupDialogVisible.value = true
}

async function saveCheckup() {
  if (!checkupForm.value.checkup_date) {
    ElMessage.warning('请选择体检日期')
    return
  }
  
  saving.value = true
  try {
    const submitData = { ...checkupForm.value }
    if (submitData.checkup_date && submitData.checkup_date instanceof Date) {
      const d = submitData.checkup_date
      submitData.checkup_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    
    if (editingCheckup.value) {
      await healthProfileAPI.checkups.update(editingCheckup.value.id, submitData)
    } else {
      await healthProfileAPI.checkups.create(submitData)
    }
    ElMessage.success('保存成功')
    checkupDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteCheckup(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条体检报告吗？', '提示', { type: 'warning' })
    await healthProfileAPI.checkups.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

// 疫苗接种相关
function showVaccinationDialog() {
  editingVaccination.value = null
  vaccinationForm.value = {
    vaccine_name: '',
    vaccination_date: null,
    hospital: null,
    batch_number: null,
    next_dose_date: null,
    notes: null
  }
  vaccinationDialogVisible.value = true
}

function editVaccination(row: any) {
  editingVaccination.value = row
  vaccinationForm.value = { ...row }
  vaccinationDialogVisible.value = true
}

async function saveVaccination() {
  if (!vaccinationForm.value.vaccine_name || !vaccinationForm.value.vaccination_date) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  saving.value = true
  try {
    const submitData = { ...vaccinationForm.value }
    if (submitData.vaccination_date && submitData.vaccination_date instanceof Date) {
      const d = submitData.vaccination_date
      submitData.vaccination_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    if (submitData.next_dose_date && submitData.next_dose_date instanceof Date) {
      const d = submitData.next_dose_date
      submitData.next_dose_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    
    if (editingVaccination.value) {
      await healthProfileAPI.vaccinations.update(editingVaccination.value.id, submitData)
    } else {
      await healthProfileAPI.vaccinations.create(submitData)
    }
    ElMessage.success('保存成功')
    vaccinationDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteVaccination(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这条接种记录吗？', '提示', { type: 'warning' })
    await healthProfileAPI.vaccinations.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}
</script>

<style scoped>
.health-profile-container {
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

/* Tabs */
.profile-content {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.custom-tabs {
  border: none;
  box-shadow: none;
}

.custom-tabs :deep(.el-tabs__header) {
  background-color: #f9fafb;
  border-bottom: 1px solid var(--color-border);
}

.custom-tabs :deep(.el-tabs__item) {
  height: 50px;
  line-height: 50px;
  font-size: 15px;
  color: var(--color-text-secondary);
}

.custom-tabs :deep(.el-tabs__item.is-active) {
  color: var(--color-primary);
  background-color: white;
  font-weight: 600;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-pane-content {
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
}

/* Form Styles */
.custom-form {
  max-width: 900px;
}

.pressure-inputs {
  display: flex;
  align-items: center;
  gap: 12px;
}

.separator {
  color: var(--color-text-light);
  font-weight: bold;
}

/* Table Styles */
.custom-table {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.custom-table :deep(th) {
  background-color: #f9fafb;
  color: var(--color-text-main);
  font-weight: 600;
}
</style>
