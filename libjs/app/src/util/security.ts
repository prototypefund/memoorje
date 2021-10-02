import { computed, reactive, ComputedRef } from 'vue'

type Passwords = {
  [key: string]: { password: string; lastUsed: Date }
}

export interface PasswordRecord {
  password: string
  expires: Date

  touch(): void
}

export interface PasswordSafe {
  retrieve(id: string): ComputedRef<PasswordRecord | null>
  open(id: string, password: string): void
}

export function createPasswordSafe(
  openForSeconds = 35 * 60,
  checkIntervalSeconds = 1
): PasswordSafe {
  const passwords = reactive<Passwords>({})

  function getExpiration(date: Date): Date {
    return new Date(date.getTime() + openForSeconds * 1000)
  }

  setInterval(() => {
    const currentTime = new Date()
    for (const key of Object.keys(passwords)) {
      if (getExpiration(passwords[key].lastUsed) < currentTime) {
        delete passwords[key]
      }
    }
  }, checkIntervalSeconds * 1000)

  return {
    retrieve(id: string) {
      return computed<PasswordRecord | null>(() => {
        if (typeof passwords[id] === 'undefined') {
          return null
        } else {
          return {
            password: passwords[id].password,
            expires: getExpiration(passwords[id].lastUsed),
            touch() {
              passwords[id].lastUsed = new Date()
            },
          }
        }
      })
    },
    open(id: string, password: string) {
      passwords[id] = { password, lastUsed: new Date() }
    },
  }
}
