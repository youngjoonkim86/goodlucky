import { configureStore } from '@reduxjs/toolkit'
import lottoReducer from './slices/lottoSlice'
import analyticsReducer from './slices/analyticsSlice'
import recommendationReducer from './slices/recommendationSlice'

export const store = configureStore({
  reducer: {
    lotto: lottoReducer,
    analytics: analyticsReducer,
    recommendation: recommendationReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

