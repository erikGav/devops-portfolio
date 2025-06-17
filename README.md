# 🚀 DevOps Portfolio: Production-Ready Chat Application

A comprehensive end-to-end DevOps project showcasing modern cloud-native practices, from application development to production deployment on AWS with Kubernetes.

## 🏗️ Architecture Overview

This portfolio demonstrates a complete DevOps lifecycle with three main components working together:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   APPLICATION   │    │ INFRASTRUCTURE  │    │     GITOPS      │
│                 │    │                 │    │                 │
│ Flask Chat App  │───▶│ AWS + Terraform │───▶│ ArgoCD + Helm   │
│ Docker + CI/CD  │    │ EKS + VPC       │    │ Kubernetes      │
│ Testing + API   │    │ IAM + Security  │    │ Monitoring      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🎯 Live Demo

- **Application**: [https://chat-app.fun](https://chat-app.fun)
- **Alternative URL**: [https://www.chat-app.fun](https://www.chat-app.fun)

## ✨ Key Features & Capabilities

### Application Features

- **Real-time Chat**: Room-based conversations with automatic message updates
- **User Management**: Dynamic username changes with message history updates
- **Responsive Design**: Mobile-friendly interface with modern UI/UX
- **Data Persistence**: MySQL backend with full message history
- **Security**: XSS protection, input validation, and CORS configuration

### DevOps Capabilities Demonstrated

- **Complete CI/CD**: Automated testing, building, and deployment pipeline
- **Infrastructure as Code**: Modular Terraform for AWS resources
- **GitOps**: Declarative Kubernetes deployments with ArgoCD
- **Containerization**: Multi-stage Docker builds with security best practices
- **Monitoring**: Prometheus metrics, ELK stack logging, and health checks
- **Security**: Let's Encrypt SSL, AWS Secrets Manager, RBAC
- **High Availability**: Multi-AZ deployment with auto-scaling

## 🛠️ Technology Stack

### Application Layer

- **Backend**: Flask 3.1.0, SQLAlchemy, PyMySQL
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: MySQL 9.3.0 with replication
- **Web Server**: Nginx (reverse proxy + static files)

### Infrastructure Layer

- **Cloud Provider**: AWS (VPC, EKS, ECR, Secrets Manager, Route53)
- **Infrastructure as Code**: Terraform with modular architecture
- **Container Orchestration**: Amazon EKS (Kubernetes 1.33)
- **Load Balancing**: AWS Network Load Balancer + Ingress NGINX

### DevOps Toolchain

- **CI/CD**: Jenkins with GitLab integration
- **GitOps**: ArgoCD with App-of-Apps pattern
- **Package Management**: Helm 3.x charts
- **Monitoring**: Prometheus + Grafana stack
- **Logging**: Elasticsearch + Kibana + Fluent-bit
- **Security**: External Secrets Operator, Cert-Manager
- **Testing**: Pytest with 35+ tests achieving 80%+ coverage

## 📁 Project Structure

```
portfolio-project/
├── 📱 APPLICATION
│   ├── app/                    # Flask application core
│   ├── static/                # Frontend assets
│   ├── tests/                 # Comprehensive test suite (35+ tests)
│   ├── docker/                # Container definitions
│   ├── compose.yaml           # Production Docker Compose
│   ├── Jenkinsfile           # CI/CD pipeline
│   └── requirements.txt       # Dependencies
│
├── 🏗️ INFRASTRUCTURE
│   ├── modules/
│   │   ├── network/           # VPC, subnets, routing
│   │   ├── iam/               # IAM roles and policies
│   │   ├── cluster/           # EKS cluster configuration
│   │   ├── oidc/              # Service account authentication
│   │   └── helm-kubernetes/   # Kubernetes resources
│   ├── helm-values/           # Helm chart configurations
│   ├── main.tf                # Root module orchestration
│   └── vars.tfvars            # Environment configuration
│
└── 🚀 GITOPS
    ├── chat-app/              # Application Helm charts
    ├── infra-app/             # Infrastructure applications
    ├── chat-app-parent.yaml   # App-of-Apps for application
    └── infra-app-parent.yaml  # App-of-Apps for infrastructure
```

## 💬 Application Architecture

### Core Functionality

- **Room-based Chat**: Multi-room chat system with persistent history
- **Real-time Updates**: Automatic message polling and display
- **Username Management**: Dynamic username changes across message history
- **API-First Design**: RESTful API with comprehensive endpoints

### API Endpoints

| Method   | Endpoint           | Description                   |
| -------- | ------------------ | ----------------------------- |
| `GET`    | `/api/chat/<room>` | Retrieve all messages in room |
| `POST`   | `/api/chat/<room>` | Send new message              |
| `PUT`    | `/api/chat/<room>` | Update username               |
| `DELETE` | `/api/chat/<room>` | Clear room messages           |
| `GET`    | `/health`          | Health check endpoint         |
| `GET`    | `/metrics`         | Prometheus metrics            |
| `GET`    | `/metrics/json`    | JSON metrics dashboard        |

### Database Schema

```sql
CREATE TABLE chat (
    id INT PRIMARY KEY AUTO_INCREMENT,
    room VARCHAR(50) NOT NULL,
    date VARCHAR(50) NOT NULL,
    time VARCHAR(50) NOT NULL,
    username VARCHAR(50) NOT NULL,
    message TEXT NOT NULL
);
```

## 🏗️ Infrastructure Architecture

### AWS Components

- **EKS Cluster**: Kubernetes 1.33 with managed node groups (3x t3a.medium)
- **VPC**: Multi-AZ setup with public/private subnets
- **Load Balancing**: Network Load Balancer with cross-zone balancing
- **Storage**: GP3 EBS volumes with encryption
- **DNS & SSL**: Route53 + Let's Encrypt certificates

### Security Implementation

- **Network Security**: Private subnets, security groups, VPC CNI
- **Identity Management**: IRSA (IAM Roles for Service Accounts)
- **Secrets Management**: AWS Secrets Manager with External Secrets Operator
- **Certificate Management**: Automated SSL via Cert-Manager + Let's Encrypt
- **RBAC**: Kubernetes role-based access control

### Terraform Module Structure

- **Network Module**: VPC, subnets, routing, NAT Gateway
- **IAM Module**: Service roles and policies
- **Cluster Module**: EKS configuration and node groups
- **OIDC Module**: Service account authentication
- **Helm Module**: Core Kubernetes applications

## 🔄 CI/CD & GitOps

### Jenkins Pipeline Stages

1. **Checkout & Versioning**: Source retrieval and semantic versioning
2. **Testing**: Unit tests and E2E API testing
3. **Building**: Multi-stage Docker image creation
4. **Publishing**: ECR image publishing with tags
5. **Deployment**: GitOps repository updates triggering ArgoCD

### GitOps Workflow

- **ArgoCD**: App-of-Apps pattern for managing deployments
- **Automated Sync**: Continuous deployment with self-healing
- **Sync Waves**: Orchestrated deployment order (namespaces → secrets → infrastructure → applications)

### Deployment Strategy

- **Rolling Updates**: Zero-downtime deployments
- **Health Checks**: Readiness and liveness probes
- **Auto-scaling**: Horizontal pod autoscaling based on metrics

## 📊 Monitoring & Observability

### Metrics Collection

- **Prometheus**: Custom application metrics and system monitoring
- **Grafana**: Visualization dashboards
- **Custom Metrics**: Chat-specific metrics (messages, users, rooms)

### Centralized Logging

- **ELK Stack**: Elasticsearch, Kibana, Fluent-bit
- **Structured Logging**: JSON-formatted logs with request tracing
- **Log Aggregation**: Kubernetes pod logs with filtering

### Health Monitoring

- **Application Health**: `/health` endpoint with database connectivity
- **Infrastructure Health**: Node and pod health monitoring
- **Alert Manager**: Prometheus-based alerting

## 🧪 Testing Strategy

### Test Categories

- **Unit Tests**: Model validation and business logic (pytest)
- **Integration Tests**: API endpoint functionality
- **End-to-End Tests**: Complete workflow validation
- **Load Tests**: Custom bash scripts for API stress testing

### Test Metrics

- **Coverage**: 80%+ code coverage requirement
- **Test Count**: 35+ comprehensive tests
- **Automation**: Full CI integration with failure handling

## 🎯 Key Technical Achievements

### Infrastructure Excellence

- ✅ **Production-Ready AWS Deployment**: Multi-AZ EKS with high availability
- ✅ **Infrastructure as Code**: 100% Terraform-managed resources
- ✅ **Security Best Practices**: Multiple security layers and compliance
- ✅ **Cost Optimization**: Resource-efficient deployment strategies

### DevOps Mastery

- ✅ **Complete Automation**: End-to-end CI/CD pipeline
- ✅ **GitOps Implementation**: Declarative deployment management
- ✅ **Comprehensive Testing**: Automated testing at multiple levels
- ✅ **Monitoring & Observability**: Full-stack monitoring solution

### Application Development

- ✅ **Modern Architecture**: Containerized microservices approach
- ✅ **API Design**: RESTful API with comprehensive documentation
- ✅ **Frontend Development**: Responsive, mobile-friendly interface
- ✅ **Database Management**: Optimized queries and connection handling

## 🔍 Skills Demonstrated

### Cloud & Infrastructure

- **AWS Services**: EKS, VPC, ECR, Secrets Manager, Route53, IAM
- **Terraform**: Modular infrastructure design and state management
- **Kubernetes**: Container orchestration, RBAC, networking, storage
- **Docker**: Multi-stage builds, security scanning, optimization

### DevOps & Automation

- **CI/CD Pipelines**: Jenkins automation with GitLab integration
- **GitOps**: ArgoCD deployment patterns and sync strategies
- **Helm**: Chart development and dependency management
- **Monitoring**: Prometheus metrics and ELK stack implementation

### Development & Testing

- **Backend Development**: Flask, SQLAlchemy, API design
- **Frontend Development**: JavaScript, responsive design, UX/UI
- **Testing**: Unit, integration, and E2E testing strategies
- **Code Quality**: Linting, formatting, coverage analysis

### Security & Compliance

- **Identity Management**: RBAC, IRSA, service account security
- **Secrets Management**: Secure credential handling and rotation
- **Network Security**: VPC design, security groups, encryption
- **Certificate Management**: Automated SSL/TLS certificate provisioning

---

**This portfolio demonstrates end-to-end DevOps capabilities with modern cloud-native technologies, showcasing practical experience in building, deploying, and maintaining production-ready applications.**
