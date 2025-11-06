/**
 * 药箱状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { userMedicationAPI, medicineAPI } from '@/api'
import type { UserMedication, Medicine, CreateMedicineData } from '@/types'

export const useMedicationStore = defineStore('medication', () => {
  const myMedications = ref<UserMedication[]>([])
  const medicines = ref<Medicine[]>([])

  // 获取我的药箱
  async function fetchMyMedications() {
    const res: any = await userMedicationAPI.list('active')
    myMedications.value = res
  }

  // 获取药品列表
  async function fetchMedicines(search?: string) {
    const res: any = await medicineAPI.list({ search })
    medicines.value = res
  }

  // 添加药品到药箱
  async function addMedication(data: any) {
    await userMedicationAPI.add(data)
    await fetchMyMedications()
  }

  // 创建新药品并添加到药箱
  async function createAndAddMedication(data: CreateMedicineData) {
    // 先创建药品
    const medicine: any = await medicineAPI.create({
      name: data.name,
      contraindications: data.contraindications,
      manufacturer: data.manufacturer,
      generic_name: data.name, // 默认通用名与药品名相同
      image_url: data.image_url
    })
    
    // 再添加到药箱
    await userMedicationAPI.add({
      medicine_id: medicine.id,
      notes: data.notes
    })
    
    await fetchMyMedications()
  }

  // 移除药哅
  async function removeMedication(id: number) {
    await userMedicationAPI.remove(id)
    await fetchMyMedications()
  }
  
  // 更新药箱中的药哅信息
  async function updateMedication(id: number, data: any) {
    await userMedicationAPI.update(id, data)
    await fetchMyMedications()
  }

  return {
    myMedications,
    medicines,
    fetchMyMedications,
    fetchMedicines,
    addMedication,
    createAndAddMedication,
    removeMedication,
    updateMedication
  }
})
