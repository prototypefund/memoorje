<template>
  <component
    :is="props.component"
    class="
      px-4
      py-2
      inline-flex
      flex-grow flex-wrap
      justify-center
      items-center
      bg-gray-200
      font-normal
      transition-colors
      md:flex-nowrap md:flex-grow-0 md:py-0 md:mx-1 md:rounded-full
      dark:bg-gray-600 dark:text-gray-300
      hover:bg-gray-300
      dark:hover:bg-gray-500
    "
    v-bind="{ ...attrs, ...routerLinkAttributes }"
  >
    <slot />
    <span v-if="label" class="block w-full text-center md:inline">{{
      props.label
    }}</span>
  </component>
</template>

<script lang="ts" setup>
import { useAttrs } from 'vue'

const attrs = useAttrs()
const props = defineProps<{
  component: string
  label?: string
}>()
// eslint-disable-next-line prefer-const
let routerLinkAttributes = $computed(() => {
  return props.component === 'router-link'
    ? {
        'active-class': 'bg-accent dark:bg-accent dark:text-primary',
      }
    : {}
})
</script>
