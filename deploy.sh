#!/bin/bash
# Automated deployment script for Azure AI Search Multimodal
# Checks dependencies and deploys infrastructure

set -e

echo "🚀 Azure AI Search Multimodal - Deployment Script"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Azure CLI
echo -n "Checking Azure CLI... "
if command -v az &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
    az --version | head -1
else
    echo -e "${RED}✗ Not installed${NC}"
    echo ""
    echo "Install with:"
    echo "  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi

# Check Python
echo -n "Checking Python... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
    exit 1
fi

# Check if logged in to Azure
echo -n "Checking Azure login... "
if az account show &> /dev/null; then
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo -e "${GREEN}✓ Logged in${NC}"
    echo "   Subscription: $SUBSCRIPTION"
else
    echo -e "${YELLOW}⚠ Not logged in${NC}"
    echo ""
    echo "Login with:"
    echo "  az login --use-device-code"
    exit 1
fi

echo ""
echo "=================================================="
echo "📝 Configuration"
echo "=================================================="
echo ""

# Get deployment parameters
read -p "Azure Region [swedencentral]: " LOCATION
LOCATION=${LOCATION:-swedencentral}

read -p "Resource Group Name [rg-ai-search-sweden]: " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-rg-ai-search-sweden}

# Generate unique names
RANDOM_SUFFIX=$(openssl rand -hex 4)
SEARCH_SERVICE="search-${RANDOM_SUFFIX}"
STORAGE_ACCOUNT="st${RANDOM_SUFFIX}"

echo ""
echo "Deployment Configuration:"
echo "  Region: $LOCATION"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Search Service: $SEARCH_SERVICE"
echo "  Storage Account: $STORAGE_ACCOUNT"
echo ""

read -p "Proceed with deployment? (y/n): " CONFIRM
if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "=================================================="
echo "🏗️ Deploying Infrastructure"
echo "=================================================="
echo ""

# Create resource group
echo "Creating resource group..."
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --output table

echo ""
echo "Deploying Azure AI Search and Storage..."
DEPLOYMENT_OUTPUT=$(az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infrastructure/main.bicep \
  --parameters location=$LOCATION \
  --parameters searchServiceName=$SEARCH_SERVICE \
  --parameters storageAccountName=$STORAGE_ACCOUNT \
  --output json)

# Extract outputs
SEARCH_ENDPOINT=$(echo $DEPLOYMENT_OUTPUT | jq -r '.properties.outputs.searchServiceEndpoint.value')
SEARCH_KEY=$(echo $DEPLOYMENT_OUTPUT | jq -r '.properties.outputs.searchServiceKey.value')
STORAGE_CONNECTION=$(echo $DEPLOYMENT_OUTPUT | jq -r '.properties.outputs.storageConnectionString.value')

echo ""
echo -e "${GREEN}✅ Infrastructure deployed successfully!${NC}"
echo ""
echo "=================================================="
echo "📋 Deployment Summary"
echo "=================================================="
echo ""
echo "Search Service:"
echo "  Name: $SEARCH_SERVICE"
echo "  Endpoint: $SEARCH_ENDPOINT"
echo "  Admin Key: ${SEARCH_KEY:0:20}..."
echo ""
echo "Storage Account:"
echo "  Name: $STORAGE_ACCOUNT"
echo "  Connection String: ${STORAGE_CONNECTION:0:50}..."
echo ""

# Save to .env
echo "Saving configuration to .env..."
cat > .env << EOF
# Azure AI Search
AZURE_SEARCH_SERVICE_NAME=$SEARCH_SERVICE
AZURE_SEARCH_ADMIN_KEY=$SEARCH_KEY
AZURE_SEARCH_QUERY_KEY=$SEARCH_KEY

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONNECTION

# Azure OpenAI (configure manually)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
EOF

echo ""
echo "=================================================="
echo "⚠️  Next Steps"
echo "=================================================="
echo ""
echo "1. Deploy Azure OpenAI resource:"
echo "   - Request access: https://aka.ms/oai/access"
echo "   - After approval, deploy GPT-4o:"
echo ""
echo "   az cognitiveservices account create \\"
echo "     --name openai-${RANDOM_SUFFIX} \\"
echo "     --resource-group $RESOURCE_GROUP \\"
echo "     --location $LOCATION \\"
echo "     --kind OpenAI --sku S0"
echo ""
echo "2. Update .env with Azure OpenAI credentials"
echo ""
echo "3. Create search index:"
echo "   python scripts/create_index.py \\"
echo "     --search-service $SEARCH_SERVICE \\"
echo "     --index-name multimodal-docs"
echo ""
echo "4. Launch Streamlit GUI:"
echo "   streamlit run app.py"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
