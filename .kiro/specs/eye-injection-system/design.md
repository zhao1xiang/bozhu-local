# 设计文档

## 概述

玻注预约系统是专为眼科玻璃体腔注射治疗设计的医疗管理平台。系统通过五个核心模块简化日常临床工作流程：工作台、每日工作、患者管理、预约管理和系统配置。

系统重点关注实际日常操作，包括预约签到、随访电话管理、文档打印和实时分析。采用现代Web应用架构，FastAPI后端和React前端，专门针对中国眼科诊所的需求进行优化。

## 系统架构

### 系统架构图

系统采用三层架构：

```
┌─────────────────────────────────────────────────────────────┐
│                    表现层 (Presentation Layer)              │
│  React + TypeScript + Ant Design + Vite                    │
│  - 患者管理界面                                              │
│  - 预约调度界面                                              │
│  - 治疗进度跟踪                                              │
│  - 管理仪表板                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │
┌─────────────────────────────────────────────────────────────┐
│                    业务逻辑层 (Business Logic Layer)         │
│  FastAPI + SQLModel + Pydantic                             │
│  - 患者管理服务                                              │
│  - 预约调度逻辑                                              │
│  - 治疗方案处理                                              │
│  - 认证与授权                                               │
│  - 文档生成                                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ SQLModel ORM
                              │
┌─────────────────────────────────────────────────────────────┐
│                    数据持久层 (Data Persistence Layer)       │
│  SQLite 数据库                                              │
│  - 患者记录                                                 │
│  - 预约数据                                                 │
│  - 治疗方案                                                 │
│  - 系统配置                                                 │
│  - 审计日志                                                 │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

**后端：**
- FastAPI: 现代、快速的Web框架，用于构建API
- SQLModel: 具有类型安全的SQL数据库ORM
- SQLite: 轻量级、基于文件的关系数据库
- Pydantic: 数据验证和序列化
- JWT: 无状态认证令牌
- Bcrypt: 密码哈希

**前端：**
- React 18: 基于组件的UI框架
- TypeScript: 类型安全的JavaScript
- Ant Design: 企业级UI组件库
- Vite: 快速构建工具和开发服务器
- Axios: API通信的HTTP客户端
- Zustand: 轻量级状态管理

## 组件和接口

### 核心领域模型

#### 患者实体
```python
class Patient:
    id: str (UUID)                    # 患者ID
    name: str                         # 姓名
    outpatient_number: str (unique)   # 门诊号（唯一）
    phone: str (unique)               # 手机号（唯一）
    diagnosis: Optional[str]          # 诊断
    drug_type: Optional[str]          # 药物类型
    left_vision: Optional[float]      # 左眼视力
    right_vision: Optional[float]     # 右眼视力
    left_eye: bool                    # 左眼治疗
    right_eye: bool                   # 右眼治疗
    patient_type: Optional[str]       # 患者类型（初治/经治）
    status: str                       # 状态
    created_at: datetime              # 创建时间
    updated_at: datetime              # 更新时间
```

#### 预约实体
```python
class Appointment:
    id: str (UUID)                        # 预约ID
    patient_id: str (FK)                  # 患者ID（外键）
    appointment_date: Optional[date]      # 预约日期
    time_slot: Optional[str]              # 时间段
    status: str                           # 状态
    notes: Optional[str]                  # 备注
    injection_number: Optional[str]       # 注药号
    injection_count: Optional[int]        # 注药次数
    eye: Optional[str]                    # 眼别
    drug_name: Optional[str]              # 药品名称
    cost_type: Optional[str]              # 费别（自费/医保）
    doctor: Optional[str]                 # 注药医生
    follow_up_date: Optional[date]        # 复诊时间
    next_follow_up_date: Optional[date]   # 下次复诊时间
    diagnosis: Optional[str]              # 诊断
    pre_op_vision_left: Optional[float]   # 左眼术前视力
    pre_op_vision_right: Optional[float]  # 右眼术前视力
    pre_op_cst_left: Optional[float]      # 左眼术前CST
    pre_op_cst_right: Optional[float]     # 右眼术前CST
    treatment_phase: Optional[str]        # 治疗周期
    created_at: datetime                  # 创建时间
    updated_at: datetime                  # 更新时间
