import { writable } from 'svelte/store';
import djangoWsClient from '$lib/services/djangoWS.js';

// 通知がここに格納される
export const notification = writable();

// イベント通知を処理する
export const connectTestWS = () => {
    // 通知を受信するためにDjango WebSocketクライアントを接続
    djangoWsClient.connectApp('/notification/', {});
     // イベントを監視
    djangoWsClient.onApp('/notification/', 'message', (data) => {
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

