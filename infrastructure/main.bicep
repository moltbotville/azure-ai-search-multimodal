// Main infrastructure deployment for Azure AI Search Multimodal
targetScope = 'resourceGroup'

@description('Azure region for resources (sweden central)')
param location string = 'swedencentral'

@description('Name for the Azure AI Search service')
param searchServiceName string

@description('SKU for Azure AI Search (basic, standard, standard2, standard3)')
@allowed([
  'basic'
  'standard'
  'standard2'
  'standard3'
])
param searchServiceSku string = 'standard'

@description('Name for the storage account')
param storageAccountName string = 'stmultimodal${uniqueString(resourceGroup().id)}'

@description('Tags for all resources')
param tags object = {
  Environment: 'Production'
  Project: 'Multimodal-Search'
  ManagedBy: 'Bicep'
}

// Deploy Azure AI Search
module searchService 'search.bicep' = {
  name: 'searchServiceDeployment'
  params: {
    location: location
    searchServiceName: searchServiceName
    sku: searchServiceSku
    tags: tags
  }
}

// Deploy Storage Account for images/documents
module storage 'storage.bicep' = {
  name: 'storageDeployment'
  params: {
    location: location
    storageAccountName: storageAccountName
    tags: tags
  }
}

// Outputs
output searchServiceName string = searchService.outputs.searchServiceName
output searchServiceEndpoint string = searchService.outputs.endpoint
output searchServiceKey string = searchService.outputs.adminKey
output storageAccountName string = storage.outputs.storageAccountName
output storageConnectionString string = storage.outputs.connectionString
output containerName string = storage.outputs.containerName
