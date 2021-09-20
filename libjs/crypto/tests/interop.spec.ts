import { spawnSync } from 'child_process'
import { join } from 'path'

import { test, expect } from '@playwright/test'

const PASSWORD = 'abc123'
const BASE_PATH = join(__dirname, '..', '..', '..')
const encoder = new TextEncoder()
const decoder = new TextDecoder()


async function memoorjeCrypto (method: string, input: Uint8Array, password: string = PASSWORD) {
  const { stdout } = spawnSync(
    'python3', ['-m', 'memoorje_crypto', method, '--password', password],
    {
      cwd: BASE_PATH,
      env: {PYTHONPATH: join(BASE_PATH, 'libpy', 'memoorje_crypto')},
      encoding: 'buffer',
      input
    }
  )
  return Uint8Array.from(stdout)
}

async function encrypt (args: { password: string, plainText: Array<number> }) {
  return Array.from(await new window.MemoorjeCrypto.EncryptionV1().encrypt(args.password, Uint8Array.from(args.plainText)))
}

async function decrypt (args: { password: string, data: Array<number> }) {
  return Array.from(await new window.MemoorjeCrypto.EncryptionV1().decrypt(args.password, Uint8Array.from(args.data)))
}

async function loadTestEnv (page) {
  await page.goto('tests/index.html')
  await page.waitForFunction(() => typeof window.MemoorjeCrypto !== 'undefined')
}

test('Data encrypted in Python can be decrypted in browser', async ({ page }) => {
  await loadTestEnv(page)
  const plainText = 'from Python to browser'
  const encryptedDataFromPython = await memoorjeCrypto('encrypt', encoder.encode(plainText))
  const decipheredDataFromBrowser = Uint8Array.from(
    await page.evaluate(decrypt, {password: PASSWORD, data: Array.from(encryptedDataFromPython)})
  )
  expect(plainText).toEqual(decoder.decode(decipheredDataFromBrowser))
})

test('Data encrypted in browser can be decrypted in Python', async ({ page }) => {
  await loadTestEnv(page)
  const plainText = 'from browser to Python'
  const encryptedDataFromBrowser = Uint8Array.from(
    await page.evaluate(encrypt, {password: PASSWORD, plainText: Array.from(encoder.encode(plainText))})
  )
  const decipheredDataFromJavaScript = await memoorjeCrypto('decrypt', encryptedDataFromBrowser)
  expect(plainText).toEqual(decoder.decode(decipheredDataFromJavaScript))
})
