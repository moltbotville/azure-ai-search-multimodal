# AWS Bedrock vs Azure AI Search - Comparison

This document compares the two semantic search implementations:

## Overview

| Feature | AWS Bedrock (eu-west-1) | Azure AI Search (Sweden Central) |
|---------|-------------------------|----------------------------------|
| **Multimodal Support** | ❌ Not yet (Nova coming) | ✅ Yes (GPT-4o Vision) |
| **Region** | Ireland | Sweden |
| **Text Embeddings** | Titan Text v2 (1024d) | GPT-4o (1536d) |
| **Image Embeddings** | N/A | GPT-4o Vision (1536d) |
| **Search Type** | Vector only | Vector + Keyword (hybrid) |
| **Monthly Cost** | ~$345 | ~$250-350 |

---

## Architecture Comparison

### AWS Bedrock Knowledge Base
```
Documents → S3
              ↓
        Bedrock Agent (ingestion)
              ↓
        Titan Embeddings (text-only)
              ↓
        OpenSearch Serverless (vectors)
              ↓
        Retrieve & Generate (Claude)
```

**Pros:**
- Fully managed end-to-end
- Tight integration with AWS services
- Bedrock Data Automation for parsing

**Cons:**
- No native multimodal yet in eu-west-1
- Higher cost ($11.50/day minimum)
- Limited to AWS ecosystem

---

### Azure AI Search
```
Documents → Azure Blob Storage
              ↓
        Custom indexing pipeline
              ↓
        GPT-4o embeddings (text + images)
              ↓
        Azure AI Search (vectors + inverted index)
              ↓
        Hybrid Search + Semantic Ranking
```

**Pros:**
- ✅ **Native multimodal** (images + text)
- ✅ **Hybrid search** (vector + keyword combined)
- ✅ **Lower cost** (~$250/month vs $345)
- ✅ **Semantic ranking** built-in
- Flexible - use any embedding model

**Cons:**
- More setup (custom indexing code)
- Need to manage vectorization yourself
- Requires Azure OpenAI access (request needed)

---

## Cost Breakdown

### AWS (eu-west-1)

| Service | Monthly Cost |
|---------|-------------|
| OpenSearch Serverless (2 OCU) | ~$345 |
| S3 Storage | ~$1 |
| Bedrock Embeddings (one-time) | ~$0.01 |
| Bedrock Queries | ~$0.10/query |
| **Total** | **~$345-350/month** |

**Daily:** ~$11.50

---

### Azure (Sweden Central)

| Service | Monthly Cost |
|---------|-------------|
| AI Search (Standard S1) | ~$250 |
| Storage (Blob) | ~$1-5 |
| OpenAI Embeddings | ~$10-50 |
| OpenAI Queries | ~$5-20 |
| **Total** | **~$270-330/month** |

**Daily:** ~$9.00

💰 **Azure is ~20-25% cheaper**

---

## Feature Comparison

### Text Search
- **AWS:** ✅ Full text + vector hybrid
- **Azure:** ✅ Full text + vector hybrid

### Image Search
- **AWS:** ❌ Text descriptions only (current)
- **Azure:** ✅ Native image embeddings

### Image-to-Image Search
- **AWS:** ❌ Not available
- **Azure:** ✅ Available with GPT-4o Vision

### Semantic Ranking
- **AWS:** ⚠️ Via LLM reranking
- **Azure:** ✅ Built-in semantic ranking

### Filters/Facets
- **AWS:** ✅ Via metadata filters
- **Azure:** ✅ Rich filtering + faceting

### Multimodal Queries
- **AWS:** ❌ Not yet
- **Azure:** ✅ Text + image queries

---

## When to Use Each

### Choose AWS Bedrock if:
- You're already in AWS ecosystem
- You want fully managed (less code)
- You're okay with text-only for now
- Nova Multimodal is coming to your region

### Choose Azure AI Search if:
- ✅ **You need multimodal NOW**
- ✅ **You want lower cost**
- ✅ **You want hybrid search**
- You're okay writing custom indexing code
- Sweden/Europe region works for you

---

## Migration Path

If you start with AWS and want to move to Azure:

1. **Export data** from S3
2. **Upload to Azure Blob Storage**
3. **Run Azure indexing pipeline**
4. **Switch application to Azure Search SDK**

Most code is portable (both use vector search concepts).

---

## Future Outlook

### AWS Bedrock
- **Nova Multimodal Embeddings** expanding to more regions
- Better cost optimization options coming
- Tighter integration with Bedrock Data Automation

### Azure AI Search
- **Computer Vision integration** for better image embeddings
- **Multi-vector fields** for richer representations
- **Foundry agent integration** for agentic workflows

---

## Recommendation

**For this use case (multimodal search in Sweden):**

✅ **Azure AI Search is the clear winner**

**Reasons:**
1. Native multimodal support (images + text)
2. ~20% lower cost
3. Sweden Central region available
4. Hybrid search built-in
5. More flexible architecture

**When to reconsider AWS:**
- If Nova Multimodal arrives in eu-west-1
- If you need tight AWS ecosystem integration
- If fully-managed is critical

---

**Related Repos:**
- [AWS Bedrock Knowledge Base](https://github.com/moltbotville/bedrock-knowledge-base)
- [Azure AI Search Multimodal](https://github.com/moltbotville/azure-ai-search-multimodal)
