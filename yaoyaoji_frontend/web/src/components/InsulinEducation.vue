<template>
  <div class="insulin-education">
    <!-- 重要提醒 -->
    <div class="warning-banner glass-card">
      <div class="card-glow"></div>
      <div class="card-content warning-content">
        <span class="warning-icon">⚠️</span>
        <span>胰岛素为处方药，所有使用方案必须在医生指导下进行，以下内容仅供科普参考。</span>
      </div>
    </div>

    <!-- 一、胰岛素类型与选择 -->
    <div class="section">
      <div class="section-header">
        <span class="section-icon">📋</span>
        <h4>胰岛素类型与选择</h4>
        <div class="header-line"></div>
      </div>
      <div class="type-cards">
        <div v-for="t in insulinTypes" :key="t.type" class="type-card glass-card">
          <div class="card-glow"></div>
          <div class="card-content">
            <div class="type-header">
              <span class="type-name">{{ t.type }}</span>
              <span class="glass-tag tag-blue">{{ t.onset }}</span>
            </div>
            <div class="type-drugs">
              <span class="meta-label">代表药物：</span>{{ t.drugs }}
            </div>
            <div class="type-duration">
              <span class="meta-label">持续时间：</span>{{ t.duration }}
            </div>
            <div class="type-usage">
              <span class="meta-label">适用场景：</span>{{ t.usage }}
            </div>
          </div>
        </div>
      </div>
      <div class="tip-note glass-alert">
        <span class="alert-icon">💡</span>
        <span>医生会根据年龄、体重、胰岛功能、胰岛素敏感性等因素制定个体化方案。</span>
      </div>
    </div>

    <!-- 二、规范注射技术 -->
    <div class="section">
      <div class="section-header">
        <span class="section-icon">💉</span>
        <h4>规范注射技术</h4>
        <div class="header-line"></div>
      </div>

      <!-- 注射前准备 -->
      <div class="sub-section glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <h5>✅ 注射前准备</h5>
          <ul class="check-list">
            <li>洗手、消毒注射部位</li>
            <li>检查胰岛素外观（应澄清无沉淀）</li>
            <li>确认剂量、有效期，安装新针头</li>
          </ul>
        </div>
      </div>

      <!-- 注射部位选择与轮换 -->
      <div class="sub-section glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <h5>✅ 注射部位选择与轮换</h5>
          <div class="absorption-order">
            <span class="order-label">吸收速度排序：</span>
            <span class="glass-tag tag-green">腹部（最快）</span>
            <span class="arrow">→</span>
            <span class="glass-tag tag-blue">上臂</span>
            <span class="arrow">→</span>
            <span class="glass-tag tag-yellow">大腿</span>
            <span class="arrow">→</span>
            <span class="glass-tag tag-purple">臀部（最慢）</span>
          </div>
          <ul class="check-list">
            <li>同一部位内：每次注射点间隔 ≥ 1厘米</li>
            <li>不同部位间：可按"腹部→大腿→上臂→臀部"顺序轮换</li>
            <li>腹部可分4个象限，每周轮换一个区域，顺时针进行</li>
            <li>避免在瘢痕、硬结、水肿处注射</li>
          </ul>
        </div>
      </div>

      <!-- 正确注射手法 -->
      <div class="sub-section glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <h5>✅ 正确注射手法</h5>
          <ul class="check-list">
            <li><span class="highlight">针头选择：</span>4mm或5mm笔用针头适用于所有成人，通常无需捏皮</li>
            <li><span class="highlight">捏皮技巧：</span>如需捏皮，用拇指和食指轻捏皮肤，避免将肌肉一同捏起</li>
            <li><span class="highlight">进针角度：</span>4-5mm针头90°垂直进针；较长针头或消瘦者需45°角</li>
            <li><span class="highlight">推注后停留：</span>注射完毕后针头停留 ≥ 10秒，确保药液完全注入</li>
            <li><span class="highlight">针头处理：</span>每次注射必须更换新针头，避免感染和脂肪增生</li>
          </ul>
          <div class="tip-note glass-alert">
            <span class="alert-icon">📊</span>
            <span>研究显示：接受规范注射培训的患者，6个月后糖化血红蛋白（HbA1c）平均可降低1%。</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 三、剂量调整原则 -->
    <div class="section">
      <div class="section-header">
        <span class="section-icon">📈</span>
        <h4>剂量调整原则</h4>
        <div class="header-line"></div>
      </div>

      <div v-for="d in dosageAdjustments" :key="d.title" class="sub-section glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <h5>{{ d.icon }} {{ d.title }}</h5>
          <ul class="check-list">
            <li v-for="(item, i) in d.items" :key="i">
              <span v-if="item.label" class="highlight">{{ item.label }}：</span>{{ item.text }}
            </li>
          </ul>
        </div>
      </div>

      <div class="tip-note glass-alert">
        <span class="alert-icon">⚠️</span>
        <span>调整需遵循"小步渐进"原则，避免大幅波动，并密切监测低血糖风险。</span>
      </div>
    </div>

    <!-- 四、胰岛素保存方法 -->
    <div class="section">
      <div class="section-header">
        <span class="section-icon">❄️</span>
        <h4>胰岛素保存方法</h4>
        <div class="header-line"></div>
      </div>

      <div class="storage-cards">
        <div v-for="s in storageInfo" :key="s.status" class="storage-card glass-card">
          <div class="card-glow"></div>
          <div class="card-content">
            <div class="storage-header">
              <span class="storage-icon">{{ s.icon }}</span>
              <span class="storage-title">{{ s.status }}</span>
            </div>
            <div class="storage-detail"><span class="meta-label">保存条件：</span>{{ s.condition }}</div>
            <div class="storage-detail"><span class="meta-label">有效期：</span>{{ s.validity }}</div>
            <div class="storage-detail"><span class="meta-label">注意事项：</span>{{ s.note }}</div>
          </div>
        </div>
      </div>

      <div class="tip-note glass-alert alert-danger">
        <span class="alert-icon">❌</span>
        <span>禁止：冷冻、高温（＞30℃）、阳光直射、剧烈摇晃</span>
      </div>
    </div>

    <!-- 五、关键安全提示 -->
    <div class="section">
      <div class="section-header">
        <span class="section-icon">⚠️</span>
        <h4>关键安全提示</h4>
        <div class="header-line"></div>
      </div>

      <div v-for="tip in safetyTips" :key="tip.title" class="sub-section glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <h5>{{ tip.icon }} {{ tip.title }}</h5>
          <ul class="check-list">
            <li v-for="(item, i) in tip.items" :key="i">{{ item }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 核心口诀 -->
    <div class="section">
      <div class="section-header">
        <span class="section-icon">🎯</span>
        <h4>科学使用胰岛素的核心口诀</h4>
        <div class="header-line"></div>
      </div>
      <div class="mantra-card glass-card">
        <div class="card-glow"></div>
        <div class="card-content">
          <ul class="mantra-list">
            <li><span class="mantra-check">✅</span> <span class="highlight">遵医嘱：</span>方案个体化，不自行大幅调整</li>
            <li><span class="mantra-check">✅</span> <span class="highlight">规范打：</span>新针头、轮换部位、正确手法</li>
            <li><span class="mantra-check">✅</span> <span class="highlight">勤监测：</span>血糖记录是调整剂量的金标准</li>
            <li><span class="mantra-check">✅</span> <span class="highlight">会保存：</span>温度适宜，避免失效</li>
            <li><span class="mantra-check">✅</span> <span class="highlight">防低糖：</span>识别症状，随身备糖</li>
          </ul>
        </div>
      </div>
      <div class="tip-note glass-alert" style="margin-top: 16px;">
        <span class="alert-icon">📌</span>
        <span>胰岛素治疗是糖尿病管理的重要工具，但需与饮食控制、规律运动、血糖监测相结合，才能实现最佳控糖效果。如有任何疑问或不适，请及时咨询内分泌专科医生。</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const insulinTypes = [
  { type: '速效胰岛素', drugs: '门冬胰岛素、赖脯胰岛素、谷赖胰岛素', onset: '起效10-15分钟', duration: '3-5小时', usage: '餐前注射，控制餐后血糖' },
  { type: '短效胰岛素', drugs: '普通胰岛素', onset: '起效30分钟', duration: '6-8小时', usage: '餐前30分钟注射' },
  { type: '中效胰岛素', drugs: '低精蛋白锌胰岛素', onset: '起效1-2小时', duration: '10-16小时', usage: '基础血糖控制' },
  { type: '长效胰岛素', drugs: '甘精胰岛素、德谷胰岛素', onset: '起效缓慢', duration: '24小时以上', usage: '每日1次，稳定基础血糖' },
  { type: '预混胰岛素', drugs: '门冬胰岛素30、精蛋白锌重组赖脯胰岛素25', onset: '含速效+中效', duration: '混合作用', usage: '每日2次，兼顾空腹和餐后' }
]

const dosageAdjustments = [
  {
    icon: '🔹', title: '基础胰岛素调整',
    items: [
      { label: '目标', text: '空腹血糖控制在4.4-7.0 mmol/L（个体化目标遵医嘱）' },
      { label: '方法', text: '连续3天空腹血糖高于目标值，增加1-2单位；低于目标则减少1-2单位' },
      { label: '频率', text: '通常每3-5天评估调整1次，直至达标' }
    ]
  },
  {
    icon: '🔹', title: '餐时胰岛素调整',
    items: [
      { label: '目标', text: '餐后2小时血糖＜10.0 mmol/L' },
      { label: '计算参考', text: '每10-15g碳水化合物约需1单位速效胰岛素' },
      { label: '校正剂量', text: '餐前血糖＞7.0 mmol/L时，每高出1 mmol/L可追加1-2单位' }
    ]
  },
  {
    icon: '🔹', title: '预混胰岛素调整',
    items: [
      { label: '', text: '早餐前剂量 → 主要影响早餐后血糖 + 次日空腹血糖' },
      { label: '', text: '晚餐前剂量 → 主要影响晚餐后血糖 + 次日空腹血糖' },
      { label: '', text: '按对应时段血糖结果分步调整' }
    ]
  }
]

const storageInfo = [
  { icon: '📦', status: '未开封', condition: '2-8℃冰箱冷藏（勿冷冻）', validity: '至包装标注有效期', note: '避免贴冰箱内壁，防止冻伤' },
  { icon: '🔓', status: '已开封', condition: '室温≤25-30℃，避光', validity: '28-30天', note: '标注开封日期，勿放回冰箱' },
  { icon: '🧳', status: '外出携带', condition: '使用保温袋，避免日晒/高温/冰冻', validity: '同已开封', note: '避免剧烈震荡' }
]

const safetyTips = [
  {
    icon: '1️⃣', title: '低血糖预防与处理',
    items: [
      '血糖＜3.9 mmol/L立即进食15g快速升糖食物（葡萄糖片、含糖饮料）',
      '随身携带糖果/葡萄糖，告知家人低血糖识别方法'
    ]
  },
  {
    icon: '2️⃣', title: '特殊时期需就医评估',
    items: [
      '发热、感染、手术、妊娠、剧烈运动前后',
      '饮食结构大幅改变或合并其他疾病时'
    ]
  },
  {
    icon: '3️⃣', title: '定期复诊与监测',
    items: [
      '新方案实施后连续监测血糖3-7天',
      '每1-3个月内分泌科复诊，评估方案有效性'
    ]
  },
  {
    icon: '4️⃣', title: '技术辅助推荐',
    items: [
      '2026 ADA指南推荐：使用胰岛素的糖尿病患者可考虑动态血糖监测（CGM），有助于减少低血糖、优化剂量调整'
    ]
  }
]
</script>

<style scoped lang="scss">
.insulin-education {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;

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
  overflow: hidden;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(64, 158, 255, 0.35);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
    .card-glow { opacity: 1; }
  }
}

