import { reactive } from 'vue'
import { encrypt, decrypt } from '~/util/crypto'
import { deferred } from '~/util/promise'

export type FileLoadingStatus = {
  bytesLoaded: number
  percentageLoaded: number
  isDone: Promise<boolean>
  error: DOMException | Error | null
}

export type FileUploadStatus = {
  bytesSent: number
  percentageSent: number
  isDone: Promise<boolean>
  error: DOMException | Error | null
}

type TransferStatus = {
  loading: FileLoadingStatus | null
  sent: FileUploadStatus | null
}

type EncryptedFileData = {
  metadataCipherText: Uint8Array | null
  dataCipherText: Uint8Array | null
  dataCipherTextUrl: string | null
}

export type FileMetadata = {
  path: string
  mimeType: string
  createdOn: Date
  updatedOn: Date
  sizeBytes: number
  type: 'file' | 'directory'
}

export type FileRecord = FileMetadata & {
  plainText: Uint8Array | null
  encrypted: EncryptedFileData
  transferStatus: TransferStatus
}

export function join(...paths: string[]) {
  let result = ''
  for (const path of paths) {
    if (result && !result.endsWith('/')) {
      result += '/'
    }
    result += path
  }
  return result
}

export function basename(path: string) {
  const parts = path.split('/')
  return parts[parts.length - 1]
}

export function dirname(path: string) {
  return join(...path.split('/').slice(0, -1))
}

export function rootName(path: string) {
  return path.split('/')[0]
}

export function stripPathPrefix(path: string, pathPrefix: string) {
  if (pathPrefix && path.startsWith(pathPrefix)) {
    const newPath = path.slice(pathPrefix.length)
    return newPath.startsWith('/') ? newPath.slice(1) : newPath
  } else {
    return path
  }
}

export async function encryptFile(
  password: string,
  file: FileRecord,
  purgePlainText = false
): Promise<void> {
  if (file.plainText === null) {
    throw new TypeError(
      'Cannot encrypt a FileRecord that does not have any data'
    )
  }

  const metadata: FileMetadata = {
    path: file.path,
    mimeType: file.mimeType,
    createdOn: file.createdOn,
    updatedOn: file.updatedOn,
    sizeBytes: file.sizeBytes,
    type: file.type,
  }

  file.encrypted.metadataCipherText = await encrypt(
    password,
    new TextEncoder().encode(
      JSON.stringify({
        ...metadata,
        createdOn: file.createdOn.toISOString(),
        updatedOn: file.updatedOn.toISOString(),
      })
    )
  )

  file.encrypted.dataCipherText = await encrypt(password, file.plainText)

  if (purgePlainText) {
    file.plainText = null
  }
}

export async function decryptFileMetadata(
  password: string,
  cipheredMetadata: Uint8Array
): Promise<FileMetadata> {
  const plainMetadata = JSON.parse(
    new TextDecoder().decode(await decrypt(password, cipheredMetadata))
  )
  const metadata: FileMetadata = {
    ...plainMetadata,
    createdOn: new Date(plainMetadata.createdOn),
    updatedOn: new Date(plainMetadata.updatedOn),
    type: plainMetadata.type || ('file' as const),
  }
  return metadata
}

export async function decryptFile(
  password: string,
  file: FileRecord,
  updateMetadata = false
): Promise<void> {
  if (file.encrypted.dataCipherText === null) {
    if (file.encrypted.dataCipherTextUrl) {
      const res = await fetch(file.encrypted.dataCipherTextUrl)
      file.encrypted.dataCipherText = new Uint8Array(await res.arrayBuffer())
    } else {
      throw new TypeError(
        'Cannot decrypt a FileRecord with no dataCipherText or dataCipherTextUrl'
      )
    }
  }

  file.plainText = await decrypt(password, file.encrypted.dataCipherText)

  if (updateMetadata) {
    if (file.encrypted.metadataCipherText === null) {
      throw new TypeError(
        'Cannot decrypt metadata for a FileRecord with no metadataCipherText.'
      )
    }
    Object.assign(
      file,
      await decryptFileMetadata(password, file.encrypted.metadataCipherText)
    )
  }
}

