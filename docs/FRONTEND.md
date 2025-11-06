# 前端功能文档

## 目录

- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [页面功能](#页面功能)
  - [登录注册](#1-登录注册)
  - [首页](#2-首页)
  - [药箱管理](#3-药箱管理)
  - [用药计划](#4-用药计划)
  - [症状记录](#5-症状记录)
  - [仪表盘](#6-仪表盘)
  - [疾病查询](#7-疾病查询)
  - [家庭管理](#8-家庭管理)
  - [健康档案](#9-健康档案)
  - [个人中心](#10-个人中心)
- [状态管理](#状态管理)
- [API 集成](#api-集成)
- [样式规范](#样式规范)

---

## 技术栈

### 核心框架
- **Vue 3.5.22** - 渐进式 JavaScript 框架
- **TypeScript 5.9.0** - 类型安全的 JavaScript 超集
- **Vite 7.1.11** - 下一代前端构建工具

### UI 组件库
- **Element Plus 2.11.5** - Vue 3 组件库
- **@element-plus/icons-vue 2.3.2** - Element Plus 图标库

### 路由与状态管理
- **Vue Router 4.6.3** - 官方路由管理器
- **Pinia 3.0.3** - 官方状态管理库（Vuex 继任者）

### HTTP 客户端
- **Axios 1.13.1** - Promise 基础的 HTTP 客户端

### 工具库
- **Day.js 1.11.18** - 轻量级日期处理库

### 开发工具
- **ESLint 9.37.0** - 代码质量检查
- **vue-tsc 3.1.1** - Vue TypeScript 类型检查
- **sass-embedded 1.93.3** - Sass/SCSS 预处理器

---

## 项目结构

```
src/
├── api/                    # API 接口封装
│   ├── config.ts           # API 基础配置（baseURL、拦截器）
│   └── index.ts            # 所有接口定义
├── assets/                 # 静态资源
│   ├── base.css            # 基础样式
│   └── main.css            # 全局样式
├── router/                 # 路由配置
│   └── index.ts            # 路由定义与守卫
├── stores/                 # 状态管理
│   ├── user.ts             # 用户状态
│   └── medication.ts       # 用药状态
├── types/                  # TypeScript 类型定义
│   └── index.ts            # 全局类型接口
├── views/                  # 页面组件
│   ├── auth/
│   │   └── LoginView.vue   # 登录注册页
│   ├── medication/
│   │   ├── MedicationBoxView.vue   # 药箱管理
│   │   ├── ScheduleView.vue        # 用药计划
│   │   └── SymptomView.vue         # 症状记录
│   ├── HomeView.vue                # 首页
│   ├── DashboardView.vue           # 仪表盘
│   ├── DoctorView.vue              # 疾病查询
│   ├── FamilyView.vue              # 家庭管理
│   ├── HealthProfileView.vue       # 健康档案
│   └── UserProfileView.vue         # 个人中心
├── App.vue                 # 根组件
└── main.ts                 # 应用入口
```

---

## 页面功能

### 1. 登录注册

**文件**: `views/auth/LoginView.vue`

**功能特性**:
- ✅ 登录/注册表单切换
- ✅ 表单验证（用户名、密码、邮箱）
- ✅ 记住登录状态（localStorage）
- ✅ 自动跳转到首页

**界面元素**:
- 品牌 Logo："药药记 · 守护您的每一份健康"
- 登录表单：用户名、密码
- 注册表单：用户名、密码、确认密码、邮箱（可选）
- 切换按钮："还没有账号？立即注册" / "已有账号？立即登录"

**验证规则**:
- 用户名：2-50 个字符，支持中文、英文、数字、下划线
- 密码：至少 6 个字符
- 确认密码：必须与密码一致
- 邮箱：格式验证（可选）

**登录流程**:
1. 用户输入凭据
2. 调用 `/api/auth/login` 获取 Token
3. 存储 Token 到 localStorage
4. 更新 Pinia 用户状态
5. 跳转到首页

---

### 2. 首页

**文件**: `views/HomeView.vue`

**功能特性**:
- ✅ 简洁的欢迎页面
- ✅ 文字标语："药药记 · 守护您的每一份健康"
- ✅ 快捷导航入口

**界面风格**:
- 极简设计，纯文字展示
- 无 Icon、无动画
- 引导用户进入主要功能模块

---

### 3. 药箱管理

**文件**: `views/medication/MedicationBoxView.vue`

**功能特性**:

#### 3.1 药品列表展示
- ✅ 卡片式布局，支持图片展示
- ✅ 显示药品名称、厂家、禁忌信息、备注
- ✅ 药品包装图预览
- ✅ 状态过滤（活跃/已停用）

#### 3.2 添加药品
- ✅ 从药品库搜索
- ✅ 手动输入药品信息
- ✅ 自定义名称和备注
- ✅ 药物冲突自动检测
- ✅ 高危冲突阻止添加，中低风险警告提示

#### 3.3 编辑药品
- ✅ 修改药品名称
- ✅ 更新厂家信息
- ✅ 编辑禁忌信息
- ✅ 上传/更换药品包装图
- ✅ 修改备注

**上传图片流程**:
1. 点击"选择图片"按钮
2. 选择本地图片文件（JPG/PNG/GIF/WebP，≤5MB）
3. 预览图片
4. 调用 `/api/upload/medicine-image` 上传
5. 获取图片 URL
6. 更新药品信息

#### 3.4 删除药品
- ✅ 软删除（标记为 inactive）
- ✅ 确认对话框防止误删

**界面组件**:
- 搜索框：快速查找药品
- 添加按钮：打开添加药品对话框
- 药品卡片：
  - 药品图片（默认占位图）
  - 药品名称
  - 厂家
  - 禁忌信息（红色警告）
  - 操作按钮（编辑/删除）

---

### 4. 用药计划

**文件**: `views/medication/ScheduleView.vue`

**功能特性**:

#### 4.1 计划列表
- ✅ 按药品分组展示
- ✅ 显示用药频率、剂量、时间
- ✅ 开始/结束日期
- ✅ 活跃计划高亮显示

#### 4.2 创建计划
- ✅ 选择药品（从我的药箱）
- ✅ 设置用药频率（每日 1-4 次）
- ✅ 多时间点选择器
- ✅ 剂量输入（如"2 片"、"10ml"）
- ✅ 开始/结束日期选择

**频率与时间点匹配**:
- 每日 1 次：选择 1 个时间点
- 每日 2 次：选择 2 个时间点
- 每日 3 次：选择 3 个时间点
- 每日 4 次：选择 4 个时间点

**验证规则**:
- 时间点数量必须与频率匹配
- 结束日期必须晚于开始日期
- 同一药品不能有重复的活跃计划

#### 4.3 编辑计划
- ✅ 修改剂量
- ✅ 调整时间点
- ✅ 延长/缩短周期

#### 4.4 删除计划
- ✅ 确认对话框
- ✅ 关联的用药记录不会被删除

#### 4.5 今日用药
- ✅ 显示今天的所有用药计划
- ✅ 时间线展示
- ✅ 标记已服用/跳过
- ✅ 实时统计服药进度

**今日用药卡片**:
- 药品名称
- 计划时间
- 剂量
- 状态标记（待服用/已服用/已跳过）
- 快捷操作按钮

---

### 5. 症状记录

**文件**: `views/medication/SymptomView.vue`

**功能特性**:

#### 5.1 记录症状
- ✅ Emoji 选择器（快速选择常见症状表情）
- ✅ 文字描述输入
- ✅ 强度滑块（1-5 级）
- ✅ 自动记录时间

**常用 Emoji**:
- 🤒 发烧
- 😷 咳嗽
- 🤧 流鼻涕
- 🤕 头痛
- 😵 头晕
- 🤮 恶心
- 😰 出汗
- 😴 疲劳

#### 5.2 症状列表
- ✅ 时间线展示（最近 → 最早）
- ✅ 显示 Emoji、描述、强度、时间
- ✅ 按日期分组

#### 5.3 筛选与搜索
- ✅ 日期范围筛选
- ✅ 最低强度过滤
- ✅ 关键词搜索

#### 5.4 编辑与删除
- ✅ 修改症状描述
- ✅ 调整强度
- ✅ 删除记录

**数据可视化**（未来）:
- 症状频率统计
- 强度趋势图
- 与用药记录关联分析

---

### 6. 仪表盘

**文件**: `views/DashboardView.vue`

**功能特性**:

#### 6.1 数据统计卡片
- ✅ **今日用药计划**: 今天需要服用的药品数量
- ✅ **已服药天数**: 基于 actual_time 去重统计
- ✅ **服药率**: (已服用次数 / 计划总次数) × 100%
- ✅ **症状记录**: 最近 7 天的症状记录数量

#### 6.2 用药日历
- ✅ 月历视图
- ✅ 标记有用药记录的日期
- ✅ 点击日期查看详情

#### 6.3 最近用药记录
- ✅ 显示最近 10 条记录
- ✅ 药品名称、时间、状态
- ✅ 快速跳转到详情

#### 6.4 症状趋势
- ✅ 最近 7 天的症状统计
- ✅ 强度分布图（柱状图）
- ✅ 点击查看详细记录

**界面布局**:
```
┌──────────────────────────────────────┐
│     统计卡片（4 个并排）              │
├──────────────────────────────────────┤
│  用药日历  │  最近用药  │  症状趋势  │
└──────────────────────────────────────┘
```

---

### 7. 疾病查询

**文件**: `views/DoctorView.vue`

**功能特性**:

#### 7.1 疾病搜索
- ✅ 输入框模糊搜索
- ✅ 支持疾病名称、别名、简介搜索
- ✅ 实时搜索结果

#### 7.2 药品反向查询
- ✅ 输入药品名称
- ✅ 查找适用该药品的疾病
- ✅ 显示推荐用药和禁忌

#### 7.3 疾病详情
- ✅ 疾病名称和别名
- ✅ 疾病简介
- ✅ 常用药物推荐
- ✅ 用药禁忌提醒

**界面元素**:
- 搜索框：支持疾病/药品搜索
- 切换标签：疾病搜索 / 药品搜索
- 结果列表：卡片式展示
- 详情对话框：点击查看完整信息

**未来扩展**（AI 医生）:
- 智能问答
- 症状匹配推荐
- 用药建议
- 健康咨询

---

### 8. 家庭管理

**文件**: `views/FamilyView.vue`

**功能特性**:

#### 8.1 我的家庭
- ✅ 显示家庭名称
- ✅ 显示邀请码
- ✅ 成员数量统计
- ✅ 管理员标识

#### 8.2 创建家庭
- ✅ 输入家庭名称
- ✅ 自动生成唯一邀请码
- ✅ 创建者成为管理员

#### 8.3 加入家庭
- ✅ 输入邀请码
- ✅ 验证邀请码有效性
- ✅ 加入后自动更新状态

#### 8.4 家庭成员列表
- ✅ 显示成员姓名、角色、年龄
- ✅ 自动计算年龄（基于出生日期）
- ✅ 显示备注信息

**成员卡片**:
- 姓名（username 或 real_name）
- 角色标签（父亲/母亲/儿童/老人/配偶/其他）
- 年龄
- 备注
- 操作按钮（编辑/移除）

#### 8.5 编辑成员
- ✅ 修改角色
- ✅ 设置出生日期
- ✅ 添加备注

#### 8.6 移除成员
- ✅ 确认对话框
- ✅ 仅管理员可移除其他成员
- ✅ 不能移除自己（需使用退出功能）

#### 8.7 退出/解散家庭
- ✅ 普通成员：退出家庭
- ✅ 管理员：解散家庭（清理所有成员）
- ✅ 二次确认

#### 8.8 家庭成员用药信息
- ✅ 显示其他成员的用药概况
- ✅ 药品种类数量
- ✅ 今日用药计划数量

#### 8.9 切换账号
- ✅ 点击成员卡片切换到该账号
- ✅ 获取新 Token
- ✅ 更新 localStorage
- ✅ 刷新页面

**切换账号流程**:
1. 点击"切换到此账号"按钮
2. 调用 `/api/family/switch-account`
3. 获取目标用户的 Token
4. 更新 `localStorage.token` 和 `localStorage.user`
5. 调用 `location.reload()` 刷新页面

#### 8.10 紧急联系人
- ✅ 添加联系人（姓名、关系、电话）
- ✅ 设置主联系人
- ✅ 编辑/删除联系人
- ✅ 点击电话号码直接拨打

**界面布局**:
```
┌──────────────────────────────────────┐
│         我的家庭信息                  │
│  家庭名称 | 邀请码 | 成员数量          │
├──────────────────────────────────────┤
│         家庭成员列表                  │
│  [成员卡片] [成员卡片] [成员卡片]     │
├──────────────────────────────────────┤
│         紧急联系人                    │
│  [联系人卡片] [联系人卡片]            │
└──────────────────────────────────────┘
```

---

### 9. 健康档案

**文件**: `views/HealthProfileView.vue`

**功能特性**:

#### 9.1 基本信息
- ✅ 真实姓名
- ✅ 血型（A/B/AB/O + Rh）
- ✅ 身高（cm）
- ✅ 体重（kg）
- ✅ 慢性病（多选）

#### 9.2 常用医学指标
- ✅ 血压（收缩压/舒张压）
- ✅ 心率（次/分）
- ✅ 血糖（mmol/L）
- ✅ 体温（℃）

#### 9.3 过敏史
- ✅ 添加过敏记录
- ✅ 过敏原类型（药物/食物/其他）
- ✅ 过敏反应描述
- ✅ 严重程度（轻微/中等/严重）
- ✅ 发现日期
- ✅ 备注

**过敏史列表**:
- 卡片式展示
- 红色警告标识
- 编辑/删除操作

#### 9.4 家族病史
- ✅ 亲属关系（父亲/母亲/祖父母等）
- ✅ 疾病名称
- ✅ 发病年龄
- ✅ 备注

#### 9.5 手术记录
- ✅ 手术名称
- ✅ 手术日期
- ✅ 医院
- ✅ 主刀医生
- ✅ 备注

#### 9.6 体检报告
- ✅ 体检日期
- ✅ 体检类型（年度体检/入职体检/专项检查）
- ✅ 医院/体检中心
- ✅ 总结
- ✅ 报告文件上传（未来）

#### 9.7 疫苗接种
- ✅ 疫苗名称
- ✅ 接种日期
- ✅ 接种医院
- ✅ 批次号
- ✅ 下次接种日期
- ✅ 备注

**界面布局**:
```
┌──────────────────────────────────────┐
│  基本信息表单                         │
├──────────────────────────────────────┤
│  常用医学指标                         │
├──────────────────────────────────────┤
│  [过敏史] [家族病史] [手术记录]       │
│  [体检报告] [疫苗接种]                │
└──────────────────────────────────────┘
```

**标签页切换**:
- 每个模块一个标签页
- 点击切换显示对应内容
- 独立的增删改查操作

---

### 10. 个人中心

**文件**: `views/UserProfileView.vue`

**功能特性**:

#### 10.1 用户信息
- ✅ 用户名（不可修改）
- ✅ 邮箱
- ✅ 注册时间

#### 10.2 修改密码
- ✅ 输入原密码
- ✅ 输入新密码
- ✅ 确认新密码
- ✅ 验证原密码正确性

#### 10.3 退出登录
- ✅ 清除 localStorage
- ✅ 清空 Pinia 状态
- ✅ 跳转到登录页

**界面元素**:
- 用户头像（默认头像或自定义）
- 信息卡片
- 修改密码对话框
- 退出登录按钮

---

## 状态管理

### User Store (stores/user.ts)

**状态**:
```typescript
interface UserState {
  token: string | null
  user: User | null
  isLoggedIn: boolean
}
```

**Actions**:
- `login(username, password)` - 用户登录
- `logout()` - 用户退出
- `fetchUserInfo()` - 获取用户信息
- `loadFromStorage()` - 从 localStorage 加载

**持久化**:
- Token 和用户信息存储在 `localStorage`
- 刷新页面时自动恢复状态

### Medication Store (stores/medication.ts)

**状态**:
```typescript
interface MedicationState {
  medications: UserMedication[]
  schedules: MedicationSchedule[]
  records: MedicationRecord[]
  symptoms: SymptomRecord[]
}
```

**Actions**:
- `fetchMedications()` - 获取我的药箱
- `fetchSchedules()` - 获取用药计划
- `fetchRecords()` - 获取用药记录
- `fetchSymptoms()` - 获取症状记录

---

## API 集成

### API 配置 (api/config.ts)

**基础配置**:
```typescript
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
})
```

**请求拦截器**:
```typescript
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

**响应拦截器**:
```typescript
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token 过期，跳转登录
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### API 接口定义 (api/index.ts)

**用户认证**:
```typescript
export const authAPI = {
  login: (data: LoginData) => apiClient.post('/api/auth/login', data),
  register: (data: RegisterData) => apiClient.post('/api/auth/register', data),
  getCurrentUser: () => apiClient.get('/api/users/me')
}
```

**药品管理**:
```typescript
export const medicineAPI = {
  getAll: (params?: { search?: string }) => 
    apiClient.get('/api/medicines/', { params }),
  create: (data: MedicineCreate) => 
    apiClient.post('/api/medicines/', data)
}
```

**用药计划**:
```typescript
export const scheduleAPI = {
  getAll: () => apiClient.get('/api/schedules/'),
  create: (data: ScheduleCreate) => 
    apiClient.post('/api/schedules/', data),
  update: (id: number, data: ScheduleUpdate) => 
    apiClient.patch(`/api/schedules/${id}`, data),
  delete: (id: number) => 
    apiClient.delete(`/api/schedules/${id}`)
}
```

---

## 样式规范

### 设计系统

**主色调**:
- 主色：`#409EFF` (Element Plus 蓝)
- 成功：`#67C23A`
- 警告：`#E6A23C`
- 危险：`#F56C6C`
- 信息：`#909399`

**间距**:
- 极小：`4px`
- 小：`8px`
- 中：`16px`
- 大：`24px`
- 极大：`32px`

**圆角**:
- 小：`4px`
- 中：`8px`
- 大：`12px`

**阴影**:
```scss
box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
```

### 响应式设计

**断点**:
- 手机：`< 768px`
- 平板：`768px - 1024px`
- 桌面：`> 1024px`

**适配策略**:
- 移动端：单列布局，大按钮
- 平板：双列布局
- 桌面：多列布局，侧边栏导航

### CSS 变量

```css
:root {
  --primary-color: #409EFF;
  --text-color: #303133;
  --border-color: #DCDFE6;
  --bg-color: #F5F7FA;
}
```

---

## 路由配置

### 路由表

```typescript
const routes = [
  { path: '/', redirect: '/home' },
  { path: '/login', component: LoginView },
  { 
    path: '/home', 
    component: HomeView,
    meta: { requiresAuth: true }
  },
  { 
    path: '/medication-box', 
    component: MedicationBoxView,
    meta: { requiresAuth: true }
  },
  { 
    path: '/schedule', 
    component: ScheduleView,
    meta: { requiresAuth: true }
  },
  // ... 其他路由
]
```

### 路由守卫

```typescript
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})
```

---

## 组件复用

### 公共组件（未来）

- **DatePicker**: 日期选择器
- **TimePicker**: 时间选择器
- **ImageUploader**: 图片上传组件
- **ConfirmDialog**: 确认对话框
- **EmptyState**: 空状态占位符
- **LoadingSpinner**: 加载动画

---

## 性能优化

### 已实施
- ✅ Vite 构建优化（按需加载、Tree-shaking）
- ✅ Element Plus 按需引入
- ✅ 图片懒加载
- ✅ 接口防抖与节流

### 待优化
- [ ] 虚拟滚动（长列表）
- [ ] Service Worker（PWA）
- [ ] 图片压缩与 WebP 格式
- [ ] Gzip 压缩

---

## 错误处理

### 全局错误处理

```typescript
app.config.errorHandler = (err, instance, info) => {
  console.error('Global error:', err, info)
  ElMessage.error('系统错误，请稍后重试')
}
```

### API 错误处理

```typescript
try {
  const res = await api.fetchData()
} catch (error) {
  if (error.response?.status === 404) {
    ElMessage.warning('数据不存在')
  } else {
    ElMessage.error('请求失败')
  }
}
```

---

## 国际化（未来）

### i18n 配置

```typescript
const messages = {
  zh: {
    welcome: '欢迎使用药药记',
    login: '登录'
  },
  en: {
    welcome: 'Welcome to YaoYaoLing',
    login: 'Login'
  }
}
```

---

## 测试（未来）

### 单元测试
- 使用 Vitest
- 组件测试：Vue Test Utils
- 工具函数测试

### E2E 测试
- 使用 Playwright
- 关键用户流程测试

---

## 部署

### 构建生产版本

```bash
npm run build
```

生成目录：`dist/`

### 环境变量

**.env.production**:
```env
VITE_API_BASE_URL=https://api.yaoyaoling.com
```

### Nginx 配置

```nginx
server {
  listen 80;
  server_name yaoyaoling.com;
  
  location / {
    root /var/www/yaoyaoling/dist;
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://localhost:8000;
  }
}
```

---

## 开发建议

### 代码规范
- 使用组合式 API (`<script setup>`)
- TypeScript 类型定义
- ESLint 自动修复：`npm run lint`
- 提交前检查类型：`npm run type-check`

### 命名约定
- 组件文件：PascalCase（如 `MedicationBoxView.vue`）
- 工具函数：camelCase（如 `formatDate`）
- 常量：UPPER_SNAKE_CASE（如 `API_BASE_URL`）

### Git 提交信息
```
feat: 添加药品包装图上传功能
fix: 修复症状记录时间显示错误
docs: 更新 README
style: 调整药箱卡片样式
refactor: 重构用药计划表单
```

---

**更新日期**: 2024-11-06