.card-glow {
  position: absolute;
  top: 0; left: 0; right: 0;
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
    margin: 0 0 14px;
    font-size: 15px;
    font-weight: 600;
    color: #e8ecf1;
    letter-spacing: 0.5px;
  }
}

// Warning banner
.warning-banner {
  border-color: rgba(230, 162, 60, 0.3);
  background: rgba(230, 162, 60, 0.08);

  .card-glow {
    background: linear-gradient(90deg, transparent, rgba(230, 162, 60, 0.6), rgba(245, 108, 108, 0.4), transparent);
  }

  .warning-content {
    display: flex;
    align-items: center;
    gap: 10px;
    color: rgba(240, 200, 130, 0.95);
    font-size: 14px;
    font-weight: 500;
  }

  .warning-icon {
    font-size: 18px;
    filter: drop-shadow(0 0 6px rgba(230, 162, 60, 0.5));
  }
}

// Type cards
.type-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.type-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;

  .type-name {
    font-weight: 600;
    font-size: 15px;
    color: #e8ecf1;
  }
}

.type-drugs, .type-duration, .type-usage {
  font-size: 14px;
  color: rgba(200, 210, 220, 0.85);
  line-height: 1.8;
}

.meta-label {
  color: rgba(160, 180, 200, 0.6);
  font-size: 13px;
}

