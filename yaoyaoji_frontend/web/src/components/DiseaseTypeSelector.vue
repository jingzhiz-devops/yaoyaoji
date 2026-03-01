<template>
  <div class="disease-type-selector">
    <div class="type-cards">
      <div
        v-for="t in diseaseTypes"
        :key="t.type"
        class="type-card"
        :class="{ active: modelValue === t.type }"
        @click="$emit('update:modelValue', t.type)"
      >
        <div class="card-icon">{{ t.icon }}</div>
        <div class="card-info">
          <h4>{{ t.displayName }}</h4>
          <p>{{ t.description }}</p>
          <div class="features">
            <el-tag v-for="f in t.features" :key="f" size="small" type="info">{{ f }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ modelValue: string }>()
defineEmits<{ 'update:modelValue': [value: string] }>()

const diseaseTypes = [
  {
    type: 'hypertension',
    displayName: '高血压',
    icon: '❤️',
    description: '以体循环动脉血压持续升高为主要特征',
    features: ['收缩压/舒张压监测', '心率追踪', 'DASH饮食建议']
  },
  {
    type: 'hyperlipidemia',
    displayName: '高血脂',
    icon: '🩸',
    description: '血脂水平过高，需定期监测血脂四项',
    features: ['血脂四项监测', '低脂饮食指导', '运动建议']
  },
  {
    type: 'diabetes',
    displayName: '糖尿病',
    icon: '💉',
    description: '以高血糖为特征的代谢性疾病',
    features: ['多时段血糖监测', '三餐饮食建议', '并发症追踪', '运动指导']
  }
]
</script>

<style scoped lang="scss">
.type-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.type-card {
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover { border-color: #409eff; box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2); }
  &.active { border-color: #409eff; background: #ecf5ff; }

  .card-icon { font-size: 32px; margin-bottom: 10px; }
  .card-info {
    h4 { margin: 0 0 8px; font-size: 16px; }
    p { margin: 0 0 10px; color: #909399; font-size: 13px; }
    .features { display: flex; flex-wrap: wrap; gap: 4px; }
  }
}
</style>
