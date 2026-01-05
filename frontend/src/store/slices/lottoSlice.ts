import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { lottoApi } from '../../services/api'

interface LottoDraw {
  id: number
  draw_no: number
  draw_date: string
  numbers: number[]
  bonus: number
  first_prize_winners: number
  first_prize_amount: number
  total_sales: number
}

interface LottoState {
  draws: LottoDraw[]
  latest: LottoDraw | null
  statistics: any
  loading: boolean
  error: string | null
}

const initialState: LottoState = {
  draws: [],
  latest: null,
  statistics: null,
  loading: false,
  error: null,
}

export const fetchHistory = createAsyncThunk(
  'lotto/fetchHistory',
  async (params?: any) => {
    const response = await lottoApi.getHistory(params)
    return response.data
  }
)

export const fetchLatest = createAsyncThunk(
  'lotto/fetchLatest',
  async () => {
    const response = await lottoApi.getLatest()
    return response.data
  }
)

export const fetchStatistics = createAsyncThunk(
  'lotto/fetchStatistics',
  async () => {
    const response = await lottoApi.getStatistics()
    return response.data
  }
)

const lottoSlice = createSlice({
  name: 'lotto',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchHistory.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchHistory.fulfilled, (state, action) => {
        state.loading = false
        state.draws = action.payload
      })
      .addCase(fetchHistory.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '데이터 로드 실패'
      })
      .addCase(fetchLatest.fulfilled, (state, action) => {
        state.latest = action.payload
      })
      .addCase(fetchStatistics.fulfilled, (state, action) => {
        state.statistics = action.payload
      })
  },
})

export default lottoSlice.reducer

