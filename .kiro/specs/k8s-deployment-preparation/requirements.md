# Requirements Document

## Introduction

本文档定义了药药记（YaoYaoJi）项目从开发环境向 Kubernetes 生产环境迁移的需求。该项目是一个健康管理应用，包含 Python FastAPI 后端、Vue 3 前端和 MySQL 数据库。目标是清理开发测试文件，整合数据库迁移脚本，并创建完整的 Helm Chart 以支持在 kind Kubernetes 集群上部署。

## Glossary

- **Project**: 药药记（YaoYaoJi）健康管理应用系统
- **Backend**: 基于 Python FastAPI 的后端 API 服务
- **Frontend**: 基于 Vue 3 和 Nginx 的前端 Web 应用
- **Database**: MySQL 8.0 数据库服务
- **Helm_Chart**: Kubernetes 应用包管理工具的配置包
- **Kind_Cluster**: Kubernetes IN Docker，本地 Kubernetes 测试集群
- **Migration_Script**: 数据库结构变更脚本
- **StatefulSet**: Kubernetes 有状态应用部署资源
- **Deployment**: Kubernetes 无状态应用部署资源
- **PVC**: Persistent Volume Claim，持久化存储声明
- **ConfigMap**: Kubernetes 配置数据存储资源
- **Secret**: Kubernetes 敏感数据存储资源
- **Ingress**: Kubernetes HTTP/HTTPS 路由规则资源

## Requirements

### Requirement 1: 清理开发测试脚本

**User Story:** 作为开发者，我希望删除不需要的开发测试脚本，以便保持代码库整洁并避免将测试代码部署到生产环境。

#### Acceptance Criteria

1. THE Project SHALL NOT contain quick_test_api.py file in yaoyaoji_backup directory
2. THE Project SHALL NOT contain verify_improvements.py file in yaoyaoji_backup directory
3. THE Project SHALL NOT contain start.sh file in yaoyaoji_backup directory


### Requirement 2: 整合数据库迁移脚本

**User Story:** 作为开发者，我希望将所有单独的数据库迁移脚本整合到统一脚本中，以便简化数据库迁移流程并减少文件数量。

#### Acceptance Criteria

1. THE Migration_Script run_all_migrations.py SHALL contain all migration logic from individual migrate_*.py files
2. THE Project SHALL NOT contain migrate_add_alerts_adherence.py file
3. THE Project SHALL NOT contain migrate_add_avatar.py file
4. THE Project SHALL NOT contain migrate_add_birth_date.py file
5. THE Project SHALL NOT contain migrate_add_medication_schedule_fields.py file
6. THE Project SHALL NOT contain migrate_chronic_disease.py file
7. WHEN run_all_migrations.py is executed, THE Migration_Script SHALL successfully apply all database schema changes

### Requirement 3: 更新版本控制忽略规则

**User Story:** 作为开发者，我希望更新 .gitignore 文件以排除 IDE 配置文件，以便避免将个人开发环境配置提交到版本控制系统。

#### Acceptance Criteria

1. THE Project .gitignore file SHALL contain .idea/ directory pattern
2. THE Project .gitignore file SHALL contain .vscode/ directory pattern
3. THE Project .gitignore file SHALL contain .DS_Store file pattern
4. WHEN developers use different IDEs, THE version control system SHALL ignore IDE-specific configuration files

### Requirement 4: 保留本地开发配置

**User Story:** 作为开发者，我希望保留 docker-compose.yml 文件，以便继续使用 Docker Compose 进行本地开发和测试。

#### Acceptance Criteria

1. THE Project SHALL contain docker-compose.yml file in root directory
2. THE docker-compose.yml file SHALL define MySQL service configuration
3. THE docker-compose.yml file SHALL define Backend service configuration
4. THE docker-compose.yml file SHALL define Frontend service configuration
5. WHEN developers run docker-compose up, THE Project SHALL start all services successfully for local development


### Requirement 5: 创建 Helm Chart 基础结构

**User Story:** 作为运维工程师，我希望创建标准的 Helm Chart 目录结构，以便使用 Helm 管理 Kubernetes 应用部署。

#### Acceptance Criteria

1. THE Project SHALL contain helm/yaoyaoji directory with standard Helm Chart structure
2. THE Helm_Chart SHALL contain Chart.yaml file with application metadata
3. THE Helm_Chart SHALL contain values.yaml file with default configuration values
4. THE Helm_Chart SHALL contain values-dev.yaml file with development environment configuration
5. THE Helm_Chart SHALL contain values-prod.yaml file with production environment configuration
6. THE Helm_Chart SHALL contain templates/ directory for Kubernetes resource templates
7. WHEN helm lint is executed, THE Helm_Chart SHALL pass validation without errors

### Requirement 6: 配置 MySQL StatefulSet

