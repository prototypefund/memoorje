import { createPinia } from 'pinia'
import { ViteSSG } from 'vite-ssg'

import routes from 'virtual:generated-pages'

import App from './App.vue'
import './index.css'
import { useMainStore } from '~/store/main'
import { isLoggedIn, getUser } from '~/util/api/auth'
import { i18n } from '~/util/i18n'

export const createApp = ViteSSG(
  // the root component
  App,
  // vue-router options
  {
    routes,
    scrollBehavior() {
      return { top: 0 }
    },
  },
  // function to have custom setups
  async ({ app, router, initialState }) => {
    const pinia = createPinia()
    app.use(pinia)
    app.use(i18n)

    async function setLoginState() {
      const mainStore = useMainStore(pinia)
      if (await isLoggedIn()) {
        mainStore.user = await getUser()
      }
    }

    if (import.meta.env.SSR) {
      initialState.pinia = pinia.state.value
    } else {
      await setLoginState()
      pinia.state.value = initialState.pinia || {}
    }

    // redirect all private urls to auth page if user is not authenticated
    router.beforeEach((to, from, next) => {
      const mainStore = useMainStore(pinia)
      if (to.path.startsWith('/my') && !mainStore.user) {
        next({ name: 'auth', query: { next: to.fullPath } })
      } else {
        next()
      }
    })

    // redirect authenticated user to the dashboard if the auth page is requested
    router.beforeEach((to, from, next) => {
      const mainStore = useMainStore(pinia)
      if (to.name === 'auth' && mainStore.user) {
        next({ name: 'my-dashboard' })
      } else {
        next()
      }
    })
  }
)
