# 实施计划：慢性病管理模块

## 概述

本实施计划将慢性病管理模块的设计转化为可执行的开发任务。实施将基于现有的ChronicDisease基础架构，通过扩展数据模型、API接口和前端组件来实现三种预设慢性病类型的专业化管理功能。

## 任务列表

- [ ] 1. 数据库模型扩展和迁移
  - [ ] 1.1 创建疾病模板表（DiseaseTemplate）
    - 在 yaoyaoji_backup/app/models/models.py 中添加 DiseaseTemplate 模型
    - 包含 disease_type, display_name, icd10_code, default_indicators 字段
    - _需求：1.1_
  
  - [ ] 1.2 创建饮食建议表（DietRecommendation）
    - 在 models.py 中添加 DietRecommendation 模型和 MealType 枚举
    - 包含 disease_type, meal_type, title, content, food_suggestions 字段
    - _需求：3.3, 4.4_
  
  - [ ] 1.3 创建并发症记录表（ComplicationRecord）
    - 在 models.py 中添加 ComplicationRecord 模型和 ComplicationSeverity 枚举
    - 包含 disease_id, complication_type, severity, discovered_date 字段
    - _需求：4.3_
  
  - [ ] 1.4 创建运动建议表（ExerciseRecommendation）
    - 在 models.py 中添加 ExerciseRecommendation 模型
    - 包含 disease_type, title, exercise_type, duration_minutes 字段
    - _需求：4.7_
  
  - [ ] 1.5 创建用药提醒表（MedicationReminder）
    - 在 models.py 中添加 MedicationReminder 模型和 ReminderStatus 枚举
    - 包含 user_id, disease_id, reminder_time, reminder_days 字段
    - _需求：2.4_
  
  - [ ] 1.6 创建数据库迁移脚本
    - 使用 Alembic 创建迁移脚本
    - 运行 `alembic revision --autogenerate -m "Add chronic disease management tables"`
    - _需求：7.1_

- [ ] 2. 初始化疾病模板和建议数据
  - [ ] 2.1 创建疾病模板初始化脚本
    - 创建 yaoyaoji_backup/init_disease_templates.py
    - 定义三种疾病类型的模板数据（高血压、高血脂、糖尿病）
    - 包含每种疾病的默认指标配置
    - _需求：1.1_
  
  - [ ] 2.2 创建饮食建议初始化数据
    - 在初始化脚本中添加饮食建议数据
    - 为高血脂添加通用饮食建议
    - 为糖尿病添加早餐、午餐、晚餐建议
    - _需求：3.3, 4.4_
  
  - [ ] 2.3 创建运动建议初始化数据
    - 在初始化脚本中添加运动建议数据
    - 为糖尿病添加有氧运动、力量训练等建议
    - _需求：4.7_


- [ ] 3. 后端API接口实现 - 疾病模板管理
  - [ ] 3.1 实现获取疾病模板列表接口
    - 在 yaoyaoji_backup/app/routers/chronic_disease.py 中添加 GET /api/disease-templates
    - 返回所有可用的疾病类型模板
    - _需求：1.1_
  
  - [ ] 3.2 编写疾病模板接口的属性测试
    - **属性 1：疾病类型限制**
    - **验证需求：1.1**
  
  - [ ] 3.3 实现基于模板创建慢性病记录接口
    - 添加 POST /api/chronic-diseases/from-template
    - 根据选择的模板自动创建疾病记录和指标配置
    - 实现数据验证和事务处理
    - _需求：1.1, 1.2_
  
  - [ ] 3.4 编写创建接口的属性测试
    - **属性 2：必填字段验证**
    - **属性 3：数据持久化往返**
    - **验证需求：1.2, 2.1, 3.1, 4.1**

