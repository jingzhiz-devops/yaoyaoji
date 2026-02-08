<template>
  <div class="medication-box-container">
    <div class="action-bar">
      <el-button type="primary" size="large" @click="handleAdd" class="add-btn">
        <el-icon><Plus /></el-icon>
        添加药品
      </el-button>
    </div>

    <div class="medication-grid" v-if="medicationStore.myMedications.length > 0">
      <div 
        v-for="med in medicationStore.myMedications" 
        :key="med.id" 
        class="medication-card"
      >
        <div class="card-image-wrapper" @click="openImageViewer(med.medicine.image_url)">
          <el-image 
            v-if="med.medicine.image_url"
            :src="getImageUrl(med.medicine.image_url)" 
            fit="cover"
            class="medicine-image"
          >
            <template #error>
              <div class="image-placeholder">
                <el-icon><Picture /></el-icon>
              </div>
            </template>
          </el-image>
          <div v-else class="image-placeholder">
            <el-icon><FirstAidKit /></el-icon>
          </div>
          
          <div class="card-actions">
            <el-button circle size="small" type="primary" @click.stop="handleEdit(med)">
              <el-icon><Edit /></el-icon>
            </el-button>
            <el-button circle size="small" type="danger" @click.stop="handleRemove(med.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>

        <div class="card-content">
          <h3 class="medicine-name">{{ med.custom_name || med.medicine.name }}</h3>
          <p class="medicine-manufacturer" v-if="med.medicine.manufacturer">{{ med.medicine.manufacturer }}</p>
          
          <div class="contraindications-section" v-if="med.medicine.contraindications">
            <div class="section-label">
              <el-icon color="#E6A23C"><Warning /></el-icon>
              <span>禁忌</span>
            </div>
            <p class="contraindications-text">{{ med.medicine.contraindications }}</p>
          </div>

          <div class="notes-section" v-if="med.notes && med.notes.trim()">
            <div class="section-label">备注</div>
            <p class="notes-text">{{ med.notes }}</p>
          </div>
        </div>
      </div>
    </div>

    <el-empty 
      v-else 
      description="药箱是空的，快去添加药品吧！" 
      :image-size="200"
    >
      <el-button type="primary" @click="handleAdd">立即添加</el-button>
    </el-empty>

    <!-- 添加/编辑药品对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="editingId ? '编辑药品' : '添加药品'" 
      width="600px"
      class="custom-dialog"
      destroy-on-close
    >
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="100px" label-position="top">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-form-item label="药品名称" prop="name" required>
              <el-input v-model="form.name" placeholder="请输入药品名称" size="large" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
             <el-form-item label="厂家">
              <el-input v-model="form.manufacturer" placeholder="可选" size="large" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="禁忌信息" prop="contraindications">
          <el-input 
            v-model="form.contraindications" 
            type="textarea" 
            :rows="3"
            placeholder="请输入药品禁忌信息,这对AI医生判断很重要(可选)" 
          />
        </el-form-item>

        <el-form-item label="药品包装图">
          <div 
            class="upload-wrapper"
            @paste.capture="handlePaste"
            tabindex="-1"
          >
            <div 
              class="medicine-image-uploader-custom"
              @click="fileInputRef?.$el.querySelector('input[type=file]')?.click()"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="handleDrop"
              :class="{ dragging: isDragging }"
            >
              <el-upload
                ref="fileInputRef"
                class="medicine-image-uploader"
                :action="''"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleImageChange"
                accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
              >
                <img v-if="form.image_url" :src="getImageUrl(form.image_url)" class="uploaded-image" />
                <div v-else class="upload-placeholder">
                  <el-icon class="upload-icon"><Plus /></el-icon>
                  <div class="upload-text">
                    <span class="main-text">点击上传或粘贴图片</span>
                    <span class="sub-text">也可拖拽或拍照上传</span>
                  </div>
                </div>
              </el-upload>
            </div>
            <div class="upload-actions">
              <el-button size="small" @click.stop="handleFileClick">
                <el-icon><Plus /></el-icon>
                点击上传
              </el-button>
              <el-button size="small" @click.stop="handleCameraClick">
                <el-icon><Camera /></el-icon>
                拍照上传
              </el-button>
              <el-button v-if="form.image_url" size="small" link type="danger" @click.stop="handleRemoveImage">删除图片</el-button>
            </div>
            <div class="upload-tip">
              支持 JPG、PNG、WEBP 格式，最大 5MB
            </div>
          </div>
          <input 
            ref="fileInputRef2"
            type="file" 
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp" 
            style="display: none;"
            @change="handleFileInputChange"
          />
          <input 
            ref="cameraInputRef"
            type="file" 
            accept="image/*" 
            capture="user"
            style="display: none;"
            @change="handleCameraInputChange"
          />
        </el-form-item>

        <el-form-item label="功效与备注">
          <el-input 
            v-model="form.notes" 
            type="textarea" 
            :rows="2"
            placeholder="药品功效、使用说明及其他备注信息(可选)" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            {{ editingId ? '保存修改' : '确认添加' }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-image-viewer 
      v-if="imageViewerVisible" 
      :url-list="imageViewerList" 
      :initial-index="0"
      @close="imageViewerVisible=false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Picture, Edit, Delete, FirstAidKit, Warning, Camera } from '@element-plus/icons-vue'
import { useMedicationStore } from '@/stores/medication'
import { uploadAPI } from '@/api'
import type { FormInstance, FormRules } from 'element-plus'
import type { CreateMedicineData } from '@/types'
import type { UploadFile } from 'element-plus'

const medicationStore = useMedicationStore()
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref<FormInstance>()
const uploadedFile = ref<File | null>(null)
const editingId = ref<number | null>(null)
const fileInputRef = ref<any>(null)
const fileInputRef2 = ref<HTMLInputElement>()
const cameraInputRef = ref<HTMLInputElement>()
const isDragging = ref(false)

// 解决预览放大时闪动
const previewSrcListMap = reactive<Record<number, string[]>>({})

watch(
  () => medicationStore.myMedications.map(m => ({ id: m.id, url: m.medicine.image_url })),
  (list) => {
    list.forEach(({ id, url }) => {
      if (url) {
        previewSrcListMap[id] = [getImageUrl(url)]
      } else {
        delete previewSrcListMap[id]
      }
    })
  },
  { deep: false, immediate: true }
)

const imageViewerVisible = ref(false)
const imageViewerList = ref<string[]>([])
function openImageViewer(url?: string) {
  const full = url ? getImageUrl(url) : ''
  if (!full) return
  imageViewerList.value = [full]
  imageViewerVisible.value = true
}

const form = reactive<CreateMedicineData>({
  name: '',
  contraindications: '',
  manufacturer: '',
  image_url: '',
  notes: ''
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入药品名称', trigger: 'blur' },
    { min: 1, max: 100, message: '药品名称长度1-100个字符', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await medicationStore.fetchMyMedications()
})

async function handleImageChange(file: UploadFile) {
  if (!file.raw) return
  
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.raw.size > maxSize) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('只支持 JPG、PNG、GIF、WEBP 格式的图片')
    return
  }
  
  uploadedFile.value = file.raw
  
  const reader = new FileReader()
  reader.onload = (e) => {
    form.image_url = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

function handlePaste(event: ClipboardEvent) {
  event.preventDefault()
  event.stopPropagation()
  
  const items = event.clipboardData?.items
  if (!items) {
    console.log('粘贴事件:未获取到剪贴板数据')
    return
  }
  
  console.log('粘贴事件触发,剪贴板内容数量:', items.length)
  
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    console.log(`项目 ${i}:`, item.type)
    if (item && item.type.startsWith('image/')) {
      const file = item.getAsFile()
      if (file) {
        console.log('检测到粘贴的图片:', file.name, file.type, file.size)
        ElMessage.success('检测到粘贴图片,正在处理...')
        processImageFile(file)
      }
      return
    }
  }
  
  console.log('粘贴事件:未检测到图片')
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (!files || files.length === 0) return
  
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (file && file.type.startsWith('image/')) {
      processImageFile(file)
      return
    }
  }
  ElMessage.error('请拖拽图片文件')
}

