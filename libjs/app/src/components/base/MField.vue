<template>
  <div class="relative mb-4">
    <label
      class="
        absolute
        left-4
        top-2
        leading-none
        block
        caps-all-small
        font-bold
        text-lg
        z-10
      "
      :for="id"
      :class="{ 'text-red-500': !isValid }"
      >{{ label }}</label
    >
    <slot></slot>
    <MValidationMessages class="px-4" :errors="errors" />
    <div
      v-if="slots.description || description"
      :id="descriptionId"
      class="text-sm mt-2"
    >
      <slot name="description">{{ description }}</slot>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { provide, useSlots } from 'vue'
import { makeId } from '~/util/string'
import { ValidationError } from '~/util/validation'

const props = defineProps<{
  label: string
  description?: string
  id?: string
  errors?: null | ValidationError[]
}>()

const slots = useSlots()
const generatedId = makeId(16, 'field-')
// eslint-disable-next-line prefer-const
let id = $computed(() => (props.id ? props.id : generatedId))
// eslint-disable-next-line prefer-const
let descriptionId = $computed(() => `${id}-description`)
// eslint-disable-next-line prefer-const
let errors = $computed(() => props.errors || [])
// eslint-disable-next-line prefer-const
let isValid = $computed(() => errors.length === 0)
provide<string>('inputId', id)
provide<string>('descriptionId', descriptionId)
</script>
