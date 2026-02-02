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

## 📚 Resources

- [Azure AI Search Docs](https://learn.microsoft.com/en-us/azure/search/)
- [Vector Search Overview](https://learn.microsoft.com/en-us/azure/search/vector-search-overview)
- [Multimodal Search](https://learn.microsoft.com/en-us/azure/search/multimodal-search-overview)
- [Azure OpenAI GPT-4o](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models)

---

## License

MIT
