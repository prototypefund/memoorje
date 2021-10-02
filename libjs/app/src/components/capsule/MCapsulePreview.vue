<template>
  <MBox
    is="router-link"
    class="group px-4 pt-3 pb-4 rounded"
    :to="{ name: 'my-capsules-capsuleId', params: { capsuleId: capsule.id } }"
  >
    <header class="mb-2">
      <h2 class="text-xl font-bold group-hover:underline group-focus:underline">
        {{ capsule.name }}
      </h2>
      <p class="text-sm text-gray-500">Updated {{ updatedOn }}</p>
    </header>
    <p class="text-sm flex items-center">
      <template v-if="closesIn">
        <icon-sui-lock-open />
        Open, closes {{ closesIn }}
      </template>
      <template v-else>
        <icon-sui-lock />
        Closed
      </template>
    </p>
  </MBox>
</template>

<script lang="ts" setup>
import { formatRelative, formatDistance } from 'date-fns'
import { Capsule } from './types'
import { BaseState, useMainStore } from '~/store/main'
import { now } from '~/util/time'

const props = defineProps<{
  capsule: Capsule
}>()
const store: BaseState = useMainStore()
const passwordRecord = store.safe.retrieve(props.capsule.id)
// eslint-disable-next-line prefer-const
let closesIn = $computed(() => {
  if (passwordRecord.value && passwordRecord.value.expires > now.value) {
    return formatDistance(passwordRecord.value.expires, now.value, {
      addSuffix: true,
    })
  }
})
// eslint-disable-next-line prefer-const
let updatedOn = $computed(() => {
  return formatRelative(props.capsule.updatedOn, now.value)
})
</script>
