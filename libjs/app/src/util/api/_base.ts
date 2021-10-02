import {
  AuthApi,
  Configuration,
  CapsulesApi,
  HTTPHeaders,
  CapsuleContentsApi,
} from '@memoorje/api'
import { split } from '../string'

// TODO: this is probably the wrong thing to do
// eslint-disable-next-line import/no-mutable-exports
export let basePath: string
if (import.meta.env.SSR) {
  basePath = ''
} else {
  basePath = window.location.origin
}

function getCookie(name: string) {
  if (document?.cookie) {
    for (let cookie of document.cookie.split(';')) {
      cookie = cookie.trim()
      const [parsedName, parsedValue] = split(cookie, '=', 1)
      if (parsedName === name) {
        return decodeURIComponent(parsedValue)
      }
    }
  }
  return null
}

export const configuration = new Configuration({
  basePath,
  get headers(): HTTPHeaders {
    const csrfToken = getCookie('csrftoken')
    return csrfToken ? { 'X-CSRFToken': csrfToken } : {}
  },
})

export const authAPI = new AuthApi(configuration)
export const capsulesAPI = new CapsulesApi(configuration)
export const capsuleContentsAPI = new CapsuleContentsApi(configuration)
