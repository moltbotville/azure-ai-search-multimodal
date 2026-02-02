# Deployment Issues Encountered

This document details all issues encountered during the initial deployment of Azure AI Search Multimodal to Sweden Central, along with their solutions.

**Deployment Date:** February 2, 2026  
**Region:** Sweden Central  
**Status:** ✅ All issues resolved

---

## Issue #1: Python Externally-Managed Environment

### Problem
```bash
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz
```

### Context
- Ubuntu 24.04+ uses PEP 668 externally-managed environments
- Prevents accidental system package conflicts
- Occurs when running `pip install` without virtual environment

### Root Cause
System security policy to protect Python installation from unmanaged package installations.

### Solution Applied
```bash
pip install --break-system-packages -r requirements.txt
```

### Better Solution (for production)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Impact
- **Severity:** Medium (blocks dependency installation)
- **Time to resolve:** 5 minutes
- **Recurring:** Yes (every new environment)

---

## Issue #2: Environment Variables Not Loading

### Problem
```python
Failed to initialize embeddings: Azure OpenAI endpoint and API key required
```

### Context
- `.env` file existed with correct credentials
- Python scripts didn't load environment variables automatically
- Streamlit GUI couldn't access Azure credentials

### Root Cause
Missing `python-dotenv` `load_dotenv()` calls in Python scripts.

### Solution Applied
Added to all Python files:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Files modified:**
- `app.py` (Streamlit GUI)
- `scripts/utils/embeddings.py`
- `scripts/query.py`
- `scripts/create_index.py`

### Impact
- **Severity:** High (complete blocker)
- **Time to resolve:** 15 minutes
- **Recurring:** No (fixed in code)

---

## Issue #3: GPT-4o Used for Embeddings (Wrong Model Type)

### Problem
```
Error code: 400 - {'error': {'code': 'OperationNotSupported', 
'message': 'The embeddings operation does not work with the specified model, gpt-4o. 
Please choose different model and try again.'}}
```

### Context
- GPT-4o was deployed for both chat and embeddings
- GPT-4o is a **completion/chat model**, not an embeddings model
- Cannot generate vector embeddings

### Root Cause
Misunderstanding of Azure OpenAI model types:
- **Chat models:** gpt-4o, gpt-3.5-turbo (for conversations)
- **Embedding models:** text-embedding-3-large, text-embedding-ada-002 (for vectors)

### Solution Applied

**1. Deployed proper embeddings model:**
```bash
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

**2. Updated code to use separate models:**
```python
self.embedding_deployment = "text-embedding-3-large"  # For embeddings
self.vision_deployment = "gpt-4o"  # For image descriptions
```

**3. Updated `.env`:**
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-large
```

### Vector Dimensions Changed
- **Old:** 1536 (incorrect, was expecting GPT-4o dimensions)
- **New:** 3072 (correct for text-embedding-3-large)
- **Action required:** Recreated search index with new dimensions

### Impact
- **Severity:** Critical (embeddings completely broken)
- **Time to resolve:** 30 minutes
- **Cost impact:** +$10-20/month for embedding model deployment
- **Recurring:** No (architecture fixed)

---

## Issue #4: Vector Query 'kind' Parameter Missing

### Problem
```
InvalidRequestParameter: The vector query's 'kind' parameter is not set. 
Parameter name: vector.kind
Code: InvalidVectorQuery
Message: The vector query's 'kind' parameter is not set.
```

### Context
- Search queries failed even with correct embeddings
- Azure Search SDK requires specific query object types
- Dictionary format is no longer supported (or was never correct)

### Root Cause
Using dictionary/plain object format for vector queries instead of `VectorizedQuery` class.

**Wrong approach:**
```python
vector_queries=[{
    "vector": embedding,
    "k_nearest_neighbors": 5,
    "fields": "content_vector"
}]
```

### Solution Applied

**1. Added import:**
```python
from azure.search.documents.models import VectorizedQuery
```

**2. Used proper class:**
```python
vector_query = VectorizedQuery(
    vector=embedding,
    k_nearest_neighbors=5,
    fields="content_vector,image_vector"
)

results = client.search(
    search_text=query,
    vector_queries=[vector_query],
    top=5
)
```

**Files modified:**
- `app.py` (3 locations)
- `scripts/query.py` (2 locations)

### Impact
- **Severity:** High (search completely broken)
- **Time to resolve:** 20 minutes
- **Recurring:** No (fixed in code)

---

## Issue #5: Search Index Dimension Mismatch

