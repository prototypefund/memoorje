import { toByteArray, fromByteArray } from 'base64-js'
import { reactive } from 'vue'
import { capsulesAPI, capsuleContentsAPI, configuration } from './_base'
import {
  parseValidationResponse,
  ServerValidationException,
} from '~/util/validation'
import { decryptFileMetadata, FileRecord, FileUploadStatus } from '~/util/file'
import { deferred } from '~/util/promise'

type CapsuleCreateData = {
  name: string
  description?: string
}

type CapsuleContent = {
  metadata: string
  data: string
}

export async function createCapsule(data: CapsuleCreateData) {
  try {
    return await capsulesAPI.capsulesCreate({
      id: '',
      name: data.name,
      description: data.description || '',
      url: '',
      createdOn: '',
      updatedOn: '',
    })
  } catch (err: any | Response) {
    throw new ServerValidationException(
      'Unable to create new capsule',
      await parseValidationResponse(err)
    )
  }
}

export async function listCapsules() {
  return await capsulesAPI.capsulesList()
}

export async function getCapsule(capsuleId: string) {
  return await capsulesAPI.capsulesRetrieve({
    id: capsuleId,
  })
}

export async function* getCapsuleContents(
  password: string,
  capsuleId: string
): AsyncIterable<FileRecord> {
  let contents: CapsuleContent[] = []
  try {
    contents = await capsuleContentsAPI.capsuleContentsList({
      capsule: capsuleId,
    })
  } catch (err: any | Response) {
    throw new ServerValidationException(
      `Unable to list contents for capsule ${capsuleId}`,
      await parseValidationResponse(err)
    )
  }
  for (const content of contents) {
    const encryptedMetadata = toByteArray(content.metadata)
    const metadata = await decryptFileMetadata(password, encryptedMetadata)
    const record: FileRecord = {
      ...metadata,
      plainText: null,
      transferStatus: {
        loading: null,
        sent: null,
      },
      encrypted: {
        metadataCipherText: encryptedMetadata,
        dataCipherText: null,
        dataCipherTextUrl: content.data,
      },
    }
    yield record
  }
}

export async function addCapsuleContent(capsuleId: string, file: FileRecord) {
  return new Promise((resolve, reject) => {
    const { promise: isDonePromise, resolve: resolveIsDone } =
      deferred<boolean>()
    const request = new XMLHttpRequest()
    const formData = new FormData()
    if (!file.encrypted.dataCipherText || !file.encrypted.metadataCipherText) {
      throw new TypeError(
        'Cannot add FileRecord as capsule with no dataCipherText or metaDataCipherText'
      )
    }
    // We do know which mime-types these files have, but
    // we don’t want to expose that to the API endpoints.
    const fileOptions = { type: 'application/octet-stream' }
    formData.set(
      'capsule',
      `${configuration.basePath}/api/capsules/${capsuleId}/`
    )
    // formData.set("metadata", new Blob([file.encrypted.metadataCipherText.buffer], fileOptions))
    formData.set('metadata', fromByteArray(file.encrypted.metadataCipherText))
    formData.set(
      'data',
      new Blob([file.encrypted.dataCipherText.buffer], fileOptions)
    )

    const sent = reactive<FileUploadStatus>({
      bytesSent: 0,
      percentageSent: 0,
      isDone: isDonePromise,
      error: null,
    })
    file.transferStatus.sent = sent
    request.onprogress = function (event) {
      if (!sent.isDone) {
        sent.bytesSent = event.loaded
        sent.percentageSent = Math.min(100, event.loaded / event.total)
      }
    }
    request.onload = function (event) {
      resolveIsDone(true)
      sent.bytesSent = event.loaded
      sent.percentageSent = Math.min(100, event.loaded / event.total)
      if (request.status === 201) {
        resolve(file)
      } else {
        reject(request)
      }
    }
    request.onerror = function () {
      resolveIsDone(true)
      sent.error = new Error('Error uploaded FileRecord')
      reject(request)
    }
    request.open('POST', `${configuration.basePath}/api/capsule-contents/`)
    if (configuration.headers) {
      for (const [key, value] of Object.entries(configuration.headers)) {
        request.setRequestHeader(key, value)
      }
    }
    request.send(formData)
  })
}
