<template>
  <component
    :is="componentType"
    tabindex="0"
    :type="buttonType"
    class="
      appearance-none
      inline-flex
      justify-center
      flex-shrink-0
      font-normal
      py-2
      px-4
      rounded
      shadow-md
      focus:outline-none focus:ring-2 focus:ring-offset-2
    "
    :class="cssClasses"
    ><slot
  /></component>
</template>

<script lang="ts" setup>
const props = defineProps<{
  is?: string
  type?: string
  design?: string
  size?: string
}>()

// eslint-disable-next-line prefer-const
let componentType: string = $computed(() => props.is || 'button')
// eslint-disable-next-line prefer-const
let buttonType = $computed(() =>
  componentType === 'button' ? props.type || 'button' : null
)
// eslint-disable-next-line prefer-const
let cssClasses = $computed(() => [
  {
    none: '',
    normal: 'py-2 px-4',
    large: 'text-2xl py-4 px-6',
  }[props.size || 'normal'],
  {
    accent: 'bg-accent text-primary',
  }[props.design || ''],
])
</script>
