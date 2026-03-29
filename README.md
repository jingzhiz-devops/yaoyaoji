# 药药记 - 智能用药安全管理系统

<div align="center">

**守护您的每一份健康**

一款专注于个人和家庭用药安全管理的全栈 Web 应用

[功能介绍](#功能特性) • [快速开始](#快速开始) • [技术架构](#技术架构) • [文档](#文档)

</div>

---

## 📖 项目简介

**药药记**是一款面向家庭健康管理的智能用药安全系统，帮助用户科学管理药品、制定用药计划、追踪症状记录、建立完善的健康档案。系统提供药物冲突检测、疾病查询、AI 智能问诊、慢性病管理、家庭成员管理等核心功能，让用药更安全、健康管理更便捷。

### ✨ 核心价值

- 🛡️ **用药安全保障**：智能检测药物冲突，预防用药风险
- 📅 **科学用药计划**：多时间点提醒，养成规律用药习惯
- 👨‍👩‍👧‍👦 **家庭健康管理**：支持多成员管理，关爱家人健康
- 🤖 **AI 智能问诊**：接入 DeepSeek 大模型，提供症状分析与用药建议
- 🏥 **慢性病管理**：指标监测、复诊计划、用药依从性追踪
- 📊 **健康数据可视化**：ECharts 图表展示用药统计、症状趋势、指标变化
- 🔒 **数据隐私保护**：JWT 身份认证，数据安全可靠
- 🛠️ **管理员后台**：用户管理、数据统计、系统监控

---

## 🎯 功能特性

### 1. 用药管理

#### 药箱管理
- ✅ 个人药品库，支持自定义名称和备注
- ✅ 药品包装图上传（支持 JPG/PNG/GIF/WebP，最大 5MB）
- ✅ 药品信息编辑（名称、厂家、禁忌、图片等）
- ✅ 药品状态管理（active/inactive）

#### 用药计划
- ✅ 灵活的用药频率设置（每日 1-4 次）
- ✅ 多时间点提醒功能
- ✅ 用药剂量和周期管理
- ✅ 计划开始/结束时间设定

#### 用药记录
- ✅ 每日用药记录追踪
- ✅ 服药状态标记（已服用/跳过/延迟）
- ✅ 漏服原因记录
- ✅ 实际服药时间记录
- ✅ 用药统计数据（已服药天数、服药率等）

### 2. 健康管理

#### 症状记录
- ✅ 症状 Emoji + 文字描述
- ✅ 症状强度分级（1-5 级）
- ✅ 时间轴展示
- ✅ 按日期/强度筛选

#### 健康档案
- ✅ **基本信息**：姓名、血型、身高、体重
- ✅ **常用医学指标**：血压、心率、血糖、体温
- ✅ **过敏史**：过敏原、反应、严重程度
- ✅ **家族病史**：亲属关系、疾病、发病年龄
- ✅ **手术记录**：手术名称、日期、医院
- ✅ **体检报告**：体检日期、类型、总结
- ✅ **疫苗接种**：疫苗名称、接种日期、批次号

### 3. 慢性病管理 🆕

#### 慢性病档案
- ✅ 慢性病记录管理（疾病名称、ICD-10 编码、诊断信息）
- ✅ 控制状态追踪（良好/一般/不佳）
- ✅ 疾病模板库（预设常见慢性病及指标）
- ✅ 并发症记录与管理

#### 指标监测
- ✅ 自定义疾病指标（血压、血糖等）
- ✅ 指标记录与历史趋势图表
- ✅ 批量指标录入
- ✅ 指标异常自动预警（黄色/橙色/红色三级告警）
- ✅ 告警处理与建议

#### 复诊管理
- ✅ 复诊计划制定（周期性/一次性）
- ✅ 复诊记录（医生、医院、诊断、处方）
- ✅ 复诊日程日历视图

#### 用药依从性
- ✅ 用药依从性追踪与评分
- ✅ 依从性与控制状态关联分析

#### 生活方式建议
- ✅ 饮食推荐（按疾病类型个性化）
- ✅ 运动建议
- ✅ 用药提醒（灵活调度）

### 4. 家庭健康

#### 家庭管理
- ✅ 创建家庭，生成唯一邀请码
- ✅ 通过邀请码加入家庭
- ✅ 家庭成员列表（显示姓名、关系、年龄）
- ✅ 成员信息编辑（出生日期、角色、备注）
- ✅ 移除成员/退出家庭/解散家庭

#### 账号切换
- ✅ 查看家庭成员用药信息
- ✅ 一键切换到家庭成员账号
- ✅ 代为管理家人用药计划
- ✅ 查看家人健康档案

#### 紧急联系人
- ✅ 添加/编辑/删除紧急联系人
- ✅ 设置主联系人
- ✅ 联系人关系和电话管理

### 5. AI 智能问诊 🆕

#### AI 医生
- ✅ 接入 DeepSeek 大语言模型
- ✅ 智能症状分析与疾病预测
- ✅ AI 药品查询（药物相互作用、禁忌）
- ✅ AI 疾病查询（治疗方案建议）
- ✅ 对话历史记录（ChatSession / ChatMessage）
- ✅ 网络异常自动重试机制
- ✅ 未配置 API Key 时提供 Mock 建议兜底

### 6. 智能辅助

#### 药物冲突检测
- ✅ 添加药品时自动检测冲突
- ✅ 基于禁忌信息的智能匹配
- ✅ 冲突严重程度分级（high/medium/low）
- ✅ 冲突警告提示

#### 疾病查询
- ✅ 疾病库检索（支持别名搜索）
- ✅ 疾病常用药物推荐
- ✅ 用药禁忌提醒
- ✅ 通过药品反向查询相关疾病

### 7. 管理员后台 🆕

#### 仪表盘
- ✅ 实时统计（用户总数、活跃用户、在线用户、药品/疾病/计划总数）
- ✅ 今日/本周新增用户统计
- ✅ 近 30 天用户增长趋势图表
- ✅ WebSocket 实时在线用户监控

#### 用户管理
- ✅ 用户列表（分页、搜索、筛选）
- ✅ 用户信息编辑与状态管理
- ✅ 创建/禁用/删除用户（级联清理关联数据）

#### 数据管理
- ✅ 药品库管理（CRUD）
- ✅ 疾病库管理（CRUD）
- ✅ 疾病模板管理
- ✅ 慢性病记录查看

#### 系统监控
- ✅ 数据库统计信息
- ✅ 系统健康检查
- ✅ 在线用户列表

### 8. 数据统计

#### 用药统计
- ✅ 今日用药计划统计
- ✅ 已服药天数统计（基于 actual_time）
- ✅ 服药率计算
- ✅ 用药趋势分析

#### 健康仪表盘
- ✅ 用药计划总览
- ✅ 症状记录统计
- ✅ 药品种类统计
- ✅ 健康档案完整度

---

## 🚀 快速开始

### 部署方式

本项目支持两种部署方式：

1. **Docker Compose**（推荐用于快速体验和本地开发）
2. **Kubernetes + Helm**（推荐用于生产环境）

### 环境要求

#### 本地开发
- **后端**：Python 3.10+、MySQL 8.0+
- **前端**：Node.js 20.19+ 或 22.12+
- **其他**：Docker、Docker Compose、Git

#### 生产部署（Kubernetes）
- **容器编排**：Kubernetes 1.19+
- **包管理**：Helm 3.0+
- **本地测试**：kind（Kubernetes in Docker）
- **其他**：Docker、kubectl

### 快速体验（Docker Compose）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/yaoyaoji.git
cd yaoyaoji

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，配置数据库密码、JWT 密钥、DeepSeek API Key

# 3. 启动所有服务
docker compose up -d

# 4. 访问应用
open http://localhost
```

### 本地开发

#### 1. 后端配置

```bash
cd yaoyaoji_backup

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件
```

**.env 配置示例**：

```env
# 数据库配置
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/yaoyaoji
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=yaoyaoji

# JWT 配置
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# DeepSeek AI 配置（可选，不配置则使用 Mock 建议）
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 应用配置
DEBUG=True
```

#### 2. 初始化数据库

```bash
# 创建数据库
python create_database.py

# 创建表结构（也可通过 FastAPI 启动时自动创建）
python init_db.py

# （可选）导入疾病模板数据
python init_disease_templates.py

# （可选）创建管理员账号
python create_admin.py
```

#### 3. 启动后端服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

访问 API 文档：http://localhost:8000/docs

#### 4. 前端配置与启动

```bash
cd yaoyaoji_frontend/web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问应用：http://localhost:5173

---

### Kubernetes 部署（生产环境）

详细的 Kubernetes 部署指南请参考：[Kubernetes 部署文档](./KUBERNETES_DEPLOYMENT.md)

#### 快速部署到 kind 集群

```bash
# 1. 创建 kind 集群并安装 Ingress Controller
cat <<EOF | kind create cluster --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
EOF

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# 2. 构建并加载镜像
docker build -t yaoyaoji-backend:latest ./yaoyaoji_backup
docker build -t yaoyaoji-frontend:latest ./yaoyaoji_frontend/web
kind load docker-image yaoyaoji-backend:latest
kind load docker-image yaoyaoji-frontend:latest

# 3. 使用 Helm 部署
helm install yaoyaoji ./helm/yaoyaoji -f ./helm/yaoyaoji/values-dev.yaml

# 4. 添加 hosts 记录
echo "127.0.0.1 yaoyaoji.local" | sudo tee -a /etc/hosts

# 5. 访问应用
open http://yaoyaoji.local
```

更多配置选项和故障排查，请查看 [Helm Chart 文档](./helm/yaoyaoji/README.md)。

---

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| FastAPI | ≥0.104.1 | 高性能 Web 框架，自动生成 API 文档 |
| SQLAlchemy | ≥2.0.23 | ORM 框架，优雅的数据库操作 |
| PyMySQL | ≥1.1.0 | MySQL 数据库驱动 |
| Pydantic | ≥2.5.0 | 数据验证和序列化 |
| python-jose | ≥3.3.0 | JWT 令牌生成与验证 |
| Passlib | ≥1.7.4 | 密码加密（Bcrypt） |
| Uvicorn | ≥0.24.0 | ASGI 服务器 |
| OpenAI SDK | ≥1.0.0 | DeepSeek API 调用（AI 问诊） |
| HTTPX | ≥0.24.0 | 异步 HTTP 客户端 |
| Captcha | ≥0.5.0 | 图形验证码生成 |

### 前端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue 3 | ^3.5.22 | 渐进式 JavaScript 框架 |
| TypeScript | ~5.9.0 | 类型安全的 JavaScript |
| Vite | ^7.1.11 | 下一代前端构建工具 |
| Element Plus | ^2.11.5 | Vue 3 UI 组件库 |
| Vue Router | ^4.6.3 | 官方路由管理 |
| Pinia | ^3.0.3 | 官方状态管理库 |
| Axios | ^1.13.1 | HTTP 客户端 |
| ECharts | ^6.0.0 | 数据可视化图表库 |
| Day.js | ^1.11.18 | 轻量级日期处理库 |
| Marked | ^17.0.3 | Markdown 渲染（AI 回复展示） |
| lunar-javascript | ^1.7.7 | 农历日期处理 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                          │
│  Vue 3 + Element Plus + ECharts + Pinia                 │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI 后端                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ 用药管理  │ │ 健康档案  │ │ 慢性病    │ │ AI 问诊    │ │
│  │ 家庭管理  │ │ 症状记录  │ │ 疾病查询  │ │ 管理后台   │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ JWT 认证 + CORS   │  │ WebSocket 实时通信            │ │
│  └──────────────────┘  └──────────────────────────────┘ │
└──────────┬──────────────────────────────┬───────────────┘
           │                              │
┌──────────▼──────────┐    ┌──────────────▼──────────────┐
│    MySQL 8.0        │    │     DeepSeek API            │
│    数据持久化        │    │     AI 大模型服务            │
└─────────────────────┘    └─────────────────────────────┘
```

### 数据库设计

**核心表结构**（30+ 张表）：

**用药模块**：
- `users` - 用户表
- `medicines` - 药品库表
- `user_medications` - 用户药箱表
- `medication_schedules` - 用药计划表
- `medication_records` - 用药记录表
- `symptom_records` - 症状记录表
- `diseases` - 疾病库表

**家庭模块**：
- `families` - 家庭表
- `family_members` - 家庭成员表
- `emergency_contacts` - 紧急联系人

**健康档案模块**：
- `health_profiles` - 健康档案主表
- `allergy_records` - 过敏史记录
- `family_histories` - 家族病史
- `surgery_records` - 手术记录
- `checkup_reports` - 体检报告
- `vaccination_records` - 疫苗接种记录

**慢性病管理模块** 🆕：
- `chronic_diseases` - 慢性病记录
- `disease_indicators` - 疾病指标定义
- `indicator_records` - 指标记录数据
- `indicator_alerts` - 指标异常告警
- `followup_plans` - 复诊计划
- `followup_records` - 复诊记录
- `medication_adherence` - 用药依从性
- `medication_reminders` - 用药提醒
- `disease_templates` - 疾病模板
- `diet_recommendations` - 饮食建议
- `exercise_recommendations` - 运动建议
- `complication_records` - 并发症记录

**AI 模块** 🆕：
- `chat_sessions` - AI 对话会话
- `chat_messages` - AI 对话消息
- `knowledge_base` - 知识库

详细的数据库设计见：[数据库设计文档](./docs/DATABASE.md)

---

## 📂 项目结构

```
yaoyaoji/
├── yaoyaoji_backup/                # 后端项目
│   ├── app/
│   │   ├── models/                 # 数据模型
│   │   │   └── models.py          # SQLAlchemy 模型定义（30+ 模型）
│   │   ├── routers/               # 路由模块
│   │   │   ├── users.py           # 用户认证与管理
│   │   │   ├── medicines.py       # 药品库与药箱管理
│   │   │   ├── schedules.py       # 用药计划与记录
│   │   │   ├── symptoms.py        # 症状记录
│   │   │   ├── diseases.py        # 疾病查询
│   │   │   ├── family.py          # 家庭管理
│   │   │   ├── health_profile.py  # 健康档案
│   │   │   ├── upload.py          # 文件上传
│   │   │   ├── ai_doctor.py       # AI 智能问诊 🆕
│   │   │   ├── chronic_disease.py # 慢性病管理 🆕
│   │   │   ├── admin.py           # 管理员后台 🆕
│   │   │   └── websocket.py       # WebSocket 心跳 🆕
│   │   ├── schemas/               # 数据验证
│   │   │   ├── schemas.py         # Pydantic Schemas
│   │   │   └── admin_schemas.py   # 管理员 Schemas 🆕
│   │   ├── services/              # 业务逻辑
│   │   │   └── conflict_checker.py # 药物冲突检测
│   │   ├── websocket/             # WebSocket 模块 🆕
│   │   │   └── manager.py         # 连接管理器
│   │   ├── auth.py                # JWT 认证
│   │   ├── captcha.py             # 图形验证码
│   │   ├── config.py              # 配置管理
│   │   ├── database.py            # 数据库连接
│   │   └── main.py                # FastAPI 应用入口
│   ├── uploads/                   # 上传文件存储
│   │   ├── medicine_images/       # 药品包装图
│   │   ├── avatars/               # 用户头像
│   │   └── exports/               # 数据导出文件
│   ├── .env.example               # 环境变量模板
│   ├── requirements.txt           # Python 依赖
│   ├── Dockerfile                 # 后端容器镜像
│   ├── create_database.py         # 创建数据库脚本
│   ├── init_db.py                 # 初始化表结构
│   ├── init_disease_templates.py  # 导入疾病模板数据
│   ├── create_admin.py            # 创建管理员账号
│   └── run_all_migrations.py      # 数据库迁移脚本
│
├── yaoyaoji_frontend/web/         # 前端项目
│   ├── src/
│   │   ├── api/                   # API 接口封装
│   │   │   ├── config.ts          # API 配置
│   │   │   └── index.ts           # 接口定义
│   │   ├── assets/                # 静态资源
│   │   ├── router/                # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/                # 状态管理
│   │   │   ├── user.ts            # 用户状态
│   │   │   └── medication.ts      # 用药状态
│   │   ├── types/                 # TypeScript 类型
│   │   │   └── index.ts
│   │   ├── views/                 # 页面组件
│   │   │   ├── auth/
│   │   │   │   └── LoginView.vue           # 登录/注册
│   │   │   ├── medication/
│   │   │   │   ├── MedicationBoxView.vue   # 药箱
│   │   │   │   ├── ScheduleView.vue        # 用药计划
│   │   │   │   └── SymptomView.vue         # 症状记录
│   │   │   ├── admin/                       # 管理员后台 🆕
│   │   │   │   ├── AdminLayout.vue         # 后台布局
│   │   │   │   ├── AdminLoginView.vue      # 管理员登录
│   │   │   │   ├── DashboardView.vue       # 数据仪表盘
│   │   │   │   ├── UsersView.vue           # 用户管理
│   │   │   │   ├── MedicinesView.vue       # 药品管理
│   │   │   │   ├── DiseasesView.vue        # 疾病管理
│   │   │   │   ├── ChronicView.vue         # 慢性病管理
│   │   │   │   └── SystemView.vue          # 系统监控
│   │   │   ├── HomeView.vue                # 首页布局
│   │   │   ├── DashboardView.vue           # 用户仪表盘
│   │   │   ├── DoctorView.vue              # 疾病查询 + AI 问诊
│   │   │   ├── FamilyView.vue              # 家庭管理
│   │   │   ├── HealthProfileView.vue       # 健康档案
│   │   │   ├── UserProfileView.vue         # 个人中心
│   │   │   ├── ChronicDiseaseView.vue      # 慢性病列表 🆕
│   │   │   ├── ChronicDiseaseDetailView.vue # 慢性病详情 🆕
│   │   │   └── FollowupScheduleView.vue    # 复诊日程 🆕
│   │   ├── App.vue                # 根组件
│   │   └── main.ts                # 应用入口
│   ├── package.json               # Node.js 依赖
│   ├── vite.config.ts             # Vite 配置
│   └── tsconfig.json              # TypeScript 配置
│
├── helm/yaoyaoji/                 # Helm Chart
│   ├── Chart.yaml
│   ├── values.yaml                # 默认配置
│   ├── values-dev.yaml            # 开发环境
│   ├── values-prod.yaml           # 生产环境
│   ├── values-ec2.yaml            # EC2 环境
│   └── templates/                 # K8s 资源模板
│
├── docker-compose.yml             # Docker Compose 配置
├── .env.example                   # Docker 环境变量模板
└── scripts/
    └── setup-ec2-kind.sh          # EC2 kind 集群搭建脚本
```

---

## 📚 文档

- [后端功能文档](./docs/BACKEND.md) - 详细的后端 API 说明
- [前端功能文档](./docs/FRONTEND.md) - 详细的前端页面与交互说明
- [Kubernetes 部署指南](./KUBERNETES_DEPLOYMENT.md) - K8s 集群部署完整指南
- [Helm Chart 文档](./helm/yaoyaoji/README.md) - Helm Chart 配置和使用说明
- [数据库设计](./docs/DATABASE.md) - 数据表结构与关系

---

## 🔐 安全性

- ✅ JWT 身份认证，有效期 24 小时
- ✅ Bcrypt 密码加密存储
- ✅ 图形验证码（登录/注册）
- ✅ CORS 跨域保护
- ✅ SQL 注入防护（ORM 参数化查询）
- ✅ 文件上传类型和大小限制
- ✅ 用户数据权限隔离
- ✅ 管理员权限独立认证

---

## 🛠️ 开发指南

### 本地开发

1. 后端热重载已启用（`--reload` 参数）
2. 前端使用 Vite HMR，修改即时生效
3. API 文档实时更新：http://localhost:8000/docs
4. 启动时自动检测并添加缺失数据库列（自动迁移）

### 代码规范

- **Python**：遵循 PEP 8，使用类型注解
- **TypeScript**：启用严格模式，使用 ESLint
- **Vue**：组合式 API（Composition API）+ `<script setup>`

### 提交规范

```
feat: 新功能
fix: 修复 Bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建/工具配置
```

---

## 🚧 待开发功能

- [ ] 用药提醒推送（Web Push Notifications）
- [ ] 数据导出功能（PDF/Excel）
- [ ] 多语言支持
- [ ] 移动端适配优化
- [ ] 深色模式支持
- [ ] AI 问诊流式输出（SSE）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE)

---

## 👨‍💻 作者

**药药记开发团队**

如有问题或建议，欢迎通过 Issue 联系我们。

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [Element Plus](https://element-plus.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [ECharts](https://echarts.apache.org/)
- [DeepSeek](https://www.deepseek.com/)

---

<div align="center">

**药药记 · 守护您的每一份健康**

Made with ❤️ by 药药记团队

</div>