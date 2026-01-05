import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 로또 API
export const lottoApi = {
  getHistory: (params?: {
    skip?: number
    limit?: number
    draw_no?: number
    start_date?: string
    end_date?: string
  }) => api.get('/lotto/history', { params }),
  
  getDrawByNo: (drawNo: number) => api.get(`/lotto/history/${drawNo}`),
  
  getLatest: () => api.get('/lotto/latest'),
  
  getStatistics: () => api.get('/lotto/statistics'),
}

// 분석 API
export const analyticsApi = {
  getVariables: (params?: {
    start_date?: string
    end_date?: string
  }) => api.get('/analytics/variables', { params }),
  
  getFrequency: (limit?: number) => api.get('/analytics/frequency', {
    params: { limit }
  }),
  
  getPatterns: () => api.get('/analytics/patterns'),
  
  getCorrelation: () => api.get('/analytics/correlation'),
}

// 추천 API
export const recommendationApi = {
  getNumbers: (params?: {
    count?: number
    include_weather?: boolean
    include_economic?: boolean
  }) => api.get('/recommendations/numbers', { params }),
  
  getConfidence: (numbers: number[]) => api.get('/recommendations/numbers/confidence', {
    params: { numbers: numbers.join(',') }
  }),
}

export default api

