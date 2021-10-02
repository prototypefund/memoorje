export function deferred<T>() {
  let _resolve: (value: T) => void
  let _reject: (value: any) => void
  const promise = new Promise<T>((resolve, reject) => {
    _resolve = resolve
    _reject = reject
  })
  return {
    promise,
    // @ts-ignore
    resolve: _resolve,
    // @ts-ignore
    reject: _reject,
  }
}

export function delay<T>(
  timeInSeconds: number,
  result?: T
): Promise<T | undefined> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(result)
    }, timeInSeconds * 1000)
  })
}
