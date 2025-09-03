# QA On-Demand Environment

This repository provisions **on-demand QA environments** using **Pulumi**, **Docker Hub**, and **GitHub Actions**.  
Each feature branch automatically builds a Docker image, pushes it to Docker Hub, and deploys a temporary Azure Container Instance (ACI) for QA testing.  

---

## 🚀 Workflow Overview

1. Developer pushes code to a branch (e.g., `feature/my-new-feature`).  
2. GitHub Actions builds the Docker image from `./application`.  
3. The image is tagged with the branch name and pushed to **Docker Hub**.  
4. Pulumi provisions an **Azure Container Instance** using the new image.  
5. QA testers get a unique URL for validation.  
6. On PR close/merge, the environment can be destroyed.

---

## 🐳 Docker Hub Setup

1. Add GitHub secrets:
   - `DOCKER_USER` → Your Docker Hub username  
   - `DOCKER_PASSWORD` → Docker Hub access token  
   - `DOCKER_REPO` → Repository (e.g., `yourusername/qa-app`)  

---

## 🔑 Azure Setup

You’ll need a service principal with access to deploy resources. Add the following GitHub secrets:  

- `AZURE_CLIENT_ID`  
- `AZURE_CLIENT_SECRET`  
- `AZURE_SUBSCRIPTION_ID`  
- `AZURE_TENANT_ID`  

---

## 🔐 Pulumi Setup

Pulumi uses a local backend with passphrase encryption.  
Add the following secret:  

- `PULUMI_CONFIG_PASSPHRASE` → Your passphrase  

Pulumi configuration (`Pulumi.dev.yaml`):  

```yaml
config:
  azure:location: eastus
  azure:env: dev
```