- [ ] 4. 后端API接口实现 - 指标记录管理
  - [ ] 4.1 实现批量记录指标接口
    - 添加 POST /api/chronic-diseases/{disease_id}/indicators/batch-record
    - 支持一次提交多条指标记录（特别是血糖多次测量）
    - 实现范围检查和自动预警生成
    - _需求：2.1, 2.2, 4.1, 4.2_
  
  - [ ] 4.2 编写指标记录的属性测试
    - **属性 6：范围检查和警告生成**
    - **属性 8：同日多次记录支持**
    - **验证需求：2.2, 3.2, 4.2**
  
  - [ ] 4.3 优化指标记录查询接口
    - 修改现有的 GET /api/chronic-diseases/{disease_id}/indicators/records
    - 添加时间倒序排序
    - 添加分页支持
    - _需求：2.3_
  
  - [ ] 4.4 编写查询接口的属性测试
    - **属性 7：时间排序一致性**
    - **验证需求：2.3**

- [ ] 5. 后端API接口实现 - 饮食建议
  - [ ] 5.1 实现获取饮食建议接口
    - 添加 GET /api/diet-recommendations
    - 支持按疾病类型和餐次筛选
    - _需求：3.3, 4.4_
  
  - [ ] 5.2 实现个性化饮食建议接口
    - 添加 GET /api/chronic-diseases/{disease_id}/personalized-diet
    - 根据患者的最新指标数据提供个性化建议
    - 糖尿病返回三餐建议
    - _需求：3.3, 4.4_
  
  - [ ] 5.3 编写饮食建议的属性测试
    - **属性 9：饮食建议完整性**
    - **验证需求：4.4**

- [ ] 6. 后端API接口实现 - 并发症管理
  - [ ] 6.1 实现记录并发症接口
    - 添加 POST /api/chronic-diseases/{disease_id}/complications
    - 验证并保存并发症信息
    - _需求：4.3_
  
  - [ ] 6.2 实现获取并发症列表接口
    - 添加 GET /api/chronic-diseases/{disease_id}/complications
    - 支持按严重程度和解决状态筛选
    - _需求：4.3_
  
  - [ ] 6.3 实现更新并发症状态接口
    - 添加 PUT /api/complications/{complication_id}
    - 支持更新严重程度和解决状态
    - _需求：4.3_
  
  - [ ] 6.4 编写并发症管理的单元测试
    - 测试创建、查询、更新并发症的各种场景
    - _需求：4.3_

- [ ] 7. 后端API接口实现 - 运动建议
  - [ ] 7.1 实现获取运动建议接口
    - 添加 GET /api/exercise-recommendations
    - 支持按疾病类型筛选
    - _需求：4.7_
  
  - [ ] 7.2 实现个性化运动建议接口
    - 添加 GET /api/chronic-diseases/{disease_id}/personalized-exercise
    - 根据患者的血糖控制情况提供建议
    - _需求：4.7_

- [ ] 8. 后端API接口实现 - 用药提醒
  - [ ] 8.1 实现创建用药提醒接口
    - 添加 POST /api/medication-reminders
    - 验证提醒时间和重复规则
    - _需求：2.4_
  
  - [ ] 8.2 实现获取用药提醒列表接口
    - 添加 GET /api/medication-reminders
    - 支持按疾病和状态筛选
    - _需求：2.4_
  
  - [ ] 8.3 实现更新提醒状态接口
    - 添加 PUT /api/medication-reminders/{reminder_id}
    - 支持暂停、恢复、完成提醒
    - _需求：2.4_


- [ ] 9. 后端API接口实现 - 搜索和筛选
  - [ ] 9.1 增强慢性病列表查询接口
    - 修改现有的 GET /api/chronic-diseases
    - 添加搜索关键词参数（search）
    - 添加疾病类型筛选参数（disease_type）
    - 添加日期范围筛选参数（start_date, end_date）
    - _需求：5.1, 5.2, 5.3_
  
  - [ ] 9.2 编写搜索和筛选的属性测试
    - **属性 10：搜索结果匹配性**
    - **属性 11：类型筛选准确性**
    - **属性 12：日期范围筛选准确性**
    - **属性 13：筛选重置完整性**
    - **验证需求：5.1, 5.2, 5.3, 5.4**