// Tags
.glass-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  backdrop-filter: blur(10px);
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

.tag-purple {
  background: rgba(160, 120, 220, 0.15);
  border: 1px solid rgba(160, 120, 220, 0.3);
  color: #c0a0ee;
}

// Absorption order
.absorption-order {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.06);

  .order-label {
    color: rgba(160, 180, 200, 0.7);
    font-size: 13px;
  }

  .arrow {
    color: rgba(160, 180, 200, 0.4);
    font-size: 14px;
  }
}

// Check list
.check-list {
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
    line-height: 1.7;

    &::before {
      content: '';
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: rgba(64, 158, 255, 0.7);
      box-shadow: 0 0 6px rgba(64, 158, 255, 0.4);
      margin-top: 9px;
      flex-shrink: 0;
    }

    &:last-child { margin-bottom: 0; }
  }
}

.highlight {
  color: #79bbff;
  font-weight: 500;
}

// Alert
.glass-alert {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid rgba(64, 158, 255, 0.2);
  border-radius: 10px;
  color: rgba(180, 210, 240, 0.9);
  font-size: 13px;
  line-height: 1.6;

  .alert-icon {
    flex-shrink: 0;
    filter: drop-shadow(0 0 4px rgba(64, 158, 255, 0.4));
  }

  &.alert-danger {
    background: rgba(245, 108, 108, 0.08);
    border-color: rgba(245, 108, 108, 0.25);
    color: rgba(248, 152, 152, 0.95);
  }
}

// Storage cards
.storage-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}

.storage-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;

  .storage-icon { font-size: 20px; }
  .storage-title {
    font-weight: 600;
    font-size: 15px;
    color: #e8ecf1;
  }
}

.storage-detail {
  font-size: 13px;
  color: rgba(200, 210, 220, 0.85);
  line-height: 1.8;
}

// Mantra
.mantra-list {
  margin: 0;
  padding: 0;
  list-style: none;

  li {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    color: rgba(200, 210, 220, 0.9);
    font-size: 15px;
    line-height: 1.6;

    &:last-child { margin-bottom: 0; }
  }

  .mantra-check {
    font-size: 16px;
    filter: drop-shadow(0 0 4px rgba(103, 194, 58, 0.4));
  }
}

// Responsive
@media (max-width: 768px) {
  .storage-cards {
    grid-template-columns: 1fr;
  }

  .absorption-order {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
