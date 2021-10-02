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
 * @interface ResetPassword
 */
export interface ResetPassword {
    /**
     * 
     * @type {string}
     * @memberof ResetPassword
     */
    userId: string;
    /**
     * 
     * @type {number}
     * @memberof ResetPassword
     */
    timestamp: number;
    /**
     * 
     * @type {string}
     * @memberof ResetPassword
     */
    signature: string;
    /**
     * 
     * @type {string}
     * @memberof ResetPassword
     */
    password: string;
}

export function ResetPasswordFromJSON(json: any): ResetPassword {
    return ResetPasswordFromJSONTyped(json, false);
}

export function ResetPasswordFromJSONTyped(json: any, ignoreDiscriminator: boolean): ResetPassword {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'userId': json['userId'],
        'timestamp': json['timestamp'],
        'signature': json['signature'],
        'password': json['password'],
    };
}

export function ResetPasswordToJSON(value?: ResetPassword | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'userId': value.userId,
        'timestamp': value.timestamp,
        'signature': value.signature,
        'password': value.password,
    };
}

