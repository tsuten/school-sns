import { writable } from 'svelte/store';

import { messages } from '$lib/stores/unifiedBaseWSStore.js';
import { apiClient } from '$lib/services/django.js';

export const chatMessages = writable([]);

// データを取得する関数
function fetchMessages() {
    messages.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type == 'chat') {
                const message = {
                    type: data.type || '',
                    content: data.content || '',
                    sender: {
                        id: data.sender?.id || '',
                        username: data.sender?.username || '',
                        displayName: data.sender?.displayName || '',
                        icon: data.sender?.icon || ''
                    },
                    created_at: data.created_at,
                    timestamp: data.timestamp
                };
                // 接続エラー時の処理
                socket.onerror = (error) => {
                    console.error('WebSocketエラー:', error);
                };

                // メッセージを追加
                messageList.update(list => [...list, message]);
            }
        } catch (error) {
            console.error('WebSocketデータを取得できませんでした:', error);
        }
    }
};
// グループに加入する
const JoinAnnouncementsGroup = async (announcements_id) => {
    try {
        await JoinGroup("announcements_" + announcements_id);
        console.log("Joined announcements group");
    } catch (error) {
        console.error(error);
    }
}
// グループから退出する関数 
const LeaveAnnouncementsGroup = async (announcements_id) => {
    await LeaveGroup("announcements_" + announcements_id);
}

// 追加データ読み込み関数(カーソルページネーション)
function fetchMoreMessage() {
    // メッセージを時系列順（古い順）にソート
    const sortedMessages = [...messageList].sort((a, b) => {
        const timeA = new Date(a.created_at || a.timestamp);
        const timeB = new Date(b.created_at || b.timestamp);
        return timeA - timeB;
    });

}

function fetchInitialMessages(user_id) {
    apiClient.get(`/chat/messages/${user_id}`).then(response => {
        chatMessages.set(response.messages);
    });
}

export function initialize(user_id) {
    fetchInitialMessages(user_id);
}