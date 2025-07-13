import { writable } from 'svelte/store';
import djangoWsClient from '$lib/services/djangoWS.js';
import { apiClient } from '$lib/services/django.js';
import { authService } from '$lib/services/auth.js';
import { addToast } from '$lib/stores/toast.js';

// 通知がここに格納される
export const Notifications = writable([]);
console.log("storeに入りましたぞ")

const getInitialNotifications = async () => {
    const response = await apiClient.get('/notifications/notifications');
    return response;
}

// WebSocket接続を確立する関数
export const connectToNotificationWS = async () => {
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
        
        addToast(data.content, 'info', 4000);
    });
}

// djangoApiClientで通知を取得してストアを更新
const initializeNotifications = async () => {
    try {
        const initialNotifications = await getInitialNotifications();
        Notifications.set(initialNotifications);
        console.log("初期通知を取得しました:", initialNotifications);
        
        // WebSocket接続も自動的に確立
        await connectToNotificationWS();
    } catch (error) {
        console.error("初期通知の取得に失敗しました:", error);
    }
}

// 初期化を実行
initializeNotifications();