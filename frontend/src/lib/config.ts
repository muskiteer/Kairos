export const config = {
  api: {
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    timeout: 30000,
  },
  app: {
    name: 'Kairos AI Trading Platform',
    version: '3.0.0',
    environment: process.env.NODE_ENV || 'development',
  },
}

// Helper function for API calls
export const getApiUrl = (endpoint: string) => {
  const baseUrl = config.api.baseURL.replace(/\/$/, '') // Remove trailing slash
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`
  return `${baseUrl}${cleanEndpoint}`
}
