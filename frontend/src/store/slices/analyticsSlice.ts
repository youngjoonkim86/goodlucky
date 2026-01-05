import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { analyticsApi } from '../../services/api'

interface AnalyticsState {
  variables: any
  frequency: any
  patterns: any
  correlation: any
  loading: boolean
  error: string | null
}

const initialState: AnalyticsState = {
  variables: null,
  frequency: null,
  patterns: null,
  correlation: null,
  loading: false,
  error: null,
}

export const fetchVariables = createAsyncThunk(
  'analytics/fetchVariables',
  async (params?: any) => {
    const response = await analyticsApi.getVariables(params)
    return response.data
  }
)

export const fetchFrequency = createAsyncThunk(
  'analytics/fetchFrequency',
  async (limit?: number) => {
    const response = await analyticsApi.getFrequency(limit)
    return response.data
  }
)

export const fetchPatterns = createAsyncThunk(
  'analytics/fetchPatterns',
  async () => {
    const response = await analyticsApi.getPatterns()
    return response.data
  }
)

export const fetchCorrelation = createAsyncThunk(
  'analytics/fetchCorrelation',
  async () => {
    const response = await analyticsApi.getCorrelation()
    return response.data
  }
)

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchVariables.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchVariables.fulfilled, (state, action) => {
        state.loading = false
        state.variables = action.payload
      })
      .addCase(fetchFrequency.fulfilled, (state, action) => {
        state.frequency = action.payload
      })
      .addCase(fetchPatterns.fulfilled, (state, action) => {
        state.patterns = action.payload
      })
      .addCase(fetchCorrelation.fulfilled, (state, action) => {
        state.correlation = action.payload
      })
      .addCase(fetchVariables.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '분석 데이터 로드 실패'
      })
  },
})

export default analyticsSlice.reducer

