#!/usr/bin/env python3
"""
Create Azure AI Search index with vector fields for multimodal search.
"""

import argparse
import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SimpleField,
    SearchableField
)
from azure.core.credentials import AzureKeyCredential


def create_multimodal_index(search_service: str, index_name: str, admin_key: str):
    """
    Create an Azure AI Search index with multimodal vector fields.
    
    Supports:
    - Text content indexing
    - Image embeddings (GPT-4o Vision)
    - Hybrid search (vector + keyword)
    - Semantic ranking
    """
    
    endpoint = f"https://{search_service}.search.windows.net"
    client = SearchIndexClient(endpoint=endpoint, credential=AzureKeyCredential(admin_key))
    
    # Define vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )
    
    # Define semantic search configuration
    semantic_search = SemanticSearch(
        configurations=[
            SemanticConfiguration(
                name="semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[
                        SemanticField(field_name="content"),
                        SemanticField(field_name="image_description")
                    ]
                )
            )
        ]
    )
    
    # Define index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, searchable=True),
        SearchableField(name="content", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="content_type", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="file_path", type=SearchFieldDataType.String),
        SearchableField(name="image_description", type=SearchFieldDataType.String, searchable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        ),
        SearchField(
            name="image_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=1536,
            vector_search_profile_name="vector-profile"
        ),
        SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset),
    ]
    
    # Create index
    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    result = client.create_or_update_index(index)
    print(f"✅ Created index: {result.name}")
    print(f"   Fields: {len(result.fields)}")
    print(f"   Vector fields: content_vector, image_vector")
    print(f"   Vector dimensions: 1536 (GPT-4o)")
    return result


def main():
    parser = argparse.ArgumentParser(description="Create Azure AI Search multimodal index")
    parser.add_argument("--search-service", required=True, help="Azure AI Search service name")
    parser.add_argument("--index-name", default="multimodal-docs", help="Index name")
    parser.add_argument("--admin-key", help="Admin API key (or set AZURE_SEARCH_ADMIN_KEY env var)")
    
    args = parser.parse_args()
    
    admin_key = args.admin_key or os.getenv("AZURE_SEARCH_ADMIN_KEY")
    if not admin_key:
        raise ValueError("Admin key required: --admin-key or AZURE_SEARCH_ADMIN_KEY")
    
    create_multimodal_index(args.search_service, args.index_name, admin_key)


if __name__ == "__main__":
    main()
