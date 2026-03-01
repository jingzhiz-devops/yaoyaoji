<template>
  <div class="exercise-recommendations">
    <div v-if="loading" v-loading="true" style="min-height: 200px" />
    <template v-else-if="data">
      <div v-if="data.current_status" class="status-bar">
        <el-alert :title="data.current_status" type="info" :closable="false" />
      </div>

      <div class="exercise-cards">
        <div v-for="ex in data.recommended_exercises" :key="ex.id" class="exercise-card">
          <div class="card-header">
            <span class="title">{{ ex.title }}</span>
            <el-tag size="small">{{ ex.exercise_type }}</el-tag>
            <el-tag v-if="ex.intensity" size="small" :type="intensityType(ex.intensity)">
              {{ intensityText(ex.intensity) }}
            </el-tag>
          </div>
          <p class="description">{{ ex.description }}</p>
          <div class="meta">
            <span v-if="ex.duration_minutes">⏱ {{ ex.duration_minutes }}分钟/次</span>
            <span v-if="ex.frequency_per_week">📅 {{ ex.frequency_per_week }}次/周</span>
          </div>
          <div v-if="ex.precautions" class="precautions">
            <el-alert :title="ex.precautions" type="warning" :closable="false" />
          </div>
        </div>
      </div>

      <div v-if="data.safety_tips.length" class="safety-tips">
        <h4>⚠️ 运动安全提示</h4>
        <ul>
          <li v-for="(tip, i) in data.safety_tips" :key="i">{{ tip }}</li>
        </ul>
      </div>

      <el-empty v-if="!data.recommended_exercises.length" description="暂无运动建议" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { exerciseAPI } from '@/api/chronic-disease'
import type { PersonalizedExercise } from '@/types'

const props = defineProps<{ diseaseId: number }>()

const loading = ref(false)
const data = ref<PersonalizedExercise | null>(null)

const intensityType = (i: string) => ({ low: 'success', moderate: 'warning', high: 'danger' }[i] || 'info') as any
const intensityText = (i: string) => ({ low: '低强度', moderate: '中等强度', high: '高强度' }[i] || i)

onMounted(async () => {
  loading.value = true
  try {
    const res = await exerciseAPI.personalized(props.diseaseId)
    data.value = res as any
  } catch { /* empty */ } finally {
    loading.value = false
  }
})
</script>

<style scoped lang="scss">
.status-bar { margin-bottom: 16px; }
.exercise-cards { display: flex; flex-direction: column; gap: 16px; }
.exercise-card {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  .card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px;
    .title { font-weight: 600; font-size: 15px; }
  }
  .description { margin: 0 0 10px; color: #606266; font-size: 14px; line-height: 1.6; }
  .meta { display: flex; gap: 16px; color: #909399; font-size: 13px; margin-bottom: 10px; }
  .precautions { margin-top: 10px; }
}
.safety-tips {
  margin-top: 20px;
  h4 { margin: 0 0 10px; }
  ul { margin: 0; padding-left: 20px; li { margin-bottom: 6px; color: #606266; font-size: 14px; } }
}
</style>
