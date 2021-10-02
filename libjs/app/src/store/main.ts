import { defineStore } from 'pinia'
import { createPasswordSafe, PasswordSafe } from '~/util/security'

interface User {
  email: string
}

export interface BaseState {
  user: null | User
  safe: PasswordSafe
}

export const useMainStore = defineStore('main', {
  state: (): BaseState => ({
    user: null,
    safe: createPasswordSafe(),
  }),
})
