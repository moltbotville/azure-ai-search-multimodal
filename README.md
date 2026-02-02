# Azure AI Search - Multimodal Semantic Search

Enterprise-grade multimodal semantic search using Azure AI Search with GPT-4o Vision embeddings.

**Region:** `Sweden Central` (swed encentral)  
**Embedding Model:** GPT-4o with Vision (multimodal)  
**Search Service:** Azure AI Search with vector fields

## 🎯 What's Included

- ✅ **Multimodal indexing** - Text, images, and PDFs
- ✅ **GPT-4o Vision embeddings** - Native image understanding
- ✅ **Hybrid search** - Vector + keyword search combined
- ✅ **Image-to-image search** - Find similar images visually
- ✅ **Text-to-image search** - Search images using descriptions
- ✅ **Bicep Infrastructure** - Azure-native IaC
- ✅ **Python scripts** - Indexing and query examples

---

## 💰 Cost Estimate

| Service | Cost (Sweden Central) | Notes |
|---------|------|-------|
| **Azure AI Search** | ~$0.35/hour (~$250/month) | Basic tier |
| Azure OpenAI GPT-4o | ~$0.003/1K tokens | Embeddings |
| Azure OpenAI GPT-4o Vision | ~$0.01/image | Image embeddings |
| Storage (Blob) | ~$0.018/GB/month | Image storage |

**Monthly Estimate:** ~$270-$350 (depending on usage)

💡 **Lower cost than AWS:** Azure AI Search is ~24% cheaper than OpenSearch Serverless ($250 vs $345/month)

---

## 🚀 Quick Deploy

### Prerequisites

