# 后端功能文档

## 目录

- [技术栈](#技术栈)
- [架构设计](#架构设计)
- [API 接口](#api-接口)
  - [用户认证](#1-用户认证)
  - [药品管理](#2-药品管理)
  - [用户药箱](#3-用户药箱)
  - [用药计划](#4-用药计划)
  - [用药记录](#5-用药记录)
  - [症状记录](#6-症状记录)
  - [疾病查询](#7-疾病查询)
  - [家庭管理](#8-家庭管理)
  - [健康档案](#9-健康档案)
  - [文件上传](#10-文件上传)
- [数据模型](#数据模型)
- [业务逻辑](#业务逻辑)

---

## 技术栈

### 核心框架
- **FastAPI 0.104.1** - 现代化、高性能的 Python Web 框架
- **SQLAlchemy 2.0.23** - 强大的 ORM 框架
- **Pydantic 2.5.0** - 数据验证和序列化

### 数据库
- **MySQL 8.0+** - 关系型数据库
- **PyMySQL 1.1.0** - MySQL 数据库驱动

### 认证安全
- **python-jose 3.3.0** - JWT 令牌处理
- **Passlib 1.7.4** - 密码加密（Bcrypt）

### 服务器
- **Uvicorn 0.24.0** - ASGI 服务器，支持热重载

---

## 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│         API 路由层 (Routers)         │
│  - 请求处理                         │
│  - 参数验证                         │
│  - 响应格式化                       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      业务逻辑层 (Services)           │
│  - 药物冲突检测                     │
│  - 数据统计                         │
│  - 业务规则                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│       数据访问层 (Models)            │
│  - ORM 模型定义                     │
│  - 数据库操作                       │
│  - 关系映射                         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│           MySQL 数据库               │
└─────────────────────────────────────┘
```

### 目录结构

```
app/
├── models/
│   └── models.py              # SQLAlchemy 模型定义
├── routers/
│   ├── users.py               # 用户认证与管理
│   ├── medicines.py           # 药品库与药箱管理
│   ├── schedules.py           # 用药计划与记录
│   ├── symptoms.py            # 症状记录
│   ├── diseases.py            # 疾病查询
│   ├── family.py              # 家庭管理
│   ├── health_profile.py      # 健康档案
│   └── upload.py              # 文件上传
├── schemas/
│   └── schemas.py             # Pydantic 数据验证
├── services/
│   └── conflict_checker.py    # 药物冲突检测服务
├── auth.py                    # JWT 认证
├── config.py                  # 配置管理
├── database.py                # 数据库连接
└── main.py                    # FastAPI 应用入口
```

---

## API 接口

### 1. 用户认证

#### 1.1 用户注册

**接口**: `POST /api/auth/register`

**请求体**:
```json
{
  "username": "zhangsan",
  "password": "password123",
  "email": "zhangsan@example.com"
}
```

**响应**:
```json
{
  "id": 1,
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "created_at": "2024-11-06T10:00:00"
}
```

**说明**:
- 用户名支持中文、英文、数字、下划线，至少 2 个字符
- 密码至少 6 个字符
- 邮箱可选

#### 1.2 用户登录

**接口**: `POST /api/auth/login`

**请求体** (Form Data):
```
username=zhangsan
password=password123
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**说明**:
- 使用 OAuth2 密码流
- Token 有效期 24 小时

#### 1.3 获取当前用户信息

**接口**: `GET /api/users/me`

**认证**: Bearer Token

**响应**:
```json
{
  "id": 1,
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "created_at": "2024-11-06T10:00:00"
}
```

#### 1.4 修改密码

**接口**: `PATCH /api/users/change-password`

**请求参数**:
- `old_password`: 原密码
- `new_password`: 新密码

---

### 2. 药品管理

#### 2.1 创建药品

**接口**: `POST /api/medicines/`

**请求体**:
```json
{
  "name": "阿莫西林胶囊",
  "generic_name": "阿莫西林",
  "manufacturer": "某某制药",
  "ingredients": "阿莫西林",
  "efficacy": "用于敏感菌所致的各种感染",
  "contraindications": "对青霉素过敏者禁用",
  "side_effects": "可能出现皮疹、腹泻等",
  "image_url": "/uploads/medicine_images/xxx.jpg"
}
```

**响应**: 返回创建的药品信息

#### 2.2 查询药品列表

**接口**: `GET /api/medicines/`

**查询参数**:
- `search`: 模糊搜索（药品名称、厂家、成分、功效等）
- `skip`: 跳过记录数（分页）
- `limit`: 返回记录数（默认 100）

**响应**:
```json
[
  {
    "id": 1,
    "name": "阿莫西林胶囊",
    "generic_name": "阿莫西林",
    "manufacturer": "某某制药",
    "contraindications": "对青霉素过敏者禁用",
    "image_url": "/uploads/medicine_images/xxx.jpg",
    "created_at": "2024-11-06T10:00:00"
  }
]
```

#### 2.3 获取药品详情

**接口**: `GET /api/medicines/{medicine_id}`

**响应**: 返回完整的药品信息

---

### 3. 用户药箱

#### 3.1 添加药品到药箱

**接口**: `POST /api/user-medications/`

**请求体**:
```json
{
  "medicine_id": 1,
  "custom_name": "我的阿莫西林",
  "notes": "饭后服用"
}
```

**功能**:
- 自动检测药物冲突
- 高危冲突会阻止添加
- 中低风险冲突会警告但允许添加

**响应**: 返回用户药箱条目（包含药品详情）

#### 3.2 获取我的药箱

**接口**: `GET /api/user-medications/`

**查询参数**:
- `status_filter`: 状态过滤（active/inactive，默认 active）

**响应**:
```json
[
  {
    "id": 1,
    "user_id": 1,
    "medicine_id": 1,
    "custom_name": "我的阿莫西林",
    "notes": "饭后服用",
    "status": "active",
    "medicine": {
      "id": 1,
      "name": "阿莫西林胶囊",
      "manufacturer": "某某制药",
      "image_url": "/uploads/medicine_images/xxx.jpg"
    }
  }
]
```

#### 3.3 更新药箱中的药品

**接口**: `PATCH /api/user-medications/{user_med_id}`

**请求体**:
```json
{
  "custom_name": "新名称",
  "notes": "新备注",
  "status": "inactive",
  "medicine_name": "更新药品名称",
  "contraindications": "更新禁忌信息",
  "manufacturer": "更新厂家",
  "image_url": "/uploads/medicine_images/new.jpg"
}
```

**说明**:
- 支持更新用户药箱字段（custom_name, notes, status）
- 支持更新关联的药品信息（name, contraindications, manufacturer, image_url）

#### 3.4 从药箱移除药品

**接口**: `DELETE /api/user-medications/{user_med_id}`

**说明**: 软删除，将状态标记为 inactive

---

### 4. 用药计划

#### 4.1 创建用药计划

**接口**: `POST /api/schedules/`

**请求体**:
```json
{
  "user_medication_id": 1,
  "scheduled_times": ["08:00:00", "20:00:00"],
  "dose": "2片",
  "frequency": "twice_daily",
  "start_date": "2024-11-06",
  "end_date": "2024-11-20"
}
```

**频率枚举**:
- `once_daily`: 每日 1 次
- `twice_daily`: 每日 2 次
- `three_times_daily`: 每日 3 次
- `four_times_daily`: 每日 4 次

**验证规则**:
- `scheduled_times` 数量必须与 `frequency` 匹配
- `end_date` 必须晚于 `start_date`

#### 4.2 获取我的用药计划

**接口**: `GET /api/schedules/`

**查询参数**:
- `active_only`: 仅返回活跃计划（默认 true）

**响应**:
```json
[
  {
    "id": 1,
    "user_medication_id": 1,
    "scheduled_times": ["08:00:00", "20:00:00"],
    "dose": "2片",
    "frequency": "twice_daily",
    "start_date": "2024-11-06",
    "end_date": "2024-11-20",
    "user_medication": {
      "id": 1,
      "medicine": {
        "name": "阿莫西林胶囊",
        "image_url": "/uploads/medicine_images/xxx.jpg"
      }
    }
  }
]
```

#### 4.3 更新用药计划

**接口**: `PATCH /api/schedules/{schedule_id}`

**请求体**: 与创建计划相同

#### 4.4 删除用药计划

**接口**: `DELETE /api/schedules/{schedule_id}`

---

### 5. 用药记录

#### 5.1 创建用药记录

**接口**: `POST /api/records/`

**请求体**:
```json
{
  "schedule_id": 1,
  "scheduled_time": "2024-11-06T08:00:00"
}
```

**说明**: 默认状态为 `pending`

#### 5.2 获取我的用药记录

**接口**: `GET /api/records/`

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `status_filter`: 状态过滤（pending/taken/skipped/delayed）

**响应**:
```json
[
  {
    "id": 1,
    "schedule_id": 1,
    "scheduled_time": "2024-11-06T08:00:00",
    "actual_time": "2024-11-06T08:05:00",
    "status": "taken",
    "skip_reason": null,
    "schedule": {
      "dose": "2片",
      "user_medication": {
        "medicine": {
          "name": "阿莫西林胶囊"
        }
      }
    }
  }
]
```

#### 5.3 获取今日用药记录

**接口**: `GET /api/records/today`

**说明**: 返回今天的所有用药记录

#### 5.4 更新用药记录

**接口**: `PATCH /api/records/{record_id}`

**请求体**:
```json
{
  "status": "taken",
  "actual_time": "2024-11-06T08:05:00",
  "skip_reason": null
}
```

**状态枚举**:
- `pending`: 待服用
- `taken`: 已服用
- `skipped`: 跳过
- `delayed`: 延迟

**自动设置**:
- 标记为 `taken` 且未指定 `actual_time` 时，自动设为当前时间

---

### 6. 症状记录

#### 6.1 创建症状记录

**接口**: `POST /api/symptoms/`

**请求体**:
```json
{
  "symptom_emoji": "🤒",
  "symptom_text": "头痛发烧",
  "intensity": 3
}
```

**强度等级**: 1-5（1 最轻，5 最严重）

#### 6.2 获取我的症状记录

**接口**: `GET /api/symptoms/`

**查询参数**:
- `start_date`: 开始日期
- `end_date`: 结束日期
- `min_intensity`: 最低强度过滤

#### 6.3 获取今日症状

**接口**: `GET /api/symptoms/today`

#### 6.4 获取症状时间轴

**接口**: `GET /api/symptoms/timeline`

**查询参数**:
- `days`: 天数（默认 7）

**说明**: 返回最近 N 天的症状记录，按时间升序排列

#### 6.5 更新/删除症状记录

**接口**: 
- `PATCH /api/symptoms/{symptom_id}`
- `DELETE /api/symptoms/{symptom_id}`

---

### 7. 疾病查询

#### 7.1 疾病列表查询

**接口**: `GET /api/diseases/`

**查询参数**:
- `search`: 按疾病名称/别名/简介/推荐药物模糊搜索
- `medicine_name`: 按药品名称反向搜索相关疾病

**响应**:
```json
[
  {
    "id": 1,
    "name": "感冒",
    "aliases": "上呼吸道感染,普通感冒",
    "description": "病毒感染引起的上呼吸道炎症",
    "recommended": "阿莫西林,感冒灵",
    "avoid": "抗生素滥用",
    "created_at": "2024-11-06T10:00:00"
  }
]
```

**使用场景**:
1. 用户搜索疾病名称，查看常用药物
2. 输入药品名称，查看该药品适用的疾病

---

### 8. 家庭管理

#### 8.1 获取我的家庭信息

**接口**: `GET /api/family/my-family`

**响应**:
```json
{
  "id": 1,
  "name": "张三的家庭",
  "created_by": 1,
  "invite_code": "ABC12345",
  "created_at": "2024-11-06T10:00:00",
  "member_count": 4
}
```

#### 8.2 创建家庭

**接口**: `POST /api/family/create-family`

**请求体**:
```json
{
  "name": "张三的家庭"
}
```

**功能**:
- 自动生成唯一 8 位邀请码
- 创建者自动加入家庭并设为管理员

#### 8.3 加入家庭

**接口**: `POST /api/family/join-family`

**请求体**:
```json
{
  "invite_code": "ABC12345"
}
```

**说明**: 通过邀请码加入家庭，加入后自动设为普通成员

#### 8.4 退出/解散家庭

**接口**: `POST /api/family/leave-family`

**逻辑**:
- 普通成员退出：仅移除自己的家庭关联
- 管理员退出：解散家庭，清理所有成员关联

#### 8.5 更新家庭信息

**接口**: `PATCH /api/family/update-family`

**权限**: 仅家庭创建者可修改

#### 8.6 获取家庭成员列表

**接口**: `GET /api/family/members`

**响应**:
```json
[
  {
    "id": 1,
    "family_id": 1,
    "guardian_id": 1,
    "name": "张三",
    "role": "admin",
    "birth_date": "1980-01-01",
    "age": 44,
    "notes": "爸爸"
  },
  {
    "id": 2,
    "name": "李四",
    "role": "spouse",
    "age": 42,
    "notes": "妈妈"
  }
]
```

**角色枚举**:
- `parent`: 家长
- `child`: 儿童
- `elderly`: 老人
- `spouse`: 配偶
- `other`: 其他

#### 8.7 编辑家庭成员

**接口**: `PATCH /api/family/members/{member_id}`

**请求体**:
```json
{
  "role": "elderly",
  "birth_date": "1950-05-20",
  "notes": "爷爷"
}
```

#### 8.8 移除家庭成员

**接口**: `DELETE /api/family/members/{member_id}`

**说明**: 不能移除自己，需使用退出家庭功能

#### 8.9 获取家庭成员用药信息

**接口**: `GET /api/family/members-medication`

**响应**:
```json
[
  {
    "user_id": 2,
    "username": "lisi",
    "real_name": "李四",
    "relation": "spouse",
    "medication_count": 3,
    "today_schedules": 2
  }
]
```

**说明**: 排除自己，仅返回其他家庭成员

#### 8.10 切换到家庭成员账号

**接口**: `POST /api/family/switch-account`

**请求体**:
```json
{
  "target_user_id": 2
}
```

**响应**:
```json
{
  "access_token": "new_token_here",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "username": "lisi",
    "real_name": "李四",
    "relation_to_admin": "spouse",
    "email": "lisi@example.com"
  }
}
```

**说明**: 
- 仅允许切换到同一家庭的成员
- 返回新的 JWT Token
- 前端需更新 localStorage 并刷新页面

#### 8.11 紧急联系人管理

**接口**:
- `GET /api/family/emergency-contacts` - 获取列表
- `POST /api/family/emergency-contacts` - 添加联系人
- `PATCH /api/family/emergency-contacts/{contact_id}` - 更新
- `DELETE /api/family/emergency-contacts/{contact_id}` - 删除

**请求体示例**:
```json
{
  "name": "王医生",
  "relationship": "家庭医生",
  "phone": "13800138000",
  "is_primary": true
}
```

---

### 9. 健康档案

#### 9.1 获取我的健康档案

**接口**: `GET /api/health-profile/`

**响应**:
```json
{
  "id": 1,
  "user_id": 1,
  "real_name": "张三",
  "blood_type": "A+",
  "height": 175,
  "weight": 70,
  "systolic_pressure": 120,
  "diastolic_pressure": 80,
  "heart_rate": 72,
  "blood_glucose": "5.5",
  "temperature": "36.5",
  "chronic_diseases": "高血压",
  "created_at": "2024-11-06T10:00:00",
  "updated_at": "2024-11-06T12:00:00"
}
```

**说明**: 如果不存在，自动创建空档案

#### 9.2 创建/更新健康档案

**接口**: `POST /api/health-profile/`

**请求体**: 所有字段均可选

#### 9.3 过敏史管理

**接口**:
- `GET /api/health-profile/allergies` - 获取列表
- `POST /api/health-profile/allergies` - 添加记录
- `PATCH /api/health-profile/allergies/{record_id}` - 更新
- `DELETE /api/health-profile/allergies/{record_id}` - 删除

**请求体示例**:
```json
{
  "allergen": "青霉素",
  "allergen_type": "药物",
  "reaction": "皮疹、荨麻疹",
  "severity": "严重",
  "discovered_date": "2020-03-15",
  "notes": "注意避免使用青霉素类药物"
}
```

#### 9.4 家族病史管理

**接口**:
- `GET /api/health-profile/family-history`
- `POST /api/health-profile/family-history`
- `PATCH /api/health-profile/family-history/{record_id}`
- `DELETE /api/health-profile/family-history/{record_id}`

**请求体示例**:
```json
{
  "relative": "父亲",
  "disease": "高血压",
  "onset_age": 50,
  "notes": "需定期监测血压"
}
```

#### 9.5 手术记录管理

**接口**:
- `GET /api/health-profile/surgeries`
- `POST /api/health-profile/surgeries`
- `PATCH /api/health-profile/surgeries/{record_id}`
- `DELETE /api/health-profile/surgeries/{record_id}`

**请求体示例**:
```json
{
  "surgery_name": "阑尾切除术",
  "surgery_date": "2018-06-20",
  "hospital": "某某医院",
  "doctor": "李医生",
  "notes": "恢复良好"
}
```

#### 9.6 体检报告管理

**接口**:
- `GET /api/health-profile/checkups`
- `POST /api/health-profile/checkups`
- `PATCH /api/health-profile/checkups/{record_id}`
- `DELETE /api/health-profile/checkups/{record_id}`

**请求体示例**:
```json
{
  "checkup_date": "2024-10-01",
  "checkup_type": "年度体检",
  "hospital": "某某体检中心",
  "summary": "各项指标正常",
  "file_url": "/uploads/reports/xxx.pdf"
}
```

#### 9.7 疫苗接种记录管理

**接口**:
- `GET /api/health-profile/vaccinations`
- `POST /api/health-profile/vaccinations`
- `PATCH /api/health-profile/vaccinations/{record_id}`
- `DELETE /api/health-profile/vaccinations/{record_id}`

**请求体示例**:
```json
{
  "vaccine_name": "流感疫苗",
  "vaccination_date": "2024-09-15",
  "hospital": "社区卫生服务中心",
  "batch_number": "20240915001",
  "next_dose_date": "2025-09-15",
  "notes": "每年接种"
}
```

---

### 10. 文件上传

#### 10.1 上传药品包装图

**接口**: `POST /api/upload/medicine-image`

**请求**: `multipart/form-data`

**支持格式**: JPG, JPEG, PNG, GIF, WebP

**最大大小**: 5MB

**响应**:
```json
{
  "message": "上传成功",
  "filename": "medicine_20241106_120530_abc12345.jpg",
  "path": "/uploads/medicine_images/medicine_20241106_120530_abc12345.jpg",
  "url": "/uploads/medicine_images/medicine_20241106_120530_abc12345.jpg"
}
```

**存储位置**: `uploads/medicine_images/`

**文件命名规则**: `medicine_{时间戳}_{8位随机ID}{扩展名}`

#### 10.2 删除药品包装图

**接口**: `DELETE /api/upload/medicine-image/{filename}`

**说明**: 物理删除文件

---

## 数据模型

### 核心关系

```
User (用户)
  ├── UserMedication (药箱)
  │     ├── Medicine (药品库)
  │     └── MedicationSchedule (用药计划)
  │           └── MedicationRecord (用药记录)
  ├── SymptomRecord (症状记录)
  ├── HealthProfile (健康档案)
  │     ├── AllergyRecord (过敏史)
  │     ├── FamilyHistory (家族病史)
  │     ├── SurgeryRecord (手术记录)
  │     ├── CheckupReport (体检报告)
  │     └── VaccinationRecord (疫苗记录)
  └── Family (家庭)
        ├── FamilyMember (家庭成员)
        └── EmergencyContact (紧急联系人)
```

### 字段说明

#### User 表
- `id`: 主键
- `username`: 用户名（唯一）
- `password_hash`: 密码哈希（Bcrypt）
- `email`: 邮箱
- `family_id`: 所属家庭 ID
- `is_family_admin`: 是否家庭管理员
- `relation_to_admin`: 与管理员的关系

#### UserMedication 表
- `id`: 主键
- `user_id`: 用户 ID（外键）
- `medicine_id`: 药品 ID（外键）
- `custom_name`: 自定义名称
- `notes`: 备注
- `status`: 状态（active/inactive）

#### MedicationSchedule 表
- `id`: 主键
- `user_medication_id`: 用户药品 ID（外键）
- `scheduled_times`: 计划用药时间列表（JSON）
- `dose`: 剂量
- `frequency`: 频率枚举
- `start_date`: 开始日期
- `end_date`: 结束日期

#### MedicationRecord 表
- `id`: 主键
- `schedule_id`: 计划 ID（外键）
- `scheduled_time`: 计划时间
- `actual_time`: 实际时间
- `status`: 状态枚举
- `skip_reason`: 跳过原因

---

## 业务逻辑

### 1. 药物冲突检测

**实现位置**: `app/services/conflict_checker.py`

**检测时机**: 添加药品到药箱时

**检测逻辑**:
1. 获取用户当前所有活跃药品
2. 将新药品加入检测列表
3. 两两检查禁忌信息
4. 文本匹配检测（简化实现）
5. 根据严重程度分级

**冲突等级**:
- **high**: 禁忌信息中明确提到对方药品 → 阻止添加
- **medium**: 包含常见危险组合关键词 → 警告但允许
- **low**: 其他潜在风险 → 提示

**改进方向**:
- 接入专业药品相互作用数据库
- 基于药品成分进行精准匹配
- 考虑剂量、用药时间等因素

### 2. 用药统计

**已服药天数统计**:
- 基于 `MedicationRecord.actual_time` 字段
- 提取日期部分（不含时间）
- 使用 Set 去重
- 统计唯一日期数量

**服药率计算**:
```
服药率 = (已服用次数 / 计划总次数) × 100%
```

### 3. 家庭成员权限

**数据隔离**:
- 所有接口通过 `current_user` 进行数据过滤
- 用户仅能访问自己的数据或同一家庭成员的数据

**切换账号机制**:
1. 验证目标用户是否在同一家庭
2. 生成新的 JWT Token（sub 为目标用户的 username）
3. 返回新 Token 和用户信息
4. 前端更新存储并刷新页面

### 4. 数据验证

**Pydantic Validators**:
- 用户名格式验证（中文、英文、数字、下划线）
- 用药时间数量与频率匹配验证
- 结束日期晚于开始日期验证
- 强度范围验证（1-5）

### 5. 文件管理

**上传流程**:
1. 检查文件扩展名
2. 读取文件内容检查大小
3. 生成唯一文件名（时间戳 + 随机 ID）
4. 保存到指定目录
5. 返回访问路径

**静态文件服务**:
```python
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

访问路径: `http://localhost:8000/uploads/medicine_images/xxx.jpg`

---

## API 文档

启动后端服务后，访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 错误处理

### HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证
- `403 Forbidden`: 无权限
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

```json
{
  "detail": "错误描述信息"
}
```

---

## 性能优化

- ✅ 数据库连接池（pool_pre_ping, pool_recycle）
- ✅ 关联查询预加载（joinedload）
- ✅ 索引优化（username, invite_code 等字段）
- ✅ 分页查询（skip, limit）

---

## 安全措施

- ✅ JWT Token 认证，有效期 24 小时
- ✅ Bcrypt 密码加密存储
- ✅ CORS 跨域保护
- ✅ SQL 注入防护（ORM 参数化查询）
- ✅ 文件上传类型和大小限制
- ✅ 用户数据权限隔离（通过 current_user 过滤）

---

## 部署建议

### 生产环境配置

1. **修改 .env 配置**:
   - 使用强密码
   - 修改 SECRET_KEY
   - 关闭 DEBUG 模式
   - 限制 CORS 允许的域名

2. **数据库优化**:
   - 定期备份
   - 配置主从复制
   - 监控慢查询

3. **使用 Nginx 反向代理**:
   - 静态文件缓存
   - HTTPS 配置
   - 负载均衡

4. **使用 Gunicorn 运行**:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 日志与监控

- ✅ SQLAlchemy echo 模式（开发环境）
- 建议集成：
  - Sentry 错误追踪
  - Prometheus 性能监控
  - ELK 日志分析

---

## 测试

### 运行测试（待实现）

```bash
pytest tests/
```

### 测试覆盖（建议）

- 单元测试：业务逻辑、数据验证
- 集成测试：API 端点、数据库操作
- 端到端测试：用户完整流程

---

## 常见问题

### Q1: 如何重置数据库？

```bash
python init_db.py --drop  # 删除所有表
python init_db.py         # 重新创建表
```

### Q2: 如何添加初始数据？

创建 `seed_data.py` 脚本，手动插入数据。

### Q3: Token 过期怎么办？

前端检测 401 错误，跳转到登录页面重新登录。

---

**更新日期**: 2024-11-06
