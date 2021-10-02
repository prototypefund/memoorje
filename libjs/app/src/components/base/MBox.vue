<template>
  <component
    :is="props.is || 'div'"
    class="w-full bg-white shadow-md dark:bg-gray-700"
  >
    <slot />
  </component>
</template>

<script lang="ts" setup>
const props = defineProps<{
  is?: string
}>()
</script>
