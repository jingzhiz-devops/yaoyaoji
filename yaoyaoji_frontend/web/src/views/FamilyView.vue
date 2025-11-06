<template>
  <div class="family-container">
    <el-card class="header-card">
      <h2>家庭健康管理</h2>
      <p class="subtitle">管理家庭成员用药，守护全家健康</p>
    </el-card>

    <el-tabs v-model="activeTab" class="family-tabs">
      <!-- 家庭信息 -->
      <el-tab-pane label="家庭信息" name="family">
        <el-card v-if="!family">
          <el-empty description="您还未加入家庭">
            <div style="display: flex; gap: 10px; justify-content: center;">
              <el-button type="primary" @click="showCreateFamilyDialog">创建家庭</el-button>
              <el-button type="success" @click="showJoinFamilyDialog">加入家庭</el-button>
            </div>
          </el-empty>
        </el-card>

        <el-card v-else class="family-info-card">
          <template #header>
            <div class="card-header">
              <span>{{ family.name }}</span>
              <div class="header-actions">
                <el-button type="primary" size="small" @click="showEditFamilyDialog">U</el-button>
                <el-button type="danger" size="small" @click="handleLeaveFamily">Q</el-button>
              </div>
            </div>
          </template>
          
          <div class="family-info-grid">
            <div class="info-item">
              <div class="info-icon">
                <el-icon :size="32" color="#409eff"><UserFilled /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-label">家庭名称</div>
                <div class="info-value">{{ family.name }}</div>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon :size="32" color="#67c23a"><User /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-header">
                  <span class="info-label">成员数量：</span>
                  <span class="info-value">{{ family.member_count }} 人</span>
                </div>
                <div class="member-names-list" v-if="memberNames.length > 0">
                  <span v-for="(name, index) in memberNames" :key="index" class="member-name-item">
                    {{ name }}
                  </span>
                </div>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon :size="32" color="#f56c6c"><Key /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-label">邀请码</div>
                <div class="invite-code-wrapper">
                  <div class="info-value invite-code">{{ family.invite_code }}</div>
                  <el-button size="small" @click="copyInviteCode">复制</el-button>
                </div>
              </div>
            </div>
            
            <div class="info-item">
              <div class="info-icon">
                <el-icon :size="32" color="#e6a23c"><Calendar /></el-icon>
              </div>
              <div class="info-content">
                <div class="info-label">创建时间</div>
                <div class="info-value">{{ formatDate(family.created_at) }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 家庭成员 -->
      <el-tab-pane label="家庭成员" name="members">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>家庭成员管理</span>
              <div v-if="family" style="display: flex; gap: 10px; align-items: center;">
                <span style="font-size: 14px; color: #909399;">邀请码：</span>
                <el-tag type="danger" size="large" style="font-family: monospace; letter-spacing: 2px; font-weight: bold;">
                  {{ family.invite_code }}
                </el-tag>
                <el-button type="success" size="small" @click="copyInviteCode">复制邀请码</el-button>
              </div>
              <el-button v-else type="success" @click="showJoinFamilyDialog">通过邀请码加入</el-button>
            </div>
          </template>

          <el-alert v-if="!family" type="warning" :closable="false" style="margin-bottom: 20px">
            请先创建或加入家庭
          </el-alert>

          <el-table :data="members" stripe v-else>
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="role" label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="getRoleTagType(row.role)" size="small">
                  {{ getRoleText(row.role) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="age" label="年龄" width="80">
              <template #default="{ row }">
                {{ row.age ? `${row.age}岁` : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="birth_date" label="出生日期" width="120" />
            <el-table-column prop="notes" label="备注" show-overflow-tooltip />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editMember(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteMember(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 紧急联系人 -->
      <el-tab-pane label="紧急联系人" name="emergency">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>紧急联系人</span>
              <el-button type="primary" @click="showEmergencyContactDialog">添加联系人</el-button>
            </div>
          </template>

          <el-table :data="emergencyContacts" stripe>
            <el-table-column prop="name" label="姓名" width="150" />
            <el-table-column prop="relationship" label="关系" width="120" />
            <el-table-column prop="phone" label="电话" width="150" />
            <el-table-column prop="is_primary" label="主联系人" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_primary" type="success" size="small">是</el-tag>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="editEmergencyContact(row)">U</el-button>
                <el-button link type="danger" size="small" @click="deleteEmergencyContact(row.id)">D</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建家庭对话框 -->
    <el-dialog v-model="createFamilyDialogVisible" title="创建家庭" width="500px">
      <el-form :model="familyForm" label-width="80px">
        <el-form-item label="家庭名称" required>
          <el-input v-model="familyForm.name" placeholder="如：张家、李家" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createFamilyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createFamily" :loading="saving">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑家庭对话框 -->
    <el-dialog v-model="editFamilyDialogVisible" title="编辑家庭" width="500px">
      <el-form :model="familyForm" label-width="80px">
        <el-form-item label="家庭名称" required>
          <el-input v-model="familyForm.name" placeholder="如：张家、李家" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editFamilyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="updateFamily" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 编辑成员对话框 -->
    <el-dialog v-model="editMemberDialogVisible" title="编辑成员信息" width="600px">
      <el-form :model="editMemberForm" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="editMemberForm.name" disabled />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="editMemberForm.role" placeholder="请选择">
            <el-option label="家长" value="parent" />
            <el-option label="儿童" value="child" />
            <el-option label="老人" value="elderly" />
            <el-option label="配偶" value="spouse" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="editMemberForm.birth_date" type="date" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editMemberForm.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editMemberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveMemberEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 加入家庭对话框 -->
    <el-dialog v-model="joinFamilyDialogVisible" title="加入家庭" width="500px">
      <el-alert type="info" :closable="false" style="margin-bottom: 15px">
        请输入家庭邀请码以加入家庭
      </el-alert>
      <el-form :model="joinFamilyForm" label-width="100px">
        <el-form-item label="邀请码" required>
          <el-input 
            v-model="joinFamilyForm.invite_code" 
            placeholder="请输入8位邀请码"
            maxlength="20"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="joinFamilyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="joinFamily" :loading="saving">加入</el-button>
      </template>
    </el-dialog>

    <!-- 紧急联系人对话框 -->
    <el-dialog v-model="emergencyContactDialogVisible" :title="editingContact ? '编辑联系人' : '添加联系人'" width="600px">
      <el-form :model="contactForm" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="contactForm.name" placeholder="联系人姓名" />
        </el-form-item>
        <el-form-item label="关系">
          <el-input v-model="contactForm.relationship" placeholder="如：父亲、母亲、朋友" />
        </el-form-item>
        <el-form-item label="电话" required>
          <el-input v-model="contactForm.phone" placeholder="联系电话" />
        </el-form-item>
        <el-form-item label="主联系人">
          <el-switch v-model="contactForm.is_primary" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="emergencyContactDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEmergencyContact" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, User, Calendar, Key } from '@element-plus/icons-vue'
import { familyAPI } from '@/api'

const activeTab = ref('family')
const saving = ref(false)

// 家庭信息
const family = ref<any>(null)
const createFamilyDialogVisible = ref(false)
const editFamilyDialogVisible = ref(false)
const joinFamilyDialogVisible = ref(false)
const familyForm = ref({
  name: ''
})
const joinFamilyForm = ref({
  invite_code: ''
})

// 家庭成员
const members = ref<any[]>([])
const editMemberDialogVisible = ref(false)
const editMemberForm = ref({
  id: 0,
  name: '',
  role: '',
  birth_date: null as Date | null,
  notes: null as string | null
})

// 计算成员名字列表
const memberNames = computed(() => {
  return members.value.map(m => m.name)
})

// 紧急联系人
const emergencyContacts = ref<any[]>([])
const emergencyContactDialogVisible = ref(false)
const editingContact = ref<any>(null)
const contactForm = ref({
  name: '',
  relationship: null,
  phone: '',
  is_primary: false
})

// 加载数据
async function loadData() {
  try {
    family.value = await familyAPI.getMyFamily()
    
    if (family.value) {
      members.value = await familyAPI.members.list()
    }
    
    emergencyContacts.value = await familyAPI.emergencyContacts.list()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载失败')
  }
}

// 创建家庭
function showCreateFamilyDialog() {
  familyForm.value = { name: '' }
  createFamilyDialogVisible.value = true
}

async function createFamily() {
  if (!familyForm.value.name) {
    ElMessage.warning('请输入家庭名称')
    return
  }
  
  saving.value = true
  try {
    await familyAPI.createFamily(familyForm.value)
    ElMessage.success('家庭创建成功')
    createFamilyDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建失败')
  } finally {
    saving.value = false
  }
}

async function handleLeaveFamily() {
  try {
    await ElMessageBox.confirm('确定要退出家庭吗？如果您是创建者，家庭将被删除。', '提示', {
      type: 'warning'
    })
    
    await familyAPI.leaveFamily()
    ElMessage.success('已退出家庭')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

// 编辑家庭
function showEditFamilyDialog() {
  familyForm.value = { name: family.value.name }
  editFamilyDialogVisible.value = true
}

async function updateFamily() {
  if (!familyForm.value.name) {
    ElMessage.warning('请输入家庭名称')
    return
  }
  
  saving.value = true
  try {
    await familyAPI.updateFamily(familyForm.value)
    ElMessage.success('修改成功')
    editFamilyDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '修改失败')
  } finally {
    saving.value = false
  }
}

// 编辑成员
function editMember(row: any) {
  editMemberForm.value = {
    id: row.id,
    name: row.name,
    role: row.role || 'other',
    birth_date: row.birth_date ? new Date(row.birth_date) : null,
    notes: row.notes
  }
  editMemberDialogVisible.value = true
}

async function saveMemberEdit() {
  if (!editMemberForm.value.role) {
    ElMessage.warning('请选择角色')
    return
  }
  
  saving.value = true
  try {
    // 处理日期格式
    const submitData: any = {
      role: editMemberForm.value.role,
      notes: editMemberForm.value.notes
    }
    
    if (editMemberForm.value.birth_date) {
      const d = editMemberForm.value.birth_date
      submitData.birth_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    }
    
    await familyAPI.members.update(editMemberForm.value.id, submitData)
    ElMessage.success('保存成功')
    editMemberDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
function copyInviteCode() {
  if (!family.value?.invite_code) return
  
  navigator.clipboard.writeText(family.value.invite_code).then(() => {
    ElMessage.success('邀请码已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 加入家庭
function showJoinFamilyDialog() {
  joinFamilyForm.value = { invite_code: '' }
  joinFamilyDialogVisible.value = true
}

async function joinFamily() {
  if (!joinFamilyForm.value.invite_code) {
    ElMessage.warning('请输入邀请码')
    return
  }
  
  saving.value = true
  try {
    await familyAPI.joinFamily(joinFamilyForm.value.invite_code)
    ElMessage.success('加入家庭成功')
    joinFamilyDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加入失败')
  } finally {
    saving.value = false
  }
}

async function deleteMember(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个成员吗？', '提示', {
      type: 'warning'
    })
    await familyAPI.members.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 紧急联系人
function showEmergencyContactDialog() {
  editingContact.value = null
  contactForm.value = {
    name: '',
    relationship: null,
    phone: '',
    is_primary: false
  }
  emergencyContactDialogVisible.value = true
}

function editEmergencyContact(row: any) {
  editingContact.value = row
  contactForm.value = { ...row }
  emergencyContactDialogVisible.value = true
}

async function saveEmergencyContact() {
  if (!contactForm.value.name || !contactForm.value.phone) {
    ElMessage.warning('请填写必填项')
    return
  }
  
  saving.value = true
  try {
    if (editingContact.value) {
      await familyAPI.emergencyContacts.update(editingContact.value.id, contactForm.value)
    } else {
      await familyAPI.emergencyContacts.create(contactForm.value)
    }
    ElMessage.success('保存成功')
    emergencyContactDialogVisible.value = false
    await loadData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteEmergencyContact(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个联系人吗？', '提示', {
      type: 'warning'
    })
    await familyAPI.emergencyContacts.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

// 辅助函数
function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  
  return `${year}年${month}月${day}日`
}

function getRoleText(role: string): string {
  const roleMap: Record<string, string> = {
    parent: '家长',
    child: '儿童',
    elderly: '老人',
    spouse: '配偶',
    other: '其他'
  }
  return roleMap[role] || role
}

function getRoleTagType(role: string): string {
  const typeMap: Record<string, string> = {
    parent: 'success',
    child: 'warning',
    elderly: 'danger',
    spouse: 'info',
    other: ''
  }
  return typeMap[role] || ''
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.family-container {
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

.family-tabs {
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
    
    .header-actions {
      display: flex;
      gap: 10px;
    }
  }
}

.family-info-card {
  .family-info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    padding: 10px 0;
  }
  
  .info-item {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #fff 100%);
    border-radius: 12px;
    border: 1px solid #e4e7ed;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-3px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
      border-color: #d0d6e0;
    }
    
    .info-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 56px;
      height: 56px;
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    
    .info-content {
      flex: 1;
      
      .info-header {
        display: flex;
        align-items: baseline;
        margin-bottom: 8px;
      }
      
      .info-label {
        font-size: 13px;
        color: #909399;
      }
      
      .info-value {
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }
      
      .member-names-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
        
        .member-name-item {
          display: inline-block;
          padding: 4px 12px;
          font-size: 13px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 6px;
          white-space: nowrap;
          font-weight: 500;
          box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
          transition: all 0.2s;
          
          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
          }
        }
      }
    }
  }
}

.invite-code-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .invite-code {
    font-family: 'Courier New', monospace;
    letter-spacing: 2px;
    color: #f56c6c;
    font-weight: 700;
  }
}

:deep(.el-table) {
  font-size: 14px;
}

:deep(.el-descriptions) {
  margin-top: 20px;
}
</style>
