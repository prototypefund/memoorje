<template>
  <div
    class="
      fixed
      z-50
      bottom-0
      mx-auto
      w-full
      flex flex-col
      md:px-6
      md:bottom-unset
      md:max-w-container
      md:transform
      md:-translate-x-1/2
      md:left-2/4
      md:top-6
    "
  >
    <a href="#main-page-content" class="sr-only">Jump to main content</a>
    <div id="navbar-pre" class="order-first md:order-last">
      <slot name="pre" />
    </div>
    <nav
      role="navigation"
      class="
        bg-white
        h-20
        flex
        items-stretch
        w-full
        md:h-12 md:p-2 md:border-0 md:rounded-full md:shadow-xl
        dark:bg-gray-700
      "
      :class="
        !mainStore.user && route.name === 'auth' ? 'hidden md:flex' : null
      "
    >
      <template v-if="mainStore.user">
        <MNavItem
          component="router-link"
          :to="{ name: 'my-dashboard' }"
          label="Dashboard"
          class="ml-0"
        >
          <MNavIcon>
            <icon-sui-coffee />
          </MNavIcon>
        </MNavItem>
        <MNavItem
          component="router-link"
          :to="{ name: 'my-capsules' }"
          label="Capsules"
        >
          <MNavIcon>
            <icon-sui-box />
          </MNavIcon>
        </MNavItem>
        <MNavItem
          component="router-link"
          :to="{ name: 'my-settings' }"
          label="Settings"
        >
          <MNavIcon>
            <icon-sui-toggles />
          </MNavIcon>
        </MNavItem>
        <MNavItem
          component="button"
          type="button"
          class="hidden md:ml-auto md:inline-flex"
          @click="doLogout"
        >
          <MNavIcon>
            <icon-sui-hand />
          </MNavIcon>
          <span>Logout</span>
        </MNavItem>
      </template>
      <template v-if="!mainStore.user">
        <router-link
          :to="{ name: 'index' }"
          class="flex items-center px-3 font-semibold dark:text-gray-300"
          >memoorje
        </router-link>
        <MNavItem
          v-if="route.name !== 'auth'"
          component="router-link"
          :to="{ name: 'auth' }"
          class="md:ml-auto"
        >
          <MNavIcon>
            <icon-sui-hand />
          </MNavIcon>
          <span>Login</span>
        </MNavItem>
      </template>
    </nav>
    <nav
      role="navigation"
      class="
        grid
        bg-white
        fixed
        top-0
        left-0
        w-full
        shadow-xl
        overflow-hidden
        items-stretch
        md:hidden
        dark:bg-gray-700 dark:text-gray-300
      "
      style="grid-template-columns: 52px [center] 1fr 52px; height: 52px"
    >
      <button
        v-if="canNavigateBack"
        type="button"
        class="text-3xl flex justify-center items-center"
        aria-label="Back to previous page"
        @click="back"
      >
        <icon-sui-arrow-left />
      </button>
      <p class="flex justify-center items-center" style="grid-column: center">
        <slot name="mobile-nav-name" />
      </p>
      <button
        v-if="mainStore.user"
        type="button"
        class="text-3xl flex justify-center items-center"
        aria-label="Logout"
        @click="doLogout"
      >
        <icon-sui-hand />
      </button>
    </nav>
    <div id="navbar-post" class="order-last md:order-first">
      <slot name="post" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { useRoute, useRouter } from 'vue-router'
import { logout } from '~/util/api/auth'
import { useMainStore } from '~/store/main'

const mainStore = useMainStore()
const router = useRouter()
const route = useRoute()

const routeMetaConfiguration = {
  auth: { parent: 'index' },
  'my-capsules-new': { parent: 'my-capsules' },
  'my-capsules-capsuleId': { parent: 'my-capsules' },
  'my-capsules-capsuleId-settings': { parent: 'my-capsules-capsuleId' },
}

// eslint-disable-next-line prefer-const
let routeMeta = $computed(() => routeMetaConfiguration[route.name])
// eslint-disable-next-line prefer-const
let canNavigateBack = $computed(() => typeof routeMeta?.parent !== 'undefined')
async function back() {
  await router.push({ name: routeMeta.parent })
}

async function doLogout() {
  await logout()
  await router.push('/')
}
</script>
