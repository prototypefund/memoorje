import { wrap, transfer, Remote } from 'comlink'
import _CryptoWorker from './crypto.worker?worker'
import { WorkerPool } from '~/util/worker'

interface CryptoWorker {
  encrypt(password: string, plainText: ArrayBuffer): ArrayBuffer

  decrypt(password: string, cipherText: ArrayBuffer): ArrayBuffer

  decryptBase64EncodedData(
    password: string,
    base64EncodedCipherText: string
  ): ArrayBuffer
}

let pool: WorkerPool<Remote<CryptoWorker>>
if (import.meta.env.SSR) {
  pool = new WorkerPool<Remote<CryptoWorker>>([])
} else {
  pool = new WorkerPool<Remote<CryptoWorker>>([
    wrap(new _CryptoWorker()),
    wrap(new _CryptoWorker()),
    wrap(new _CryptoWorker()),
    wrap(new _CryptoWorker()),
  ])
}

export async function encrypt(
  password: string,
  plainText: Uint8Array
): Promise<Uint8Array> {
  return await pool.requestWorker(async (worker) => {
    return new Uint8Array(
      await worker.encrypt(password, transfer(plainText, [plainText.buffer]))
    )
  })
}

export async function decrypt(
  password: string,
  cipherText: Uint8Array
): Promise<Uint8Array> {
  return await pool.requestWorker(async (worker) => {
    return new Uint8Array(
      await worker.decrypt(password, transfer(cipherText, [cipherText.buffer]))
    )
  })
}
