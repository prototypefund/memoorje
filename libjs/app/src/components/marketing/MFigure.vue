<template>
  <div class="flex-1 mb-12 md:mb-0">
    <div class="flex items-center justify-center md:ar-1">
      <component :is="illustration" class="mx-12 mb-6 md:m-0" />
    </div>
    <div class="text-justify hyphens">
      <h3 class="text-xl font-semibold mb-3 text-center">{{ title }}</h3>
      <slot />
    </div>
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  title: string
  illustration: any
}>()
</script>
