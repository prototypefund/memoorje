<template>
  <icon-clarity-directory-solid v-if="file.type === 'directory'" />
  <icon-ant-design-file-pdf-outlined v-else-if="file.path.endsWith('.pdf')" />
  <icon-ant-design-file-image-outlined
    v-else-if="file.mimeType.startsWith('image/')"
  />
  <icon-ant-design-file-excel-outlined
    v-else-if="file.path.endsWith('.xsl') || file.path.endsWith('.xslx')"
  />
  <icon-ant-design-file-word-outlined
    v-else-if="file.path.endsWith('.doc') || file.path.endsWith('.docx')"
  />
  <icon-ant-design-file-zip-outlined
    v-else-if="
      file.path.endsWith('.zip') ||
      file.path.endsWith('.rar') ||
      file.path.endsWith('.7z') ||
      file.path.includes('.tar')
    "
  />
  <icon-ant-design-file-outlined v-else />
</template>

<script lang="ts" setup>
import {
  ExtendedPathFileMetadata,
  ExtendedPathFileRecord,
} from '~/components/files/types'

const props = defineProps<{
  file: ExtendedPathFileMetadata | ExtendedPathFileRecord
}>()
</script>