**User Story:** 作为运维工程师，我希望部署 MySQL 作为 StatefulSet，以便确保数据库的持久化存储和稳定的网络标识。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain mysql-statefulset.yaml template
2. THE StatefulSet SHALL configure MySQL 8.0 container image
3. THE StatefulSet SHALL define volumeClaimTemplate for data persistence
4. THE StatefulSet SHALL configure environment variables for database initialization
5. THE StatefulSet SHALL define readiness probe to verify MySQL availability
6. THE StatefulSet SHALL define liveness probe to detect MySQL failures
7. WHEN MySQL pod restarts, THE Database SHALL retain all data through PVC

### Requirement 7: 配置后端应用 Deployment

**User Story:** 作为运维工程师，我希望部署后端 API 服务为 Deployment，以便实现高可用和负载均衡。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain backend-deployment.yaml template
2. THE Deployment SHALL configure 3 replicas for production environment
3. THE Deployment SHALL configure Backend container with FastAPI application
4. THE Deployment SHALL mount PVC for uploads directory persistence
5. THE Deployment SHALL reference ConfigMap for non-sensitive configuration
6. THE Deployment SHALL reference Secret for sensitive credentials
7. THE Deployment SHALL define readiness probe on /health endpoint
8. THE Deployment SHALL define liveness probe on /health endpoint
9. WHEN Backend pod fails health check, THE Kubernetes SHALL restart the pod automatically


### Requirement 8: 配置前端应用 Deployment

**User Story:** 作为运维工程师，我希望部署前端 Web 应用为 Deployment，以便提供静态资源服务和反向代理。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain frontend-deployment.yaml template
2. THE Deployment SHALL configure 2 replicas for production environment
3. THE Deployment SHALL configure Frontend container with Nginx and Vue 3 application
4. THE Deployment SHALL define readiness probe on root path
5. THE Deployment SHALL define liveness probe on root path
6. WHEN Frontend pod fails health check, THE Kubernetes SHALL restart the pod automatically

### Requirement 9: 配置 Kubernetes Services

**User Story:** 作为运维工程师，我希望创建 Service 资源，以便为应用组件提供稳定的网络访问端点。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain mysql-service.yaml template with ClusterIP type
2. THE Helm_Chart SHALL contain backend-service.yaml template with ClusterIP type
3. THE Helm_Chart SHALL contain frontend-service.yaml template with ClusterIP type
4. THE mysql Service SHALL expose port 3306 to Backend pods
5. THE backend Service SHALL expose port 8000 to Frontend pods
6. THE frontend Service SHALL expose port 80 to Ingress controller
7. WHEN pods are recreated, THE Service SHALL maintain stable DNS names and IP addresses

### Requirement 10: 配置持久化存储

**User Story:** 作为运维工程师，我希望配置 PersistentVolumeClaim 资源，以便为数据库和上传文件提供持久化存储。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain mysql-pvc.yaml template for database data
2. THE Helm_Chart SHALL contain backend-uploads-pvc.yaml template for uploaded files
3. THE PVC SHALL request storage size configurable through values.yaml
4. THE PVC SHALL specify storageClassName configurable through values.yaml
5. THE PVC SHALL use ReadWriteOnce access mode for MySQL data
6. THE PVC SHALL use ReadWriteMany access mode for backend uploads when multiple replicas exist
7. WHEN pods are deleted, THE PVC SHALL retain data for pod recreation


### Requirement 11: 配置 ConfigMap 和 Secret

**User Story:** 作为运维工程师，我希望使用 ConfigMap 和 Secret 管理配置，以便分离配置和代码，并安全存储敏感信息。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain configmap.yaml template for non-sensitive configuration
2. THE Helm_Chart SHALL contain secret.yaml template for sensitive credentials
3. THE ConfigMap SHALL store database connection parameters
4. THE ConfigMap SHALL store application configuration parameters
5. THE Secret SHALL store database passwords with base64 encoding
6. THE Secret SHALL store API keys with base64 encoding
7. THE Secret SHALL store JWT secret keys with base64 encoding
8. WHEN configuration changes, THE Backend pods SHALL reload configuration without code changes

### Requirement 12: 配置 Ingress 路由

**User Story:** 作为运维工程师，我希望配置 Ingress 资源，以便通过统一的域名访问前端和后端服务。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain ingress.yaml template
2. THE Ingress SHALL route root path / to Frontend service
3. THE Ingress SHALL route /api path to Backend service
4. THE Ingress SHALL configure host domain through values.yaml
5. THE Ingress SHALL support TLS configuration through values.yaml
6. WHEN Ingress is enabled in values.yaml, THE Kubernetes SHALL create Ingress resource
7. WHEN users access configured domain, THE Ingress SHALL route requests to appropriate services

### Requirement 13: 支持多环境配置

**User Story:** 作为运维工程师，我希望通过不同的 values 文件支持开发和生产环境，以便使用相同的 Helm Chart 部署到不同环境。

#### Acceptance Criteria

