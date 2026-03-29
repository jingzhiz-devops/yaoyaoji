<template>
  <div class="diet-recommendations">
    <div v-if="loading" v-loading="true" style="min-height: 200px" />
    <template v-else>
      <!-- 三餐建议 -->
      <div v-if="diet?.breakfast || diet?.lunch || diet?.dinner" class="meal-sections">
        <div v-for="(meals, mealType) in mealSections" :key="mealType" class="meal-section">
          <div class="section-header">
            <span class="section-icon">{{ mealIcons[mealType] }}</span>
            <h4>{{ mealLabels[mealType] }}</h4>
            <div class="header-line"></div>
          </div>
          <div v-for="item in meals" :key="item.id" class="diet-card glass-card">
            <div class="card-glow"></div>
            <div class="card-content">
              <h5>{{ item.title }}</h5>
              <p>{{ item.content }}</p>
              <div v-if="item.food_suggestions?.length" class="food-list good">
                <span class="label">
                  <span class="dot dot-green"></span>
                  推荐
                </span>
                <div class="tags-wrap">
                  <span v-for="f in item.food_suggestions" :key="f" class="glass-tag tag-green">{{ f }}</span>
                </div>
              </div>
              <div v-if="item.food_restrictions?.length" class="food-list bad">
                <span class="label">
                  <span class="dot dot-red"></span>
                  避免
                </span>
                <div class="tags-wrap">
                  <span v-for="f in item.food_restrictions" :key="f" class="glass-tag tag-red">{{ f }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 通用建议 -->
      <div v-if="diet?.general_tips?.length" class="general-section">
        <div class="section-header">
          <span class="section-icon">📋</span>
          <h4>饮食总则</h4>
          <div class="header-line"></div>
        </div>
        <div v-for="tip in diet.general_tips" :key="tip.id" class="diet-card glass-card">
          <div class="card-glow"></div>
          <div class="card-content">
            <h5>{{ tip.title }}</h5>
            <p>{{ tip.content }}</p>
            <div v-if="tip.food_suggestions?.length" class="food-list good">
              <span class="label">
                <span class="dot dot-green"></span>
                推荐
              </span>
              <div class="tags-wrap">
                <span v-for="f in tip.food_suggestions" :key="f" class="glass-tag tag-green">{{ f }}</span>
              </div>
            </div>
            <div v-if="tip.food_restrictions?.length" class="food-list bad">
              <span class="label">
                <span class="dot dot-red"></span>
                避免
              </span>
              <div class="tags-wrap">
                <span v-for="f in tip.food_restrictions" :key="f" class="glass-tag tag-red">{{ f }}</span>
              </div>
            </div>
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

const mealIcons: Record<string, string> = {
  breakfast: '🌅',
  lunch: '☀️',
  dinner: '🌙'
}

const mealLabels: Record<string, string> = {
  breakfast: '早餐建议',
  lunch: '午餐建议',
  dinner: '晚餐建议'
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
.diet-recommendations {
  position: relative;
}

.meal-sections {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;

  .section-icon {
    font-size: 22px;
    filter: drop-shadow(0 0 6px rgba(64, 158, 255, 0.4));
  }

  h4 {
    margin: 0;
    font-size: 17px;
    font-weight: 600;
    color: #e0e6ed;
    letter-spacing: 1px;
  }

  .header-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(64, 158, 255, 0.5), transparent);
  }
}

.glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  margin-bottom: 14px;
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(64, 158, 255, 0.35);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);

    .card-glow {
      opacity: 1;
    }
  }
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(64, 158, 255, 0.6), rgba(103, 194, 58, 0.4), transparent);
  opacity: 0.5;
  transition: opacity 0.3s ease;
}

.card-content {
  padding: 20px;
  position: relative;
  z-index: 1;

  h5 {
    margin: 0 0 10px;
    font-size: 15px;
    font-weight: 600;
    color: #e8ecf1;
    letter-spacing: 0.5px;
  }

  p {
    margin: 0 0 14px;
    color: rgba(200, 210, 220, 0.85);
    font-size: 14px;
    line-height: 1.7;
  }
}

.food-list {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;

  .label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: rgba(180, 190, 200, 0.9);
    white-space: nowrap;
    padding-top: 4px;
  }

  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
  }

  .dot-green {
    background: #67c23a;
    box-shadow: 0 0 6px rgba(103, 194, 58, 0.6);
  }

  .dot-red {
    background: #f56c6c;
    box-shadow: 0 0 6px rgba(245, 108, 108, 0.6);
  }
}

.tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.glass-tag {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.2s ease;
  cursor: default;

  &:hover {
    transform: scale(1.05);
  }
}

.tag-green {
  background: rgba(103, 194, 58, 0.15);
  border: 1px solid rgba(103, 194, 58, 0.3);
  color: #95d475;

  &:hover {
    background: rgba(103, 194, 58, 0.25);
    box-shadow: 0 0 12px rgba(103, 194, 58, 0.2);
  }
}

.tag-red {
  background: rgba(245, 108, 108, 0.15);
  border: 1px solid rgba(245, 108, 108, 0.3);
  color: #f89898;

  &:hover {
    background: rgba(245, 108, 108, 0.25);
    box-shadow: 0 0 12px rgba(245, 108, 108, 0.2);
  }
}

.general-section {
  margin-top: 28px;
}
</style>
