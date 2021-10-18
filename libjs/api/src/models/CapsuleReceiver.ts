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
 * @interface CapsuleReceiver
 */
export interface CapsuleReceiver {
    /**
     * 
     * @type {string}
     * @memberof CapsuleReceiver
     */
    capsule: string;
    /**
     * 
     * @type {string}
     * @memberof CapsuleReceiver
     */
    email: string;
    /**
     * 
     * @type {number}
     * @memberof CapsuleReceiver
     */
    readonly id: number;
    /**
     * 
     * @type {string}
     * @memberof CapsuleReceiver
     */
    readonly url: string;
}

export function CapsuleReceiverFromJSON(json: any): CapsuleReceiver {
    return CapsuleReceiverFromJSONTyped(json, false);
}

export function CapsuleReceiverFromJSONTyped(json: any, ignoreDiscriminator: boolean): CapsuleReceiver {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'capsule': json['capsule'],
        'email': json['email'],
        'id': json['id'],
        'url': json['url'],
    };
}

export function CapsuleReceiverToJSON(value?: CapsuleReceiver | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'capsule': value.capsule,
        'email': value.email,
    };
}

