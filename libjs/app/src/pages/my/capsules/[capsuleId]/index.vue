<template>
  <MPage unsized>
    <div class="m-auto lg:max-w-container lg:px-6">
      <template v-if="passwordRecord">
        <div class="lg:max-w-container">
          <MDropzone
            style="min-height: 300px"
            class="lg:rounded"
            @file="handleFile"
          >
            <MFileTree
              :files="files"
              :route="{ name: 'my-capsules-capsuleId', params: { capsuleId } }"
              @file="handleFile"
            />
          </MDropzone>
        </div>
      </template>
      <template v-else>
        <MCapsuleOpenDialog :capsule-id="capsuleId" />
      </template>
    </div>
  </MPage>
</template>

<script lang="ts" setup>
import { watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BaseState, useMainStore } from '~/store/main'
import {
  addCapsuleContent,
  getCapsule,
  getCapsuleContents,
} from '~/util/api/capsule'
import { encryptFile, FileRecord } from '~/util/file'

const router = useRouter()
const route = useRoute()
const store: BaseState = useMainStore()
const capsuleId = route.params.capsuleId
const passwordRecord = store.safe.retrieve(capsuleId)
let isLoading = $ref(false)
let capsule = $ref(null)
let files: FileRecord[] = $ref([])

async function updateCapsule() {
  const password = passwordRecord.value?.password
  if (password) {
    isLoading = true
    capsule = null
    files = []
    try {
      capsule = await getCapsule(route.params.capsuleId)
      for await (const file of getCapsuleContents(password, capsuleId)) {
        files.push(file)
      }
    } catch (err) {
      console.error('error loading capsule', err)
    } finally {
      isLoading = false
    }
  }
}

async function handleFile(file: FileRecord) {
  passwordRecord.value?.touch()
  files.push(file)
  await file.transferStatus.loading?.isDone
  await encryptFile(passwordRecord.value.password, file)
  await addCapsuleContent(capsule.id, file)
}

watch(
  () => passwordRecord.value === null,
  (shouldCloseCapsule, wasClosed) => {
    if (shouldCloseCapsule) {
      files = []
    }
    if (!shouldCloseCapsule && wasClosed) {
      updateCapsule()
    }
  },
  { immediate: true }
)

nextTick(() => {
  updateCapsule()
})
</script>
