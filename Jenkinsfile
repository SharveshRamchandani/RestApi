pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        AWS_REGION     = 'us-east-1'
        ECR_REPO_API   = 'n8n-pop-api'
        ECR_REPO_WORKER= 'n8n-pop-worker'
        IMAGE_TAG      = "${env.BUILD_NUMBER}"
        EKS_CLUSTER    = 'my-n8n-cluster'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Login to AWS ECR') {
            steps {
                script {
                    sh "aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    sh "docker build -t ${ECR_REPO_API}:${IMAGE_TAG} -f api/Dockerfile ."
                    sh "docker build -t ${ECR_REPO_WORKER}:${IMAGE_TAG} -f ingest/Dockerfile ."
                }
            }
        }

        stage('Push to ECR') {
            steps {
                script {
                    // Tag for ECR
                    sh "docker tag ${ECR_REPO_API}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_API}:${IMAGE_TAG}"
                    sh "docker tag ${ECR_REPO_WORKER}:${IMAGE_TAG} ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_WORKER}:${IMAGE_TAG}"
                    
                    // Push
                    sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_API}:${IMAGE_TAG}"
                    sh "docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_WORKER}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                script {
                    // Update kubeconfig
                    sh "aws eks update-kubeconfig --region ${AWS_REGION} --name ${EKS_CLUSTER}"
                    
                    // Replace image tag in k8s manifests (simple sed replacement for demo)
                    // In real production, use Helm or Kustomize
                    sh "sed -i 's|image: .*n8n-pop-api:.*|image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_API}:${IMAGE_TAG}|' infra/k8s/api.yaml"
                    sh "sed -i 's|image: .*n8n-pop-worker:.*|image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_WORKER}:${IMAGE_TAG}|' infra/k8s/worker.yaml"
                    
                    // Apply
                    sh "kubectl apply -f infra/k8s/dependencies.yaml"
                    sh "kubectl apply -f infra/k8s/secrets.yaml"
                    sh "kubectl apply -f infra/k8s/api.yaml"
                    sh "kubectl apply -f infra/k8s/worker.yaml"
                }
            }
        }
    }
}
