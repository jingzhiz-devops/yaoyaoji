<template>
  <div class="diseases-container">
    <h2 class="page-title">疾病管理</h2>

    <!-- 搜索和操作 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <el-input v-model="search" placeholder="搜索疾病名称" clearable style="width: 300px" @keyup.enter="loadDiseases">
          <template #append>
            <el-button @click="loadDiseases">搜索</el-button>
          </template>
        </el-input>
        <el-button type="primary" @click="openDialog()">新增疾病</el-button>
      </div>
    </el-card>

    <!-- 疾病列表 -->
    <el-card shadow="never">
      <el-table :data="diseases" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="疾病名称" min-width="150" />
        <el-table-column prop="aliases" label="别名" min-width="120" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="recommended" label="常用药物" min-width="150" show-overflow-tooltip />
        <el-table-column prop="avoid" label="避免搭配" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadDiseases"
          @current-change="loadDiseases"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑疾病' : '新增疾病'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="疾病名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入疾病名称" />
        </el-form-item>
        <el-form-item label="别名">
          <el-input v-model="form.aliases" placeholder="多个别名用逗号分隔" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入疾病描述" />
        </el-form-item>
        <el-form-item label="常用药物">
          <el-input v-model="form.recommended" type="textarea" :rows="2" placeholder="多个药物用逗号分隔" />
        </el-form-item>
        <el-form-item label="避免搭配">
          <el-input v-model="form.avoid" type="textarea" :rows="2" placeholder="多个药物用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminDiseases, createAdminDisease, updateAdminDisease, deleteAdminDisease } from '@/api/admin'
import type { AdminDisease, DiseaseCreate } from '@/types/admin'

const loading = ref(false)
const submitting = ref(false)
const diseases = ref<AdminDisease[]>([])
const search = ref('')
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const formRef = ref()

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

const form = reactive<DiseaseCreate>({
  name: '',
  aliases: '',
  description: '',
  recommended: '',
  avoid: ''
})

const rules = {
  name: [{ required: true, message: '请输入疾病名称', trigger: 'blur' }]
}

async function loadDiseases() {
  loading.value = true
  try {
    const res = await getAdminDiseases({
      page: pagination.page,
      page_size: pagination.page_size,
      search: search.value || undefined
    })
    diseases.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载疾病列表失败')
  } finally {
    loading.value = false
  }
}

function openDialog(disease?: AdminDisease) {
  if (disease) {
    isEdit.value = true
    editId.value = disease.id
    Object.assign(form, {
      name: disease.name,
      aliases: disease.aliases || '',
      description: disease.description || '',
      recommended: disease.recommended || '',
      avoid: disease.avoid || ''
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, {
      name: '',
      aliases: '',
      description: '',
      recommended: '',
      avoid: ''
    })
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value && editId.value) {
          await updateAdminDisease(editId.value, form)
          ElMessage.success('更新成功')
        } else {
          await createAdminDisease(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadDiseases()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

async function handleDelete(disease: AdminDisease) {
  try {
    await ElMessageBox.confirm(`确定要删除疾病 "${disease.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteAdminDisease(disease.id)
    ElMessage.success('删除成功')
    loadDiseases()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => {
  loadDiseases()
})
</script>

<style scoped>
.diseases-container {
  max-width: 1400px;
}

.page-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