1. THE values-dev.yaml SHALL configure 1 Backend replica for development
2. THE values-dev.yaml SHALL configure 1 Frontend replica for development
3. THE values-dev.yaml SHALL configure smaller resource requests and limits
4. THE values-prod.yaml SHALL configure 3 Backend replicas for production
5. THE values-prod.yaml SHALL configure 2 Frontend replicas for production
6. THE values-prod.yaml SHALL configure production-grade resource requests and limits
7. WHEN helm install uses -f values-dev.yaml, THE Kubernetes SHALL deploy development configuration
8. WHEN helm install uses -f values-prod.yaml, THE Kubernetes SHALL deploy production configuration


### Requirement 14: 数据库初始化支持

**User Story:** 作为运维工程师，我希望在首次部署时自动执行数据库迁移，以便初始化数据库结构。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain init-job.yaml template for database initialization
2. THE init Job SHALL execute run_all_migrations.py script
3. THE init Job SHALL run before Backend deployment starts
4. THE init Job SHALL use Helm hooks for pre-install and pre-upgrade phases
5. WHEN Helm Chart is installed, THE init Job SHALL create all required database tables
6. WHEN database migration fails, THE Helm installation SHALL fail with error message
7. IF database tables already exist, THEN THE init Job SHALL skip creating existing tables

### Requirement 15: 资源限制和请求配置

**User Story:** 作为运维工程师，我希望为所有容器配置资源请求和限制，以便确保集群资源的合理分配和防止资源耗尽。

#### Acceptance Criteria

1. THE Backend Deployment SHALL define CPU requests configurable through values.yaml
2. THE Backend Deployment SHALL define memory requests configurable through values.yaml
3. THE Backend Deployment SHALL define CPU limits configurable through values.yaml
4. THE Backend Deployment SHALL define memory limits configurable through values.yaml
5. THE Frontend Deployment SHALL define resource requests and limits configurable through values.yaml
6. THE MySQL StatefulSet SHALL define resource requests and limits configurable through values.yaml
7. WHEN pod resource usage exceeds limits, THE Kubernetes SHALL throttle or restart the pod

### Requirement 16: 健康检查和就绪探测

**User Story:** 作为运维工程师，我希望为所有服务配置健康检查，以便 Kubernetes 能够自动检测和恢复故障服务。

#### Acceptance Criteria

1. THE Backend Deployment SHALL define livenessProbe with /health endpoint
2. THE Backend Deployment SHALL define readinessProbe with /health endpoint
3. THE Frontend Deployment SHALL define livenessProbe with HTTP GET on root path
4. THE Frontend Deployment SHALL define readinessProbe with HTTP GET on root path
5. THE MySQL StatefulSet SHALL define livenessProbe with mysqladmin ping command
6. THE MySQL StatefulSet SHALL define readinessProbe with mysqladmin ping command
7. THE probe configurations SHALL be configurable through values.yaml
8. WHEN service fails liveness probe, THE Kubernetes SHALL restart the container
9. WHEN service fails readiness probe, THE Kubernetes SHALL remove pod from Service endpoints


### Requirement 17: Helm Chart 文档

**User Story:** 作为运维工程师，我希望 Helm Chart 包含完整的文档，以便了解如何安装、配置和使用该 Chart。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain README.md file with installation instructions
2. THE README.md SHALL document all configurable values in values.yaml
3. THE README.md SHALL provide examples for development and production deployment
4. THE README.md SHALL document prerequisites for kind cluster setup
5. THE README.md SHALL document how to access the application after deployment
6. THE README.md SHALL document how to upgrade and rollback deployments
7. WHEN engineers read README.md, THE documentation SHALL provide sufficient information to deploy the application

### Requirement 18: Kind 集群兼容性

**User Story:** 作为开发者，我希望 Helm Chart 能够在 kind Kubernetes 集群上成功部署，以便在本地环境测试 Kubernetes 部署。

#### Acceptance Criteria

1. THE Helm_Chart SHALL use container images accessible from public registries
2. THE Helm_Chart SHALL configure Ingress compatible with kind cluster
3. THE Helm_Chart SHALL use storageClassName compatible with kind default storage provisioner
4. THE values-dev.yaml SHALL configure settings optimized for kind cluster
5. WHEN deployed to kind cluster, THE application SHALL be accessible through localhost
6. WHEN deployed to kind cluster, THE MySQL SHALL successfully persist data
7. WHEN deployed to kind cluster, THE Backend SHALL successfully connect to MySQL

### Requirement 19: 部署验证和测试

**User Story:** 作为运维工程师，我希望验证 Helm Chart 部署的正确性，以便确保所有组件正常工作。

#### Acceptance Criteria

1. THE Helm_Chart SHALL contain NOTES.txt template with post-installation instructions
2. THE NOTES.txt SHALL display commands to check deployment status
3. THE NOTES.txt SHALL display commands to access the application
4. THE NOTES.txt SHALL display commands to view logs
5. WHEN helm install completes, THE Kubernetes SHALL display NOTES.txt content
6. WHEN all pods are running, THE Backend SHALL successfully connect to Database
7. WHEN all pods are running, THE Frontend SHALL successfully proxy requests to Backend

