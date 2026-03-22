<template>
  <div class="users-container">
    <h2 class="page-title">用户管理</h2>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="搜索">
          <el-input v-model="filters.search" placeholder="用户名/邮箱/姓名" clearable @keyup.enter="loadUsers" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="filters.is_admin" placeholder="全部" clearable>
            <el-option label="管理员" :value="true" />
            <el-option label="普通用户" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.is_active" placeholder="全部" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadUsers">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户列表 -->
    <el-card shadow="never">
      <el-table :data="users" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="用户名" width="110" />
        <el-table-column prop="email" label="邮箱" min-width="140" show-overflow-tooltip />
        <el-table-column prop="real_name" label="姓名" width="80" />
        <el-table-column label="角色" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">
              {{ row.is_admin ? '管理员' : '用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="70">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="medication_count" label="药品数" width="70" />
        <el-table-column prop="schedule_count" label="计划数" width="70" />
        <el-table-column prop="family_name" label="家庭" width="90" show-overflow-tooltip />
        <el-table-column prop="created_at" label="注册时间" width="170">
          <template #default="{ row }">
            <div class="time-cell">
              <span class="time-date">{{ formatDatePart(row.created_at) }}</span>
              <span class="time-clock">{{ formatTimePart(row.created_at) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="toggleActive(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button size="small" @click="toggleAdmin(row)">
              {{ row.is_admin ? '取消管理员' : '设为管理员' }}
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadUsers"
          @current-change="loadUsers"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAdminUsers, updateAdminUser, deleteAdminUser } from '@/api/admin'
import type { AdminUser, AdminUserListParams } from '@/types/admin'

const loading = ref(false)
const users = ref<AdminUser[]>([])

const filters = reactive<AdminUserListParams>({
  search: '',
  is_admin: undefined,
  is_active: undefined
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

async function loadUsers() {
  loading.value = true
  try {
    const res = await getAdminUsers({
      page: pagination.page,
      page_size: pagination.page_size,
      search: filters.search || undefined,
      is_admin: filters.is_admin,
      is_active: filters.is_active
    })
    users.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.search = ''
  filters.is_admin = undefined
  filters.is_active = undefined
  pagination.page = 1
  loadUsers()
}

async function toggleActive(user: AdminUser) {
  const action = user.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户 "${user.username}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateAdminUser(user.id, { is_active: !user.is_active })
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || `${action}失败`)
    }
  }
}

async function toggleAdmin(user: AdminUser) {
  const action = user.is_admin ? '取消管理员' : '设为管理员'
  try {
    await ElMessageBox.confirm(`确定要将用户 "${user.username}" ${action}吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateAdminUser(user.id, { is_admin: !user.is_admin })
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || `${action}失败`)
    }
  }
}

async function handleDelete(user: AdminUser) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作将同时删除该用户的所有药箱、用药计划和记录数据，且不可恢复！`,
      '危险操作',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error'
      }
    )
    await deleteAdminUser(user.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function formatDatePart(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function formatTimePart(dateStr: string) {
  const d = new Date(dateStr)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.users-container {
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

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time-date {
  font-size: 13px;
  color: #303133;
}

.time-clock {
  font-size: 12px;
  color: #909399;
}
</style>
