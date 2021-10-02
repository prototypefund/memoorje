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
 * Default serializer used for e-mail registration (e-mail change).
 * @export
 * @interface DefaultRegisterEmail
 */
export interface DefaultRegisterEmail {
    /**
     * 
     * @type {string}
     * @memberof DefaultRegisterEmail
     */
    email: string;
}

export function DefaultRegisterEmailFromJSON(json: any): DefaultRegisterEmail {
    return DefaultRegisterEmailFromJSONTyped(json, false);
}

export function DefaultRegisterEmailFromJSONTyped(json: any, ignoreDiscriminator: boolean): DefaultRegisterEmail {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'email': json['email'],
    };
}

export function DefaultRegisterEmailToJSON(value?: DefaultRegisterEmail | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'email': value.email,
    };
}

