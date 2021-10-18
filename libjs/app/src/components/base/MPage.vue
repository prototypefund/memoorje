<template>
  <MNavbar>
    <template #pre>
      <slot name="navbar-pre" />
    </template>
    <template #post>
      <slot name="navbar-post" />
    </template>
    <template #mobile-nav-name>
      {{ props.title || '' }}
    </template>
  </MNavbar>
  <div
    class="py-24 min-h-screen bg-gray-100 dark:bg-gray-800 sm:min-h-screen-3/4"
  >
    <main
      id="main-page-content"
      class="m-auto text-primary dark:text-gray-300"
      :class="{ 'max-w-container px-6': !props.unsized }"
    >
      <slot />
    </main>
  </div>
  <footer
    class="text-primary dark:text-gray-300 pt-12 pb-24"
    style="box-shadow: inset 0 25px 50px -36px rgba(0, 0, 0, 0.25)"
  >
    <div
      class="max-w-container px-6 m-auto text-normal leading-relaxed content"
    >
      <div class="grid grid-cols-1 gap-x-3 gap-y-6 grid-cols-2 sm:grid-cols-4">
        <div>
          <h2 class="text-3xl mb-1 caps-all-small font-semibold">Social</h2>
          <a class="block" href="https://memoorje.org"> Web </a>
          <a class="block" href="https://chaos.social/@memoorje"> Mastodon </a>
          <a class="block" href="https://twitter.com/memoorje_app"> Twitter </a>
        </div>
        <div>
          <h2 class="text-3xl mb-1 caps-all-small font-semibold">Legal</h2>
          <a class="block" href="#">Impressum</a>
          <a class="block" href="#">Privacy</a>
        </div>
        <div>
          <h2 class="text-3xl mb-1 caps-all-small font-semibold">
            memmorje.org
          </h2>
          <router-link
            class="block"
            :to="{ name: 'auth', query: { mode: 'registration' } }"
            >Sign Up
          </router-link>
          <a class="block" href="https://git.hack-hro.de/memoorje/memoorje"
            >Source Code</a
          >
        </div>
        <div style="grid-column: span 2">
          <h2 class="text-3xl mb-1 caps-all-small font-semibold">
            Sponsorship
          </h2>
          <p>
            memoorje has been sponsored by the German Federal Ministry of
            Education and Research from September 2021 through February 2022 as
            part of the
            <a href="https://prototypefund.de/">PrototypeFund</a>.
          </p>
          <BMBFLogo
            alt="Logo des Bundesministerium für Bildung und Forschung"
            style="max-width: 175px"
          />
        </div>
      </div>
    </div>
  </footer>
</template>

<script lang="ts" setup>
import { useHead } from '@vueuse/head'
import BMBFLogo from '../../assets/bmbf-logo.svg?component'

const props = defineProps<{
  unsized?: boolean
  title?: string
}>()

useHead({
  title: props.title,
})
</script>
