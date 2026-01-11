/**
 * Helper pour les appels API
 * Utilise fetch() natif au lieu d'axios
 */

// Les cookies sont automatiquement envoyés avec fetch() sur la même origine
// Plus besoin de gérer les tokens manuellement

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`/api${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include', // Inclure les cookies
  })

  if (!response.ok) {
    if (response.status === 401) {
      // Rediriger vers login si non authentifié
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
      throw new Error('Non authentifié')
    }
    const error = await response.json().catch(() => ({ error: 'Erreur serveur' }))
    throw new Error(error.error || `Erreur HTTP: ${response.status}`)
  }

  return response.json()
}

export async function apiPost<T>(endpoint: string, data: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function apiGet<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'GET',
  })
}

export async function apiPut<T>(endpoint: string, data: any): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function apiDelete<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'DELETE',
  })
}

// Pour compatibilité avec l'ancien code
export const apiClient = {
  get: (url: string) => apiGet(url.replace('/api', '')),
  post: (url: string, data?: any) => apiPost(url.replace('/api', ''), data),
  put: (url: string, data?: any) => apiPut(url.replace('/api', ''), data),
  delete: (url: string) => apiDelete(url.replace('/api', '')),
}

export default apiClient
