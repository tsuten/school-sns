import { writable, get } from 'svelte/store';

import { messages, latestMessage } from '$lib/stores/unifiedBaseWSStore.js';
import { apiClient } from '$lib/services/django.js';

export const chatConfig = writable({
    type: null,
    room_id: null,
});

export const chatMessages = writable([]);

// メッセージ削除処理
const deleteMessage = (messageId) => {
    chatMessages.update((messages) => messages.filter(message => message.id !== messageId));
};

// メッセージ復元処理
const restoreMessage = (data) => {
    const config = get(chatConfig);
    console.log("Restore data:", data);
    console.log("Config:", config);
    
    if (config.type === 'private' && config.room_id == data.sender.id) {
        const message = {
            id: data.id || crypto.randomUUID(),
            content: data.content,
            created_at: data.created_at,
            sender: data.sender,
            type: 'message'
        };
        chatMessages.update((messages) => [...messages, message]);
        console.log("Message restored:", message);
    }
};

// メッセージ追加処理
const addMessage = (data) => {
    const config = get(chatConfig);
    console.log("chatConfig", config.type);
    console.log("data.data.sender.id", data.data.sender.id);
    console.log("chatConfig.room_id", config.room_id);
    
    if (config.type === 'private' && config.room_id == data.data.sender.id) {
        const message = {
            id: data.data.id || crypto.randomUUID(), // IDを追加
            content: data.data.content,
            created_at: data.data.created_at,
            sender: data.data.sender,
            type: 'message'
        };
        chatMessages.update((messages) => [...messages, message]);
    }
};

// 自分が送信したメッセージを先頭に追加する関数
export const addOwnMessage = (content, receiver_id) => {
    const config = get(chatConfig);
    
    if (config.type === 'private' && config.room_id == receiver_id) {
        const message = {
            id: crypto.randomUUID(),
            content: content,
            created_at: new Date().toISOString(),
            sent_by: 'request_user', // 自分が送信したメッセージ
            type: 'message',
            isOwn: true // 自分のメッセージであることを示すフラグ
        };
        
        // メッセージを先頭に追加
        chatMessages.update((messages) => [message, ...messages]);
        
        return message; // 作成したメッセージを返す
    }
};

// 変数更新用購読ハンドラ
latestMessage.subscribe((data) => {
    try {
        if (data.type === 'message') {
            // operationがdeleteの場合、メッセージを削除
            if (data.operation === 'delete' && data.data && data.data.id) {
                deleteMessage(data.data.id);
                return;
            }
            
            // operationがrestoreの場合、メッセージを復元
            if (data.operation === 'restore' && data.data) {
                restoreMessage(data.data);
                return;
            }
            
            // メッセージを追加
            addMessage(data);
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
    apiClient.get(`/pm/messages/${user_id}`).then(response => {
        chatMessages.set(response.data.messages)
    });
}

export function initialize(user_id) {
    fetchInitialMessages(user_id);
}

