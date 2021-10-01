/* tslint:disable */
/* eslint-disable */
/**
 * Memoorje API
 * Sicherer, selbstverwalteter digitaler Nachlass für alle
 *
 * The version of the OpenAPI document: 0.0.1
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 */

import { exists, mapValues } from '../runtime';
/**
 * 
 * @export
 * @interface ChangePassword
 */
export interface ChangePassword {
    /**
     * 
     * @type {string}
     * @memberof ChangePassword
     */
    oldPassword: string;
    /**
     * 
     * @type {string}
     * @memberof ChangePassword
     */
    password: string;
    /**
     * 
     * @type {string}
     * @memberof ChangePassword
     */
    passwordConfirm: string;
}

export function ChangePasswordFromJSON(json: any): ChangePassword {
    return ChangePasswordFromJSONTyped(json, false);
}

export function ChangePasswordFromJSONTyped(json: any, ignoreDiscriminator: boolean): ChangePassword {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'oldPassword': json['oldPassword'],
        'password': json['password'],
        'passwordConfirm': json['passwordConfirm'],
    };
}

export function ChangePasswordToJSON(value?: ChangePassword | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'oldPassword': value.oldPassword,
        'password': value.password,
        'passwordConfirm': value.passwordConfirm,
    };
}


