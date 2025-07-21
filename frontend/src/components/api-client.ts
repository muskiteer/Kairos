import { config, getApiUrl } from '@/lib/config'

class ApiClient {
  private baseURL: string
  private timeout: number

  constructor() {
    this.baseURL = config.api.baseURL
    this.timeout = config.api.timeout
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const url = getApiUrl(endpoint)
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    }

    try {
      const response = await fetch(url, defaultOptions)
      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }
      
      return await response.json()
    } catch (error) {
      clearTimeout(timeoutId);
      console.error(`API request failed for ${endpoint}:`, error)
      throw error
    }
  }

  // Helper methods
  get(endpoint: string) {
    return this.request(endpoint, { method: 'GET' })
  }

  post(endpoint: string, data?: any) {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  put(endpoint: string, data?: any) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  delete(endpoint: string) {
    return this.request(endpoint, { method: 'DELETE' })
  }
}

export const apiClient = new ApiClient()
