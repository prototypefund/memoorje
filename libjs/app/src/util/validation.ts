// eslint-disable-next-line import/no-named-as-default
import useVuelidate from '@vuelidate/core'
import { helpers } from '@vuelidate/validators'
import { reactive, Ref, watchEffect } from 'vue'

export interface ValidationError {
  id: string
  message: string
}

interface ServerValidated {
  [field: string]: ValidationError[]
}

export interface Validation {
  isValid: boolean
  errors: ValidationError[]
  $trigger(field?: string): void
}

export class ServerValidationException extends Error {
  validation: ServerValidated

  constructor(message: string, validation?: ServerValidated) {
    super(message)
    this.validation = validation || {}
  }
}

export function fromServer(state: Ref<any>, field: string) {
  return helpers.withMessage(
    ($invalid) => {
      return $invalid ? state.value[field][0].message : ''
    },
    () => {
      if (state.value === null) return true
      return !Array.isArray(state.value[field])
    }
  )
}

export function vuelidateToCommon(rules: any, state: any): Validation {
  const validation = useVuelidate(rules, state)
  const newValidation: any = reactive({
    $trigger(field?: string) {
      let validator: any = validation.value
      if (typeof field === 'string') {
        validator = validator[field]
      }
      validator.$validate()
    },
  })

  function updateValidationState() {
    Object.getOwnPropertyNames(validation.value)
      .filter((propName) => !propName.startsWith('$'))
      .forEach((propName) => {
        const errors = []
        for (const error of validation.value[propName].$errors) {
          try {
            errors.push({
              id: error.$uid,
              message: error.$message,
            })
          } catch (err) {
            console.info(
              `Error on wrapping vuelidate validation for ${propName}`,
              err
            )
          }
        }
        const isValid = errors.length === 0
        newValidation[propName] = { isValid, errors }
      })
  }
  updateValidationState()
  watchEffect(updateValidationState, { flush: 'post' })
  return newValidation
}

interface RestFrameworkValidationResponseObject {
  [field: string]:
    | string
    | Array<string>
    | RestFrameworkValidationResponseObject
}

export async function parseValidationResponse(
  res: Response
): Promise<ServerValidated> {
  if (!(res instanceof Response)) {
    throw res
  }

  const data: RestFrameworkValidationResponseObject = await res.json()
  let id = 0
  const nextId = () => `restframework-server-validated-${id++}`

  function* iter(
    obj: RestFrameworkValidationResponseObject,
    keyBase = ''
  ): Iterable<[string, ValidationError[]]> {
    for (const [key, value] of Object.entries(obj)) {
      const newKey = keyBase + key
      if (typeof value === 'string') {
        if (key === 'detail') {
          yield ['$GLOBAL_STATE', [{ id: nextId(), message: value }]]
        }
      } else if (Array.isArray(value)) {
        yield [newKey, value.map((message) => ({ id: nextId(), message }))]
      } else {
        yield* iter(value, `${newKey}.`)
      }
    }
  }

  return Object.fromEntries(iter(data))
}
