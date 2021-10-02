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
 * Default serializer used for user profile. It will use these:
 * 
 * * User fields
 * * :ref:`user-hidden-fields-setting` setting
 * * :ref:`user-public-fields-setting` setting
 * * :ref:`user-editable-fields-setting` setting
 * 
 * to automagically generate the required serializer fields.
 * @export
 * @interface DefaultUserProfile
 */
export interface DefaultUserProfile {
    /**
     * 
     * @type {number}
     * @memberof DefaultUserProfile
     */
    readonly id: number;
    /**
     * 
     * @type {string}
     * @memberof DefaultUserProfile
     */
    readonly email: string;
    /**
     * 
     * @type {string}
     * @memberof DefaultUserProfile
     */
    name?: string;
}

export function DefaultUserProfileFromJSON(json: any): DefaultUserProfile {
    return DefaultUserProfileFromJSONTyped(json, false);
}

export function DefaultUserProfileFromJSONTyped(json: any, ignoreDiscriminator: boolean): DefaultUserProfile {
    if ((json === undefined) || (json === null)) {
        return json;
    }
    return {
        
        'id': json['id'],
        'email': json['email'],
        'name': !exists(json, 'name') ? undefined : json['name'],
    };
}

export function DefaultUserProfileToJSON(value?: DefaultUserProfile | null): any {
    if (value === undefined) {
        return undefined;
    }
    if (value === null) {
        return null;
    }
    return {
        
        'name': value.name,
    };
}

