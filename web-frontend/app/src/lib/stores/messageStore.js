import { writable } from 'svelte/store';

import { messages, latestMessage } from '$lib/stores/unifiedBaseWSStore.js';
import { apiClient } from '$lib/services/django.js';

export const chatMessages = writable([]);

latestMessage.subscribe((data) => {
    try {
        if (data.type === 'message') {
            const message = {
                content: data.data.content,
                created_at: data.data.created_at,
            };
            chatMessages.update((messages) => [...messages, message]);
        }
    } catch (error) {
        console.error('WebSocketデータの解析に失敗しました:', error);
    }
})

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
        chatMessages.set(response.messages)
    });
}

export function initialize(user_id) {
    fetchInitialMessages(user_id);
}