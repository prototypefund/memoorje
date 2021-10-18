<template>
  <MPage unsized title="memoorje">
    <div class="max-w-container px-6 m-auto font-semibold text-2xl">
      <h1 class="text-5xl max-w-prose font-black mb-6 leading-tight">
        Securely preserve <br class="hidden sm:block" />your
        <span
          class="underline"
          style="text-decoration-color: rgba(4, 216, 157, var(--tw-bg-opacity))"
        >
          digital inheritance</span
        >.
      </h1>
      <div class="grid gap-9 sm:grid-cols-cta w-full mb-9 sm:mb-3">
        <div>
          <p class="max-w-prose">
            Store photos, letters, passwords or any other data. Encrypted in
            your browser, safe from our and everyone else’s eyes and accessible
            only by those you want to.
          </p>
        </div>
        <div>
          <MButton
            is="router-link"
            design="accent"
            size="large"
            class="w-full sm:w-auto"
            style="min-width: 260px"
            :to="{ name: 'auth', query: { mode: 'registration' } }"
            >Sign Up Now
          </MButton>
          <div class="flex justify-center mt-3">
            <a href="#" class="text-lg font-semibold">Donate</a>
          </div>
        </div>
      </div>

      <p class="max-w-prose">
        Digital inheritance should be a public service. That’s why you can use
        memoorje free of charge. To finance the software development and keep
        the servers running we rely on donations.
      </p>
    </div>

    <div class="max-w-720p m-auto mt-16">
      <div class="md:rounded overflow-hidden">
        <picture class="block">
          <source
            type="image/avif"
            srcset="
              ../assets/wave-768.avif   768w,
              ../assets/wave-1280.avif 1280w,
              ../assets/wave-1920.avif 1920w,
              ../assets/wave.avif      3024w
            "
          />
          <source
            type="image/jpeg"
            srcset="
              ../assets/wave-768.jpg   768w,
              ../assets/wave-1280.jpg 1280w,
              ../assets/wave-1920.jpg 1920w,
              ../assets/wave.jpg      3024w
            "
          />
          <img
            class="w-full"
            alt=""
            width="3024"
            height="1134"
            src="../assets/wave-1920.jpg"
          />
        </picture>
      </div>
    </div>

    <div class="max-w-container m-auto px-6 mt-16">
      <h2 class="sr-only">About memoorje</h2>
      <div class="md:flex gap-12 justify-center">
        <MFigure :illustration="IllustrationVault" title="Secure by default">
          <p>
            memoorje encrypts your data before it is send to our servers. So
            even if we wanted to, we would not be able to see the contents.
          </p>
        </MFigure>
        <MFigure
          :illustration="IllustrationRealTimeCollaboration"
          title="Social by default"
        >
          <p>
            In case of your death the people you’ve defined as caretakers of
            your digital inheritance will be able to open it. No administrators,
            lawyers, or solicitors are involved.
          </p>
        </MFigure>
        <MFigure
          :illustration="IllustrationFreeSoftware"
          title="Open by default"
        >
          <p>
            memoorje is free and open source software. People who feel
            comfortable with it can setup their own servers, and developers can
            modify the source code and adapt it to their needs.
          </p>
        </MFigure>
      </div>
    </div>
  </MPage>
</template>

<script lang="ts" setup>
import { useHead } from '@vueuse/head'
import IllustrationRealTimeCollaboration from '~/assets/illustrations/real-time-collaboration.svg?component'
import IllustrationVault from '~/assets/illustrations/vault.svg?component'
import IllustrationFreeSoftware from '~/assets/illustrations/free-software.svg?component'

const parent = 'index'

useHead({
  title: 'memoorje',
})
</script>
