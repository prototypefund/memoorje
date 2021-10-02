import { expose, transfer } from 'comlink'
import { EncryptionV1 } from '@memoorje/crypto'

const encryptionV1 = new EncryptionV1()

async function encrypt(password: string, plainText: ArrayBuffer) {
  const data = await encryptionV1.encrypt(password, new Uint8Array(plainText))
  return transfer(data, [data.buffer])
}

async function decrypt(password: string, cipherText: ArrayBuffer) {
  const data = await encryptionV1.decrypt(password, new Uint8Array(cipherText))
  return transfer(data, [data.buffer])
}

expose({
  encrypt,
  decrypt,
})
