# Tools Required for Azure Deployment

Complete list of tools needed to deploy and run the Azure AI Search multimodal project.

---

## ✅ Currently Have

| Tool | Version | Status |
|------|---------|--------|
| Python | 3.12.3 | ✅ Installed |
| pip | Latest | ✅ Installed |
| Git | Latest | ✅ Installed |

---

## ❌ Need to Install

### 1. Azure CLI

**What it does:** Deploy and manage Azure resources via command line

**Installation:**

```bash
# Linux (Ubuntu/Debian)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify installation
az --version

# Should show: azure-cli 2.x.x
```

**After installation:**

```bash
# Login to Azure
az login --use-device-code

# The --use-device-code flag is useful for remote/headless sessions
# Follow the URL and enter the code shown

# Verify you're logged in
az account show

# List available subscriptions
az account list --output table

# Set default subscription (if you have multiple)
az account set --subscription "Your Subscription Name"
```

**Official docs:** [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

---

### 2. jq (JSON processor)

**What it does:** Parse JSON output from Azure CLI

**Installation:**

```bash
sudo apt-get update
sudo apt-get install jq

# Verify
jq --version
```

Used by `deploy.sh` to extract deployment outputs.

---

## ⚠️ Azure Prerequisites

### 1. Azure Subscription

**Required:**
- Active Azure subscription
- Payment method configured
- Owner or Contributor role on subscription

**Check:**
```bash
az account show
```

---

### 2. Azure OpenAI Access ⚠️ **BLOCKER**

**Status:** Requires approval from Microsoft

**How to request:**

1. Go to [https://aka.ms/oai/access](https://aka.ms/oai/access)
2. Fill out the form:
   - Business email
   - Company name
   - Use case description
   - Expected usage
3. Wait for approval email
4. Typical wait time: **Days to weeks**

**Why it's required:**
- GPT-4o for multimodal embeddings
- Without it, you can't generate image embeddings
- Core functionality of this repo

**Alternative while waiting:**
- Use text-only embeddings with Azure AI Search
- Switch to Computer Vision API for image embeddings (different approach)

---

### 3. Resource Quotas

**Check available quotas:**

```bash
# Check AI Search quota
az search service list --output table

# Check Cognitive Services quota
az cognitiveservices account list --output table
```

**Required quotas:**
- Azure AI Search: 1 Standard tier service
- Azure OpenAI: 1 S0 tier instance
- Storage: 1 Standard_LRS account

---

## 📦 Python Dependencies

Install via `requirements.txt`:

```bash
pip install -r requirements.txt
```

**Key packages:**
- `azure-search-documents` - Azure AI Search SDK
- `azure-storage-blob` - Blob storage SDK
- `openai` - Azure OpenAI SDK
- `streamlit` - GUI framework
- `Pillow` - Image processing

---

## 🚀 Quick Install Guide

### Step 1: Install Azure CLI

```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Step 2: Install jq

```bash
sudo apt-get install jq
```

### Step 3: Login to Azure

```bash
az login --use-device-code
```

### Step 4: Verify Setup

```bash
# Check Azure CLI
az --version

# Check logged in
az account show

# Check jq
jq --version

# Check Python
python3 --version
```

### Step 5: Request Azure OpenAI Access

Go to [https://aka.ms/oai/access](https://aka.ms/oai/access) and submit request.

**⏳ Wait for approval before deploying!**

---

## 🎯 Deployment Checklist

- [ ] Azure CLI installed
- [ ] jq installed
- [ ] Logged into Azure (`az login`)
- [ ] Azure subscription active
- [ ] **Azure OpenAI access approved** ⚠️
- [ ] Resource quotas available
- [ ] Python dependencies installed

**When all checked, run:**

```bash
./deploy.sh
```

---

## 🆘 Troubleshooting

### "az: command not found"

Azure CLI not installed. Run:
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### "Please run 'az login' to setup account"

Not logged in. Run:
```bash
az login --use-device-code
```

### "jq: command not found"

Install jq:
```bash
sudo apt-get install jq
```

### "Deployment quota exceeded"

Check quotas:
```bash
az quota list --location swedencentral
```

Request quota increase in Azure Portal.

### "Azure OpenAI not available"

You need approval. Request at [aka.ms/oai/access](https://aka.ms/oai/access).

---

## 📚 Resources

- [Azure CLI Docs](https://learn.microsoft.com/en-us/cli/azure/)
- [Azure AI Search Docs](https://learn.microsoft.com/en-us/azure/search/)
- [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Bicep Docs](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/)

---

## ⏱️ Estimated Setup Time

| Task | Time |
|------|------|
| Install Azure CLI | 5 min |
| Install jq + Python deps | 2 min |
| Azure login | 2 min |
| **Request OpenAI access** | **Days to weeks** ⏳ |
| Run deployment script | 10 min |
| **Total** | **~20 min + wait time** |

**The Azure OpenAI access approval is the bottleneck.**

Without it, you can deploy infrastructure but can't use multimodal features.
