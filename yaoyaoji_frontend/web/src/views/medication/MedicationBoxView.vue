<template>
  <div class="medication-box-container">
    <!-- 页面标题 -->
    <div class="page-hero">
      <div class="hero-icon">💊</div>
      <div class="hero-text">
        <h2>我的药箱</h2>
        <p>共 {{ medicationStore.myMedications.length }} 种药品</p>
      </div>
      <el-button type="primary" @click="handleAdd" round class="add-btn">
        <el-icon><Plus /></el-icon> 添加药品
      </el-button>
    </div>

    <div class="medication-grid" v-if="medicationStore.myMedications.length > 0">
      <div
        v-for="(med, index) in medicationStore.myMedications"
        :key="med.id"
        class="medication-card"
      >
        <!-- 序号角标 -->
        <div class="card-index">{{ index + 1 }}</div>

        <!-- 操作按钮 -->
        <div class="card-actions">
          <el-button circle size="small" type="primary" @click.stop="handleEdit(med)">
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button circle size="small" type="danger" @click.stop="handleRemove(med.id)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <!-- 图片区 -->
        <div class="card-image-wrapper" @click="openImageViewer(med.medicine.image_url)">
          <el-image
            v-if="med.medicine.image_url"
            :src="getImageUrl(med.medicine.image_url)"
            fit="contain"
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
        </div>

        <!-- 内容区 -->
        <div class="card-body">
          <h3 class="medicine-name">{{ med.custom_name || med.medicine.name }}</h3>
          <p class="medicine-manufacturer" v-if="med.medicine.manufacturer">{{ med.medicine.manufacturer }}</p>

          <!-- 信息行 -->
          <div class="card-info-list">
            <div class="info-row" v-if="med.medicine.contraindications">
              <span class="info-tag info-tag-warn">禁忌</span>
              <el-tooltip 
                :content="med.medicine.contraindications" 
                placement="top" 
                :show-after="300"
                effect="dark"
              >
                <span class="info-text">{{ med.medicine.contraindications }}</span>
              </el-tooltip>
            </div>

            <div class="info-row" v-if="med.notes && med.notes.trim()">
              <span class="info-tag">备注</span>
              <el-tooltip 
                :content="med.notes" 
                placement="top" 
                :show-after="300"
                effect="dark"
              >
                <span class="info-text">{{ med.notes }}</span>
              </el-tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-empty
      v-else
      description="药箱是空的，快去添加药品吧！"
      :image-size="160"
    >
      <el-button type="primary" @click="handleAdd" round>立即添加</el-button>
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
/* ===== 容器 ===== */
.medication-box-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* ===== 页面 Hero ===== */
.page-hero {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px 24px;
  background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
  border-radius: 16px;
  border: 1px solid rgba(16, 185, 129, 0.15);
}

.hero-icon {
  font-size: 40px;
  line-height: 1;
}

.hero-text {
  flex: 1;
}

.hero-text h2 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
}

.hero-text p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.add-btn {
  flex-shrink: 0;
}

/* ===== 药品网格 ===== */
.medication-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

/* ===== 药品卡片 ===== */
.medication-card {
  position: relative;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.medication-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

/* 序号角标 */
.card-index {
  position: absolute;
  top: 10px;
  left: 10px;
  min-width: 24px;
  height: 24px;
  padding: 0 6px;
  background: rgba(16, 185, 129, 0.9);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

/* 操作按钮 */
.card-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  z-index: 10;
}

.medication-card:hover .card-actions {
  opacity: 1;
}

.card-actions .el-button {
  width: 28px;
  height: 28px;
}

/* 图片区 */
.card-image-wrapper {
  width: 100%;
  height: 140px;
  background: #f9fafb;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #f3f4f6;
}

.medicine-image {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d1d5db;
}

.image-placeholder .el-icon {
  font-size: 40px;
}

/* 内容区 */
.card-body {
  padding: 14px;
}

.medicine-name {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.medicine-manufacturer {
  margin: 0 0 10px;
  font-size: 12px;
  color: #9ca3af;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 信息列表 */
.card-info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 12px;
  line-height: 1.5;
}

.info-tag {
  flex-shrink: 0;
  padding: 2px 6px;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.info-tag-warn {
  background: #fef3c7;
  color: #d97706;
}

.info-text {
  color: #6b7280;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  cursor: pointer;
}

.info-text:hover {
  color: #374151;
}

/* ===== 对话框 ===== */
.custom-dialog :deep(.el-dialog__header) {
  padding: 20px 24px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.custom-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.custom-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.custom-dialog :deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
}

/* 上传区域 */
.upload-wrapper {
  outline: none;
}

.medicine-image-uploader-custom {
  border: 2px dashed #d1d5db;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.medicine-image-uploader-custom:hover,
.medicine-image-uploader-custom.dragging {
  border-color: #10b981;
  background: #f0fdf4;
}

.medicine-image-uploader {
  width: 100%;
}

.uploaded-image {
  max-width: 100%;
  max-height: 200px;
  border-radius: 8px;
  object-fit: contain;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px;
}

.upload-icon {
  font-size: 36px;
  color: #10b981;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.upload-text .main-text {
  font-size: 14px;
  color: #475569;
}

.upload-text .sub-text {
  font-size: 12px;
  color: #94a3b8;
}

.upload-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 12px;
}

.upload-tip {
  text-align: center;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .medication-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 12px;
  }
  
  .page-hero {
    flex-wrap: wrap;
  }
  
  .add-btn {
    width: 100%;
    margin-top: 12px;
  }
}

@media (max-width: 480px) {
  .medication-grid {
    grid-template-columns: 1fr;
  }
}
</style>

