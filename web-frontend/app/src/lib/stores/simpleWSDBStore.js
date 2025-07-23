import { writable } from "svelte/store";
import { authService } from "$lib/services/auth.js";
import djangoWsClient from "$lib/services/djangoWS.js";
import { browser } from '$app/environment';
import { datetimeNormalize } from "$lib/utils/datetimeNormalize";

const token = await authService.getAccessTokenFromCookie();

export const database = writable({});

export const connectToWS = async () => {
    if (!browser) return;
    
    djangoWsClient.connectApp("/unified?token=" + token);    
    djangoWsClient.onApp("/unified?token=" + token, 'message', (data) => {
        console.log("Received WebSocket message:", data);
        database.update(state => {
            const currentMessages = state[data.type] || []; // 既存のリスト、または新しい空のリスト
            return {
                ...state,
                [data.type]: [
                    ...currentMessages,
                    {
                        data: data.data,
                        timestamp: data.timestamp || datetimeNormalize(new Date())
                    }
                ]
            };
        });
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