function readFile(file: File, pathPrefix: string): FileRecord {
  const now = new Date()
  const { promise, resolve } = deferred<boolean>()
  const record: FileRecord = {
    path: join(pathPrefix, file?.webkitRelativePath || file.name),
    type: 'file' as const,
    mimeType: file.type,
    sizeBytes: file.size,
    // we want both of these to be the same time,
    // but they shouldn’t reference the same object
    createdOn: new Date(now.getTime()),
    updatedOn: new Date(now.getTime()),
    plainText: null,
    encrypted: {
      metadataCipherText: null,
      dataCipherText: null,
      dataCipherTextUrl: null,
    },
    transferStatus: {
      sent: null,
      loading: {
        bytesLoaded: 0,
        percentageLoaded: 0,
        isDone: promise,
        error: null,
      },
    },
  }

  let reader: FileReader | null = new FileReader()
  let isDone = false
  reader.onprogress = function (event) {
    // onprogress shouldn’t be called after onload/onerror but with browser you
    // never know so we check if isDone has been set.
    if (!isDone) {
      record.sizeBytes = event.total
      record.transferStatus.loading.bytesLoaded = event.loaded
      record.transferStatus.loading.percentageLoaded = Math.min(
        100,
        (event.loaded / event.total) * 100
      )
    }
  }
  reader.onloadend = function () {
    reader = null
  }
  reader.onload = function () {
    isDone = true
    record.plainText = new Uint8Array(reader.result as ArrayBuffer)
    record.transferStatus.loading.bytesLoaded = record.sizeBytes
    record.transferStatus.loading.percentageLoaded = 100
    resolve(true)
  }
  reader.onerror = function () {
    isDone = true
    record.transferStatus.loading.error = reader.error
    resolve(true)
  }
  reader.readAsArrayBuffer(file)

  return reactive<FileRecord>(record)
}

function readFileEntry(
  fileEntry: FileSystemFileEntry,
  pathPrefix: string
): Promise<FileRecord> {
  return new Promise<FileRecord>((resolve, reject) => {
    fileEntry.file(
      async (file) => {
        resolve(await readFile(file, pathPrefix))
      },
      (error) => {
        reject(error)
      }
    )
  })
}

async function* readFileEntries(
  entries: FileSystemEntry[],
  pathPrefix: string
): AsyncIterable<FileRecord> {
  for (const entry of entries) {
    if (entry) {
      // checking instanceof FileSystemFileEntry or instanceof FileSystemDirectoryEntry
      // will break things because these types are not available globally in browsers
      if (entry.isFile) {
        yield await readFileEntry(entry as FileSystemFileEntry, pathPrefix)
      } else if (entry.isDirectory) {
        const reader = (entry as FileSystemDirectoryEntry).createReader()
        let subEntries: FileSystemEntry[] = []
        try {
          subEntries = await new Promise<FileSystemEntry[]>(
            (resolve, reject) => {
              reader.readEntries(
                (subEntries: FileSystemEntry[]) => {
                  resolve(subEntries)
                },
                (error) => {
                  reject(error)
                }
              )
            }
          )
        } catch (err) {
          console.error(
            `error while reading file subdirectory: ${entry.fullPath}`,
            err
          )
        }
        yield* await readFileEntries(subEntries, join(pathPrefix, entry.name))
      }
    }
  }
}

export async function* createFileRecords(
  items: FileList | DataTransferItemList,
  pathPrefix = ''
): AsyncIterable<FileRecord> {
  for (const item of items) {
    if (item instanceof File) {
      yield readFile(item, pathPrefix)
    } else if (item instanceof DataTransferItem) {
      const entry: FileSystemEntry =
        typeof item.getAsEntry !== 'undefined'
          ? item.getAsEntry()
          : typeof item.webkitGetAsEntry !== 'undefined'
          ? item.webkitGetAsEntry()
          : null
      if (entry) {
        yield* await readFileEntries([entry], pathPrefix)
      }
    }
  }
}
