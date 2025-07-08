import { writable } from 'svelte/store';
import djangoWsClient from '$lib/services/djangoWS.js';

export const testWSStore = writable([]);

export const connectTestWS = () => {
    djangoWsClient.connectApp('/test/', { username: 'test' });
    djangoWsClient.onApp('/test/', 'message', (data) => {
        testWSStore.update(state => [
            ...state,
            {
                message: data.message,
                type: data.type
            }
        ]);
    });
}