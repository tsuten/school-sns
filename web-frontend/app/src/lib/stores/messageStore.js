import { writable } from 'svelte/store';

import { messages } from '$lib/stores/unifiedBaseWSStore.js';
import { apiClient } from '$lib/services/django.js';

export const chatMessages = writable([]);

messages.subscribe((data) => {
    messages.onerror = (error) => {
        console.error('WebSocketエラー:', error);
    };
    try {
        console.log(data.toReversed()[0])
        if (data.toReversed()[0].type === 'message') {
            const message = {
                content: data.content,
                sender: {
                    id: data.sender?.id,
                    username: data.sender?.username,
                    display_name: data.sender?.display_name,
                    pfp: data.sender?.pfp
                },
                created_at: data.created_at,
            };

            console.log(data.toReversed()[0])
            chatMessages.update((messages) => [...messages, data.toReversed()[0]]);
            console.log("追加できました")
        }
    } catch (error) {
        console.error('WebSocketデータの解析に失敗しました:', error);
    }
})
// // データを取得する関数
// // WebSocketメッセージリスナーを設定する関数
// function setupMessageListener() {
//     messages.onerror = (error) => {
//         console.error('WebSocketエラー:', error);
//     };
//     console.log("関数走ってますよ")

//     messages.onmessage = (event) => {
//         try {
//             const data = JSON.parse(event.data);
//             console.log("if入る前だよ")

//             if (data.type === 'message') {
//                 const message = {
//                     type: data.type || '',
//                     content: data.content || '',
//                     sender: {
//                         id: data.sender?.id || '',
//                         username: data.sender?.username || '',
//                         displayName: data.sender?.displayName || '',
//                         icon: data.sender?.icon || ''
//                     },
//                     created_at: data.created_at,
//                     timestamp: data.timestamp
//                 };

//                 console.log(message)
//                 messageList.push(message);
//             }
//         } catch (error) {
//             console.error('WebSocketデータの解析に失敗しました:', error);
//         }
//     };
// }
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
        console.log("これはchatMessageですぞ",chatMessages)
    });
}

export function initialize(user_id) {
    fetchInitialMessages(user_id);
}