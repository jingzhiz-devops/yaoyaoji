<template>
  <div class="medicines-container">
    <h2 class="page-title">药品管理</h2>

    <!-- 搜索和操作 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <el-input v-model="search" placeholder="搜索药品名称" clearable style="width: 300px" @keyup.enter="loadMedicines">
          <template #append>
            <el-button @click="loadMedicines">搜索</el-button>
          </template>
        </el-input>
        <el-button type="primary" @click="openDialog()">新增药品</el-button>
      </div>
    </el-card>

    <!-- 药品列表 -->
    <el-card shadow="never">
      <el-table :data="medicines" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="药品名称" min-width="150" />
        <el-table-column prop="generic_name" label="通用名" min-width="120" show-overflow-tooltip />
        <el-table-column prop="manufacturer" label="生产厂家" min-width="150" show-overflow-tooltip />
        <el-table-column prop="efficacy" label="功效" min-width="200" show-overflow-tooltip />
        <el-table-column label="用户" width="120">
          <template #default="{ row }">
            <template v-if="row.users && row.users.length">
              <el-tooltip :content="row.users.join('、')" placement="top" v-if="row.users.length > 1">
                <span>{{ row.users[0] }} 等{{ row.users.length }}人</span>
              </el-tooltip>
              <span v-else>{{ row.users[0] }}</span>
            </template>
            <span v-else style="color: #909399">—</span>
          </template>
        </el-table-column>
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
          @size-change="loadMedicines"
          @current-change="loadMedicines"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑药品' : '新增药品'" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="药品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入药品名称" />
        </el-form-item>
        <el-form-item label="通用名">
          <el-input v-model="form.generic_name" placeholder="请输入通用名" />
        </el-form-item>
        <el-form-item label="生产厂家">
          <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
        </el-form-item>
        <el-form-item label="主要成分">
          <el-input v-model="form.ingredients" type="textarea" :rows="2" placeholder="请输入主要成分" />
        </el-form-item>
        <el-form-item label="功效作用">
          <el-input v-model="form.efficacy" type="textarea" :rows="2" placeholder="请输入功效作用" />
        </el-form-item>
        <el-form-item label="禁忌信息">
          <el-input v-model="form.contraindications" type="textarea" :rows="2" placeholder="请输入禁忌信息" />
        </el-form-item>
        <el-form-item label="副作用">
          <el-input v-model="form.side_effects" type="textarea" :rows="2" placeholder="请输入副作用" />
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
import { getAdminMedicines, createAdminMedicine, updateAdminMedicine, deleteAdminMedicine } from '@/api/admin'
import type { AdminMedicine, MedicineCreate } from '@/types/admin'

const loading = ref(false)
const submitting = ref(false)
const medicines = ref<AdminMedicine[]>([])
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

const form = reactive<MedicineCreate>({
  name: '',
  generic_name: '',
  manufacturer: '',
  ingredients: '',
  efficacy: '',
  contraindications: '',
  side_effects: ''
})

const rules = {
  name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }]
}

async function loadMedicines() {
  loading.value = true
  try {
    const res = await getAdminMedicines({
      page: pagination.page,
      page_size: pagination.page_size,
      search: search.value || undefined
    })
    medicines.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载药品列表失败')
  } finally {
    loading.value = false
  }
}

function openDialog(medicine?: AdminMedicine) {
  if (medicine) {
    isEdit.value = true
    editId.value = medicine.id
    Object.assign(form, {
      name: medicine.name,
      generic_name: medicine.generic_name || '',
      manufacturer: medicine.manufacturer || '',
      ingredients: medicine.ingredients || '',
      efficacy: medicine.efficacy || '',
      contraindications: medicine.contraindications || '',
      side_effects: medicine.side_effects || ''
    })
  } else {
    isEdit.value = false
    editId.value = null
    Object.assign(form, {
      name: '',
      generic_name: '',
      manufacturer: '',
      ingredients: '',
      efficacy: '',
      contraindications: '',
      side_effects: ''
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
          await updateAdminMedicine(editId.value, form)
          ElMessage.success('更新成功')
        } else {
          await createAdminMedicine(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadMedicines()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

async function handleDelete(medicine: AdminMedicine) {
  try {
    await ElMessageBox.confirm(`确定要删除药品 "${medicine.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteAdminMedicine(medicine.id)
    ElMessage.success('删除成功')
    loadMedicines()
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
  loadMedicines()
})
</script>

<style scoped>
.medicines-container {
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
