#!/usr/bin/env python3
"""
Streamlit GUI for Azure AI Search Multimodal Semantic Search
"""

# Load environment variables FIRST (before any other imports)
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
from io import BytesIO
from PIL import Image
import base64
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from scripts.utils.embeddings import get_embeddings_client

# Page config
st.set_page_config(
    page_title="Azure AI Search - Multimodal",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0078D4;
        margin-bottom: 0;
    }
    .sub-header {
        color: #666;
        font-size: 1rem;
        margin-top: 0;
    }
    .result-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #0078D4;
        margin-bottom: 1rem;
    }
    .score-badge {
        background-color: #0078D4;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🔍 Azure AI Search</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multimodal Semantic Search - Sweden Central</p>', unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    search_service = st.text_input(
        "Search Service Name",
        value=os.getenv("AZURE_SEARCH_SERVICE_NAME", ""),
        help="Your Azure AI Search service name"
    )
    
    search_key = st.text_input(
        "Search API Key",
        value=os.getenv("AZURE_SEARCH_QUERY_KEY", ""),
        type="password",
        help="Query or Admin API key"
    )
    
    index_name = st.text_input(
        "Index Name",
        value="multimodal-docs",
        help="Name of your search index"
    )
    
    st.divider()
    
    st.header("🎯 Search Options")
    
    top_k = st.slider(
        "Number of Results",
        min_value=1,
        max_value=20,
        value=5,
        help="How many results to retrieve"
    )
    
    search_mode = st.radio(
        "Search Mode",
        ["Hybrid (Vector + Keyword)", "Vector Only", "Keyword Only"],
        help="Combine different search strategies"
    )
    
    st.divider()
    
    st.markdown("### 📊 About")
    st.info("""
    **Region:** Sweden Central  
    **Model:** GPT-4o with Vision  
    **Features:**
    - Text search
    - Image search
    - Hybrid retrieval
    - Semantic ranking
    """)

# Main content
tab1, tab2 = st.tabs(["📝 Text Search", "🖼️ Image Search"])

# Initialize search client
@st.cache_resource
def get_search_client(_service_name, _api_key, _index_name):
    """Initialize Azure Search client."""
    if not _service_name or not _api_key:
        return None
    
    endpoint = f"https://{_service_name}.search.windows.net"
    return SearchClient(
        endpoint=endpoint,
        index_name=_index_name,
        credential=AzureKeyCredential(_api_key)
    )

@st.cache_resource
def get_embeddings():
    """Initialize embeddings client."""
    try:
        return get_embeddings_client()
    except Exception as e:
        st.error(f"Failed to initialize embeddings: {e}")
        return None

def display_result(result, index):
    """Display a single search result."""
    with st.container():
        st.markdown(f"""
        <div class="result-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0;">{index}. {result.get('title', 'Untitled')}</h3>
                <span class="score-badge">Score: {result.get('@search.score', 0):.4f}</span>
            </div>
            <p style="color: #666; margin: 0.5rem 0;">
                <strong>Type:</strong> {result.get('content_type', 'unknown')}
                | <strong>Path:</strong> {result.get('file_path', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display content
        if result.get('image_description'):
            st.markdown(f"**Description:** {result['image_description']}")
        elif result.get('content'):
            content = result['content']
            st.markdown(f"**Content:** {content[:300]}..." if len(content) > 300 else content)
        
        # Display image if available
        # Note: This would require actual image URLs from blob storage
        # Placeholder for future implementation
        
        st.divider()

# Tab 1: Text Search
with tab1:
    st.subheader("🔍 Search with Text")
    
    query = st.text_input(
        "Enter your search query",
        placeholder="e.g., mountain landscapes at sunset, cat photos, modern architecture...",
        key="text_query"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if search_button and query:
        client = get_search_client(search_service, search_key, index_name)
        embeddings = get_embeddings()
        
        if not client:
            st.error("⚠️ Please configure your Azure Search credentials in the sidebar")
        elif not embeddings:
            st.error("⚠️ Please configure Azure OpenAI credentials (AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY)")
        else:
            with st.spinner("Searching..."):
                try:
                    # Generate query embedding
                    query_vector = embeddings.encode_text(query)
                    
                    # Build search parameters
                    search_params = {
                        "select": ["title", "content", "content_type", "file_path", "image_description"],
                        "top": top_k
                    }
                    
                    if "Vector Only" in search_mode:
                        search_params["search_text"] = None
                        vector_query = VectorizedQuery(
                            vector=query_vector,
                            k_nearest_neighbors=top_k,
                            fields="content_vector,image_vector"
                        )
                        search_params["vector_queries"] = [vector_query]
                    elif "Keyword Only" in search_mode:
                        search_params["search_text"] = query
                    else:  # Hybrid
                        search_params["search_text"] = query
                        vector_query = VectorizedQuery(
                            vector=query_vector,
                            k_nearest_neighbors=top_k,
                            fields="content_vector,image_vector"
                        )
                        search_params["vector_queries"] = [vector_query]
                    
                    # Execute search
                    results = client.search(**search_params)
                    
                    # Display results
                    st.success(f"✅ Found results for: **{query}**")
                    
                    results_list = list(results)
                    if not results_list:
                        st.warning("No results found. Try a different query.")
                    else:
                        for i, result in enumerate(results_list, 1):
                            display_result(result, i)
                    
                except Exception as e:
                    st.error(f"❌ Search failed: {str(e)}")

# Tab 2: Image Search
with tab2:
    st.subheader("🖼️ Search with Image")
    
    st.markdown("""
    Upload an image to find visually similar content in the index.  
    The image will be analyzed using GPT-4o Vision to generate embeddings.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["jpg", "jpeg", "png"],
        help="Upload a JPG or PNG image"
    )
    
    if uploaded_file:
        # Display uploaded image
        col1, col2 = st.columns([1, 2])
        
        with col1:
            image = Image.open(uploaded_file)
            st.image(image, caption="Query Image", use_container_width=True)
        
        with col2:
            search_button_img = st.button("🔍 Search Similar", type="primary", key="img_search")
        
        if search_button_img:
            client = get_search_client(search_service, search_key, index_name)
            embeddings = get_embeddings()
            
            if not client or not embeddings:
                st.error("⚠️ Please configure your credentials in the sidebar")
            else:
                with st.spinner("Analyzing image and searching..."):
                    try:
                        # Save uploaded image temporarily
                        temp_path = f"/tmp/query_image_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Generate image embedding
                        image_vector, description = embeddings.encode_image(temp_path)
                        
                        st.info(f"**Image Analysis:** {description[:200]}...")
                        
                        # Search
                        vector_query = VectorizedQuery(
                            vector=image_vector,
                            k_nearest_neighbors=top_k,
                            fields="content_vector,image_vector"
                        )
                        
                        results = client.search(
                            search_text=None,
                            vector_queries=[vector_query],
                            select=["title", "content_type", "file_path", "image_description"],
                            top=top_k
                        )
                        
                        # Display results
                        st.success("✅ Found similar content:")
                        
                        results_list = list(results)
                        if not results_list:
                            st.warning("No similar content found.")
                        else:
                            for i, result in enumerate(results_list, 1):
                                display_result(result, i)
                        
                        # Cleanup
                        os.remove(temp_path)
                        
                    except Exception as e:
                        st.error(f"❌ Image search failed: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.875rem;">
    <p>
        Azure AI Search Multimodal | 
        <a href="https://github.com/moltbotville/azure-ai-search-multimodal" target="_blank">GitHub</a> | 
        Region: Sweden Central
    </p>
</div>
""", unsafe_allow_html=True)
