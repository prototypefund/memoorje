<template>
  <MPage unsized title="Create new Capsule">
    <MNewCapsule @created="onCreated" />
  </MPage>
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router'
import { useMainStore } from '~/store/main'

const router = useRouter()
const store = useMainStore()

function onCreated(capsule) {
  store.safe.open(capsule.id, capsule.password)
  router.push({
    name: 'my-capsules-capsuleId',
    params: { capsuleId: capsule.id },
  })
}
</script>