function handleFileClick() {
  console.log('点击上传按钮')
  fileInputRef2.value?.click()
}

function handleFileInputChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0 && input.files[0]) {
    const file = input.files[0]
    console.log('选择文件:', file.name, file.type, file.size)
    processImageFile(file)
    input.value = '' // Reset input
  }
}

function handleCameraClick() {
  console.log('拍照上传按钮')
  cameraInputRef.value?.click()
}

function handleCameraInputChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files.length > 0 && input.files[0]) {
    const file = input.files[0]
    console.log('拍照文件:', file.name, file.type, file.size)
    ElMessage.success('获取拍照图片,正在处理...')
    processImageFile(file)
    input.value = '' // Reset input
  } else {
    console.log('拍照:未获取到文件')
  }
}

function processImageFile(file: File) {
  console.log('开始处理图片文件:', file.name, file.type, file.size)
  
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.size > maxSize) {
    ElMessage.error('图片大小不能超过 5MB')
    console.error('图片太大:', file.size)
    return
  }
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('只支持 JPG、PNG、GIF、WEBP 格式的图片')
    console.error('不支持的图片类型:', file.type)
    return
  }
  
  uploadedFile.value = file
  console.log('图片文件已设置到 uploadedFile')
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    form.image_url = result
    console.log('图片预览已加载,长度:', result.length)
    ElMessage.success('图片加载成功')
  }
  reader.onerror = (e) => {
    console.error('读取图片失败:', e)
    ElMessage.error('读取图片失败')
  }
  reader.readAsDataURL(file)
}

function handleRemoveImage() {
  form.image_url = ''
  uploadedFile.value = null
}

function getImageUrl(url: string): string {
  if (!url) return ''
  if (url.startsWith('data:') || url.startsWith('http')) {
    return url
  }
  return `http://localhost:8000${url}`
}

function handleAdd() {
  resetForm()
  dialogVisible.value = true
}