- [ ] 10. 后端API接口实现 - 数据导出
  - [ ] 10.1 实现导出任务创建接口
    - 添加 POST /api/chronic-diseases/export
    - 创建异步导出任务
    - 支持CSV和PDF格式
    - _需求：6.1, 6.2, 6.3_
  
  - [ ] 10.2 实现导出任务状态查询接口
    - 添加 GET /api/export-tasks/{task_id}
    - 返回任务状态和下载链接
    - _需求：6.4_
  
  - [ ] 10.3 实现文件下载接口
    - 添加 GET /api/downloads/{filename}
    - 验证文件访问权限
    - 设置文件过期时间
    - _需求：6.4_
  
  - [ ] 10.4 实现CSV导出逻辑
    - 创建 yaoyaoji_backup/app/services/export_service.py
    - 实现将慢性病数据导出为CSV格式
    - _需求：6.3_
  
  - [ ] 10.5 编写数据导出的属性测试
    - **属性 14：导出数据完整性**
    - **属性 15：导出任务状态一致性**
    - **验证需求：6.3, 6.4**

- [ ] 11. 后端服务层实现 - 权限和安全
  - [ ] 11.1 实现数据访问权限检查中间件
    - 在 yaoyaoji_backup/app/auth.py 中添加权限检查函数
    - 验证用户只能访问自己的慢性病数据
    - _需求：10.1, 10.2_
  
  - [ ] 11.2 编写权限检查的属性测试
    - **属性 4：查询完整性**
    - **属性 21：权限隔离**
    - **验证需求：1.3, 10.1, 10.2**
  
  - [ ] 11.3 实现操作审计日志
    - 创建 yaoyaoji_backup/app/services/audit_service.py
    - 记录所有数据修改操作
    - _需求：7.3, 10.5_
  
  - [ ] 11.4 编写审计日志的属性测试
    - **属性 22：操作日志完整性**
    - **验证需求：7.3, 10.5**

- [ ] 12. 后端服务层实现 - 数据完整性
  - [ ] 12.1 实现级联删除逻辑
    - 在删除慢性病记录时自动删除关联数据
    - 使用软删除机制
    - _需求：1.5, 7.4_
  
  - [ ] 12.2 编写级联删除的属性测试
    - **属性 5：级联删除完整性**
    - **属性 18：软删除一致性**
    - **验证需求：1.5, 7.4**
  
  - [ ] 12.3 实现时间戳自动管理
    - 确保所有模型的 created_at 和 updated_at 正确设置
    - _需求：7.1_
  
  - [ ] 12.4 编写时间戳管理的属性测试
    - **属性 16：时间戳自动设置**
    - **验证需求：7.1**
  
  - [ ] 12.5 实现事务管理和错误恢复
    - 在所有数据修改操作中使用数据库事务
    - 实现错误时的自动回滚
    - _需求：7.2, 7.5_
  
  - [ ] 12.6 编写事务管理的属性测试
    - **属性 17：事务原子性**
    - **验证需求：7.2, 7.5**

- [ ] 13. 检查点 - 后端API完成
  - 运行所有后端测试确保通过
  - 验证API文档自动生成正确
  - 如有问题请向用户报告

- [ ] 14. 前端类型定义和API客户端
  - [ ] 14.1 创建TypeScript类型定义
    - 在 yaoyaoji_frontend/web/src/types/ 中创建 chronic-disease.ts
    - 定义所有数据模型的TypeScript接口
    - _需求：1.1, 1.2_
  
  - [ ] 14.2 创建API客户端模块
    - 在 yaoyaoji_frontend/web/src/api/ 中创建 chronic-disease.ts
    - 封装所有慢性病管理相关的API调用
    - 使用axios进行HTTP请求
    - _需求：9.1, 9.2_

