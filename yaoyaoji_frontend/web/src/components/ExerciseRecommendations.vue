<template>
  <div class="exercise-recommendations">
    <div v-if="loading" v-loading="true" style="min-height: 200px" />
    <template v-else-if="data">
      <div v-if="data.current_status" class="status-bar glass-card">
        <div class="card-glow"></div>
        <div class="status-content">
          <span class="status-dot"></span>
          <span>{{ data.current_status }}</span>
        </div>
      </div>

      <div class="exercise-cards">
        <div v-for="ex in data.recommended_exercises" :key="ex.id" class="exercise-card glass-card">
          <div class="card-glow"></div>
          <div class="card-content">
            <div class="card-header">
              <span class="title">{{ ex.title }}</span>
              <span class="glass-tag tag-blue">{{ ex.exercise_type }}</span>
              <span v-if="ex.intensity" class="glass-tag" :class="intensityTagClass(ex.intensity)">
                {{ intensityText(ex.intensity) }}
              </span>
            </div>
            <p class="description">{{ ex.description }}</p>
            <div class="meta">
              <span v-if="ex.duration_minutes" class="meta-item">
                <span class="meta-icon">⏱</span> {{ ex.duration_minutes }}分钟/次
              </span>
              <span v-if="ex.frequency_per_week" class="meta-item">
                <span class="meta-icon">📅</span> {{ ex.frequency_per_week }}次/周
              </span>
            </div>
            <div v-if="ex.precautions" class="precautions glass-alert">
              <span class="alert-icon">⚡</span>
              <span>{{ ex.precautions }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="data.safety_tips.length" class="safety-tips glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <h4>
            <span class="section-icon">⚠️</span>
            运动安全提示
          </h4>
          <ul>
            <li v-for="(tip, i) in data.safety_tips" :key="i">
              <span class="tip-bullet"></span>
              {{ tip }}
            </li>
          </ul>
        </div>
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

const intensityText = (i: string) => ({ low: '低强度', moderate: '中等强度', high: '高强度' }[i] || i)
const intensityTagClass = (i: string) => ({
  low: 'tag-green',
  moderate: 'tag-yellow',
  high: 'tag-red'
}[i] || 'tag-blue')

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
.status-bar {
  margin-bottom: 16px;
  .status-content {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    color: rgba(180, 210, 240, 0.9);
    font-size: 14px;
  }
  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #409eff;
    box-shadow: 0 0 8px rgba(64, 158, 255, 0.6);
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.exercise-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.glass-card {
  position: relative;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(64, 158, 255, 0.35);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);

    .card-glow { opacity: 1; }
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
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;

  .title {
    font-weight: 600;
    font-size: 15px;
    color: #e8ecf1;
    letter-spacing: 0.5px;
  }
}

.description {
  margin: 0 0 12px;
  color: rgba(200, 210, 220, 0.85);
  font-size: 14px;
  line-height: 1.7;
}

.meta {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;

  .meta-item {
    display: flex;
    align-items: center;
    gap: 6px;
    color: rgba(160, 180, 200, 0.8);
    font-size: 13px;
  }

  .meta-icon {
    font-size: 14px;
    filter: drop-shadow(0 0 4px rgba(64, 158, 255, 0.3));
  }
}

.glass-alert {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(230, 162, 60, 0.1);
  border: 1px solid rgba(230, 162, 60, 0.25);
  border-radius: 10px;
  color: rgba(240, 200, 130, 0.9);
  font-size: 13px;
  line-height: 1.6;
  margin-top: 4px;

  .alert-icon {
    filter: drop-shadow(0 0 4px rgba(230, 162, 60, 0.4));
  }
}

.glass-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.tag-blue {
  background: rgba(64, 158, 255, 0.15);
  border: 1px solid rgba(64, 158, 255, 0.3);
  color: #79bbff;
}

.tag-green {
  background: rgba(103, 194, 58, 0.15);
  border: 1px solid rgba(103, 194, 58, 0.3);
  color: #95d475;
}

.tag-yellow {
  background: rgba(230, 162, 60, 0.15);
  border: 1px solid rgba(230, 162, 60, 0.3);
  color: #eebe77;
}

.tag-red {
  background: rgba(245, 108, 108, 0.15);
  border: 1px solid rgba(245, 108, 108, 0.3);
  color: #f89898;
}

.safety-tips {
  margin-top: 20px;

  h4 {
    margin: 0 0 14px;
    font-size: 16px;
    color: #e0e6ed;
    display: flex;
    align-items: center;
    gap: 8px;

    .section-icon {
      filter: drop-shadow(0 0 6px rgba(230, 162, 60, 0.4));
    }
  }

  ul {
    margin: 0;
    padding: 0;
    list-style: none;

    li {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 10px;
      color: rgba(200, 210, 220, 0.85);
      font-size: 14px;
      line-height: 1.6;

      .tip-bullet {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: rgba(230, 162, 60, 0.7);
        box-shadow: 0 0 6px rgba(230, 162, 60, 0.4);
        margin-top: 8px;
        flex-shrink: 0;
      }
    }
  }
}
</style>
