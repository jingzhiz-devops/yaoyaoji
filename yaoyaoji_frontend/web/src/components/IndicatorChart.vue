<template>
  <div class="indicator-chart">
    <div class="chart-header">
      <h3>{{ indicatorName }}</h3>
      <span class="unit">{{ unit }}</span>
    </div>
    
    <div class="chart-content">
      <div v-if="records.length > 0" class="records-list">
        <div v-for="(record, index) in records" :key="index" class="record-item">
          <div class="record-value">
            <span class="value">{{ record.value }}</span>
            <span class="status" :class="getStatus(record.value)">
              {{ getStatusText(record.value) }}
            </span>
          </div>
          <div class="record-date">{{ formatDate(record.measurement_date) }}</div>
        </div>
      </div>
      <el-empty v-else description="暂无数据" />
    </div>

    <div class="chart-info" v-if="normalRange">
      <div>正常值范围: {{ normalRange.min }} - {{ normalRange.max }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { IndicatorRecord } from '@/types'

interface Props {
  indicatorName: string
  unit?: string
  records: IndicatorRecord[]
  normalRange?: {
    min: number
    max: number
  }
}

defineProps<Props>()

const getStatus = (value: number): string => {
  if (!value) return 'unknown'
  return 'normal'
}

const getStatusText = (value: number): string => {
  if (!value) return '未知'
  return '正常'
}

const formatDate = (date: string): string => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN')
}
</script>

<style scoped lang="scss">
.indicator-chart {
  background: white;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;

  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    border-bottom: 2px solid #409eff;
    padding-bottom: 10px;

    h3 {
      margin: 0;
      font-size: 18px;
    }

    .unit {
      color: #909399;
      font-size: 14px;
    }
  }

  .chart-content {
    min-height: 100px;
    margin-bottom: 15px;

    .records-list {
      display: flex;
      flex-direction: column;
      gap: 10px;

      .record-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background: #f5f7fa;
        border-radius: 4px;

        .record-value {
          display: flex;
          align-items: center;
          gap: 10px;

          .value {
            font-size: 18px;
            font-weight: 600;
            color: #303133;
          }

          .status {
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 12px;

            &.normal {
              background: #f0f9ff;
              color: #67c23a;
            }

            &.warning {
              background: #fef0f0;
              color: #f56c6c;
            }

            &.unknown {
              background: #f5f7fa;
              color: #909399;
            }
          }
        }

        .record-date {
          color: #909399;
          font-size: 12px;
        }
      }
    }
  }

  .chart-info {
    padding-top: 10px;
    border-top: 1px solid #ebeef5;
    color: #606266;
    font-size: 12px;
  }
}
</style>
