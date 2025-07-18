import { writable } from "svelte/store";
import { authService } from "$lib/services/auth.js";
import djangoWsClient from "$lib/services/djangoWS.js";
import { browser } from '$app/environment';
import { datetimeNormalize } from "$lib/utils/datetimeNormalize";

const token = await authService.getAccessTokenFromCookie();

export const messages = writable([]);

export const latestMessage = writable({});

export const connectToWS = async () => {
    if (!browser) return;
    
    djangoWsClient.connectApp("/unified?token=" + token);    
    djangoWsClient.onApp("/unified?token=" + token, 'message', (data) => {
        console.log("Received WebSocket message:", data);
        latestMessage.set(data);
        messages.update(state => [
            ...state,
            {
                type: data.type,
                data: data.data,
                timestamp: data.timestamp || datetimeNormalize(new Date())
            }
        ]);
    });
}

export const disconnectFromWS = async () => {
    if (!browser) return;

    try {
        djangoWsClient.disconnect("/unified?token=" + token);
    } catch (error) {
        console.error('WebSocket切断エラー:', error);
    }
}

const InitializeMessages = async () => {
    await connectToWS();
}

export const JoinGroup = async (group_name) => {
    djangoWsClient.send("/unified?token=" + token, {
        action: 'join_group',
        group_name: group_name
    });
}

export const LeaveGroup = async (group_name) => {
    djangoWsClient.send("/unified?token=" + token, {
        action: 'leave_group',
        group_name: group_name
    });
}

InitializeMessages();