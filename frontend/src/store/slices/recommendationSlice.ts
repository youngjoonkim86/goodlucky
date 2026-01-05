import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { recommendationApi } from '../../services/api'

interface Recommendation {
  numbers: number[]
  confidence: number
  features: Record<string, number>
  explanation?: string
}

interface RecommendationState {
  recommendations: Recommendation[]
  confidence: any
  loading: boolean
  error: string | null
}

const initialState: RecommendationState = {
  recommendations: [],
  confidence: null,
  loading: false,
  error: null,
}

export const fetchRecommendations = createAsyncThunk(
  'recommendation/fetchRecommendations',
  async (params?: any) => {
    const response = await recommendationApi.getNumbers(params)
    return response.data
  }
)

export const fetchConfidence = createAsyncThunk(
  'recommendation/fetchConfidence',
  async (numbers: number[]) => {
    const response = await recommendationApi.getConfidence(numbers)
    return response.data
  }
)

const recommendationSlice = createSlice({
  name: 'recommendation',
  initialState,
  reducers: {
    clearRecommendations: (state) => {
      state.recommendations = []
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRecommendations.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchRecommendations.fulfilled, (state, action) => {
        state.loading = false
        state.recommendations = action.payload
      })
      .addCase(fetchRecommendations.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '추천 생성 실패'
      })
      .addCase(fetchConfidence.fulfilled, (state, action) => {
        state.confidence = action.payload
      })
  },
})

export const { clearRecommendations } = recommendationSlice.actions
export default recommendationSlice.reducer

