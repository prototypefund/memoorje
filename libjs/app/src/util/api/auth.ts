import { authAPI } from './_base'
import {
  parseValidationResponse,
  ServerValidationException,
} from '~/util/validation'
import { useMainStore } from '~/store/main'

type UserData = {
  id: number
  email: string
}

export async function getUser(): Promise<UserData> {
  return await authAPI.authProfileRetrieve()
}

export async function isLoggedIn(): Promise<boolean> {
  try {
    return !!(await getUser())
  } catch (err: any | Response) {
    return false
  }
}

type RegistrationData = {
  email: string
  password: string
  passwordConfirm: string
}

export async function register(data: RegistrationData): Promise<UserData> {
  try {
    await authAPI.authRegisterCreate({
      id: 0,
      email: data.email,
      password: data.password,
      passwordConfirm: data.passwordConfirm,
    })
  } catch (err: any | Response) {
    throw new ServerValidationException(
      'Unable to register',
      await parseValidationResponse(err)
    )
  }

  const user = await getUser()
  const mainStore = useMainStore()
  mainStore.user = user
  return user
}

type LoginData = {
  email: string
  password: string
}

export async function login(data: LoginData): Promise<UserData> {
  if (!(await isLoggedIn())) {
    try {
      await authAPI.authLoginCreate({
        login: data.email,
        password: data.password,
      })
    } catch (err: any | Response) {
      throw new ServerValidationException(
        'Unable to login',
        await parseValidationResponse(err)
      )
    }
  }

  const user = await getUser()
  const mainStore = useMainStore()
  mainStore.user = user
  return user
}

type PasswordResetData = {
  email: string
}

export async function resetPassword(data: PasswordResetData) {
  try {
    await authAPI.authSendResetPasswordLinkCreate({
      login: data.email,
    })
  } catch (err: any | Response) {
    throw new ServerValidationException(
      'Unable to request reset password link',
      await parseValidationResponse(err)
    )
  }
}

export async function logout(): Promise<void> {
  try {
    await authAPI.authLogoutCreate({
      revokeToken: true,
    })
  } catch (err: any | Response) {
    throw new ServerValidationException(
      'Unable to logout user',
      await parseValidationResponse(err)
    )
  }

  const mainStore = useMainStore()
  mainStore.user = null
}
