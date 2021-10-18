import { createI18n } from 'vue-i18n'
import { Locale } from 'date-fns'
import { ref, Ref, watch } from 'vue'

const messages = Object.fromEntries(
  Object.entries(import.meta.globEager('../locales/*.y(a)?ml')).map(
    ([key, module]) => {
      const localeKey = key.split('/').slice(-1)[0].split('.')[0]
      return [localeKey, module.default || {}]
    }
  )
)

export const i18n = createI18n({
  locale: (function () {
    let language: string

    if (import.meta.env.SSR) {
      language = 'en'
    } else {
      const browserLanguage = navigator.languages[0].split('-')[0]
      const preferredLanguage = localStorage.getItem('preferredLanguage')
      language = preferredLanguage || browserLanguage
    }

    return language
  })(),
  messages,
})

function dateFnLocaleFrom(loader: Promise<{ default: any }>): Promise<Locale> {
  return loader.then((module) => module.default) as Promise<Locale>
}

const dateFnLocaleList: { [key: string]: () => Promise<Locale> } = {
  de: () => dateFnLocaleFrom(import('date-fns/locale/de')),
}

export const dateFnLocale: Ref<Locale | undefined> = (function () {
  const dateFnLocale: Ref<Locale | undefined> = ref(undefined)
  // @ts-ignore
  const { locale }: { locale: Ref<string> } = i18n.global
  watch(
    () => locale,
    async () => {
      if (typeof dateFnLocaleList[locale.value] !== 'undefined') {
        dateFnLocale.value = await dateFnLocaleList[locale.value]()
      }
    },
    { immediate: true }
  )
  return dateFnLocale
})()
