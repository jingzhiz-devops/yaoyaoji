<template>
  <div class="medication-box">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2>💊 我的药箱</h2>
      <el-button type="primary" @click="handleAdd">添加药品</el-button>
    </div>

    <div class="medication-list" style="margin-top: 20px">
      <el-row :gutter="20">
        <el-col :span="8" v-for="med in medicationStore.myMedications" :key="med.id">
          <el-card class="medication-card">
            <template #header>
              <div class="card-header">
                <span>{{ med.custom_name || med.medicine.name }}</span>
                <div>
                  <el-button type="primary" size="small" @click="handleEdit(med)">U</el-button>
                  <el-button type="danger" size="small" @click="handleRemove(med.id)">D</el-button>
                </div>
              </div>
            </template>
            
            <!-- 药哅图片 -->
            <div v-if="med.medicine.image_url" class="medicine-image-container">
              <el-image 
                :src="getImageUrl(med.medicine.image_url)" 
                fit="contain"
                class="medicine-image"
                @click="openImageViewer(med.medicine.image_url)"
              >
                <template #error>
                  <div class="image-error">
                    <el-icon><Picture /></el-icon>
                    <span>图片加载失败</span>
                  </div>
                </template>
              </el-image>
            </div>
            
            <p><strong>药品名:</strong> {{ med.medicine.name }}</p>
            <p v-if="med.medicine.manufacturer"><strong>厂家:</strong> {{ med.medicine.manufacturer }}</p>
            
            <!-- 禁忌信息 -->
            <div v-if="med.medicine.contraindications" style="margin: 10px 0;">
              <el-tag type="warning" size="small">禁忌</el-tag>
              <p style="margin-top: 5px; color: #e6a23c; font-size: 13px;">
                {{ med.medicine.contraindications }}
              </p>
            </div>
            
            <p v-if="med.notes" style="margin-top: 10px;">
              <strong>功效与备注:</strong> {{ med.notes }}
            </p>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="medicationStore.myMedications.length === 0" description="药箱是空的，快去添加药品吧！" />
    </div>

    <!-- 添加/编辑药品对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑药品' : '添加药品'" width="600px">
      <el-form :model="form" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="药品名称" prop="name" required>
          <el-input v-model="form.name" placeholder="请输入药品名称" />
        </el-form-item>
        <el-form-item label="禁忌" prop="contraindications" required>
          <el-input 
            v-model="form.contraindications" 
            type="textarea" 
            :rows="3"
            placeholder="请输入药品禁忌信息" 
          />
        </el-form-item>
        <el-form-item label="厂家">
          <el-input v-model="form.manufacturer" placeholder="请输入药品厂家(可选)" />
        </el-form-item>
        <el-form-item label="药品包装图">
          <el-upload
            class="medicine-image-uploader"
            :action="''"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleImageChange"
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
          >
            <img v-if="form.image_url" :src="getImageUrl(form.image_url)" class="uploaded-image" />
            <el-icon v-else class="image-uploader-icon"><Plus /></el-icon>
          </el-upload>
          <div style="margin-top: 8px; color: #909399; font-size: 12px;">
            支持 JPG、PNG、GIF、WEBP 格式，最大 5MB
          </div>
          <el-button v-if="form.image_url" size="small" type="danger" text @click="handleRemoveImage">
            删除图片
          </el-button>
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
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ editingId ? '确定修改' : '确定添加' }}
        </el-button>
      </template>
    </el-dialog>
    <el-image-viewer v-if="imageViewerVisible" :url-list="imageViewerList" :key="imageViewerList[0]" @close="imageViewerVisible=false" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Picture } from '@element-plus/icons-vue'
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
const editingId = ref<number | null>(null) // 当前编辑的药品ID

// 解决预览放大时闪动：为每个药品维持稳定的预览数组引用
const previewSrcListMap = reactive<Record<number, string[]>>({})
function ensurePreviewList(id: number, url?: string): string[] {
  const existing = previewSrcListMap[id]
  if (existing) return existing
  if (url) {
    previewSrcListMap[id] = [getImageUrl(url)]
    return previewSrcListMap[id]
  }
  return []
}

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

