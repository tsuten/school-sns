import { writable } from "svelte/store";
import { apiClient } from "$lib/services/django";
import { authService } from "$lib/services/auth.js";
import djangoWsClient from "$lib/services/djangoWS.js";
import { browser } from '$app/environment';

const token = await authService.getAccessTokenFromCookie();

export const messages = writable([]);

const fetchInitialMessages = async (path) => {
    // 初期化
    messages.set([]);

    const response = await apiClient.get(path);
    console.log("response", response);
    return response.messages;
}

export const connectToChatWS = async (WSPath) => {
    // ブラウザ環境でのみ実行
    if (!browser) return;
    
    // 通知を受信するためにDjango WebSocketクライアントを接続
    djangoWsClient.connectApp(WSPath + "?token=" + token);
     // イベントを監視
    djangoWsClient.onApp(WSPath + "?token=" + token, 'message', (data) => {
        messages.update(state => [
            ...state,
            {
                content: data.data.content,
                created_at: data.data.created_at
            }
        ]);
    });
}

export const disconnectFromChatWS = async (WSPath) => {
    // ブラウザ環境でのみ実行
    if (!browser) return;
    
    try {
        djangoWsClient.disconnectApp(WSPath + "?token=" + token);
    } catch (error) {
        console.error('WebSocket切断エラー:', error);
    }
}

const InitializeMessages = async (path, WSPath) => {
    const initialMessages = await fetchInitialMessages(path);
    console.log("initialMessages", initialMessages);
    await connectToChatWS(WSPath);
    messages.set(initialMessages);
}

export { InitializeMessages };