<template>
  <div class="health-profile-container">
    <el-card class="header-card">
      <h2>健康档案</h2>
      <p class="subtitle">完善您的健康档案，让用药更安全</p>
    </el-card>

    <el-tabs v-model="activeTab" class="profile-tabs">
      <!-- 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>基本健康信息</span>
              <el-button type="primary" @click="saveBasicInfo" :loading="saving">保存</el-button>
            </div>
          </template>
          
          <el-form :model="basicInfo" label-width="120px">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="真实姓名">
                  <el-input v-model="basicInfo.real_name" placeholder="请输入真实姓名" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="血型">
                  <el-select v-model="basicInfo.blood_type" placeholder="请选择血型" clearable>
                    <el-option label="A型" value="A" />
                    <el-option label="B型" value="B" />
                    <el-option label="AB型" value="AB" />
                    <el-option label="O型" value="O" />
                    <el-option label="未知" value="未知" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="身高 (cm)">
                  <el-input-number v-model="basicInfo.height" :min="0" :max="300" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="体重 (kg)">
                  <el-input-number v-model="basicInfo.weight" :min="0" :max="500" style="width: 100%;" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="BMI">
                  <el-input :value="bmi" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="血压 (mmHg)">
                  <div style="display: flex; gap: 10px; align-items: center;">
                    <el-input-number 
                      v-model="basicInfo.systolic_pressure" 
                      :min="0" 
                      :max="300" 
                      placeholder="收缩压"
                      style="flex: 1;"
                    />
                    <span>/</span>
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
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="心率 (次/分)">
                  <el-input-number v-model="basicInfo.heart_rate" :min="0" :max="300" style="width: 100%;" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="血糖 (mmol/L)">
                  <el-input v-model="basicInfo.blood_glucose" placeholder="如: 5.6" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
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
        </el-card>
      </el-tab-pane>

      <!-- 过敏史 -->
      <el-tab-pane label="过敏史" name="allergies">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>过敏史记录</span>
              <el-button type="primary" @click="showAllergyDialog">添加过敏记录</el-button>
            </div>
          </template>
          
          <el-table :data="allergies" stripe>
            <el-table-column prop="allergen" label="过敏原" width="150" />
            <el-table-column prop="allergen_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.allergen_type" size="small">{{ row.allergen_type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reaction" label="过敏反应" />
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.severity === '严重'" type="danger" size="small">严重</el-tag>
                <el-tag v-else-if="row.severity === '中等'" type="warning" size="small">中等</el-tag>
                <el-tag v-else-if="row.severity === '轻微'" type="success" size="small">轻微</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editAllergy(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteAllergy(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 家族病史 -->
      <el-tab-pane label="家族病史" name="family-history">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>家族病史</span>
              <el-button type="primary" @click="showFamilyHistoryDialog">添加病史</el-button>
            </div>
          </template>
          
          <el-table :data="familyHistories" stripe>
            <el-table-column prop="relative" label="亲属关系" width="120" />
            <el-table-column prop="disease" label="疾病" width="180" />
            <el-table-column prop="onset_age" label="发病年龄" width="100" />
            <el-table-column prop="notes" label="备注" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editFamilyHistory(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteFamilyHistory(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 手术记录 -->
      <el-tab-pane label="手术记录" name="surgeries">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>手术记录</span>
              <el-button type="primary" @click="showSurgeryDialog">添加手术记录</el-button>
            </div>
          </template>
          
          <el-table :data="surgeries" stripe>
            <el-table-column prop="surgery_name" label="手术名称" width="200" />
            <el-table-column prop="surgery_date" label="手术日期" width="120" />
            <el-table-column prop="hospital" label="医院" width="180" />
            <el-table-column prop="doctor" label="主刀医生" width="100" />
            <el-table-column prop="notes" label="备注" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editSurgery(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteSurgery(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 体检报告 -->
      <el-tab-pane label="体检报告" name="checkups">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>体检报告</span>
              <el-button type="primary" @click="showCheckupDialog">添加体检报告</el-button>
            </div>
          </template>
          
          <el-table :data="checkups" stripe>
            <el-table-column prop="checkup_date" label="体检日期" width="120" />
            <el-table-column prop="checkup_type" label="体检类型" width="150" />
            <el-table-column prop="hospital" label="医院" width="180" />
            <el-table-column prop="summary" label="总结" show-overflow-tooltip />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editCheckup(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteCheckup(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 疫苗接种 -->
      <el-tab-pane label="疫苗接种" name="vaccinations">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>疫苗接种记录</span>
              <el-button type="primary" @click="showVaccinationDialog">添加接种记录</el-button>
            </div>
          </template>
          
          <el-table :data="vaccinations" stripe>
            <el-table-column prop="vaccine_name" label="疫苗名称" width="180" />
            <el-table-column prop="vaccination_date" label="接种日期" width="120" />
            <el-table-column prop="hospital" label="接种地点" width="180" />
            <el-table-column prop="batch_number" label="批次号" width="120" />
            <el-table-column prop="next_dose_date" label="下次接种" width="120" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editVaccination(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteVaccination(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 过敏史对话框 -->
    <el-dialog v-model="allergyDialogVisible" :title="editingAllergy ? '编辑过敏记录' : '添加过敏记录'" width="600px">
      <el-form :model="allergyForm" label-width="100px">
        <el-form-item label="过敏原" required>
          <el-input v-model="allergyForm.allergen" placeholder="如：青霉素、花生" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="allergyForm.allergen_type" placeholder="请选择" clearable>
            <el-option label="药物" value="药物" />
            <el-option label="食物" value="食物" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="过敏反应">
          <el-input v-model="allergyForm.reaction" type="textarea" :rows="2" placeholder="如：皮疹、呼吸困难" />
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="allergyForm.severity" placeholder="请选择">
            <el-option label="轻微" value="轻微" />
            <el-option label="中等" value="中等" />
            <el-option label="严重" value="严重" />
          </el-select>
        </el-form-item>
        <el-form-item label="发现日期">
          <el-date-picker v-model="allergyForm.discovered_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="allergyForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="allergyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAllergy" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 家族病史对话框 -->
    <el-dialog v-model="familyHistoryDialogVisible" :title="editingFamilyHistory ? '编辑家族病史' : '添加家族病史'" width="600px">
      <el-form :model="familyHistoryForm" label-width="100px">
        <el-form-item label="亲属关系" required>
          <el-input v-model="familyHistoryForm.relative" placeholder="如：父亲、母亲、祖父" />
        </el-form-item>
        <el-form-item label="疾病" required>
          <el-input v-model="familyHistoryForm.disease" placeholder="如：高血压、糖尿病" />
        </el-form-item>
        <el-form-item label="发病年龄">
          <el-input-number v-model="familyHistoryForm.onset_age" :min="0" :max="150" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="familyHistoryForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="familyHistoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFamilyHistory" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 手术记录对话框 -->
    <el-dialog v-model="surgeryDialogVisible" :title="editingSurgery ? '编辑手术记录' : '添加手术记录'" width="600px">
      <el-form :model="surgeryForm" label-width="100px">
        <el-form-item label="手术名称" required>
          <el-input v-model="surgeryForm.surgery_name" placeholder="如：阑尾切除术" />
        </el-form-item>
        <el-form-item label="手术日期" required>
          <el-date-picker v-model="surgeryForm.surgery_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="医院">
          <el-input v-model="surgeryForm.hospital" placeholder="医院名称" />
        </el-form-item>
        <el-form-item label="主刀医生">
          <el-input v-model="surgeryForm.doctor" placeholder="医生姓名" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="surgeryForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="surgeryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSurgery" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 体检报告对话框 -->
    <el-dialog v-model="checkupDialogVisible" :title="editingCheckup ? '编辑体检报告' : '添加体检报告'" width="600px">
      <el-form :model="checkupForm" label-width="100px">
        <el-form-item label="体检日期" required>
          <el-date-picker v-model="checkupForm.checkup_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="体检类型">
          <el-input v-model="checkupForm.checkup_type" placeholder="如：入职体检、年度体检" />
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
        <el-button @click="checkupDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCheckup" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 疫苗接种对话框 -->
    <el-dialog v-model="vaccinationDialogVisible" :title="editingVaccination ? '编辑接种记录' : '添加接种记录'" width="600px">
      <el-form :model="vaccinationForm" label-width="100px">
        <el-form-item label="疫苗名称" required>
          <el-input v-model="vaccinationForm.vaccine_name" placeholder="如：新冠疫苗、流感疫苗" />
        </el-form-item>
        <el-form-item label="接种日期" required>
          <el-date-picker v-model="vaccinationForm.vaccination_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="接种地点">
          <el-input v-model="vaccinationForm.hospital" placeholder="医院或社区卫生服务中心" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="vaccinationForm.batch_number" placeholder="疫苗批次号" />
        </el-form-item>
        <el-form-item label="下次接种">
          <el-date-picker v-model="vaccinationForm.next_dose_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="vaccinationForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="vaccinationDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVaccination" :loading="saving">保存</el-button>
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

const route = useRoute()
const activeTab = ref('basic')
const saving = ref(false)

// 基本信息
const basicInfo = ref({
  real_name: null as string | null,
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

// 计算BMI
const bmi = computed(() => {
  if (basicInfo.value.height && basicInfo.value.weight) {
    const h = basicInfo.value.height / 100
    const bmiValue = basicInfo.value.weight / (h * h)
    return bmiValue.toFixed(1)
  }
  return '-'
})

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

// 加载数据
async function loadData() {
  try {
    const profile = await healthProfileAPI.get()
    if (profile) {
      basicInfo.value = {
        real_name: profile.real_name,
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
  // 防止重复提交
  if (saving.value) {
    console.log('⚠️ 正在保存中，请勿重复点击')
    return
  }
  
  saving.value = true
  try {
    console.log('📤 提交的数据:', JSON.stringify(basicInfo.value, null, 2))
    const result = await healthProfileAPI.createOrUpdate(basicInfo.value)
    console.log('✅ 保存成功:', result)
    ElMessage.success('保存成功')
  } catch (error: any) {
    console.error('❌ 保存失败:', error)
    console.error('❌ 错误详情:', {
      message: error.message,
      response: error.response,
      status: error.response?.status,
      data: error.response?.data
    })
    
    const errorMsg = error.response?.data?.detail || error.message || '保存失败'
    console.error('❌ 显示错误消息:', errorMsg)
    ElMessage.error(errorMsg)
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
    // 处理日期格式
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
    await ElMessageBox.confirm('确定要删除这条过敏记录吗？', '提示', {
      type: 'warning'
    })
    await healthProfileAPI.allergies.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
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
    await ElMessageBox.confirm('确定要删除这条家族病史吗？', '提示', {
      type: 'warning'
    })
    await healthProfileAPI.familyHistory.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
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
    // 处理日期格式
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
    await ElMessageBox.confirm('确定要删除这条手术记录吗？', '提示', {
      type: 'warning'
    })
    await healthProfileAPI.surgeries.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
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
    // 处理日期格式
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
    await ElMessageBox.confirm('确定要删除这条体检报告吗？', '提示', {
      type: 'warning'
    })
    await healthProfileAPI.checkups.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
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
    // 处理日期格式
    const submitData = { ...vaccinationForm.value }
    
    // 接种日期
    if (submitData.vaccination_date && submitData.vaccination_date instanceof Date) {
      const d = submitData.vaccination_date
      submitData.vaccination_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}` as any
    }
    
    // 下次接种日期
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
    await ElMessageBox.confirm('确定要删除这条接种记录吗？', '提示', {
      type: 'warning'
    })
    await healthProfileAPI.vaccinations.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

onMounted(() => {
  // 检查URL参数，设置默认标签页
  const tabParam = route.query.tab as string
  if (tabParam) {
    activeTab.value = tabParam
  }
  loadData()
})
</script>

<style scoped lang="scss">
.health-profile-container {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
  
  h2 {
    margin: 0 0 8px 0;
    font-size: 24px;
    color: #303133;
  }
  
  .subtitle {
    margin: 0;
    color: #909399;
    font-size: 14px;
  }
}

.profile-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      font-size: 16px;
      font-weight: 500;
    }
  }
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
