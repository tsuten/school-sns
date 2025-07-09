import { writable } from 'svelte/store';
import djangoWsClient from '$lib/services/djangoWS.js';
import { authService } from '$lib/services/auth.js';

// 通知がここに格納される
export const notification = writable([]);
console.log("storeに入りましたぞ")
// イベント通知を処理する
export const connectTestWS = async () => {
    let token = await authService.getAccessTokenFromCookie()
    // 通知を受信するためにDjango WebSocketクライアントを接続
    djangoWsClient.connectApp('/notification?token=' + token);
     // イベントを監視
    djangoWsClient.onApp('/notification', 'message', (data) => {
        console.log("通知通ってますぞ")
        notification.update(state => [
            ...state,
            {
                name: data.name,
                title: data.title,
                is_read: data.is_read,
                createdAt: data.createdAt
            }
        ]);
    });
}