- [ ] 15. 前端组件实现 - 疾病类型选择
  - [ ] 15.1 创建疾病类型选择组件
    - 创建 yaoyaoji_frontend/web/src/components/DiseaseTypeSelector.vue
    - 显示三种预设疾病类型的卡片
    - 展示每种疾病的特点和图标
    - _需求：1.1_
  
  - [ ] 15.2 创建疾病创建对话框组件
    - 创建 yaoyaoji_frontend/web/src/components/CreateDiseaseDialog.vue
    - 集成疾病类型选择器
    - 收集诊断日期、医院等基本信息
    - _需求：1.1, 1.2_

- [ ] 16. 前端组件实现 - 慢性病列表
  - [ ] 16.1 增强慢性病列表视图
    - 修改 yaoyaoji_frontend/web/src/views/ChronicDiseaseView.vue
    - 添加搜索框和筛选器
    - 优化空状态显示
    - _需求：1.3, 1.4, 5.1, 5.2, 5.3_
  
  - [ ] 16.2 实现搜索和筛选功能
    - 添加实时搜索逻辑
    - 添加疾病类型筛选下拉框
    - 添加日期范围选择器
    - 添加清除筛选按钮
    - _需求：5.1, 5.2, 5.3, 5.4_


- [ ] 17. 前端组件实现 - 指标记录
  - [ ] 17.1 创建指标记录表单组件
    - 创建 yaoyaoji_frontend/web/src/components/IndicatorRecordForm.vue
    - 根据疾病类型动态显示对应的指标输入字段
    - 高血压：收缩压、舒张压
    - 高血脂：总胆固醇、甘油三酯、高密度脂蛋白、低密度脂蛋白
    - 糖尿病：血糖值、测量时段
    - _需求：2.1, 3.1, 4.1_
  
  - [ ] 17.2 实现实时数据验证
    - 添加输入范围验证
    - 显示正常范围参考值
    - 超出范围时显示警告提示
    - _需求：2.2, 3.2_
  
  - [ ] 17.3 支持多次测量记录
    - 添加"添加更多记录"按钮
    - 支持在同一表单中输入多条记录
    - 特别优化血糖多次测量场景
    - _需求：4.2_

- [ ] 18. 前端组件实现 - 饮食建议
  - [ ] 18.1 创建饮食建议组件
    - 创建 yaoyaoji_frontend/web/src/components/DietRecommendations.vue
    - 显示个性化饮食建议
    - 高血脂：显示通用饮食指导
    - 糖尿病：分别显示早餐、午餐、晚餐建议
    - _需求：3.3, 4.4_
  
  - [ ] 18.2 实现建议卡片展示
    - 使用卡片布局展示建议
    - 显示推荐食物和禁忌食物
    - 添加收藏和分享功能
    - _需求：3.3, 4.4_

- [ ] 19. 前端组件实现 - 并发症管理
  - [ ] 19.1 创建并发症管理组件
    - 创建 yaoyaoji_frontend/web/src/components/ComplicationManager.vue
    - 显示并发症列表
    - 支持添加新并发症
    - _需求：4.3_
  
  - [ ] 19.2 创建并发症时间线视图
    - 以时间线形式展示并发症历史
    - 显示发现日期、严重程度、治疗方案
    - 支持更新并发症状态
    - _需求：4.3_

- [ ] 20. 前端组件实现 - 运动建议
  - [ ] 20.1 创建运动建议组件
    - 创建 yaoyaoji_frontend/web/src/components/ExerciseRecommendations.vue
    - 显示个性化运动建议
    - 展示运动类型、时长、频率
    - 显示注意事项
    - _需求：4.7_

- [ ] 21. 前端组件实现 - 用药提醒
  - [ ] 21.1 创建用药提醒设置组件
    - 创建 yaoyaoji_frontend/web/src/components/MedicationReminderSettings.vue
    - 支持设置提醒时间
    - 支持选择提醒日期（周一到周日）
    - 支持设置提前提醒时间
    - _需求：2.4_
  
  - [ ] 21.2 创建提醒列表组件
    - 显示所有活动的用药提醒
    - 支持暂停、恢复、删除提醒
    - _需求：2.4_

