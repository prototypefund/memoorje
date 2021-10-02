<template>
  <form class="mx-auto bg-white md:rounded p-6 sm:shadow-md dark:bg-gray-700">
    <h1 v-if="label" class="text-3xl caps-all-small text-center mb-6">
      {{ label }}
    </h1>
    <slot />
  </form>
</template>

<script lang="ts" setup>
const props = defineProps<{
  label?: string
}>()
</script>
