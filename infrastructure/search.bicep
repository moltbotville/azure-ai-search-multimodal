// Azure AI Search service
param location string
param searchServiceName string
param sku string
param tags object

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    disableLocalAuth: false
    authOptions: {
      apiKeyOnly: {}
    }
  }
}

output searchServiceName string = searchService.name
output endpoint string = 'https://${searchService.name}.search.windows.net'
output adminKey string = searchService.listAdminKeys().primaryKey
output id string = searchService.id