function handleEdit(med: any) {
  editingId.value = med.id
  form.name = med.medicine.name
  form.contraindications = med.medicine.contraindications
  form.manufacturer = med.medicine.manufacturer || ''
  form.image_url = med.medicine.image_url || ''
  form.notes = med.notes || ''
  dialogVisible.value = true
}

function handleCancel() {
  dialogVisible.value = false
  resetForm()
}

function resetForm() {
  formRef.value?.resetFields()
  form.name = ''
  form.contraindications = ''
  form.manufacturer = ''
  form.image_url = ''
  form.notes = ''
  uploadedFile.value = null
  editingId.value = null
}

async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      let imageUrl = ''
      if (uploadedFile.value) {
        try {
          const uploadResult: any = await uploadAPI.uploadMedicineImage(uploadedFile.value)
          imageUrl = uploadResult.url
          ElMessage.success('图片上传成功')
        } catch (error: any) {
          ElMessage.error(error.response?.data?.detail || '图片上传失败')
          loading.value = false
          return
        }
      }
      
      if (editingId.value) {
        const updateData: any = {
          medicine_name: form.name,
          contraindications: form.contraindications || '',
          manufacturer: form.manufacturer || '',
          notes: form.notes || ''
        }
        
        if (imageUrl) {
          updateData.image_url = imageUrl
        } else if (form.image_url && !form.image_url.startsWith('data:')) {
          updateData.image_url = form.image_url
        }
        
        await medicationStore.updateMedication(editingId.value, updateData)
        ElMessage.success('修改成功')
        dialogVisible.value = false
        resetForm()
      } else {
        await medicationStore.createAndAddMedication({
          name: form.name,
          contraindications: form.contraindications,
          manufacturer: form.manufacturer || undefined,
          image_url: imageUrl || undefined,
          notes: form.notes || undefined
        })
        
        ElMessage.success('添加成功')
        dialogVisible.value = false
        resetForm()
      }
    } catch (error: any) {
      if (error.response?.data?.detail?.includes('冲突')) {
        ElMessageBox.alert(error.response.data.detail, '用药冲突警告', {
          confirmButtonText: '知道了',
          type: 'warning'
        })
      } else {
        ElMessage.error(error.response?.data?.detail || (editingId.value ? '修改失败' : '添加失败'))
      }
    } finally {
      loading.value = false
    }
  })
}

async function handleRemove(id: number) {
  try {
    await ElMessageBox.confirm('确定要移除这个药品吗？', '提示', {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    
    await medicationStore.removeMedication(id)
    ElMessage.success('移除成功')
  } catch (error) {
    // Cancelled
  }
}
</script>

<style scoped>
.medication-box-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

/* Action Bar */
.action-bar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 24px;
}

.add-btn {
  box-shadow: var(--shadow-sm);
}

/* Grid Layout */
.medication-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.medication-card {
  background: white;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: var(--shadow-card);
  transition: transform 0.3s, box-shadow 0.3s;
  display: flex;
  flex-direction: column;
}

.medication-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

/* Card Image */
.card-image-wrapper {
  height: 180px;
  background-color: #f8f9fa;
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.medicine-image {
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
}

.card-image-wrapper:hover .medicine-image {
  transform: scale(1.05);
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #dcdfe6;
  font-size: 48px;
  background-color: #f5f7fa;
}

/* Card Actions Overlay */
.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s;
}

.medication-card:hover .card-actions {
  opacity: 1;
  transform: translateY(0);
}

/* Card Content */
.card-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.medicine-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.medicine-manufacturer {
  font-size: 12px;
  color: var(--color-text-light);
  margin: 0 0 12px 0;
}

.tags-container {
  margin-bottom: 12px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.contraindications-section {
  background-color: #fff7ed;
  border-left: 3px solid #E6A23C;
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: 4px;
}

.contraindications-text {
  font-size: 13px;
  color: #78350f;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notes-section {
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.notes-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

/* Upload Styles */
.upload-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.medicine-image-uploader-custom {
  border: 2px dashed var(--el-border-color);
  border-radius: 8px;
  transition: all 0.3s ease;
  padding: 0;
  outline: none;
  background-color: #fafbfc;
  overflow: hidden;
}

.medicine-image-uploader-custom:focus {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}

.medicine-image-uploader-custom.dragging {
  border-color: var(--el-color-primary);
  background-color: #f0f9ff;
}

.medicine-image-uploader :deep(.el-upload) {
  border: none;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 100%;
  min-height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
}

.medicine-image-uploader :deep(.el-upload:hover) {
  background-color: rgba(64, 158, 255, 0.05);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 12px;
  gap: 12px;
  padding: 40px 20px;
  width: 100%;
}

.upload-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.upload-text .main-text {
  color: #606266;
  font-weight: 500;
}

.upload-text .sub-text {
  color: #909399;
  font-size: 11px;
}

.upload-icon {
  font-size: 32px;
  color: #c0c4cc;
}

.uploaded-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.upload-actions .el-button {
  flex: 0 1 auto;
}

.upload-tip {
  font-size: 12px;
  color: var(--color-text-light);
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
