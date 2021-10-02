<template>
  <div class="relative">
    <textarea
      v-if="props.type === 'textarea'"
      v-model="localValue"
      v-bind="attribs"
    ></textarea>
    <input v-else v-model="localValue" :type="inputType" v-bind="attribs" />
    <button
      v-if="props.type === 'password'"
      type="button"
      tabindex="-1"
      :aria-label="!revealInput ? 'Reveal Password' : 'Hide Password'"
      class="absolute bottom-3 left-4"
      @click="revealInput = !revealInput"
    >
      <icon-sui-eye v-if="!revealInput" />
      <icon-sui-eye-closed v-else />
    </button>
  </div>
</template>

<script lang="ts">
export default {
  inheritAttrs: false,
}
</script>

<script lang="ts" setup>
import { inject, useAttrs } from 'vue'

type modelValueType = string | number

interface Props {
  type?: string
  modelValue: modelValueType
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
})
const emit = defineEmits<{
  (e: 'update:modelValue', id: modelValueType): void
}>()
const attrs = useAttrs()

// eslint-disable-next-line prefer-const
let id = inject<string>('inputId')
// eslint-disable-next-line prefer-const
let descriptionId = inject<string>('descriptionId')
// eslint-disable-next-line prefer-const
let localValue = $computed({
  get: () => props.modelValue,
  set: (value: modelValueType) => {
    emit('update:modelValue', value)
  },
})
// eslint-disable-next-line prefer-const
let revealInput: boolean = $ref(false)
// eslint-disable-next-line prefer-const
let inputType = $computed(() =>
  props.type === 'password' && revealInput ? 'text' : props.type
)
// eslint-disable-next-line prefer-const
let attribs = $computed(() => ({
  ...useAttrs(),
  id,
  name: id,
  class: [
    'appearance-none border border-transparent bg-white placeholder-gray-400 block w-full px-4 pt-7 pb-2 rounded focus:outline-none focus:ring-2 focus:border-transparent bg-gray-200',
    'dark:bg-gray-800',
    props.type === 'password' ? 'pl-10' : null,
  ],
  'aria-describedby': descriptionId,
}))
</script>

<style>
input:-webkit-autofill {
  transition: all 0s 50000s;
}
/*input:-webkit-autofill,*/
/*input:-webkit-autofill:hover,*/
/*input:-webkit-autofill:focus,*/
/*input:-webkit-autofill:active {*/
/*  -webkit-box-shadow: 0 0 0 30px theme('colors.gray.200') inset !important;*/
/*}*/

/*.dark input:-webkit-autofill,*/
/*.dark input:-webkit-autofill:hover,*/
/*.dark input:-webkit-autofill:focus,*/
/*.dark input:-webkit-autofill:active {*/
/*  -webkit-background-clip: text;*/
/*  !*-webkit-box-shadow: 0 0 0 30px theme('colors.gray.800') inset !important;*!*/
/*  !*color: inherit;*!*/
/*  !*border: none;*!*/
/*}*/
</style>
