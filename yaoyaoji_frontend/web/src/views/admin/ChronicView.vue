<template>
  <div class="chronic-container">
    <h2 class="page-title">慢性病管理</h2>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <!-- 疾病模板 -->
      <el-tab-pane label="疾病模板" name="templates">
        <el-card class="filter-card" shadow="never">
          <div class="filter-row">
            <el-input v-model="tplSearch" placeholder="搜索模板名称" clearable style="width: 300px" @keyup.enter="loadTemplates">
              <template #append><el-button @click="loadTemplates">搜索</el-button></template>
            </el-input>
            <el-button type="primary" @click="openTplDialog()">新增模板</el-button>
          </div>
        </el-card>
        <el-card shadow="never">
          <el-table :data="templates" v-loading="tplLoading" stripe>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="display_name" label="疾病名称" width="120" />
            <el-table-column prop="disease_type" label="类型标识" width="140" />
            <el-table-column prop="icd10_code" label="ICD-10" width="100" />
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="默认指标" min-width="200">
              <template #default="{ row }">
                <el-tag v-for="ind in (row.default_indicators || [])" :key="ind.name" size="small" style="margin: 2px">
                  {{ ind.name }}{{ ind.unit ? `(${ind.unit})` : '' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="160">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="openTplDialog(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDeleteTpl(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrapper">
            <el-pagination v-model:current-page="tplPage.page" v-model:page-size="tplPage.page_size"
              :total="tplPage.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
              @size-change="loadTemplates" @current-change="loadTemplates" />
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 用户慢性病记录 -->
      <el-tab-pane label="用户记录" name="records">
        <el-card class="filter-card" shadow="never">
          <div class="filter-row">
            <div class="filter-left">
              <el-input v-model="recSearch" placeholder="搜索疾病名称或用户名" clearable style="width: 300px" @keyup.enter="loadRecords">
                <template #append><el-button @click="loadRecords">搜索</el-button></template>
              </el-input>
              <el-select v-model="recStatus" placeholder="控制状态" clearable style="width: 140px" @change="loadRecords">
                <el-option label="控制良好" value="good" />
                <el-option label="控制中等" value="fair" />
                <el-option label="控制不良" value="poor" />
              </el-select>
            </div>
          </div>
        </el-card>
        <el-card shadow="never">
          <el-table :data="records" v-loading="recLoading" stripe>
            <el-table-column prop="id" label="ID" width="70" />
            <el-table-column prop="username" label="用户" width="120" />
            <el-table-column prop="disease_name" label="疾病名称" width="120" />
            <el-table-column prop="icd10_code" label="ICD-10" width="90" />
            <el-table-column prop="diagnosis_date" label="诊断日期" width="120" />
            <el-table-column prop="diagnosis_hospital" label="诊断医院" min-width="150" show-overflow-tooltip />
            <el-table-column prop="diagnosis_doctor" label="诊断医生" width="100" />
            <el-table-column prop="current_treatment" label="治疗方案" min-width="180" show-overflow-tooltip />
            <el-table-column prop="control_status" label="控制状态" width="100">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.control_status)" size="small">{{ statusLabel(row.control_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="160">
              <template #default="{ row }">{{ row.updated_at ? formatDate(row.updated_at) : '' }}</template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrapper">
            <el-pagination v-model:current-page="recPage.page" v-model:page-size="recPage.page_size"
              :total="recPage.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
              @size-change="loadRecords" @current-change="loadRecords" />
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 模板弹窗 -->
    <el-dialog v-model="tplDialogVisible" :title="tplIsEdit ? '编辑模板' : '新增模板'" width="650px">
      <el-form :model="tplForm" :rules="tplRules" ref="tplFormRef" label-width="100px">
        <el-form-item label="类型标识" prop="disease_type">
          <el-input v-model="tplForm.disease_type" placeholder="如 hypertension" :disabled="tplIsEdit" />
        </el-form-item>
        <el-form-item label="疾病名称" prop="display_name">
          <el-input v-model="tplForm.display_name" placeholder="如 高血压" />
        </el-form-item>
        <el-form-item label="ICD-10编码">
          <el-input v-model="tplForm.icd10_code" placeholder="如 I10" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="tplForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="默认指标">
          <div v-for="(ind, idx) in tplForm.default_indicators" :key="idx" class="indicator-row">
            <el-input v-model="ind.name" placeholder="指标名" style="width: 120px" />
            <el-input v-model="ind.unit" placeholder="单位" style="width: 80px" />
            <el-input-number v-model="ind.normal_min" placeholder="最小值" :controls="false" style="width: 90px" />
            <span>~</span>
            <el-input-number v-model="ind.normal_max" placeholder="最大值" :controls="false" style="width: 90px" />
            <el-button type="danger" :icon="Delete" circle size="small" @click="tplForm.default_indicators.splice(idx, 1)" />
          </div>
          <el-button type="primary" size="small" @click="tplForm.default_indicators.push({ name: '', unit: '', normal_min: null, normal_max: null, check_frequency: 'daily' })">
            添加指标
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tplDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmitTpl">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import {
  getAdminDiseaseTemplates, createAdminDiseaseTemplate, updateAdminDiseaseTemplate, deleteAdminDiseaseTemplate,
  getAdminChronicRecords
} from '@/api/admin'
import type { AdminDiseaseTemplate, DiseaseTemplateCreate, AdminChronicRecord } from '@/types/admin'

