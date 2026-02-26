# Tasks

## Phase 1: Project Cleanup

- [x] 1.1 Delete development test scripts
  - [x] 1.1.1 Delete yaoyaoji_backup/quick_test_api.py
  - [x] 1.1.2 Delete yaoyaoji_backup/verify_improvements.py
  - [x] 1.1.3 Delete yaoyaoji_backup/start.sh

- [x] 1.2 Delete individual migration scripts
  - [x] 1.2.1 Delete yaoyaoji_backup/migrate_add_alerts_adherence.py
  - [x] 1.2.2 Delete yaoyaoji_backup/migrate_add_avatar.py
  - [x] 1.2.3 Delete yaoyaoji_backup/migrate_add_birth_date.py
  - [x] 1.2.4 Delete yaoyaoji_backup/migrate_add_medication_schedule_fields.py
  - [x] 1.2.5 Delete yaoyaoji_backup/migrate_chronic_disease.py

- [x] 1.3 Update .gitignore file
  - [x] 1.3.1 Verify .idea/ pattern exists in .gitignore
  - [x] 1.3.2 Verify .vscode/ pattern exists in .gitignore
  - [x] 1.3.3 Verify .DS_Store pattern exists in .gitignore

## Phase 2: Helm Chart Structure

- [x] 2.1 Create Helm Chart directory structure
  - [x] 2.1.1 Create helm/yaoyaoji directory
  - [x] 2.1.2 Create helm/yaoyaoji/templates directory

- [x] 2.2 Create Chart metadata files
  - [x] 2.2.1 Create Chart.yaml with application metadata
  - [x] 2.2.2 Create .helmignore file
  - [x] 2.2.3 Create templates/_helpers.tpl with template functions

## Phase 3: Configuration Files

- [x] 3.1 Create values files
  - [x] 3.1.1 Create values.yaml with default configuration
  - [x] 3.1.2 Create values-dev.yaml with development overrides
  - [x] 3.1.3 Create values-prod.yaml with production overrides

- [x] 3.2 Create ConfigMap and Secret templates
  - [x] 3.2.1 Create templates/configmap.yaml for application configuration
  - [x] 3.2.2 Create templates/secret.yaml for sensitive credentials

## Phase 4: MySQL Resources

- [x] 4.1 Create MySQL StatefulSet
  - [x] 4.1.1 Create templates/mysql-statefulset.yaml
  - [x] 4.1.2 Configure MySQL 8.0 container with environment variables
  - [x] 4.1.3 Configure volumeClaimTemplate for data persistence
  - [x] 4.1.4 Configure liveness and readiness probes
  - [x] 4.1.5 Configure resource requests and limits

- [x] 4.2 Create MySQL Service
  - [x] 4.2.1 Create templates/mysql-service.yaml
  - [x] 4.2.2 Configure ClusterIP service on port 3306

- [ ] 4.3 Create MySQL PVC (if not using volumeClaimTemplate)
  - [ ] 4.3.1 Create templates/mysql-pvc.yaml (optional alternative approach)


## Phase 5: Backend Resources

- [x] 5.1 Create Backend Deployment
  - [x] 5.1.1 Create templates/backend-deployment.yaml
  - [x] 5.1.2 Configure backend container with image and ports
  - [x] 5.1.3 Configure environment variables from ConfigMap
  - [x] 5.1.4 Configure environment variables from Secret
  - [x] 5.1.5 Configure volume mount for uploads directory
  - [x] 5.1.6 Configure liveness and readiness probes on /health endpoint
  - [x] 5.1.7 Configure resource requests and limits
  - [x] 5.1.8 Configure replica count from values

- [x] 5.2 Create Backend Service
  - [x] 5.2.1 Create templates/backend-service.yaml
  - [x] 5.2.2 Configure ClusterIP service on port 8000

- [x] 5.3 Create Backend PVC
  - [x] 5.3.1 Create templates/backend-pvc.yaml
  - [x] 5.3.2 Configure storage size and access mode

## Phase 6: Frontend Resources

- [x] 6.1 Create Frontend Deployment
  - [x] 6.1.1 Create templates/frontend-deployment.yaml
  - [x] 6.1.2 Configure frontend container with image and ports
  - [x] 6.1.3 Configure liveness and readiness probes on / endpoint
  - [x] 6.1.4 Configure resource requests and limits
  - [x] 6.1.5 Configure replica count from values

