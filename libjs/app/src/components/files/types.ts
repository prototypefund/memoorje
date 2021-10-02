import { FileMetadata, FileRecord } from '~/util/file'

export type ExtendedPathFileMetadata = FileMetadata & {
  pathWithoutPrefix: string
}
export type ExtendedPathFileRecord = ExtendedPathFileMetadata & FileRecord
