# Smart Manufacturing Machine Efficiency Prediction - GitOps MLOps Project

## 🚀 Project Overview

This project demonstrates a complete MLOps pipeline using GitOps principles for deploying a machine learning model that predicts manufacturing machine efficiency. The system combines modern DevOps practices with machine learning deployment, featuring continuous integration, containerization, and automated deployment using ArgoCD on Kubernetes.

## 🏗️ Architecture Overview

```
Developer → GitHub → Jenkins → Docker Hub → ArgoCD → Kubernetes → Production
```

The project implements a full GitOps workflow where:
- **Source Code Management**: GitHub repository hosts the ML model and application code
- **CI/CD Pipeline**: Jenkins automates build, test, and deployment processes
- **Containerization**: Docker packages the application for consistent deployment
- **Container Registry**: Docker Hub stores and manages container images
- **GitOps Deployment**: ArgoCD continuously synchronizes desired state with actual deployment
- **Orchestration**: Kubernetes (Minikube) manages container orchestration and scaling
- **Infrastructure**: Google Cloud Platform VM instances provide the compute resources

## 📋 Table of Contents

- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [CI/CD Pipeline](#cicd-pipeline)
- [GitOps Workflow](#gitops-workflow)
- [Infrastructure Setup](#infrastructure-setup)
- [Deployment Process](#deployment-process)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## 📁 Project Structure

```
.
├── src/                          # Source code for ML pipeline
│   ├── __init__.py
│   ├── custom_exception.py       # Custom exception handling
│   ├── logger.py                 # Logging configuration
│   ├── data_processing.py        # Data preprocessing and feature engineering
│   └── model_training.py         # Model training and evaluation
├── pipeline/                     # Training pipeline orchestration
│   ├── __init__.py
│   └── training_pipeline.py      # Main training pipeline
├── templates/                    # Flask application templates
│   └── index.html               # Web interface for predictions
├── manifests/                    # Kubernetes deployment manifests
│   ├── deployment.yaml          # Kubernetes deployment configuration
│   └── service.yaml             # Kubernetes service configuration
├── application.py               # Flask web application
├── dockerfile                   # Container configuration
├── Jenkinsfile                  # Jenkins CI/CD pipeline
├── setup.py                     # Python package configuration
└── README.md                    # Project documentation
```

## 🛠️ Technology Stack

### **Machine Learning & Data Processing**
- **Python 3.9**: Core programming language
- **scikit-learn**: Machine learning library for model training
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **joblib**: Model serialization and persistence

### **Web Application**
- **Flask**: Lightweight web framework
- **HTML/CSS/JavaScript**: Frontend technologies
- **Bootstrap**: Responsive UI framework

### **DevOps & Infrastructure**
- **Jenkins**: CI/CD automation server
- **Docker**: Containerization platform
- **Docker Hub**: Container registry
- **Kubernetes (Minikube)**: Container orchestration
- **ArgoCD**: GitOps continuous delivery tool

### **Cloud & Infrastructure**
- **Google Cloud Platform (GCP)**: Cloud infrastructure
- **VM Instances**: Compute resources
- **GitHub**: Version control and source code management

## 🤖 Machine Learning Pipeline

### **Data Processing (`src/data_processing.py`)**
The data processing pipeline handles:

1. **Data Loading**: Reads raw CSV data from the artifacts directory
2. **Feature Engineering**: 
   - Extracts time-based features (Year, Month, Day, Hour) from timestamps
   - Handles categorical variables with appropriate encoding
   - Scales numerical features using StandardScaler

3. **Data Preprocessing**:
   - **Categorical Encoding**: 
     - Operation Mode: Label encoding (Manual=0, Semi-Auto=1, Automatic=2)
     - Efficiency Status: Ordinal encoding (Low=0, Medium=1, High=2)
   - **Feature Selection**: 14 key features including operational, network, and temporal variables
   - **Data Splitting**: 80/20 train-test split with stratification

4. **Data Persistence**: Saves processed data and scaler for model training and inference

### **Model Training (`src/model_training.py`)**
The model training component:

1. **Algorithm**: Logistic Regression with multi-class classification
2. **Training**: Fits the model on scaled training data
3. **Evaluation**: Provides comprehensive metrics:
   - Accuracy
   - Precision (weighted average)
   - Recall (weighted average)
   - F1-Score (weighted average)
4. **Model Persistence**: Saves trained model using joblib

### **Feature Set**
The model uses 14 engineered features:
- **Operational**: Operation Mode, Temperature, Vibration, Power Consumption
- **Network**: Network Latency, Packet Loss Percentage
- **Quality**: Defect Rate, Production Speed, Error Rate
- **Maintenance**: Predictive Maintenance Score
- **Temporal**: Year, Month, Day, Hour

## 🔄 CI/CD Pipeline

### **Jenkins Pipeline (`Jenkinsfile`)**
The Jenkins pipeline automates the entire deployment process:

#### **Stage 1: Checkout GitHub**
```groovy
stage('Checkout Github') {
    steps {
        checkout scmGit(branches: [[name: '*/main']], 
                       extensions: [], 
                       userRemoteConfigs: [[credentialsId: 'github-token-vm', 
                                          url: 'https://github.com/rasinmuhammed/machine-efficiency-prediction.git']])
    }
}
```
- Pulls the latest code from the GitHub repository
- Uses secured credentials for authentication

#### **Stage 2: Build Docker Image**
```groovy
stage('Build Docker Image') {
    steps {
        script {
            dockerImage = docker.build("${DOCKER_HUB_REPO}:latest")
        }
    }
}
```
- Builds Docker image using the provided Dockerfile
- Tags the image with the latest version

#### **Stage 3: Push to Docker Hub**
```groovy
stage('Push Image to DockerHub') {
    steps {
        script {
            docker.withRegistry('https://registry.hub.docker.com', "${DOCKER_HUB_CREDENTIALS_ID}") {
                dockerImage.push('latest')
            }
        }
    }
}
```
- Pushes the built image to Docker Hub registry
- Uses secured credentials for Docker Hub authentication

#### **Stage 4: Install Tools**
```groovy
stage('Install Kubectl & ArgoCD CLI Setup') {
    steps {
        sh '''
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x kubectl
        mv kubectl /usr/local/bin/kubectl
        curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /usr/local/bin/argocd
        '''
    }
}
```
- Installs kubectl for Kubernetes cluster interaction
- Installs ArgoCD CLI for GitOps operations

#### **Stage 5: Deploy and Sync**
```groovy
stage('Apply Kubernetes & Sync App with ArgoCD') {
    steps {
        script {
            kubeconfig(credentialsId: 'kubeconfig', serverUrl: 'https://192.168.49.2:8443') {
                sh '''
                argocd login 34.134.210.98:30751 --username admin --password $(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d) --insecure
                argocd app sync gitops-app
                '''
            }
        }
    }
}
```
- Logs into ArgoCD using admin credentials
- Synchronizes the GitOps application with the latest changes

## 🔄 GitOps Workflow

### **ArgoCD Configuration**
ArgoCD implements the GitOps methodology by:

1. **Repository Monitoring**: Continuously monitors the GitHub repository for changes
2. **Automatic Synchronization**: Detects changes in Kubernetes manifests and automatically applies them
3. **Desired State Management**: Ensures the cluster state matches the desired state defined in Git
4. **Rollback Capabilities**: Provides easy rollback to previous versions if needed

### **Kubernetes Manifests**

#### **Deployment (`manifests/deployment.yaml`)**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: machine-efficiency-prediction
spec:
  replicas: 2
  selector:
    matchLabels:
      app: machine-efficiency-prediction
  template:
    metadata:
      labels:
        app: machine-efficiency-prediction
    spec:
      containers:
      - name: machine-efficiency-prediction
        image: muhammedrasin0/gitops-project:latest
        ports:
        - containerPort: 5002
```
- Defines deployment with 2 replicas for high availability
- Uses the Docker image from Docker Hub
- Exposes port 5002 for the Flask application

#### **Service (`manifests/service.yaml`)**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: machine-efficiency-prediction
spec:
  selector:
    app: machine-efficiency-prediction
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5002
  type: LoadBalancer
```
- Creates a LoadBalancer service for external access
- Maps external port 80 to container port 5002

## 🚀 Infrastructure Setup

### **Google Cloud Platform Setup**
1. **VM Instance Creation**: 
   - Created GCP VM instances for Jenkins and Kubernetes
   - Configured appropriate firewall rules
   - Set up networking for inter-service communication

2. **Minikube Installation**:
   - Installed Minikube on GCP VM
   - Configured kubectl for cluster management
   - Set up cluster networking

3. **ArgoCD Installation**:
   - Deployed ArgoCD on the Kubernetes cluster
   - Configured ArgoCD server with external access
   - Set up authentication and RBAC

### **Jenkins Setup**
1. **Jenkins Installation**: Installed on dedicated GCP VM
2. **Plugin Configuration**: 
   - Docker Pipeline plugin
   - Kubernetes plugin
   - Git plugin
3. **Credential Management**: 
   - GitHub token for repository access
   - Docker Hub credentials for image push
   - Kubernetes config for cluster access

## 📊 Deployment Process

### **Complete Deployment Flow**

1. **Developer commits code** to GitHub repository
2. **Jenkins webhook triggers** the CI/CD pipeline automatically
3. **Jenkins pulls latest code** from GitHub
4. **Docker image is built** containing the ML model and Flask app
5. **Image is pushed** to Docker Hub registry
6. **ArgoCD detects changes** in the repository
7. **Kubernetes manifests are applied** to the cluster
8. **Application is deployed** with load balancing and scaling
9. **Health checks ensure** application is running correctly

### **Monitoring and Logging**
- **Application Logs**: Centralized logging using the custom logger
- **Kubernetes Logs**: Pod and container logs accessible via kubectl
- **ArgoCD Dashboard**: Visual monitoring of deployment status

### **Prediction API**
The Flask application accepts the following parameters:
- `Operation_Mode`: 0 (Manual), 1 (Semi-Auto), 2 (Automatic)
- `Temperature_C`: Temperature in Celsius
- `Vibration_Hz`: Vibration frequency in Hz
- `Power_Consumption_kW`: Power consumption in kW
- `Network_Latency_ms`: Network latency in milliseconds
- `Packet_Loss_%`: Packet loss percentage
- `Quality_Control_Defect_Rate_%`: Defect rate percentage
- `Production_Speed_units_per_hr`: Production speed
- `Predictive_Maintenance_Score`: Maintenance score
- `Error_Rate_%`: Error rate percentage
- `Year`, `Month`, `Day`, `Hour`: Temporal features

## 🚀 Getting Started

### **Prerequisites**
- Google Cloud Platform account
- GitHub account
- Docker Hub account
- Basic knowledge of Kubernetes and Jenkins

### **Step-by-Step Setup**

#### **1. Infrastructure Setup**
```bash
# Create GCP VM instances
gcloud compute instances create jenkins-vm --machine-type=e2-medium --zone=us-central1-a
gcloud compute instances create k8s-vm --machine-type=e2-standard-2 --zone=us-central1-a
```

#### **2. Jenkins Installation**
```bash
# Install Jenkins on jenkins-vm
sudo apt update
sudo apt install openjdk-11-jdk -y
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt update
sudo apt install jenkins -y
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

#### **3. Kubernetes Setup**
```bash
# Install Minikube on k8s-vm
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
minikube start
```

#### **4. ArgoCD Installation**
```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

#### **5. Application Deployment**
1. Fork the repository
2. Configure Jenkins pipeline with your credentials
3. Set up ArgoCD application pointing to your repository
4. Trigger the pipeline or push changes to see GitOps in action

## 🔧 Troubleshooting

### **Common Issues**

#### **Jenkins Pipeline Failures**
```bash
# Check Jenkins logs
sudo journalctl -u jenkins -f

# Verify Docker installation
docker --version
docker ps
```

#### **ArgoCD Sync Issues**
```bash
# Check ArgoCD application status
argocd app get gitops-app
argocd app sync gitops-app --force
```

#### **Kubernetes Deployment Issues**
```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

#### **Application Not Accessible**
```bash
# Check service and endpoints
kubectl get svc
kubectl get endpoints
kubectl port-forward svc/machine-efficiency-prediction 8080:80
```

## 📈 Performance and Scaling

### **Model Performance**
- **Training Accuracy**: Monitored during training pipeline
- **Inference Speed**: Optimized for real-time predictions
- **Resource Usage**: Minimal CPU and memory footprint

### **Infrastructure Scaling**
- **Horizontal Pod Autoscaler**: Can be configured for automatic scaling
- **Resource Limits**: Set in deployment manifests
- **Load Balancing**: Handled by Kubernetes service

## 🔐 Security Considerations

### **Credential Management**
- All sensitive credentials stored in Jenkins credential store
- Kubernetes secrets used for sensitive data
- No hardcoded credentials in code

### **Network Security**
- Firewall rules configured for necessary ports only
- Internal cluster communication secured
- HTTPS can be configured for production use

## 🚀 Future Enhancements

### **Potential Improvements**
1. **Model Monitoring**: Implement model drift detection
2. **A/B Testing**: Deploy multiple model versions
3. **Advanced Monitoring**: Prometheus and Grafana integration
4. **Security**: Implement HTTPS and authentication
5. **Database Integration**: Add database for prediction history
6. **Notifications**: Slack/Email notifications for deployments

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request


*This project demonstrates modern MLOps practices with GitOps methodology for continuous deployment of machine learning models.*
