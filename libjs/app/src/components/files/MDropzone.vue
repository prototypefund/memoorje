<template>
  <form>
    <header class="w-full mb-3 px-3 flex items-center lg:px-0">
      <slot name="header-pre" />
      <MButton is="label" design="accent" class="ml-auto">
        <input
          type="file"
          class="sr-only"
          tabindex="-1"
          multiple
          @change="handleFiles($event.target.files)"
        />
        <MIcon>
          <icon-sui-plus />
        </MIcon>
        Add files
      </MButton>
      <slot name="header-post" />
    </header>
    <MBox
      :class="{ 'ring-2': isDragging }"
      v-bind="attrs"
      @drop.prevent.stop="onDrop"
      @dragleave.prevent.stop="isDragging = false"
      @dragenter.prevent.stop="isDragging = true"
      @dragover.prevent.stop="isDragging = true"
    >
      <slot />
    </MBox>
  </form>
</template>

<script lang="ts">
export default {
  inheritAttrs: false,
}
</script>

<script lang="ts" setup>
import { useAttrs } from 'vue'
import { createFileRecords, FileRecord } from '~/util/file'

const attrs = useAttrs()
const props = defineProps<{
  pathPrefix?: string
}>()
const emit = defineEmits<{
  (e: 'file', file: FileRecord): void
}>()

let isDragging = $ref(false)

async function handleFiles(items: FileList | DataTransferItemList) {
  for await (const file of createFileRecords(items)) {
    emit('file', file)
  }
}

function onDrop(event: DragEvent) {
  isDragging = false
  handleFiles(event.dataTransfer.items)
}
</script>
