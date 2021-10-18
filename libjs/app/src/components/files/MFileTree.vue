<template>
  <div ref="root" class="relative py-3 md:py-0 md:pb-3">
    <div
      class="
        bg-accent
        text-primary
        rounded
        h-px
        z-0
        pointer-events-none
        shadow-lg
        absolute
        top-0
        left-3
        right-3
        transform-gpu
        origin-top-left
        transition-transform transition-opacity
        hidden
        md:block
        dark:bg-gray-800
      "
      :class="[showIndicator ? 'opacity-100' : 'opacity-0']"
      role="presentation"
      style="transition-property: opacity, transform, height"
      :style="indicatorStyle"
    ></div>
    <table class="w-full relative z-10 text-left m-file-tree">
      <colgroup>
        <!-- force name column to take the maximum possible space -->
        <col style="width: 100%" />
        <col style="width: 0" />
      </colgroup>
      <thead class="hidden md:table-header-group mb-3">
        <tr>
          <th class="pl-6 py-3 whitespace-nowrap" :class="headerClasses">
            Name
          </th>
          <th class="pr-6 py-3 whitespace-nowrap" :class="headerClasses">
            Updated on
          </th>
        </tr>
        <tr>
          <th colspan="2" class="py-1"></th>
        </tr>
      </thead>
      <tbody
        class=""
        @focusin="moveIndicator"
        @focusout="showIndicator = false"
        @mouseenter="showIndicator = true"
        @mouseleave="showIndicator = false"
      >
        <tr v-if="backLinkTarget" class="group" @mouseenter="moveIndicator">
          <td colspan="2">
            <router-link :to="backLinkTarget" :class="itemClasses">
              <icon-sui-backward class="text-primary" />
              Back
            </router-link>
          </td>
        </tr>
        <tr
          v-for="file in sortedAndFilteredFiles"
          :key="file.path"
          class="dark:hover:text-accent"
          @mouseenter="moveIndicator"
        >
          <td :colspan="!file.updatedOn ? 2 : null">
            <MFileTreeItem
              :class="itemClasses"
              :file="file"
              :route="route"
              :base-path="basePath"
              :password-record="props.password"
            />
          </td>
          <td
            v-if="file.updatedOn"
            class="py-3 pr-6 whitespace-nowrap hidden md:table-cell"
          >
            {{ formatDistanceFromToday(file.updatedOn).value }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
export default {
  name: 'MFileTree',
}
</script>

<script lang="ts" setup>
import { sort } from 'fast-sort'
import { ComputedRef } from 'vue'
import { useRoute } from 'vue-router'
import { ExtendedPathFileMetadata, ExtendedPathFileRecord } from './types'
import {
  dirname,
  FileMetadata,
  FileRecord,
  rootName,
  stripPathPrefix,
} from '~/util/file'
import { PasswordRecord } from '~/util/security'
import { formatDistanceFromToday } from '~/util/time'

const props = defineProps<{
  files: FileRecord[]
  passwordRecord?: ComputedRef<PasswordRecord>
  route: object
}>()
const route = useRoute()

// eslint-disable-next-line prefer-const
let sortReverse = $ref(false)
// eslint-disable-next-line prefer-const
let basePath: string = $computed(() => route.query.basePath || '')
// eslint-disable-next-line prefer-const
let root = $ref(null)
// eslint-disable-next-line prefer-const
let showIndicator = $ref(false)
// eslint-disable-next-line prefer-const
let indicatorStyle = $ref(null)
const sortBy = [
  (file: ExtendedPathFileMetadata) => file.type !== 'directory',
  (file: ExtendedPathFileMetadata) => file.path,
]
// eslint-disable-next-line prefer-const
let backLinkTarget = $computed(() => {
  const oneBack = dirname(basePath)
  return basePath ? { ...route, query: { basePath: oneBack } } : null
})
const headerClasses =
  'border-b font-semibold text-lg caps-all-small dark:border-gray-800'
const itemClasses = 'flex items-center gap-2 transition-colors py-3 pl-6 w-full'

function newImplicitDirectory(file: FileRecord): ExtendedPathFileMetadata {
  const dir = dirname(file.path)
  return {
    path: dir,
    pathWithoutPrefix: stripPathPrefix(dir, basePath),
    type: 'directory',
    mimeType: 'text/directory',
    sizeBytes: 0,
    updatedOn: null,
    createdOn: null,
  }
}

// eslint-disable-next-line prefer-const
let sortedAndFilteredFiles = $computed(() => {
  const currentPathRecords: ExtendedPathFileRecord[] = props.files
    .filter((record) => record.path.startsWith(basePath))
    .map((record: FileRecord) => ({
      ...record,
      pathWithoutPrefix: stripPathPrefix(record.path, basePath),
    }))

  const implicitDirectories = currentPathRecords
    .filter(
      (record) =>
        record.type === 'file' && record.pathWithoutPrefix.includes('/')
    )
    .map((record) => newImplicitDirectory(record))
  const explicitDirectories = currentPathRecords.filter(
    (record) => record.type === 'directory'
  )
  const processedDirectories = new Set()
  const directories = []
    .concat(implicitDirectories, explicitDirectories)
    .filter((record: ExtendedPathFileMetadata) => {
      const name = rootName(record.path)
      const shouldUse = !processedDirectories.has(name)
      processedDirectories.add(name)
      return shouldUse
    })

  const actualFiles = currentPathRecords.filter(
    (record) =>
      record.type === 'file' && !record.pathWithoutPrefix.includes('/')
  )
  return sort<FileMetadata | FileRecord>(
    [].concat(directories, actualFiles)
  ).by(sortBy)
})

function moveIndicator(event) {
  showIndicator = true
  const target =
    event.target.nodeName !== 'TR' ? event.target.closest('tr') : event.target
  const el = target.children[0]
  const elSize = el.getBoundingClientRect()
  const height = elSize.height
  const top = elSize.top - root.getBoundingClientRect().top
  // animating height is not really optimal but border-radius is based on the elements size
  // and does not take scale into account :(
  indicatorStyle = {
    '--tw-translate-y': `${top}px`,
    height: `${height}px`,
  }
}
</script>

<style>
@media (min-width: 900px) {
  .m-file-tree {
    grid-template-columns: max-content min-content;
  }
}
</style>
