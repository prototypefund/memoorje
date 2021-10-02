<template>
  <MForm
    style="max-width: 450px"
    autocomplete="off"
    label="New Capsule"
    @submit.prevent="doCreateCapsule"
  >
    <MField id="new-capsule-name" label="Name of your Capsule">
      <MInput
        v-model="state.name"
        autofocus
        aria-describedby="new-capsule-name-description"
      />
    </MField>

    <MField id="new-capsule-password" label="Password for Encryption">
      <MInput
        v-model="state.password"
        type="password"
        aria-describedby="new-capsule-password-description"
      />
      <template #description>
        <p class="mb-3">
          This password will be used to encrypt the contents of your capsule. It
          should but doesn’t have to be different from your account password.
        </p>
        <p>We <strong>will never</strong> ask your for your passwords.</p>
      </template>
    </MField>

    <MField id="new-capsule-password-confirm" label="Password (confirm)">
      <MInput v-model="state.passwordConfirm" type="password" />
    </MField>

    <MButton
      type="submit"
      design="accent"
      class="w-full sm:w-auto sm:order-last sm:mx-0 flex-grow sm:max-w-1/2"
      @click="doCreateCapsule"
      >Create Capsule
    </MButton>
  </MForm>
</template>

<script lang="ts" setup>
import { computed, reactive } from 'vue'
import { helpers, required, sameAs } from '@vuelidate/validators'
import { fromServer, vuelidateToCommon } from '~/util/validation'
import { createCapsule } from '~/util/api/capsule'

const emit = defineEmits<{
  (e: 'created', capsule: any): void
}>()

const state = reactive({
  name: '',
  password: '',
  passwordConfirm: '',
})
// eslint-disable-next-line prefer-const
let serverValidationData = $ref(null)
const dataValidationRules = {
  name: { required, server: fromServer($$(serverValidationData), 'name') },
  password: { required },
  passwordConfirm: {
    required,
    sameAsPassword: helpers.withMessage(
      'Passwords need to match',
      sameAs(computed(() => state.password))
    ),
  },
}
const validation = vuelidateToCommon(dataValidationRules, state)

async function doCreateCapsule() {
  const capsule = await createCapsule({
    name: state.name,
  })
  emit('created', {
    ...capsule,
    password: state.password,
  })
}
</script>
