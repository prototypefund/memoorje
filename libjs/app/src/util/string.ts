export function makeId(length: number, prefix?: string) {
  const characters =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  return (
    (prefix || '') +
    Array(length)
      .fill(null)
      .map(() =>
        characters.charAt(Math.floor(Math.random() * characters.length))
      )
      .join('')
  )
}

// python-compatible split implementation
export function* split(
  str: string,
  separator: string,
  limit?: number
): Iterable<string> {
  if (limit === 0) {
    yield str
    return
  }
  const parts = str.split(separator)
  if (typeof limit === 'number' && limit < 0) {
    limit = undefined
  }
  if (typeof limit === 'undefined') {
    yield* parts
  } else {
    while (limit > 0 && parts.length > 0) {
      // technically .shift() might return undefined, but we already checked that there
      // are still elements in parts so we’re good
      // @ts-ignore
      yield parts.shift()
      limit--
    }
    if (parts.length > 0) {
      yield parts.join(separator)
    }
  }
}

export function secondsToTime(seconds: number, includeSeconds = false) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)

  let result = ''
  if (hours) {
    result += hours.toString().padStart(2, '0')
  }
  if (minutes) {
    result += minutes.toString().padStart(2, '0')
  }
  if (includeSeconds) {
    seconds = Math.floor(seconds % 60)
    result += result ? seconds.toString().padStart(2, '0') : seconds.toString()
  }

  return result
}
