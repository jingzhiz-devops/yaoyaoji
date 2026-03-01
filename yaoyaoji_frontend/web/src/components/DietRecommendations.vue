<template>
  <div class="diet-recommendations">
    <div v-if="loading" v-loading="true" style="min-height: 200px" />
    <template v-else>
      <!-- 三餐建议（糖尿病） -->
      <div v-if="diet?.breakfast || diet?.lunch || diet?.dinner" class="meal-sections">
        <div v-for="(meals, mealType) in mealSections" :key="mealType" class="meal-section">
          <h4>{{ mealLabels[mealType] }}</h4>
          <div v-for="item in meals" :key="item.id" class="diet-card">
            <h5>{{ item.title }}</h5>
            <p>{{ item.content }}</p>
            <div v-if="item.food_suggestions?.length" class="food-list good">
              <span class="label">✅ 推荐：</span>
              <el-tag v-for="f in item.food_suggestions" :key="f" size="small" type="success">{{ f }}</el-tag>
            </div>
            <div v-if="item.food_restrictions?.length" class="food-list bad">
              <span class="label">❌ 避免：</span>
              <el-tag v-for="f in item.food_restrictions" :key="f" size="small" type="danger">{{ f }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 通用建议 -->
      <div v-if="diet?.general_tips?.length" class="general-section">
        <h4>饮食总则</h4>
        <div v-for="tip in diet.general_tips" :key="tip.id" class="diet-card">
          <h5>{{ tip.title }}</h5>
          <p>{{ tip.content }}</p>
          <div v-if="tip.food_suggestions?.length" class="food-list good">
            <span class="label">✅ 推荐：</span>
            <el-tag v-for="f in tip.food_suggestions" :key="f" size="small" type="success">{{ f }}</el-tag>
          </div>
          <div v-if="tip.food_restrictions?.length" class="food-list bad">
            <span class="label">❌ 避免：</span>
            <el-tag v-for="f in tip.food_restrictions" :key="f" size="small" type="danger">{{ f }}</el-tag>
          </div>
        </div>
      </div>

      <el-empty v-if="!diet || (!diet.breakfast && !diet.lunch && !diet.dinner && !diet.general_tips?.length)" description="暂无饮食建议" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { dietAPI } from '@/api/chronic-disease'
import type { PersonalizedDiet, DietRecommendation } from '@/types'

const props = defineProps<{ diseaseId: number }>()

const loading = ref(false)
const diet = ref<PersonalizedDiet | null>(null)

const mealLabels: Record<string, string> = {
  breakfast: '🌅 早餐建议',
  lunch: '☀️ 午餐建议',
  dinner: '🌙 晚餐建议'
}

const mealSections = computed(() => {
  const sections: Record<string, DietRecommendation[]> = {}
  if (diet.value?.breakfast?.length) sections.breakfast = diet.value.breakfast
  if (diet.value?.lunch?.length) sections.lunch = diet.value.lunch
  if (diet.value?.dinner?.length) sections.dinner = diet.value.dinner
  return sections
})

const loadDiet = async () => {
  loading.value = true
  try {
    const res = await dietAPI.personalized(props.diseaseId)
    diet.value = res as any
  } catch { /* empty */ } finally {
    loading.value = false
  }
}

onMounted(loadDiet)
</script>

<style scoped lang="scss">
.meal-sections { display: flex; flex-direction: column; gap: 20px; }
.meal-section, .general-section {
  h4 { margin: 0 0 12px; font-size: 16px; color: #303133; }
}
.diet-card {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  h5 { margin: 0 0 8px; font-size: 15px; }
  p { margin: 0 0 12px; color: #606266; font-size: 14px; line-height: 1.6; }
}
.food-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  .label { font-size: 13px; color: #909399; }
}
.general-section { margin-top: 20px; }
</style>