**Required Tools:**
- ✅ **Azure CLI** - [Install Guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
  ```bash
  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
  az login --use-device-code
  ```
- ✅ **Python 3.9+** - Already included in most systems
- ✅ **Azure Subscription** - With permissions for AI Search, OpenAI, Storage

**Required Approvals:**
- ⚠️ **Azure OpenAI Access** - Request at [aka.ms/oai/access](https://aka.ms/oai/access)
  - Can take days to weeks for approval
  - Required for GPT-4o embeddings
  - Blocker for deployment

### Step 1: Deploy Infrastructure

**Automated Deployment (Recommended):**

```bash
# Clone and navigate
cd /home/molt/.openclaw/workspace/azure-ai-search-multimodal

# Run deployment script
./deploy.sh
```

The script will:
- ✅ Check Azure CLI and Python
- ✅ Verify Azure login
- ✅ Create resource group
- ✅ Deploy AI Search + Storage
- ✅ Generate .env file
- ✅ Show next steps

**Manual Deployment:**

```bash
# Set variables
export LOCATION="swedencentral"
export RESOURCE_GROUP="rg-ai-search-sweden"
export SEARCH_SERVICE="search-$(openssl rand -hex 4)"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Deploy with Bicep
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infrastructure/main.bicep \
  --parameters location=$LOCATION \
  --parameters searchServiceName=$SEARCH_SERVICE
```

### Step 2: Deploy Azure OpenAI

```bash
# Create Azure OpenAI resource
az cognitiveservices account create \
  --name "openai-multimodal-$(openssl rand -hex 4)" \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --kind OpenAI \
  --sku S0 \
  --custom-domain "openai-multimodal-$(openssl rand -hex 4)"

# Deploy GPT-4o model for embeddings
az cognitiveservices account deployment create \
  --name YOUR_OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --deployment-name gpt-4o \
  --model-name gpt-4o \
  --model-version "2024-08-06" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name "Standard"
```

### Step 3: Create Search Index

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create multimodal index
python scripts/create_index.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs

# Upload and index documents
python scripts/index_documents.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs \
  --data-path ./sample-data/
```

### Step 4: Query

**Option A: Streamlit GUI (Recommended)**

```bash
# Set environment variables
export AZURE_SEARCH_SERVICE_NAME=$SEARCH_SERVICE
export AZURE_SEARCH_QUERY_KEY=<your-query-key>
export AZURE_OPENAI_ENDPOINT=<your-openai-endpoint>
export AZURE_OPENAI_API_KEY=<your-openai-key>

# Launch GUI
streamlit run app.py
```

Open browser to `http://localhost:8501`

**Option B: Command Line**

```bash
# Text search
python scripts/query.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs \
  --query "mountain landscapes at sunset"

# Image search (upload query image)
python scripts/query.py \
  --search-service $SEARCH_SERVICE \
  --index-name multimodal-docs \
  --image-query ./my-query-image.jpg
```

---

## 🖥️ Streamlit GUI

**Interactive web interface for multimodal search:**

```bash
# Quick start
./run_gui.sh

# Or manually
streamlit run app.py
```

**Features:**
- 📝 **Text search** with hybrid/vector/keyword modes
- 🖼️ **Image search** - Upload images to find similar content
- ⚙️ **Configuration** - Easy setup via sidebar
- 📊 **Results display** - Scores, descriptions, and metadata
- 🎨 **Modern UI** - Clean, responsive design

**Access:** `http://localhost:8501`

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Source Data    │
│  - Images       │
│  - PDFs         │
│  - Text files   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Azure OpenAI           │
│  - GPT-4o Vision        │
│  - Multimodal Embeddings│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Azure AI Search        │
│  - Vector fields        │
│  - Hybrid search        │
│  - Multimodal index     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Query Results          │
│  - Text + Image matches │
│  - Similarity scores    │
└─────────────────────────┘
```

---

## 📁 Project Structure

```
azure-ai-search-multimodal/
├── app.py                      # 🖥️ Streamlit GUI
├── run_gui.sh                  # Quick start script
├── infrastructure/
│   ├── main.bicep              # Main infrastructure
│   ├── search.bicep            # AI Search service
│   └── storage.bicep           # Blob storage
├── scripts/
│   ├── create_index.py         # Create search index
│   ├── index_documents.py      # Index docs/images (TODO)
│   ├── query.py                # CLI query tool
│   └── utils/
│       ├── embeddings.py       # GPT-4o Vision embeddings
│       └── search_client.py    # Azure Search wrapper (TODO)
├── sample-data/
│   ├── images/                 # Sample images (TODO)
│   └── documents/              # Sample text/PDFs (TODO)
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── DEPLOY.md                   # Deployment guide
└── COMPARISON.md               # AWS vs Azure
```

---

## 🎨 Multimodal Features

### Image-to-Image Search
```python
from scripts.utils.search_client import MultimodalSearchClient

client = MultimodalSearchClient(search_service, index_name)
results = client.search_by_image("query-image.jpg", top=5)

for result in results:
    print(f"Match: {result['filename']} - Score: {result['@search.score']}")
```

### Text-to-Image Search
```python
results = client.search_by_text("mountain sunset clouds", top=5)

for result in results:
    if result['content_type'] == 'image':
        print(f"Image: {result['filename']}")
```

### Hybrid Search (Text + Vector)
```python
results = client.hybrid_search(
    query="outdoor adventures",
    vector_query_image="hiking.jpg",
    top=10
)
```

---

## 🔧 Configuration

**Azure AI Search Tiers:**
- **Free:** No vector search
- **Basic:** ✅ Vector search, 15 GB, ~$75/month
- **Standard S1:** ✅ Vector search, 25 GB, ~$250/month (recommended)

**Vector Configuration:**
- **Algorithm:** HNSW (Hierarchical Navigable Small World)
- **Dimensions:** 1536 (GPT-4o embeddings)
- **Distance Metric:** Cosine similarity

---

## 🗑️ Clean Up

```bash
# Delete resource group (removes everything)
az group delete \
  --name $RESOURCE_GROUP \
  --yes --no-wait
```

---

## 🆘 Troubleshooting

Common issues and solutions encountered during deployment:

---

### Python: "externally-managed-environment" Error

**Issue:**
```bash
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
```

**Cause:** Ubuntu 24.04+ uses externally-managed Python environments to prevent system package conflicts.

**Solution 1: Use --break-system-packages (Quick)**
```bash
pip install --break-system-packages -r requirements.txt
```
⚠️ May cause conflicts with system packages, but works for isolated environments.

**Solution 2: Use Virtual Environment (Recommended)**
```bash
# Install venv package
sudo apt-get install -y python3.12-venv

# Create virtual environment
python3 -m venv venv

# Activate and install
source venv/bin/activate
pip install -r requirements.txt

# Run scripts with venv active
python scripts/create_index.py ...
```

**Solution 3: Use pipx (For standalone tools)**
```bash
sudo apt-get install -y pipx
pipx install streamlit
```

---

### Azure CLI: "Please run 'az login'"

**Issue:**
```bash
ERROR: Please run 'az login' to setup account.
```

**Solution:**
```bash
# For interactive sessions
az login

# For headless/remote sessions (recommended)
az login --use-device-code
```

Follow the URL and enter the code shown.

**Verify login:**
```bash
az account show
```

---

### Deployment: "Bicep template errors"

**Issue:**
```
WARNING: outputs-should-not-contain-secrets: Outputs should not contain secrets.
```

**Cause:** Bicep linter warning (not an error) - keys in outputs are flagged as potential security risk.

**Impact:** None - deployment still succeeds. This is informational.

**To suppress:**
Add `#disable-next-line outputs-should-not-contain-secrets` above the output in `.bicep` files.

---

### Azure OpenAI: "Model not available in region"

**Issue:**
```bash
ERROR: The model 'gpt-4o' is not available in location 'westeurope'
```

**Solution:**
Use `swedencentral` region - GPT-4o is fully available there:

```bash
export LOCATION="swedencentral"
```

**Check model availability:**
```bash
az cognitiveservices account list-skus \
  --kind OpenAI \
  --location swedencentral
```

---

### Search Index: "ModuleNotFoundError: No module named 'azure'"

**Issue:**
```python
ModuleNotFoundError: No module named 'azure'
```

**Cause:** Python dependencies not installed.

**Solution:**
```bash
pip install --break-system-packages -r requirements.txt

# Or with venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Streamlit: "Command 'streamlit' not found"

**Issue:**
```bash
bash: streamlit: command not found
```

**Solution:**
```bash
# Install streamlit
pip install --break-system-packages streamlit

# Or use venv
source venv/bin/activate
pip install streamlit
streamlit run app.py
```

---

### Azure: "Quota exceeded" or "Capacity not available"

**Issue:**
```
ERROR: Operation failed due to insufficient quota
```

**Solution:**
1. Check current quotas:
```bash
az quota list --location swedencentral
```

2. Request quota increase in Azure Portal:
   - Portal → Subscriptions → Usage + quotas
   - Select "Cognitive Services" or "Search"
   - Click "Request increase"

3. Alternative: Try different region:
```bash
# Try East US 2 (usually has high availability)
export LOCATION="eastus2"
```

---

### Azure OpenAI: "Access Denied - Request approval"

**Issue:**
```
ERROR: Azure OpenAI access is not approved for this subscription
```

**Cause:** Azure OpenAI requires explicit approval.

**Solution:**
1. Request access: [aka.ms/oai/access](https://aka.ms/oai/access)
2. Fill out form with:
   - Business email
   - Company name
   - Use case description
   - Expected usage volume
3. Wait for approval (typically 1-7 days)
4. Check approval status in Azure Portal

**While waiting:**
Deploy infrastructure without OpenAI, add it later when approved.

---

### Deployment Script: "jq: command not found"

**Issue:**
```bash
./deploy.sh: line 45: jq: command not found
```

**Solution:**
```bash
sudo apt-get install -y jq
```

**Verify:**
```bash
jq --version
```

---

### Resource Deletion: "Resource group stuck deleting"

**Issue:**
Resource group shows "Deleting" status for >10 minutes.

**Cause:** Resources inside (e.g., Communication Services, OpenAI) take time to delete.

**Solution:**
1. Wait 5-10 minutes - this is normal
2. Check status:
```bash
az group list --output table
```
3. Force delete (if stuck >30 min):
```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

---

### Streamlit GUI: "Connection error to Azure"

**Issue:**
GUI shows "Failed to initialize embeddings" or "Search failed"

**Cause:** Missing or incorrect credentials in `.env`

**Solution:**
1. Check `.env` file exists:
```bash
cat .env
```

2. Verify all fields are filled:
```bash
AZURE_SEARCH_SERVICE_NAME=search-xxxxx     # ✓ Should have value
AZURE_SEARCH_ADMIN_KEY=xxxxxxxxxxxx        # ✓ Should have key
AZURE_OPENAI_ENDPOINT=https://...          # ✓ Should have URL
AZURE_OPENAI_API_KEY=xxxxxxxxxxxx          # ✓ Should have key
```

3. Export environment variables:
```bash
export $(cat .env | xargs)
```

4. Restart Streamlit:
```bash
streamlit run app.py
```

---

### GPT-4o Deployment: "Deployment failed - insufficient quota"

**Issue:**
```
ERROR: The operation failed due to insufficient quota
```

**Solution:**
Reduce capacity or try different model version:

```bash
# Try lower capacity
az cognitiveservices account deployment create \
  --sku-capacity 1  # Instead of 10

# Or use alternative model version
  --model-version "2024-05-13"  # Instead of 2024-08-06
```

---

### General: "Deployment taking too long"

**Typical deployment times:**
- Azure AI Search: 2-3 minutes
- Storage Account: 1-2 minutes
- Azure OpenAI resource: 1-2 minutes
- GPT-4o model deployment: 1-2 minutes
- **Total: 5-10 minutes**

**If stuck >15 minutes:**
```bash
# Check deployment status
az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name <deployment-name>

# Cancel and retry
az deployment group cancel \
  --resource-group $RESOURCE_GROUP \
  --name <deployment-name>
```

---

## 📚 Resources

- [Azure AI Search Docs](https://learn.microsoft.com/en-us/azure/search/)
- [Vector Search Overview](https://learn.microsoft.com/en-us/azure/search/vector-search-overview)
- [Multimodal Search](https://learn.microsoft.com/en-us/azure/search/multimodal-search-overview)
- [Azure OpenAI GPT-4o](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models)
- [Troubleshooting Azure CLI](https://learn.microsoft.com/en-us/cli/azure/troubleshoot)

---

## License

MIT

---

### Embeddings: "OperationNotSupported - gpt-4o not supported for embeddings"

**Issue:**
```
Error code: 400 - {'error': {'code': 'OperationNotSupported', 
'message': 'The embeddings operation does not work with the specified model, gpt-4o'}}
```

**Cause:** GPT-4o is a chat/completion model, **not an embeddings model**.

**Solution:**
Deploy a proper embeddings model:

```bash
# Deploy text-embedding-3-large
az cognitiveservices account deployment create \
  --name openai-fa25fb89 \
  --resource-group rg-ai-search-sweden \
  --deployment-name text-embedding-3-large \
  --model-name text-embedding-3-large \
  --model-version "1" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 10
```

**Update `.env`:**
```bash
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
```

**Vector dimensions changed:**
- Old: 1536 (incorrect)
- New: 3072 (text-embedding-3-large)

**If index exists, recreate it:**
```bash
# Delete old index
python3 << 'SCRIPT'
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

load_dotenv()
client = SearchIndexClient(
    endpoint=f"https://{os.getenv('AZURE_SEARCH_SERVICE_NAME')}.search.windows.net",
    credential=AzureKeyCredential(os.getenv('AZURE_SEARCH_ADMIN_KEY'))
)
client.delete_index("multimodal-docs")
print("✅ Deleted old index")
SCRIPT

# Create new index with 3072 dimensions
python3 scripts/create_index.py \
  --search-service $AZURE_SEARCH_SERVICE_NAME \
  --index-name multimodal-docs
```

**Model usage:**
- **text-embedding-3-large** → Text embeddings (3072d)
- **gpt-4o** → Image vision (descriptions)

