import { DataStreamPositionTracker, DataType, Struct } from './util.js'

abstract class EncryptionFormat {
  static readonly VERSION: string

  static get VERSION_FIELD_STRUCT(): Struct {
    return new Struct(`>${this.VERSION.length}s`)
  }

  private static parseVersion(data: Uint8Array): string {
    const rawVersionData = data.slice(0, this.VERSION_FIELD_STRUCT.size)
    return new TextDecoder().decode(rawVersionData)
  }

  static doesHandleDataStream(data: Uint8Array): boolean {
    return this.parseVersion(data) === this.VERSION
  }

  protected static createBuffer(...buffers: Uint8Array[]): Uint8Array {
    const dataSize = buffers.reduce((total, buffer) => total + buffer.length, 0) + this.VERSION_FIELD_STRUCT.size
    const data = new Uint8Array(dataSize)
    const tracker = new DataStreamPositionTracker(data)
    tracker.set(this.VERSION_FIELD_STRUCT.pack([this.VERSION]))
    for (const buffer of buffers) {
      tracker.set(buffer)
    }
    return data
  }

  abstract encrypt (password: string, plainText: Uint8Array): Promise<Uint8Array>
  abstract decrypt (password: string, data: Uint8Array): Promise<Uint8Array>
}

interface EncryptionV1Cipher {
  encrypt (plainText: Uint8Array): Promise<Uint8Array>
  decrypt (cipherText: Uint8Array): Promise<Uint8Array>
}

class EncryptionV1Metadata  {
  saltSizeBytes: number
  ivSizeBytes: number
  encryptionKeySizeBytes: number
  hashIterations: number

  constructor(saltSizeBytes: number, ivSizeBytes: number, encryptionKeySizeBytes: number, hashIterations: number) {
    this.saltSizeBytes = saltSizeBytes
    this.ivSizeBytes = ivSizeBytes
    this.encryptionKeySizeBytes = encryptionKeySizeBytes
    this.hashIterations = hashIterations
  }

  * [Symbol.iterator] (): Iterator<DataType> {
    yield this.saltSizeBytes
    yield this.ivSizeBytes
    yield this.encryptionKeySizeBytes
    yield this.hashIterations
  }
}

class EncryptionV1Header {
  metadata: EncryptionV1Metadata
  salt: Uint8Array
  iv: Uint8Array

  constructor(metadata: EncryptionV1Metadata, salt: Uint8Array, iv: Uint8Array) {
    this.metadata = metadata
    this.salt = salt
    this.iv = iv
  }
}

export class EncryptionV1 extends EncryptionFormat {
  static readonly VERSION = "memoorje:encdata:v1"

  saltSizeBytes: number
  ivSizeBytes: number
  encryptionKeySizeBytes: number
  hashIterations: number

  static METADATA_FIELD_STRUCT: Struct = new Struct(">HHHL")

  constructor (saltSizeBytes: number = 64, ivSizeBytes: number = 12, encryptionKeySizeBytes: number = 32, hashIterations: number = 250_000) {
    super()
    this.saltSizeBytes = saltSizeBytes
    this.ivSizeBytes = ivSizeBytes
    this.encryptionKeySizeBytes = encryptionKeySizeBytes
    this.hashIterations = hashIterations
  }

  private splitIntoHeaderAndCipherText (data: Uint8Array): [EncryptionV1Header, Uint8Array] {
    const tracker = new DataStreamPositionTracker(data, EncryptionV1.VERSION_FIELD_STRUCT.size)
    const rawMetadata = tracker.get(EncryptionV1.METADATA_FIELD_STRUCT.size)
    const metadata: EncryptionV1Metadata = new EncryptionV1Metadata(
      // @ts-ignore
      ...EncryptionV1.METADATA_FIELD_STRUCT.unpack(rawMetadata)
    )
    const salt = tracker.get(metadata.saltSizeBytes)
    const iv = tracker.get(metadata.ivSizeBytes)

    return [
      new EncryptionV1Header(metadata, salt, iv),
      tracker.get()
    ]
  }

  private async createCipher (
    password: string,
    salt: Uint8Array,
    iv: Uint8Array,
    encryptionKeySizeBytes: number,
    hashIterations: number
  ): Promise<EncryptionV1Cipher> {
    const passwordKey = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(password),
      "PBKDF2",
      false,
      ["deriveKey"]
    )
    const cipherKey = await crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        hash: "SHA-256",
        iterations: hashIterations,
        salt
      },
      passwordKey,
      { name: "AES-GCM", length: encryptionKeySizeBytes * 8 },
      false,
      ["encrypt", "decrypt"]
    )

    return {
      async encrypt (plainText: Uint8Array): Promise<Uint8Array> {
        return new Uint8Array(
          await crypto.subtle.encrypt(
            { name: "AES-GCM", iv },
            cipherKey,
            plainText
          )
        )
      },
      async decrypt(cipherText: Uint8Array): Promise<Uint8Array> {
        return new Uint8Array(
          await crypto.subtle.decrypt(
            { name: "AES-GCM", iv },
            cipherKey,
            cipherText
          )
        )
      }
    }
  }

  async encrypt (password: string, plainText: Uint8Array): Promise<Uint8Array> {
    const salt: Uint8Array = crypto.getRandomValues(new Uint8Array(this.saltSizeBytes))
    const iv: Uint8Array = crypto.getRandomValues(new Uint8Array(this.ivSizeBytes))
    const cipher = await this.createCipher(
      password,
      salt,
      iv,
      this.encryptionKeySizeBytes,
      this.hashIterations
    )
    return EncryptionV1.createBuffer(
      EncryptionV1.METADATA_FIELD_STRUCT.pack(
        new EncryptionV1Metadata(
          this.saltSizeBytes,
          this.ivSizeBytes,
          this.encryptionKeySizeBytes,
          this.hashIterations
        )
      ),
      salt,
      iv,
      await cipher.encrypt(plainText)
    )
  }

  async decrypt (password: string, data: Uint8Array): Promise<Uint8Array> {
    const [header, cipherText] = this.splitIntoHeaderAndCipherText(data)
    const cipher = await this.createCipher(
      password,
      header.salt,
      header.iv,
      header.metadata.encryptionKeySizeBytes,
      header.metadata.hashIterations
    )
    return await cipher.decrypt(cipherText)
  }
}
