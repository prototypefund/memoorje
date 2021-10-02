<template>
  <MForm style="max-width: 450px" class="mt-12" @submit.prevent="open">
    <MField id="capsule-password" label="password">
      <MInput v-model="password" type="password" autofocus />
    </MField>
    <MButton design="accent" type="submit" @click="open">Open</MButton>
  </MForm>
</template>

<script lang="ts" setup>
import { BaseState, useMainStore } from '~/store/main'

const props = defineProps<{
  capsuleId: string
}>()
// eslint-disable-next-line prefer-const
let password = $ref('')
const store: BaseState = useMainStore()

function open() {
  store.safe.open(props.capsuleId, password)
}
</script>
