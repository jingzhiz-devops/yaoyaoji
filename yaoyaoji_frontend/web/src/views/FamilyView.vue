<template>
  <div class="family-view-container">
    <div class="family-content">
      <el-tabs v-model="activeTab" class="custom-tabs" type="border-card">
        <!-- 家庭信息 -->
        <el-tab-pane name="family">
          <template #label>
            <span class="tab-label"><el-icon><HomeFilled /></el-icon> 家庭信息</span>
          </template>
          
          <div class="tab-pane-content">
            <div v-if="!family" class="no-family-state">
              <el-empty description="您还未加入任何家庭" :image-size="200">
                <div class="action-buttons">
                  <el-button type="primary" size="large" @click="showCreateFamilyDialog">创建新家庭</el-button>
                  <el-button size="large" @click="showJoinFamilyDialog">加入已有家庭</el-button>
                </div>
              </el-empty>
            </div>

            <div v-else class="family-dashboard">
              <div class="family-header-card">
                <div class="family-title">
                  <div class="avatar-placeholder">{{ family.name.charAt(0) }}</div>
                  <div class="title-info">
                    <h1>{{ family.name }}</h1>
                    <p>创建于 {{ formatDate(family.created_at) }}</p>
                  </div>
                </div>
                <div class="family-actions">
                  <el-button type="primary" plain @click="showEditFamilyDialog">编辑信息</el-button>
                  <el-button type="danger" plain @click="handleLeaveFamily">退出家庭</el-button>
                </div>
              </div>

              <div class="stats-grid">
                <el-card class="stat-card" shadow="hover">
                  <div class="stat-icon member-icon"><el-icon><User /></el-icon></div>
                  <div class="stat-info">
                    <span class="stat-label">成员数量</span>
                    <span class="stat-value">{{ family.member_count }} 人</span>
                  </div>
                </el-card>
                
                <el-card class="stat-card" shadow="hover">
                  <div class="stat-icon code-icon"><el-icon><Key /></el-icon></div>
                  <div class="stat-info">
                    <span class="stat-label">家庭邀请码</span>
                    <div class="code-value">
                      <span>{{ family.invite_code }}</span>
                      <el-button link type="primary" @click="copyInviteCode">复制</el-button>
                    </div>
                  </div>
                </el-card>
              </div>

              <div class="members-section">
                <div class="section-header">
                  <h3>家庭成员</h3>
                  <el-tag type="info" round>共 {{ members.length }} 人</el-tag>
                </div>
                
                <div class="members-grid">
                  <div v-for="member in members" :key="member.id" class="member-card">
                    <div class="member-card-bg" :style="{ background: getMemberGradient(member.role) }"></div>
                    <div class="member-card-body">
                      <div class="member-avatar-wrapper">
                        <div class="member-avatar" :style="{ background: getMemberGradient(member.role) }">
                          {{ member.name.charAt(0) }}
                        </div>
                        <span class="member-status-dot"></span>
                      </div>
                      <div class="member-name">{{ member.name }}</div>
                      <div class="member-meta">
                        <el-tag 
                          :color="getRoleColor(member.role)" 
                          effect="dark" 
                          size="small" 
                          round
                          style="border: none;"
                        >
                          {{ getRoleText(member.role) }}
                        </el-tag>
                        <span class="member-age" v-if="member.age">{{ member.age }}岁</span>
                        <span class="member-age no-age" v-else>年龄未知</span>
                      </div>
                      <div class="member-actions">
                        <el-tooltip content="编辑" placement="top">
                          <button class="action-btn edit-btn" @click="editMember(member)">
                            <el-icon><Edit /></el-icon>
                          </button>
                        </el-tooltip>
                        <el-tooltip content="删除" placement="top">
                          <button class="action-btn delete-btn" @click="deleteMember(member.id)">
                            <el-icon><Delete /></el-icon>
                          </button>
                        </el-tooltip>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 邀请卡片 -->
                  <div class="member-card invite-card" @click="copyInviteCode">
                    <div class="invite-content">
                      <div class="invite-icon-wrapper">
                        <el-icon class="invite-icon"><Plus /></el-icon>
                      </div>
                      <span class="invite-text">邀请成员</span>
                      <span class="invite-hint">复制邀请码分享给家人</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 紧急联系人 -->
        <el-tab-pane name="emergency">
          <template #label>
            <span class="tab-label"><el-icon><PhoneFilled /></el-icon> 紧急联系人</span>
          </template>
          
          <div class="tab-pane-content">
            <div class="section-header">
              <h3>紧急联系人列表</h3>
              <el-button type="primary" @click="showEmergencyContactDialog">添加联系人</el-button>
            </div>
            
            <div class="contacts-grid">
              <el-card v-for="contact in emergencyContacts" :key="contact.id" class="contact-card" shadow="hover">
                <div class="contact-main">
                  <div class="contact-avatar">
                    <el-icon><UserFilled /></el-icon>
                  </div>
                  <div class="contact-info">
                    <div class="contact-name-row">
                      <h4>{{ contact.name }}</h4>
                      <el-tag v-if="contact.is_primary" type="danger" size="small" effect="dark">主联系人</el-tag>
                    </div>
                    <p class="contact-relation">{{ contact.relationship || '关系未知' }}</p>
                    <p class="contact-phone"><el-icon><Phone /></el-icon> {{ contact.phone }}</p>
                  </div>
                </div>
                <div class="contact-actions">
                  <el-button link type="primary" @click="editEmergencyContact(contact)">编辑</el-button>
                  <el-button link type="danger" @click="deleteEmergencyContact(contact.id)">删除</el-button>
                </div>
              </el-card>
              
              <el-empty v-if="emergencyContacts.length === 0" description="暂无紧急联系人" :image-size="100" />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Dialogs -->
    <el-dialog v-model="createFamilyDialogVisible" title="创建新家庭" width="400px" class="custom-dialog">
      <el-form :model="familyForm" label-position="top">
        <el-form-item label="家庭名称" required>
          <el-input v-model="familyForm.name" placeholder="例如：幸福一家人" size="large" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createFamilyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createFamily" :loading="saving">立即创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="joinFamilyDialogVisible" title="加入家庭" width="400px" class="custom-dialog">
      <div class="dialog-tip">请输入管理员分享给您的8位邀请码</div>
      <el-form :model="joinFamilyForm" label-position="top">
        <el-form-item label="邀请码" required>
          <el-input 
            v-model="joinFamilyForm.invite_code" 
            placeholder="8位邀请码"
            maxlength="20"
            size="large"
            class="code-input"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="joinFamilyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="joinFamily" :loading="saving">加入</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editMemberDialogVisible" title="编辑成员信息" width="500px" class="custom-dialog">
      <el-form :model="editMemberForm" label-width="80px" label-position="top">
        <el-form-item label="姓名">
          <el-input v-model="editMemberForm.name" disabled />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="editMemberForm.role" placeholder="请选择" style="width: 100%">
            <el-option label="家长" value="parent" />
            <el-option label="儿童" value="child" />
            <el-option label="老人" value="elderly" />
            <el-option label="配偶" value="spouse" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="editMemberForm.role === 'custom'" label="自定义角色名称" required>
          <el-input v-model="editMemberForm.customRole" placeholder="请输入自定义角色名称" maxlength="20" />
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="editMemberForm.birth_date" type="date" placeholder="选择日期" style="width: 100%" />
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

    <el-dialog v-model="emergencyContactDialogVisible" :title="editingContact ? '编辑联系人' : '添加联系人'" width="500px" class="custom-dialog">
      <el-form :model="contactForm" label-width="80px" label-position="top">
        <el-form-item label="姓名" required>
          <el-input v-model="contactForm.name" placeholder="联系人姓名" />
        </el-form-item>
        <el-form-item label="关系">
          <el-input v-model="contactForm.relationship" placeholder="如：父亲、母亲、朋友" />
        </el-form-item>
        <el-form-item label="电话" required>
          <el-input v-model="contactForm.phone" placeholder="联系电话" />
        </el-form-item>
        <el-form-item label="设为主联系人">
          <el-switch v-model="contactForm.is_primary" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="emergencyContactDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEmergencyContact" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editFamilyDialogVisible" title="编辑家庭信息" width="400px" class="custom-dialog">
      <el-form :model="familyForm" label-position="top">
        <el-form-item label="家庭名称" required>
          <el-input v-model="familyForm.name" placeholder="家庭名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editFamilyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="updateFamily" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, User, Key, HomeFilled, PhoneFilled, Edit, Delete, Plus, Phone } from '@element-plus/icons-vue'
