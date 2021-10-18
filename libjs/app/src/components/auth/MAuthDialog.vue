<template>
  <MForm
    style="max-width: 450px"
    :label="
      {
        login: 'Login',
        registration: 'Registration',
        'lost-password': 'Reset Password',
      }[currentMode]
    "
    @submit.prevent="currentAction"
  >
    <MField id="user-email" label="Email" :errors="validation.email?.errors">
      <MInput
        v-model="state.email"
        type="email"
        autofocus
        autocomplete="email"
      />
    </MField>

    <MField
      v-if="!mode.lostPassword"
      id="user-password"
      label="Password"
      :errors="validation.password?.errors"
    >
      <MInput v-model="state.password" type="password" />
    </MField>

    <MField
      v-if="mode.isRegistration"
      id="user-password-confirm"
      label="Password (confirm)"
      :errors="validation.passwordConfirm?.errors"
    >
      <MInput v-model="state.passwordConfirm" type="password" />
    </MField>

    <MValidationMessages :errors="serverValidationData?.$GLOBAL_STATE" />

    <p v-if="!mode.lostPassword" class="mb-3 text-sm">
      By signing up or logging in you agree to the use of cookies 🍪. We only
      use first-party cookies for handling your session. No tracking or anything
      else.
    </p>

    <div class="flex flex-wrap justify-between items-center">
      <hr class="block sm:hidden w-full mt-8 mb-4 dark:border-gray-600" />

      <button
        v-if="mode.isLogin"
        type="button"
        :class="secondaryButtonClasses"
        @click="currentMode = 'registration'"
      >
        Register
      </button>
      <button
        v-if="!mode.isLogin"
        type="button"
        :class="secondaryButtonClasses"
        @click="currentMode = 'login'"
      >
        Login
      </button>
      <button
        v-if="!mode.lostPassword"
        type="button"
        :class="secondaryButtonClasses"
        @click="currentMode = 'lost-password'"
      >
        Lost Password?
      </button>

      <MButton
        type="submit"
        design="accent"
        class="
          w-full
          order-first
          sm:w-auto sm:order-last sm:mx-0
          flex-grow
          sm:max-w-1/2
        "
        >{{ currentActionLabel }}
      </MButton>
    </div>
  </MForm>
</template>

<script lang="ts" setup>
import { computed, reactive, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { required, email, sameAs, helpers } from '@vuelidate/validators'
import { login, register, resetPassword } from '~/util/api/auth'
import { fromServer, vuelidateToCommon } from '~/util/validation'

const router = useRouter()
const route = useRoute()

// api handling
/* eslint-disable no-use-before-define */
function wrapApiCall(
  apiCall,
  onPost: (data?: any) => any = () => undefined,
  onErr: (err: Error) => any = () => undefined
) {
  return async function () {
    try {
      return await onPost(
        await apiCall({
          email: state.email,
          password: state.password,
          passwordConfirm: state.passwordConfirm,
        })
      )
    } catch (err: any) {
      serverValidationData = err.validation
      validation.$trigger()
      if (!serverValidationData) {
        await onErr(err)
      }
    }
  }
}
/* eslint-enable */

const doLogin = wrapApiCall(login, async () => {
  if (route.query.next) {
    await router.push(route.query.next as string)
  } else {
    await router.push({ name: 'my-dashboard' })
  }
})
const doRegister = wrapApiCall(register, async () => {
  await router.push({ name: 'my-dashboard' })
})
const doResetPassword = wrapApiCall(resetPassword)

// local data
type Mode = 'registration' | 'login' | 'lost-password'
const availableModes = ['registration', 'login', 'lost-password']
let modeFromQuery
let hostname
if (import.meta.env.SSR) {
  modeFromQuery = 'login'
  hostname = 'memoorje'
} else {
  modeFromQuery = new URL(window.location.href).searchParams.get('mode')
  hostname =
    window.location.hostname === 'localhost'
      ? 'memoorje'
      : window.location.hostname
}
// eslint-disable-next-line prefer-const
let currentMode: Mode = $ref(
  availableModes.includes(modeFromQuery) ? modeFromQuery : 'login'
)
// eslint-disable-next-line prefer-const
let mode: { isRegistration: boolean; isLogin: boolean; lostPassword: boolean } =
  $computed(() => ({
    isRegistration: currentMode === 'registration',
    isLogin: currentMode === 'login',
    lostPassword: currentMode === 'lost-password',
  }))
// eslint-disable-next-line prefer-const
let currentAction = $computed(
  () =>
    ({
      login: doLogin,
      registration: doRegister,
      'lost-password': doResetPassword,
    }[currentMode])
)
// eslint-disable-next-line prefer-const
let currentActionLabel = $computed(
  () =>
    ({
      login: 'Login',
      registration: 'Sign Up',
      'lost-password': 'Reset Password',
    }[currentMode])
)

const secondaryButtonClasses = 'text-base underline mr-6'
const state = reactive({
  email: '',
  password: '',
  passwordConfirm: '',
})

// validation
let serverValidationData = $ref(null)
const dataValidationRules = {
  email: {
    required,
    email,
    server: fromServer($$(serverValidationData), 'email'),
  },
  password: {
    required,
    server: fromServer($$(serverValidationData), 'password'),
  },
  passwordConfirm: {
    required,
    sameAsPassword: helpers.withMessage(
      'Passwords need to match',
      sameAs(computed(() => state.password))
    ),
  },
}
const validation = vuelidateToCommon(dataValidationRules, state)
// TODO: Validation should be triggered by the reactive state. It’s unclear why that does not work.
watch(
  () => state.email,
  () => {
    validation.$trigger('email')
  }
)
watch(
  () => state.password,
  () => {
    validation.$trigger('password')
  }
)
watch(
  () => state.passwordConfirm,
  () => {
    validation.$trigger('passwordConfirm')
  }
)
watch($$(currentMode), () => {
  serverValidationData = null
})
</script>
