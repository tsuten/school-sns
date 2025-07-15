import { writable } from "svelte/store";
import { authService } from "$lib/services/auth.js";
import djangoWsClient from "$lib/services/djangoWS.js";
import { browser } from '$app/environment';
import { datetimeNormalize } from "$lib/utils/datetimeNormalize";

const token = await authService.getAccessTokenFromCookie();

export const messages = writable([]);

export const connectToWS = async () => {
    if (!browser) return;
    
    djangoWsClient.connectApp("/unified?token=" + token);    
    djangoWsClient.onApp("/unified?token=" + token, 'message', (data) => {
        messages.update(state => [
            ...state,
            {
                data: data.data.message,
                timestamp: datetimeNormalize(new Date())
            }
        ]);
    });
}

export const disconnectFromWS = async () => {
    if (!browser) return;

    try {
        djangoWsClient.disconnectApp("/unified?token=" + token);
    } catch (error) {
        console.error('WebSocket切断エラー:', error);
    }
}

const InitializeMessages = async () => {
    await connectToWS();
}

InitializeMessages();