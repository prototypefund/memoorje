<template>
  <component
    :is="componentType"
    :title="name"
    :to="newRoute"
    v-bind="customAttribs"
    aria-current-value="false"
  >
    <MFileIcon
      :file="props.file"
      class="flex-shrink-0 self-baseline mt-1 md:mt-0 md:self-center"
    />
    <div class="text-left max-w-full">
      <div class="break-all">{{ name }}</div>
      <div v-if="file.updatedOn" class="text-gray-500 text-sm md:hidden">
        Updated {{ updatedOn }}
      </div>
    </div>
  </component>
</template>

<script lang="ts" setup>
import { ComputedRef } from 'vue'
import { ExtendedPathFileMetadata, ExtendedPathFileRecord } from './types'
import { basename, join, rootName } from '~/util/file'
import { PasswordRecord } from '~/util/security'
import { formatDistanceFromToday } from '~/util/time'

const props = defineProps<{
  file: ExtendedPathFileMetadata | ExtendedPathFileRecord
  basePath: string
  route: object
  passwordRecord?: ComputedRef<PasswordRecord>
}>()
// eslint-disable-next-line prefer-const
let name = $computed(() => {
  return props.file.type === 'file'
    ? basename(props.file.pathWithoutPrefix)
    : rootName(props.file.pathWithoutPrefix)
})
// eslint-disable-next-line prefer-const
let newRoute = $computed(() => {
  if (props.file.type === 'directory') {
    return {
      ...props.route,
      query: {
        basePath: join(props.basePath, name),
      },
    }
  }
})
// eslint-disable-next-line prefer-const
let componentType = $computed(() => {
  return props.file.type === 'file' ? 'button' : 'router-link'
})
// eslint-disable-next-line prefer-const
let customAttribs = $computed(() => {
  if (props.file.type === 'file') {
    return {
      type: 'button',
    }
  }
})
// eslint-disable-next-line prefer-const
const updatedOn = formatDistanceFromToday(props.file.updatedOn)
</script>
