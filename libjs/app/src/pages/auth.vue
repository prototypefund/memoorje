<template>
  <MPage unsized>
    <MAuthDialog class="fixed bottom-0 w-full mx-auto sm:static md:mt-24" />
  </MPage>
</template>

<script lang="ts" setup>
import { useHead } from '@vueuse/head'

useHead({
  title: 'memoorje login',
})
</script>