- [x] 6.2 Create Frontend Service
  - [x] 6.2.1 Create templates/frontend-service.yaml
  - [x] 6.2.2 Configure ClusterIP service on port 80

## Phase 7: Ingress Configuration

- [x] 7.1 Create Ingress resource
  - [x] 7.1.1 Create templates/ingress.yaml
  - [x] 7.1.2 Configure ingress class (nginx)
  - [x] 7.1.3 Configure host from values
  - [x] 7.1.4 Configure path / routing to frontend service
  - [x] 7.1.5 Configure path /api routing to backend service
  - [x] 7.1.6 Configure optional TLS settings
  - [x] 7.1.7 Add conditional rendering based on ingress.enabled value

## Phase 8: Database Initialization

- [x] 8.1 Create database initialization Job
  - [x] 8.1.1 Create templates/init-job.yaml
  - [x] 8.1.2 Configure Job with backend image
  - [x] 8.1.3 Configure command to run run_all_migrations.py
  - [x] 8.1.4 Configure environment variables from ConfigMap and Secret
  - [x] 8.1.5 Configure Helm hooks for pre-install and pre-upgrade
  - [x] 8.1.6 Configure restart policy and backoff limit
  - [x] 8.1.7 Add initContainer to wait for MySQL readiness

## Phase 9: Documentation

- [x] 9.1 Create Helm Chart README
  - [x] 9.1.1 Create helm/yaoyaoji/README.md
  - [x] 9.1.2 Document prerequisites (kind, kubectl, helm)
  - [x] 9.1.3 Document kind cluster setup with ingress
  - [x] 9.1.4 Document image building and loading
  - [x] 9.1.5 Document installation commands for dev and prod
  - [x] 9.1.6 Document configuration values
  - [x] 9.1.7 Document how to access the application
  - [x] 9.1.8 Document upgrade and rollback procedures
  - [x] 9.1.9 Document troubleshooting tips

- [x] 9.2 Create post-installation notes
  - [x] 9.2.1 Create templates/NOTES.txt
  - [x] 9.2.2 Add commands to check deployment status
  - [x] 9.2.3 Add commands to access the application
  - [x] 9.2.4 Add commands to view logs


## Phase 10: Testing and Validation

- [ ] 10.1 Validate Helm Chart
  - [ ] 10.1.1 Run helm lint on the chart
  - [ ] 10.1.2 Run helm template to verify rendering
  - [ ] 10.1.3 Run helm install --dry-run to validate

- [ ] 10.2 Test development deployment
  - [ ] 10.2.1 Create kind cluster with ingress support
  - [ ] 10.2.2 Build and load backend image
  - [ ] 10.2.3 Build and load frontend image
  - [ ] 10.2.4 Install chart with values-dev.yaml
  - [ ] 10.2.5 Verify all pods are running
  - [ ] 10.2.6 Verify services are created
  - [ ] 10.2.7 Verify ingress is configured
  - [ ] 10.2.8 Test frontend access via browser
  - [ ] 10.2.9 Test backend API health endpoint
  - [ ] 10.2.10 Test database connectivity
  - [ ] 10.2.11 Verify data persistence after pod restart

- [ ] 10.3 Test production configuration
  - [ ] 10.3.1 Render templates with values-prod.yaml
  - [ ] 10.3.2 Verify replica counts are correct
  - [ ] 10.3.3 Verify resource limits are appropriate

- [ ] 10.4 Test upgrade and rollback
  - [ ] 10.4.1 Make a change to values and upgrade
  - [ ] 10.4.2 Verify rolling update works
  - [ ] 10.4.3 Test helm rollback command
  - [ ] 10.4.4 Verify application still works after rollback

## Phase 11: Final Cleanup and Documentation

- [ ] 11.1 Update project root README
  - [ ] 11.1.1 Add section about Kubernetes deployment
  - [ ] 11.1.2 Link to Helm Chart README
  - [ ] 11.1.3 Document docker-compose.yml is for local development only

- [ ] 11.2 Verify all cleanup tasks completed
  - [ ] 11.2.1 Confirm test scripts are deleted
  - [ ] 11.2.2 Confirm individual migration scripts are deleted
  - [ ] 11.2.3 Confirm .gitignore is updated
  - [ ] 11.2.4 Confirm docker-compose.yml is preserved

- [ ] 11.3 Create deployment checklist
  - [ ] 11.3.1 Document pre-deployment checklist
  - [ ] 11.3.2 Document post-deployment verification steps
  - [ ] 11.3.3 Document common issues and solutions