const activeTab = ref('templates')
const submitting = ref(false)

// ===== 模板 =====
const tplLoading = ref(false)
const templates = ref<AdminDiseaseTemplate[]>([])
const tplSearch = ref('')
const tplPage = reactive({ page: 1, page_size: 20, total: 0 })
const tplDialogVisible = ref(false)
const tplIsEdit = ref(false)
const tplEditId = ref<number | null>(null)
const tplFormRef = ref()
const tplForm = reactive<DiseaseTemplateCreate>({
  disease_type: '', display_name: '', icd10_code: '', description: '', default_indicators: []
})
const tplRules = {
  disease_type: [{ required: true, message: '请输入类型标识', trigger: 'blur' }],
  display_name: [{ required: true, message: '请输入疾病名称', trigger: 'blur' }]
}

async function loadTemplates() {
  tplLoading.value = true
  try {
    const res = await getAdminDiseaseTemplates({ page: tplPage.page, page_size: tplPage.page_size, search: tplSearch.value || undefined })
    templates.value = res.items
    tplPage.total = res.total
  } catch { ElMessage.error('加载模板失败') }
  finally { tplLoading.value = false }
}

function openTplDialog(row?: AdminDiseaseTemplate) {
  if (row) {
    tplIsEdit.value = true
    tplEditId.value = row.id
    Object.assign(tplForm, { disease_type: row.disease_type, display_name: row.display_name, icd10_code: row.icd10_code || '', description: row.description || '', default_indicators: JSON.parse(JSON.stringify(row.default_indicators || [])) })
  } else {
    tplIsEdit.value = false
    tplEditId.value = null
    Object.assign(tplForm, { disease_type: '', display_name: '', icd10_code: '', description: '', default_indicators: [] })
  }
  tplDialogVisible.value = true
}

async function handleSubmitTpl() {
  await tplFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    submitting.value = true
    try {
      if (tplIsEdit.value && tplEditId.value) {
        await updateAdminDiseaseTemplate(tplEditId.value, tplForm)
        ElMessage.success('更新成功')
      } else {
        await createAdminDiseaseTemplate(tplForm)
        ElMessage.success('创建成功')
      }
      tplDialogVisible.value = false
      loadTemplates()
    } catch (e: any) { ElMessage.error(e.response?.data?.detail || '操作失败') }
    finally { submitting.value = false }
  })
}

async function handleDeleteTpl(row: AdminDiseaseTemplate) {
  try {
    await ElMessageBox.confirm(`确定删除模板 "${row.display_name}" 吗？`, '提示', { type: 'warning' })
    await deleteAdminDiseaseTemplate(row.id)
    ElMessage.success('删除成功')
    loadTemplates()
  } catch (e: any) { if (e !== 'cancel') ElMessage.error(e.response?.data?.detail || '删除失败') }
}

// ===== 用户慢性病记录 =====
const recLoading = ref(false)
const records = ref<AdminChronicRecord[]>([])
const recSearch = ref('')
const recStatus = ref('')
const recPage = reactive({ page: 1, page_size: 20, total: 0 })

const statusMap: Record<string, string> = { good: '控制良好', fair: '控制中等', poor: '控制不良' }
const statusTagMap: Record<string, string> = { good: 'success', fair: 'warning', poor: 'danger' }
function statusLabel(s: string | null) { return s ? statusMap[s] || s : '未知' }
function statusTagType(s: string | null) { return (s ? statusTagMap[s] : 'info') as any }

async function loadRecords() {
  recLoading.value = true
  try {
    const res = await getAdminChronicRecords({ page: recPage.page, page_size: recPage.page_size, search: recSearch.value || undefined, control_status: recStatus.value || undefined })
    records.value = res.items
    recPage.total = res.total
  } catch { ElMessage.error('加载用户记录失败') }
  finally { recLoading.value = false }
}

// ===== 通用 =====
function handleTabChange(tab: string) {
  if (tab === 'templates') loadTemplates()
  else if (tab === 'records') loadRecords()
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => { loadTemplates() })
</script>

<style scoped>
.chronic-container { max-width: 1400px; }
.page-title { margin: 0 0 20px 0; font-size: 20px; font-weight: 600; color: #303133; }
.filter-card { margin-bottom: 20px; }
.filter-row { display: flex; justify-content: space-between; align-items: center; }
.filter-left { display: flex; gap: 12px; align-items: center; }
.pagination-wrapper { margin-top: 20px; display: flex; justify-content: flex-end; }
.indicator-row { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
</style>
