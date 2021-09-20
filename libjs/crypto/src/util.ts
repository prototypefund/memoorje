export {
  DataStreamPositionTracker,
  DataType,
  Struct
}

type Iterableify<T> = { [K in keyof T]: Iterable<T[K]> }

function* zip<T extends Array<any>>(...toZip: Iterableify<T>): Generator<T> {
  const iterators = toZip.map(i => i[Symbol.iterator]())
  while (true) {
    const results = iterators.map(i => i.next())
    if (results.some(({ done }) => done)) {
      // abort if any of the iterables is exhausted
      break
    }
    yield results.map(({ value }) => value) as T
  }
}

function sum<T> (iterable: Iterable<T>, map: (value: T) => number) {
  let length = 0
  for (const item of iterable) {
    length += map(item)
  }
  return length
}

type DataType = number | string | boolean

abstract class StructType<T> {
  initializer: string

  constructor(initializer: string) {
    this.initializer = initializer
  }

  abstract get length(): number

  abstract encode (data: T, bigEndian: boolean): Uint8Array
  abstract decode (data: Uint8Array, bigEndian: boolean): T
}

class StructStringType extends StructType<string> {
  public static readonly format: RegExp = /\d+s/

  get length () {
    return parseInt(this.initializer.slice(0, -1))
  }

  encode(data: string, bigEndian: boolean): Uint8Array {
    return Uint8Array.from(
      Array.from(data).map(s => s.charCodeAt(0))
    )
  }

  decode(data: Uint8Array, bigEndian: boolean): string {
    return Array.from(data)
      .map((num) => String.fromCharCode(num))
      .join('')
  }
}

class StructUnsignedLongType extends StructType<number> {
  public static readonly format: RegExp = /L/
  length = 4

  encode(data: number, bigEndian: boolean): Uint8Array {
    const encoded = new Uint8Array(this.length)
    const dv = new DataView(encoded.buffer)
    dv.setUint32(0, data, bigEndian)
    return encoded
  }

  decode(data: Uint8Array, bigEndian: boolean): number {
    const dv = new DataView(data.buffer)
    return dv.getUint32(0, bigEndian)
  }
}

class StructUnsignedShortType extends StructType<number> {
  public static readonly format: RegExp = /H/
  length = 2

  encode(data: number, bigEndian: boolean): Uint8Array {
    const encoded = new Uint8Array(this.length)
    const dv = new DataView(encoded.buffer)
    dv.setUint16(0, data, bigEndian)
    return encoded
  }

  decode(data: Uint8Array, bigEndian: boolean): number {
    const dv = new DataView(data.buffer)
    return dv.getUint16(0, bigEndian)
  }
}

class Struct {
  private static dataTypes = [
    StructStringType,
    StructUnsignedShortType,
    StructUnsignedLongType,
  ]
  private readonly formatComponents: StructType<DataType>[]
  private readonly bigEndian: boolean

  private static parseFormat (format: string) {
    const formatComponents: StructType<any>[] = []
    const bigEndian = {
      '<': true,
      '>': false
    }[format[0]]

    if (typeof bigEndian === 'undefined') {
      throw new Error(`Invalid format string (missing endian encoding): ${format}`)
    }

    let dataFormat = format.slice(1)
    while (dataFormat) {
      let matched = false

      for (const dataType of this.dataTypes) {
        const match = dataFormat.match(dataType.format)
        if (match !== null && match.index === 0) {
          const value = match[0]
          formatComponents.push(new dataType(value))
          dataFormat = dataFormat.slice(value.length)
          matched = true
        }
      }

      if (!matched) {
        throw new Error(`Invalid format string: ${format}`)
      }
    }

    return {
      bigEndian,
      formatComponents
    }
  }

  constructor (format: string) {
    const { bigEndian, formatComponents } = Struct.parseFormat(format)
    this.bigEndian = bigEndian
    this.formatComponents = formatComponents
  }

  pack (data: Iterable<DataType>): Uint8Array {
    const result = new Uint8Array(this.size)
    const tracker = new DataStreamPositionTracker(result)
    for (const [dataType, value] of zip(this.formatComponents, Array.from(data))) {
      tracker.set(dataType.encode(value, this.bigEndian))
    }
    return result
  }

  unpack (data: Uint8Array): DataType[] {
    const result = []
    const tracker = new DataStreamPositionTracker(data)
    for (const dataType of this.formatComponents) {
      result.push(dataType.decode(tracker.get(dataType.length), this.bigEndian))
    }
    return result
  }

  get size (): number {
    return sum(this.formatComponents, (value: StructType<any>) => value.length)
  }
}

class DataStreamPositionTracker {
  private data: Uint8Array
  private position: number

  constructor(data: Uint8Array, initialPosition: number = 0) {
    this.data = data
    this.position = initialPosition
  }

  get (byteCount?: number) {
    const newPosition: number =
      typeof byteCount == 'number'
        ? this.position + byteCount
        : this.data.length
    const result: Uint8Array = this.data.slice(this.position, newPosition)
    this.position = newPosition
    return result
  }

  set (data: Uint8Array) {
    this.data.set(data, this.position)
    this.position = this.position + data.length
  }
}