// 全局单例图片预览，确保多次点击仅保留一个预览
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
  ],
  contraindications: [
    { required: true, message: '请输入禁忌信息', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await medicationStore.fetchMyMedications()
})

// 处理图片选择
async function handleImageChange(file: UploadFile) {
  if (!file.raw) return
  
  // 检查文件大小
  const maxSize = 5 * 1024 * 1024 // 5MB
  if (file.raw.size > maxSize) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  // 检查文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.raw.type)) {
    ElMessage.error('只支持 JPG、PNG、GIF、WEBP 格式的图片')
    return
  }
  
  // 保存文件引用
  uploadedFile.value = file.raw
  
  // 预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    form.image_url = e.target?.result as string
  }
  reader.readAsDataURL(file.raw)
}

// 删除图片
function handleRemoveImage() {
  form.image_url = ''
  uploadedFile.value = null
}

// 获取图片URL（处理本地和服务器图片）
function getImageUrl(url: string): string {
  if (!url) return ''
  // 如果是base64或完整URL，直接返回
  if (url.startsWith('data:') || url.startsWith('http')) {
    return url
  }
  // 否则拼接后端域名
  return `http://localhost:8000${url}`
}

// 处理添加
function handleAdd() {
  resetForm()
  dialogVisible.value = true
}

// 处理编辑
function handleEdit(med: any) {
  editingId.value = med.id
  
  // 填充表单数据（所有字段均可编辑）
  form.name = med.medicine.name
  form.contraindications = med.medicine.contraindications
  form.manufacturer = med.medicine.manufacturer || ''
  form.image_url = med.medicine.image_url || ''
  form.notes = med.notes || ''
  
  dialogVisible.value = true
}

// 取消操作
function handleCancel() {
  dialogVisible.value = false
  resetForm()
}

// 重置表单
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

// 统一的提交处理
async function handleSubmit() {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    loading.value = true
    try {
      // 如果有上传的图片，先上传图片
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
        // 编辑模式：更新所有字段
        const updateData: any = {
          medicine_name: form.name,
          contraindications: form.contraindications,
          manufacturer: form.manufacturer || undefined,
          notes: form.notes || undefined
        }
        
        // 如果上传了新图片，使用新图片URL
        if (imageUrl) {
          updateData.image_url = imageUrl
        } else if (form.image_url && !form.image_url.startsWith('data:')) {
          // 如果没有上传新图片但有现有图片，保持原有图片
          updateData.image_url = form.image_url
        }
        
        await medicationStore.updateMedication(editingId.value, updateData)
        ElMessage.success('修改成功')
        dialogVisible.value = false
        resetForm()
      } else {
        // 添加模式：创建新药哅
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
  await ElMessageBox.confirm('确定要移除这个药品吗？', '提示', {
    type: 'warning'
  })
  
  await medicationStore.removeMedication(id)
  ElMessage.success('移除成功')
}
</script>

<style scoped>
.medication-box {
  width: 100%;
  height: 100%;
}

.medication-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.medication-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header > div {
  display: flex;
  gap: 8px;
}

.medication-list {
  margin-top: 20px;
}

/* 药哅图片容器 */
.medicine-image-container {
  width: 100%;
  height: 180px;
  margin-bottom: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.medicine-image {
  width: 100%;
  height: 100%;
}

.medicine-image :deep(.el-image__inner) {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 8px;
}

/* 图片加载失败样式 */
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}

.image-error .el-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.medication-card p {
  margin: 8px 0;
  font-size: 14px;
  line-height: 1.5;
}

/* 图片上传组件样式 */
.medicine-image-uploader :deep(.el-upload) {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
  width: 178px;
  height: 178px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.medicine-image-uploader :deep(.el-upload:hover) {
  border-color: var(--el-color-primary);
}

.image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.uploaded-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