```

### API接口设计

#### RESTful端点

**患者管理：**
- `POST /api/patients` - 创建新患者
- `GET /api/patients` - 获取患者列表（支持筛选）
- `GET /api/patients/{id}` - 获取患者详情
- `PUT /api/patients/{id}` - 更新患者信息

**预约管理：**
- `POST /api/appointments` - 创建预约
- `POST /api/appointments/batch` - 批量创建预约
- `GET /api/appointments` - 获取预约列表（支持筛选）
- `PATCH /api/appointments/{id}` - 更新预约
- `DELETE /api/appointments/{id}` - 取消预约

**治疗方案：**
- `GET /api/schemes` - 获取可用治疗方案列表
- `POST /api/schemes/apply/{scheme_id}` - 为患者应用方案

**系统配置：**
- `GET /api/data-dictionary` - 获取配置数据
- `POST /api/data-dictionary` - 创建配置项
- `PUT /api/data-dictionary/{id}` - 更新配置

**随访管理：**
- `GET /api/follow-ups/reminders` - 获取随访提醒列表
- `POST /api/follow-ups/record` - 记录随访结果

**仪表板：**
- `GET /api/dashboard` - 获取仪表板统计数据

### 前端组件架构

```
App
├── AuthProvider (认证上下文)
├── MainLayout
│   ├── Navigation (左侧菜单栏)
│   ├── Header (用户信息 & 退出登录)
│   └── Content
│       ├── Dashboard (工作台)
│       │   ├── KPICards (关键指标卡片)
│       │   ├── InjectionTrendChart (注药趋势图)
│       │   ├── DoctorWorkloadChart (医生工作量统计)
│       │   └── DrugDistributionChart (药品分布图)
│       ├── DailyWork (每日工作)
│       │   ├── AppointmentCheckIn (预约签到)
│       │   ├── FollowUpReminders (随访提醒)
│       │   └── FollowUpRecordModal (记录结果弹窗)
│       ├── Patients (患者管理)
│       │   ├── PatientList (患者列表)
│       │   ├── PatientForm (患者表单)
│       │   └── TreatmentProgress (治疗进度)
│       ├── Appointments (预约管理)
│       │   ├── AppointmentCalendar (预约日历)
│       │   ├── AppointmentForm (预约表单)
│       │   └── AppointmentList (预约列表)
│       ├── PrintCenter (打印中心)
│       │   ├── DocumentTemplates (文档模板)
│       │   └── PrintQueue (打印队列)
│       └── SystemConfig (系统配置)
│           ├── DoctorManagement (医生管理)
│           ├── GeneralSettings (通用设置)
│           └── SecuritySettings (安全设置)
└── Login (登录页面)
```

## 数据模型

### 实体关系图

```
患者 (Patient) ||--o{ 预约 (Appointment) : 拥有
患者 (Patient) ||--o{ 打印记录 (PrintRecord) : 生成
患者 (Patient) ||--o{ 随访记录 (FollowUpRecord) : 接受

预约 (Appointment) ||--o{ 打印记录 (PrintRecord) : 产生
预约 (Appointment) ||--o{ 随访记录 (FollowUpRecord) : 触发

用户 (User) ||--o{ 打印记录 (PrintRecord) : 创建
用户 (User) ||--o{ 随访记录 (FollowUpRecord) : 执行

数据字典 (DataDictionary) }o--|| 分类 (Category) : 属于
系统设置 (SystemSetting) }o--|| 配置 (Configuration) : 部分
```

### 数据验证规则

1. **患者验证：**
   - 姓名：必填，非空字符串
   - 门诊号：必填，唯一，字母数字组合
   - 手机号：必填，唯一，有效手机号格式
   - 至少指定一只治疗眼

2. **预约验证：**
   - 患者ID：必须引用现有的活跃患者
   - 预约日期：不能是过去的日期
   - 状态：必须来自预定义枚举
   - 注药次数：如果指定，必须是正整数

3. **治疗方案验证：**
   - 药物类型：必须与患者的药物类型匹配
   - 计划：必须有有效的间隔和阶段
   - 状态：必须是活跃状态才能应用

## 正确性属性

*属性是系统所有有效执行中都应该保持为真的特征或行为——本质上是关于系统应该做什么的正式声明。属性是人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性反思

在分析所有验收标准后，可以合并几个属性：
- 属性 1.1、2.1、4.1、6.2 都测试基本数据持久性，可以合并为综合数据完整性属性
- 属性 1.4、2.3、5.4、6.2、7.2、7.5 都测试审计日志，可以统一
- 属性 3.1、3.2 都测试方案应用，可以合并
- 属性 6.1、6.3 都测试文档生成，可以统一
- 属性 8.1、8.3 都测试实时数据计算，可以合并

### 核心属性

**属性 1：数据持久性完整性**
*对于任何*有效实体（患者、预约、随访记录、打印记录），当通过系统创建或更新时，所有必填字段都应准确存储并可从数据库中检索
**验证：需求 1.1、2.1、2.2、2.4、4.1、5.1**

**属性 2：重复预防**
*对于任何*使用重复门诊号或手机号创建患者的尝试，系统应阻止创建并提供现有患者信息
**验证：需求 1.2**

**属性 3：搜索功能**
*对于任何*患者搜索查询，结果应包括姓名、手机号或门诊号包含搜索词的所有患者
**验证：需求 1.3**

**属性 4：审计跟踪维护**
*对于任何*数据修改操作（患者更新、预约状态变更、配置更改、打印事件、认证尝试），系统应记录时间戳和相关审计信息
**验证：需求 1.4、2.3、5.4、6.2、7.2、7.5**

**属性 5：业务规则验证**
*对于任何*违反业务规则的操作（非活跃患者预约、缺少治疗眼、无效方案应用），系统应阻止操作并提供适当的错误消息
**验证：需求 1.5、2.5、3.3、3.5、4.5、5.3、6.5**

**属性 6：治疗方案应用**
*对于任何*应用于兼容患者的有效治疗方案，系统应根据方案的计划生成具有正确间隔和治疗阶段的预约
**验证：需求 3.1、3.2**

**属性 7：数据关系完整性**
*对于任何*具有外键关系的实体（预约到患者、随访到预约和患者），系统应维护引用完整性并允许适当的关联查询
**验证：需求 3.4、4.3、4.4**

**属性 8：随访工作流管理**
*对于任何*状态为"无人接听"的随访记录，系统应允许安排重试尝试，同时保持与原始预约的连接
**验证：需求 4.2**

**属性 9：配置生命周期管理**
*对于任何*被停用的数据字典项，系统应阻止其在新记录中使用，同时保留其与历史数据的关联
**验证：需求 5.2**

**属性 10：文档生成准确性**
*对于任何*具有完整必需数据的打印请求，系统应生成所有模板字段都从当前患者和预约信息中准确填充的文档
**验证：需求 6.1、6.3、6.4**

**属性 11：认证和安全**
*对于任何*认证尝试，系统应根据存储的账户验证凭据，适当管理会话过期，并加密敏感数据
**验证：需求 7.1、7.3、7.4**

**属性 12：实时数据聚合**
*对于任何*仪表板或报告请求，系统应从当前数据库状态计算指标和统计信息，并提供适当的筛选选项
**验证：需求 8.1、8.2、8.3、8.4、8.5**

## 错误处理

### 错误分类

1. **验证错误：**
   - 无效输入数据格式
   - 缺少必填字段
   - 业务规则违反
   - 响应：400 Bad Request，包含详细字段错误

2. **认证错误：**
   - 无效凭据
   - 过期令牌
   - 权限不足
   - 响应：401 Unauthorized 或 403 Forbidden

3. **资源错误：**
   - 实体未找到
   - 重复键违反
   - 外键约束失败
   - 响应：404 Not Found 或 409 Conflict

4. **系统错误：**
   - 数据库连接失败
   - 外部服务不可用
   - 意外异常
   - 响应：500 Internal Server Error

### 错误响应格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入验证失败",
    "details": {
      "field": "outpatient_number",
      "issue": "该门诊号已被其他患者使用"
    },
    "timestamp": "2024-02-05T10:30:00Z"
  }
}
```

### 前端错误处理

- 全局错误边界处理未捕获异常
- 用户友好错误的Toast通知
- 表单验证与内联错误消息
- 网络失败的重试机制
- 缺失数据的优雅降级

## 测试策略

### 双重测试方法

系统将采用单元测试和基于属性的测试来确保全面覆盖：

**单元测试：**
- 演示正确行为的具体示例
- 边界情况和错误条件
- 组件之间的集成点
- API端点功能
- UI组件行为

**基于属性的测试：**
- 应该在所有输入中保持的通用属性
- 数据完整性和一致性规则
- 业务逻辑验证
- 安全和认证属性
- 负载下的性能特征

### 基于属性的测试实现

**框架选择：**
- 后端：Hypothesis（Python）用于基于属性的测试
- 前端：fast-check（TypeScript）用于基于属性的测试

**配置：**
- 每个属性测试最少100次迭代
- 每个属性测试标记格式：**Feature: eye-injection-system, Property {number}: {property_text}**
- 每个正确性属性由单个基于属性的测试实现

**测试数据生成：**
- 约束到有效输入空间的智能生成器
- 现实的医疗数据模式
- 通过生成器策略覆盖边界情况
- 工作流场景的状态测试

### 测试要求

1. **单元测试：**
   - 测试具体示例和边界情况
   - 验证系统组件之间的集成
   - 验证API合约和响应
   - 测试UI组件渲染和交互

2. **基于属性的测试：**
   - 每个正确性属性必须实现为基于属性的测试
   - 测试必须运行最少100次迭代
   - 测试必须标记明确的属性引用
   - 生成器必须在有效域内产生现实的测试数据

3. **集成测试：**
   - 端到端工作流测试
   - 数据库事务完整性
   - 认证和授权流程
   - 文档生成管道

4. **性能测试：**
   - 正常负载下的响应时间验证
   - 数据库查询优化验证
   - 内存使用监控
   - 并发用户模拟