import { familyAPI } from '@/api'

const activeTab = ref('family')
const saving = ref(false)

// 家庭信息
const family = ref<any>(null)
const createFamilyDialogVisible = ref(false)
const editFamilyDialogVisible = ref(false)
const joinFamilyDialogVisible = ref(false)
const familyForm = ref({ name: '' })
const joinFamilyForm = ref({ invite_code: '' })

// 家庭成员
const members = ref<any[]>([])
const editMemberDialogVisible = ref(false)
const editMemberForm = ref({
  id: 0,
  name: '',
  role: '',
  customRole: '',
  birth_date: null as Date | null,
  notes: null as string | null
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

onMounted(() => {
  loadData()
})

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

// 家庭操作
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
    await ElMessageBox.confirm('确定要退出家庭吗？如果您是创建者，家庭将被删除。', '提示', { type: 'warning' })
    await familyAPI.leaveFamily()
    ElMessage.success('已退出家庭')
    family.value = null
    members.value = []
    await loadData()
  } catch (error) {}
}

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

function copyInviteCode() {
  if (!family.value?.invite_code) return
  navigator.clipboard.writeText(family.value.invite_code).then(() => {
    ElMessage.success('邀请码已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}

// 成员操作
function editMember(row: any) {
  const predefinedRoles = ['parent', 'child', 'elderly', 'spouse', 'admin', 'member']
  const isCustomRole = row.role && !predefinedRoles.includes(row.role) && row.role !== 'other'
  editMemberForm.value = {
    id: row.id,
    name: row.name,
    role: isCustomRole ? 'custom' : (row.role || 'custom'),
    customRole: isCustomRole ? row.role : '',
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
  if (editMemberForm.value.role === 'custom' && !editMemberForm.value.customRole?.trim()) {
    ElMessage.warning('请输入自定义角色名称')
    return
  }
  saving.value = true
  try {
    const actualRole = editMemberForm.value.role === 'custom'
      ? editMemberForm.value.customRole.trim()
      : editMemberForm.value.role
    const submitData: any = {
      role: actualRole,
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

async function deleteMember(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除这个成员吗？', '提示', { type: 'warning' })
    await familyAPI.members.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

// 紧急联系人操作
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
    await ElMessageBox.confirm('确定要删除这个联系人吗？', '提示', { type: 'warning' })
    await familyAPI.emergencyContacts.delete(id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {}
}

// 辅助函数
function formatDate(dateStr: string | undefined): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return '-'
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

function getRoleText(role: string): string {
  const roleMap: Record<string, string> = {
    parent: '家长',
    child: '儿童',
    elderly: '老人',
    spouse: '配偶'
  }
  return roleMap[role] || role
}

function getRoleTagType(role: string): string {
  const typeMap: Record<string, string> = {
    parent: 'success',
    child: 'warning',
    elderly: 'danger',
    spouse: 'info'
  }
  return typeMap[role] || ''
}

function getRoleColor(role: string): string {
  const colorMap: Record<string, string> = {
    parent: '#67c23a',
    child: '#e6a23c',
    elderly: '#f56c6c',
    spouse: '#909399',
    other: '#409eff'
  }
  return colorMap[role] || '#409eff'
}

function getMemberGradient(role: string): string {
  const gradientMap: Record<string, string> = {
    parent: 'linear-gradient(135deg, #67c23a, #95d475)',
    child: 'linear-gradient(135deg, #e6a23c, #f0c78a)',
    elderly: 'linear-gradient(135deg, #f56c6c, #fab6b6)',
    spouse: 'linear-gradient(135deg, #909399, #c0c4cc)',
    other: 'linear-gradient(135deg, #409eff, #79bbff)'
  }
  return gradientMap[role] || gradientMap.other
}
</script>

<style scoped>
.family-view-container {
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

.family-content {
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

/* No Family State */
.no-family-state {
  padding: 40px 0;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-top: 24px;
}

/* Family Dashboard */
.family-header-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: var(--radius-md);
  margin-bottom: 24px;
}

.family-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-placeholder {
  width: 64px;
  height: 64px;
  background: var(--color-primary);
  color: white;
  font-size: 28px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(42, 157, 143, 0.3);
}

.title-info h1 {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: var(--color-text-main);
}

.title-info p {
  margin: 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.family-actions {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  border: none;
  background: #f9fafb;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.member-icon {
  background: #ecfdf5;
  color: #10b981;
}

.code-icon {
  background: #fff7ed;
  color: #f97316;
}

.stat-info {
  flex: 1;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: var(--color-text-light);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-main);
}

.code-value {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: monospace;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-text-main);
}

/* Members Section */
.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.member-card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  background: #fff;
  border: 1px solid #eef2f7;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: default;
}

.member-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.04);
  border-color: transparent;
}

.member-card-bg {
  height: 56px;
  opacity: 0.85;
}

.member-card-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 16px 20px;
  margin-top: -30px;
  position: relative;
}

.member-avatar-wrapper {
  position: relative;
  margin-bottom: 10px;
}

.member-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: #fff;
  border: 3px solid #fff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.member-status-dot {
  position: absolute;
  bottom: 2px;
  right: 2px;
  width: 12px;
  height: 12px;
  background: #67c23a;
  border: 2px solid #fff;
  border-radius: 50%;
}

.member-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main, #1f2937);
  margin-bottom: 8px;
  text-align: center;
  line-height: 1.3;
}

.member-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.member-age {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
}

.member-age.no-age {
  color: var(--color-text-light, #9ca3af);
  font-style: italic;
}

.member-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(4px);
  transition: all 0.25s ease;
}

.member-card:hover .member-actions {
  opacity: 1;
  transform: translateY(0);
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.edit-btn {
  background: #f0f9ff;
  color: #3b82f6;
}

.edit-btn:hover {
  background: #3b82f6;
  color: #fff;
}

.delete-btn {
  background: #fef2f2;
  color: #ef4444;
}

.delete-btn:hover {
  background: #ef4444;
  color: #fff;
}

/* Invite Card */
.invite-card {
  border: 2px dashed #d1d5db;
  background: #fafbfc;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 200px;
  transition: all 0.3s ease;
}

.invite-card:hover {
  border-color: var(--color-primary, #2a9d8f);
  background: #f0fdf9;
  transform: translateY(-6px);
  box-shadow: 0 12px 32px rgba(42, 157, 143, 0.08);
}

.invite-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px 16px;
}

.invite-icon-wrapper {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #e8f5f3;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.invite-card:hover .invite-icon-wrapper {
  background: var(--color-primary, #2a9d8f);
}

.invite-icon {
  font-size: 24px;
  color: var(--color-primary, #2a9d8f);
  transition: color 0.3s;
}

.invite-card:hover .invite-icon {
  color: #fff;
}

.invite-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-main, #1f2937);
}

.invite-hint {
  font-size: 12px;
  color: var(--color-text-light, #9ca3af);
}

/* Contacts Grid */
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.contact-card {
  border: none;
  background: #f9fafb;
}

.contact-card :deep(.el-card__body) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
}

.contact-main {
  display: flex;
  align-items: center;
  gap: 16px;
}

.contact-avatar {
  width: 48px;
  height: 48px;
  background: #e0e7ff;
  color: #4f46e5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.contact-info h4 {
  margin: 0;
  font-size: 16px;
  color: var(--color-text-main);
}

.contact-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.contact-relation {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.contact-phone {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-main);
  display: flex;
  align-items: center;
  gap: 4px;
}

.contact-actions {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dialog-tip {
  background: #f0f9ff;
  color: #0369a1;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  text-align: center;
}

.code-input :deep(.el-input__inner) {
  text-align: center;
  font-family: monospace;
  font-size: 18px;
  letter-spacing: 2px;
}
</style>
