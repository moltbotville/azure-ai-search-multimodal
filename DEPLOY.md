# Deployment Guide - Azure AI Search Multimodal

## Prerequisites

1. **Azure Subscription** with permissions to create:
   - Resource Groups
   - Azure AI Search services
   - Azure OpenAI resources
   - Storage Accounts

2. **Azure CLI** installed and logged in:
   ```bash
   az login
   az account set --subscription "Your Subscription Name"
   ```

3. **Python 3.9+** installed

4. **Azure OpenAI Access** - Request at [oai.azure.com/portal](https://oai.azure.com/portal)

---

## Step-by-Step Deployment

### 1. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/azure-ai-search-multimodal.git
cd azure-ai-search-multimodal

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Azure Region and Names

```bash
export LOCATION="swedencentral"
export RESOURCE_GROUP="rg-ai-search-sweden"
export SEARCH_SERVICE="search-$(openssl rand -hex 4)"
export OPENAI_SERVICE="openai-$(openssl rand -hex 4)"
export STORAGE_ACCOUNT="st$(openssl rand -hex 6)"
```

### 3. Create Resource Group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 4. Deploy Infrastructure with Bicep

```bash
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infrastructure/main.bicep \
  --parameters location=$LOCATION \
  --parameters searchServiceName=$SEARCH_SERVICE \
  --parameters storageAccountName=$STORAGE_ACCOUNT
```

**Save the outputs:**
- `searchServiceEndpoint`
- `searchServiceKey`
- `storageConnectionString`

### 5. Deploy Azure OpenAI

```bash
# Create OpenAI resource
az cognitiveservices account create \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0 \
  --yes

# Get endpoint and key
OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint \
  --output tsv)

OPENAI_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --query key1 \
  --output tsv)

echo "OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "OpenAI Key: $OPENAI_KEY"
```

### 6. Deploy GPT-4o Model

```bash
az cognitiveservices account deployment create \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 10
```

**Wait ~2 minutes for deployment to complete.**

### 7. Configure Environment

```bash
cp .env.example .env

# Edit .env with your values
nano .env
```

Fill in:
```bash
AZURE_SEARCH_SERVICE_NAME=$SEARCH_SERVICE
AZURE_SEARCH_ADMIN_KEY=<from step 4 outputs>
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY=$OPENAI_KEY
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

### 8. Create Search Index

```bash
python scripts/create_index.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs \
  --admin-key $SEARCH_ADMIN_KEY
```

**Expected output:**
```
✅ Created index: multimodal-docs
   Fields: 9
   Vector fields: content_vector, image_vector
   Vector dimensions: 1536 (GPT-4o)
```

### 9. Test with Sample Data

```bash
# Upload test images (coming soon)
python scripts/index_documents.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs \
  --data-path ./sample-data/

# Query
python scripts/query.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs \
  --query "mountain landscapes"
```

---

## Cost Monitoring

```bash
# Check current costs
az consumption usage list \
  --resource-group $RESOURCE_GROUP \
  --start-date $(date -d '30 days ago' +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d)

# Set budget alert
az consumption budget create \
  --resource-group $RESOURCE_GROUP \
  --budget-name monthly-limit \
  --amount 500 \
  --time-period monthly
```

---

## Teardown

```bash
# Delete everything
az group delete \
  --name $RESOURCE_GROUP \
  --yes --no-wait

# Verify deletion
az group list --query "[?name=='$RESOURCE_GROUP']"
```

---

## Troubleshooting

### "GPT-4o deployment not found"
Wait 2-5 minutes after creating the deployment. Check status:
```bash
az cognitiveservices account deployment show \
  --name $OPENAI_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o
```

### "Search service quota exceeded"
Free tier doesn't support vector search. Upgrade to Basic or Standard:
```bash
az search service update \
  --name $SEARCH_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --sku standard
```

### "Invalid API key"
Regenerate keys:
```bash
az search admin-key renew \
  --service-name $SEARCH_SERVICE \
  --resource-group $RESOURCE_GROUP \
  --key-kind primary
```

---

## Region Availability

**Sweden Central** supports:
- ✅ Azure AI Search (all tiers)
- ✅ Azure OpenAI GPT-4o
- ✅ Storage Accounts
- ✅ Computer Vision (for alternative image embeddings)

**Alternative regions:**
- East US 2
- West Europe
- UK South
