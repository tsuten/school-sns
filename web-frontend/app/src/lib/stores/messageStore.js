import { writable } from 'svelte/store';

import { messages } from '$lib/compornents/stores/unifiedBaseWSStore.js';
// const messageList = {
//   type: $state(),
//   content: $state(),
//   sender: {
//     id: $state(),
//     username: $state(),
//     displayName: $state(),
//     icon: $state()
//   },
//   created_at: $state(),
//   timestamp: $state()
// };
const messageList = writable([]);

// 初期化関数
function initialize(messageList) {
    return {
        type: '',
        content: '',
        sender: {
            id: '',
            username: '',
            displayName: '',
            icon: ''
        },
        created_at: null,
        timestamp: null
    };
}

// データを取得する関数
function get() {
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