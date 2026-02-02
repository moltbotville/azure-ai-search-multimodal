#!/usr/bin/env python3
"""
Query the Azure AI Search multimodal index.
"""

import argparse
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from scripts.utils.embeddings import get_embeddings_client


def text_search(search_client: SearchClient, query: str, top: int = 5):
    """Perform hybrid text + vector search."""
    
    # Get embeddings client
    embeddings = get_embeddings_client()
    query_vector = embeddings.encode_text(query)
    
    # Hybrid search: keyword + vector
    results = search_client.search(
        search_text=query,
        vector_queries=[{
            "vector": query_vector,
            "k_nearest_neighbors": top,
            "fields": "content_vector,image_vector"
        }],
        select=["title", "content", "content_type", "file_path", "image_description"],
        top=top
    )
    
    print(f"\n🔍 Search results for: '{query}'\n")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']} ({result['content_type']})")
        print(f"   Score: {result['@search.score']:.4f}")
        print(f"   Path: {result['file_path']}")
        
        if result.get('image_description'):
            print(f"   Description: {result['image_description'][:100]}...")
        elif result.get('content'):
            print(f"   Content: {result['content'][:100]}...")
        
        print("-" * 80)


def image_search(search_client: SearchClient, image_path: str, top: int = 5):
    """Search using an image query."""
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Get embeddings client
    embeddings = get_embeddings_client()
    image_vector, description = embeddings.encode_image(image_path)
    
    print(f"\n🖼️  Image query: {image_path}")
    print(f"   Generated description: {description[:100]}...\n")
    
    # Vector-only search
    results = search_client.search(
        search_text=None,
        vector_queries=[{
            "vector": image_vector,
            "k_nearest_neighbors": top,
            "fields": "content_vector,image_vector"
        }],
        select=["title", "content_type", "file_path", "image_description"],
        top=top
    )
    
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']} ({result['content_type']})")
        print(f"   Score: {result['@search.score']:.4f}")
        print(f"   Path: {result['file_path']}")
        
        if result.get('image_description'):
            print(f"   Description: {result['image_description'][:100]}...")
        
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Query Azure AI Search multimodal index")
    parser.add_argument("--search-service", required=True, help="Azure AI Search service name")
    parser.add_argument("--index-name", default="multimodal-docs", help="Index name")
    parser.add_argument("--query-key", help="Query API key (or set AZURE_SEARCH_QUERY_KEY env var)")
    
    # Query options
    parser.add_argument("--query", "-q", help="Text query")
    parser.add_argument("--image-query", "-i", help="Path to query image")
    parser.add_argument("--top", type=int, default=5, help="Number of results")
    
    args = parser.parse_args()
    
    query_key = args.query_key or os.getenv("AZURE_SEARCH_QUERY_KEY")
    if not query_key:
        raise ValueError("Query key required: --query-key or AZURE_SEARCH_QUERY_KEY")
    
    endpoint = f"https://{args.search_service}.search.windows.net"
    search_client = SearchClient(
        endpoint=endpoint,
        index_name=args.index_name,
        credential=AzureKeyCredential(query_key)
    )
    
    if args.query:
        text_search(search_client, args.query, args.top)
    elif args.image_query:
        image_search(search_client, args.image_query, args.top)
    else:
        print("❌ Provide either --query or --image-query")
        parser.print_help()


if __name__ == "__main__":
    main()
