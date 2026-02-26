import { create } from 'zustand'
import type { Run } from '../types'
import { api } from '../api'

interface RunState {
  runs: Run[]
  loading: boolean
  fetch: () => Promise<void>
}

export const useRunStore = create<RunState>((set) => ({
  runs: [],
  loading: false,
  fetch: async () => {
    set({ loading: true })
    try {
      const runs = await api.runs.list()
      set({ runs, loading: false })
    } catch {
      set({ loading: false })
    }
  },
}))
