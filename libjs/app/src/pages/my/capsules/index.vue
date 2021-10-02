<template>
  <MPage title="Your Capsules">
    <div class="my-12">
      <div
        v-if="hasNoCapsules"
        class="content mx-auto font-semibold text-2xl"
        style="max-width: 400px"
      >
        <IllustrationNotFound />
        <p class="text-center">
          Can’t find any capsules. <br />Did someone hide them?
        </p>
      </div>
      <div v-else-if="isLoadingCapsules">Loading capsules</div>
      <div v-else>
        <div class="grid md:grid-cols-2 lg:grid-cols-3">
          <MCapsulePreview
            v-for="capsule in capsules"
            :key="capsule.id"
            :capsule="capsule"
          />
        </div>
      </div>
      <p class="text-center pt-12">
        <MButton
          is="router-link"
          :to="{ name: 'my-capsules-new' }"
          design="accent"
          size="large"
        >
          <MIcon>
            <icon-sui-component-add />
          </MIcon>
          Create Capsule
        </MButton>
      </p>
    </div>
  </MPage>
</template>

<script lang="ts" setup>
import { useHead } from '@vueuse/head'
import IllustrationNotFound from '~/assets/illustrations/not-found.svg?component'
import { listCapsules } from '~/util/api/capsule'
import MCapsulePreview from '~/components/capsule/MCapsulePreview.vue'

let capsules = $ref([])
let isLoadingCapsules: boolean = $ref(false)
// eslint-disable-next-line prefer-const
let hasNoCapsules = $computed(() => !isLoadingCapsules && capsules.length === 0)

async function updateCapsules() {
  isLoadingCapsules = true
  try {
    capsules = await listCapsules()
  } catch (err) {
    console.error('error loading capsules', err)
  } finally {
    isLoadingCapsules = false
  }
}

// don’t await this. async setup break $things
updateCapsules()

useHead({
  title: 'memoorje - My Capsules',
})
</script>
