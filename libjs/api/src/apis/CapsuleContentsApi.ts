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


import * as runtime from '../runtime';
import {
    CapsuleContent,
    CapsuleContentFromJSON,
    CapsuleContentToJSON,
} from '../models';

export interface CapsuleContentsCreateRequest {
    capsule: string;
    metadata: string;
    data: string;
}

export interface CapsuleContentsDestroyRequest {
    id: string;
}

/**
 * 
 */
export class CapsuleContentsApi extends runtime.BaseAPI {

    /**
     * Capsule content access for authenticated users
     */
    async capsuleContentsCreateRaw(requestParameters: CapsuleContentsCreateRequest): Promise<runtime.ApiResponse<CapsuleContent>> {
        if (requestParameters.capsule === null || requestParameters.capsule === undefined) {
            throw new runtime.RequiredError('capsule','Required parameter requestParameters.capsule was null or undefined when calling capsuleContentsCreate.');
        }

        if (requestParameters.metadata === null || requestParameters.metadata === undefined) {
            throw new runtime.RequiredError('metadata','Required parameter requestParameters.metadata was null or undefined when calling capsuleContentsCreate.');
        }

        if (requestParameters.data === null || requestParameters.data === undefined) {
            throw new runtime.RequiredError('data','Required parameter requestParameters.data was null or undefined when calling capsuleContentsCreate.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && (this.configuration.username !== undefined || this.configuration.password !== undefined)) {
            headerParameters["Authorization"] = "Basic " + btoa(this.configuration.username + ":" + this.configuration.password);
        }
        const consumes: runtime.Consume[] = [
            { contentType: 'application/x-www-form-urlencoded' },
            { contentType: 'multipart/form-data' },
            { contentType: 'application/json' },
        ];
        // @ts-ignore: canConsumeForm may be unused
        const canConsumeForm = runtime.canConsumeForm(consumes);

        let formParams: { append(param: string, value: any): any };
        let useForm = false;
        if (useForm) {
            formParams = new FormData();
        } else {
            formParams = new URLSearchParams();
        }

        if (requestParameters.capsule !== undefined) {
            formParams.append('capsule', requestParameters.capsule as any);
        }

        if (requestParameters.metadata !== undefined) {
            formParams.append('metadata', requestParameters.metadata as any);
        }

        if (requestParameters.data !== undefined) {
            formParams.append('data', requestParameters.data as any);
        }

        const response = await this.request({
            path: `/api/capsule-contents/`,
            method: 'POST',
            headers: headerParameters,
            query: queryParameters,
            body: formParams,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => CapsuleContentFromJSON(jsonValue));
    }

    /**
     * Capsule content access for authenticated users
     */
    async capsuleContentsCreate(requestParameters: CapsuleContentsCreateRequest): Promise<CapsuleContent> {
        const response = await this.capsuleContentsCreateRaw(requestParameters);
        return await response.value();
    }

    /**
     * Capsule content access for authenticated users
     */
    async capsuleContentsDestroyRaw(requestParameters: CapsuleContentsDestroyRequest): Promise<runtime.ApiResponse<void>> {
        if (requestParameters.id === null || requestParameters.id === undefined) {
            throw new runtime.RequiredError('id','Required parameter requestParameters.id was null or undefined when calling capsuleContentsDestroy.');
        }

        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && (this.configuration.username !== undefined || this.configuration.password !== undefined)) {
            headerParameters["Authorization"] = "Basic " + btoa(this.configuration.username + ":" + this.configuration.password);
        }
        const response = await this.request({
            path: `/api/capsule-contents/{id}/`.replace(`{${"id"}}`, encodeURIComponent(String(requestParameters.id))),
            method: 'DELETE',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.VoidApiResponse(response);
    }

    /**
     * Capsule content access for authenticated users
     */
    async capsuleContentsDestroy(requestParameters: CapsuleContentsDestroyRequest): Promise<void> {
        await this.capsuleContentsDestroyRaw(requestParameters);
    }

    /**
     * Capsule content access for authenticated users
     */
    async capsuleContentsListRaw(): Promise<runtime.ApiResponse<Array<CapsuleContent>>> {
        const queryParameters: any = {};

        const headerParameters: runtime.HTTPHeaders = {};

        if (this.configuration && (this.configuration.username !== undefined || this.configuration.password !== undefined)) {
            headerParameters["Authorization"] = "Basic " + btoa(this.configuration.username + ":" + this.configuration.password);
        }
        const response = await this.request({
            path: `/api/capsule-contents/`,
            method: 'GET',
            headers: headerParameters,
            query: queryParameters,
        });

        return new runtime.JSONApiResponse(response, (jsonValue) => jsonValue.map(CapsuleContentFromJSON));
    }

    /**
     * Capsule content access for authenticated users
     */
    async capsuleContentsList(): Promise<Array<CapsuleContent>> {
        const response = await this.capsuleContentsListRaw();
        return await response.value();
    }

}
