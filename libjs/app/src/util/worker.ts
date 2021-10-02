import { delay } from '~/util/promise'

export class WorkerPool<T> {
  private workers: T[]

  constructor(workers: T[]) {
    this.workers = workers
  }

  async requestWorker<K>(callback: (worker: T) => Promise<K>): Promise<K> {
    const getWorker = async () => {
      while (true) {
        const worker = this.workers.shift()
        if (worker) {
          return worker
        } else {
          await delay(0.05)
        }
      }
    }

    console.group('new worker context')
    const worker = await getWorker()
    console.debug('assigned a worker')
    const result = await callback(worker)
    console.debug('worker returned result')
    this.workers.push(worker)
    console.debug('returned worker as available')
    console.groupEnd()
    return result
  }
}