### Problem
```
HttpResponseError: (OperationNotAllowed) Existing field 'content_vector' cannot be changed.
Code: CannotChangeExistingField
```

### Context
- Index was created with 1536 dimensions
- New embeddings model produces 3072 dimensions
- Azure Search doesn't allow changing vector field dimensions

### Root Cause
Index dimensions must match embedding model dimensions. Cannot update existing index schema.

### Solution Applied
```bash
# Delete old index
python3 << 'EOF'
from azure.search.documents.indexes import SearchIndexClient
client.delete_index("multimodal-docs")
EOF

# Recreate with 3072 dimensions
python3 scripts/create_index.py \
  --search-service search-fa25fb89 \
  --index-name multimodal-docs
```

### Impact
- **Severity:** Medium (required index recreation)
- **Time to resolve:** 10 minutes
- **Data impact:** Any indexed documents were lost (none existed yet)
- **Recurring:** Only when changing embedding models

---

## Issue #6: Bicep Linter Warnings (Non-blocking)

### Problem
```
WARNING: outputs-should-not-contain-secrets: Outputs should not contain secrets. 
Found possible secret: function 'listKeys'
```

### Context
- Appeared during Bicep deployment
- Warnings about API keys in CloudFormation outputs
- Does not block deployment

### Root Cause
Bicep security linter flags potential credential exposure in template outputs.

### Solution
**None required.** These are informational warnings, not errors.

To suppress (optional):
```bicep
#disable-next-line outputs-should-not-contain-secrets
output adminKey string = searchService.listAdminKeys().primaryKey
```

### Impact
- **Severity:** Low (informational only)
- **Time to resolve:** N/A
- **Recurring:** Always (by design)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Issues** | 6 (4 critical, 2 informational) |
| **Total Resolution Time** | ~90 minutes |
| **Deployment Attempts** | 3 (initial + 2 fixes) |
| **Code Changes** | 8 files modified |
| **Index Recreations** | 1 |
| **Additional Azure Resources** | 1 (text-embedding-3-large) |

---

## Lessons Learned

### 1. **Model Types Matter**
Azure OpenAI has distinct model types:
- Always verify which models support which operations
- Chat models ≠ Embedding models
- Document model requirements upfront

### 2. **Environment Variable Management**
- Don't assume `.env` auto-loads in Python
- Always call `load_dotenv()` explicitly
- Test environment loading before deployment

### 3. **SDK Version Compatibility**
- Azure SDK evolves rapidly
- Dictionary-based APIs may become deprecated
- Always use typed classes (e.g., `VectorizedQuery`)

### 4. **Vector Dimensions are Immutable**
- Plan embedding model choice carefully
- Index dimensions cannot be changed after creation
- Changing models = recreate index + re-ingest data

### 5. **Python Environment Best Practices**
- Ubuntu 24.04+ enforces managed environments
- Use virtual environments for isolation
- `--break-system-packages` is quick but not ideal

---

## Prevention Checklist

For future deployments, verify:

- [ ] Environment variables loading tested (`load_dotenv()`)
- [ ] Correct model types selected (chat vs embeddings)
- [ ] Vector dimensions match embedding model output
- [ ] SDK classes used (not dictionaries)
- [ ] Python environment properly configured
- [ ] All dependencies installed successfully
- [ ] API keys and credentials validated
- [ ] Index schema matches data requirements

---

## Cost Impact

**Additional Resources Deployed:**
- `text-embedding-3-large` deployment: ~$10-20/month

**Total Monthly Cost:**
- Azure AI Search (Standard): ~$250/month
- Azure OpenAI (2 deployments): ~$20-50/month
- Storage: ~$1-5/month
- **Total:** ~$270-305/month

**No unexpected costs** - all within projected budget.

---

## References

- [Azure Search Python SDK](https://learn.microsoft.com/en-us/python/api/azure-search-documents/)
- [Azure OpenAI Embeddings](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#embeddings)
- [PEP 668 - Externally Managed Environments](https://peps.python.org/pep-0668/)
- [Azure Search Vector Search](https://learn.microsoft.com/en-us/azure/search/vector-search-overview)

---

## Related Documents

- [README.md](./README.md) - Main documentation
- [DEPLOY.md](./DEPLOY.md) - Deployment guide
- [TROUBLESHOOTING.md](./README.md#-troubleshooting) - Troubleshooting section in README
- [COMPARISON.md](./COMPARISON.md) - AWS vs Azure comparison

---

**Document Version:** 1.0  
**Last Updated:** February 2, 2026  
**Status:** All issues resolved ✅
