import { configureStore } from '@reduxjs/toolkit'
import investigation from '../features/investigationSlice'
export const store = configureStore({ reducer: { investigation } })
