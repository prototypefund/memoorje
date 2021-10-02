<template>
  <template v-if="props.errors">
    <p
      v-for="error in props.errors"
      :key="error.id"
      class="mt-2 mb-4 text-red-500 font-semibold"
      v-bind="attrs"
    >
      {{ error.message }}
    </p>
  </template>
</template>

<script lang="ts">
export default {
  inheritAttrs: false,
}
</script>

<script lang="ts" setup>
import { useAttrs } from 'vue'
import { ValidationError } from '~/util/validation'

const attrs = useAttrs()
const props = defineProps<{
  errors?: null | ValidationError[]
}>()
</script>
