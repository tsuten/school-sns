import { writable } from 'svelte/store';
import djangoWsClient from '$lib/services/djangoWS.js';
import { authService } from '$lib/services/auth.js';

// 通知がここに格納される
export const Notifications = writable([]);
console.log("storeに入りましたぞ")
// イベント通知を処理する
export const connectTestWS = async () => {
    let token = await authService.getAccessTokenFromCookie()
    // 通知を受信するためにDjango WebSocketクライアントを接続
    djangoWsClient.connectApp('/notification?token=' + token);
    console.log("接続しましたぞ")
     // イベントを監視
    djangoWsClient.onApp('/notification?token=' + token, 'message', (data) => {
        console.log("通知通ってますぞ")
        Notifications.update(state => [
            ...state,
            {
                content: data.content,
                is_read: data.is_read,
                created_at: data.created_at
            }
        ]);
    });
}