- [ ] 22. 前端组件实现 - 数据导出
  - [ ] 22.1 创建数据导出对话框
    - 创建 yaoyaoji_frontend/web/src/components/ExportDialog.vue
    - 支持选择导出格式（CSV、PDF）
    - 支持选择导出内容（指标、用药、并发症）
    - 支持选择日期范围
    - _需求：6.1, 6.2_
  
  - [ ] 22.2 实现导出进度显示
    - 显示导出任务状态
    - 轮询检查任务完成状态
    - 完成后提供下载链接
    - _需求：6.4, 6.5_

- [ ] 23. 前端组件实现 - 数据可视化
  - [ ] 23.1 创建指标趋势图表组件
    - 创建 yaoyaoji_frontend/web/src/components/IndicatorTrendChart.vue
    - 使用ECharts或类似图表库
    - 显示血压、血脂、血糖的时间趋势
    - 支持切换时间范围（周、月、年）
    - _需求：2.5, 3.5, 4.8_

- [ ] 24. 前端路由和导航
  - [ ] 24.1 配置路由
    - 修改 yaoyaoji_frontend/web/src/router/index.ts
    - 确保所有新页面和组件可访问
    - 添加路由守卫进行权限检查
    - _需求：10.1_

- [ ] 25. 前端状态管理
  - [ ] 25.1 创建慢性病管理Store
    - 在 yaoyaoji_frontend/web/src/stores/ 中创建 chronic-disease.ts
    - 使用Pinia管理慢性病数据状态
    - 实现数据缓存和更新逻辑
    - _需求：1.3_

- [ ] 26. 前端响应式设计
  - [ ] 26.1 优化移动端布局
    - 确保所有组件在移动设备上正常显示
    - 使用Element Plus的响应式栅格系统
    - 优化触摸交互
    - _需求：8.4_

- [ ] 27. 检查点 - 前端功能完成
  - 在浏览器中测试所有功能
  - 验证与后端API的集成
  - 检查响应式布局
  - 如有问题请向用户报告

- [ ] 28. 集成测试
  - [ ] 28.1 编写端到端测试场景
    - 测试完整的用户流程：创建疾病 → 记录指标 → 查看建议 → 导出数据
    - 测试搜索和筛选功能
    - 测试权限隔离
    - _需求：1.1, 1.2, 2.1, 5.1, 6.3, 10.2_

- [ ] 29. 性能优化
  - [ ] 29.1 优化数据库查询
    - 添加必要的数据库索引
    - 优化复杂查询的SQL
    - _需求：8.1_
  
  - [ ] 29.2 实现API响应缓存
    - 对疾病模板、建议数据等静态内容添加缓存
    - 使用Redis或内存缓存
    - _需求：8.1_
  
  - [ ] 29.3 优化前端资源加载
    - 实现组件懒加载
    - 优化图片和静态资源
    - _需求：8.1_

- [ ] 30. 文档和部署
  - [ ] 30.1 更新API文档
    - 确保FastAPI自动生成的文档包含所有新接口
    - 添加接口使用示例
  
  - [ ] 30.2 编写部署说明
    - 更新数据库迁移步骤
    - 说明初始数据加载过程
    - 更新Kubernetes配置（如需要）
  
  - [ ] 30.3 编写用户使用指南
    - 创建功能使用说明文档
    - 添加常见问题解答

- [ ] 31. 最终检查点
  - 运行所有测试（单元测试、属性测试、集成测试）
  - 验证所有需求都已实现
  - 进行代码审查
  - 准备发布

## 注意事项

- 标记为 `*` 的任务是可选的测试任务，可以根据时间安排决定是否实施
- 每个任务都标注了相关的需求编号，便于追溯
- 建议按顺序执行任务，确保依赖关系正确
- 在每个检查点暂停，确保前面的工作质量
- 属性测试使用Hypothesis库，每个测试至少运行100次迭代
- 所有数据修改操作都应记录审计日志
- 确保所有API接口都有适当的权限检查
