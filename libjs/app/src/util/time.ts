import { formatDistance } from 'date-fns'
import { computed, ComputedRef, ref } from 'vue'
import { dateFnLocale } from './i18n'

export const now = (function () {
  const now = ref(new Date())

  setInterval(() => {
    now.value = new Date()
  }, 1000)

  return now
})()

export function formatDistanceFromToday(
  time: Date,
  options?: { includeSeconds?: boolean; addSuffix?: boolean }
): ComputedRef<string> {
  return computed(() =>
    formatDistance(time, now.value, {
      locale: dateFnLocale.value,
      addSuffix: true,
      ...(options || {}),
    })
  )
}
