/**
 * Chat Store for WebSocket Chat System
 * Circle固有のリアルタイムチャット機能を提供
 * 
 * == 使い方（Svelteコンポーネント内） ==
 * 
 * <script>
 *   import { onMount, onDestroy } from 'svelte';
 *   import chatStore, { 
 *     isChatConnected, isChatConnecting, chatMessages, 
 *     onlineUsers, typingUsers, chatErrors 
 *   } from '$lib/stores/chatStore.js';
 * 
 *   let message = '';
 *   let typingTimeout;
 * 
 *   // 接続管理
 *   async function connect() {
 *     try {
 *       await chatStore.connect('username');
 *     } catch (error) {
 *       console.error('Connection failed:', error);
 *     }
 *   }
 * 
 *   // メッセージ送信
 *   function sendMessage() {
 *     if (message.trim()) {
 *       chatStore.sendMessage(message);
 *       message = '';
 *       chatStore.sendStopTyping();
 *     }
 *   }
 * 
 *   // タイピング処理
 *   function handleTyping() {
 *     chatStore.sendTyping();
 *     clearTimeout(typingTimeout);
 *     typingTimeout = setTimeout(() => chatStore.sendStopTyping(), 2000);
 *   }
 * 
 *   onMount(connect);
 *   onDestroy(() => chatStore.disconnect());
 * </script>
 * 
 * <!-- UI -->
 * {#if $isChatConnecting}
 *   <p>Connecting...</p>
 * {:else if $isChatConnected}
 *   <!-- メッセージ一覧 -->
 *   {#each $chatMessages as msg}
 *     <div>{msg.username}: {msg.message}</div>
 *   {/each}
 * 
 *   <!-- オンラインユーザー -->
 *   <div>Online: {$onlineUsers.map(u => u.username).join(', ')}</div>
 * 
 *   <!-- 入力 -->
 *   <input bind:value={message} on:input={handleTyping} on:keypress={e => e.key === 'Enter' && sendMessage()} />
 *   <button on:click={sendMessage}>Send</button>
 * {:else}
 *   <p>Disconnected</p>
 * {/if}
 * 
 * == ストアと機能 ==
 * chatMessages: メッセージ履歴 [{id, username, message, timestamp}]
 * onlineUsers: オンラインユーザー [{user_id, username}]
 * typingUsers: タイピング中ユーザー [{user_id, username}]
 * isChatConnected: 接続状態 (boolean)
 * isChatConnecting: 接続中状態 (boolean)
 * chatErrors: エラーメッセージ (string|null)
 * 
 * == 独自機能 ==
 * - Circle IDベースのルーム管理
 * - 自動的な参加・退室通知
 * - Django Channels WebSocket連携
 * - システムメッセージの自動生成
 */

import { writable, derived } from 'svelte/store';
import djangoWsClient from '$lib/services/djangoWS.js';

let circle_id = "53fdc303-966b-411f-a509-60121092abc4";

// チャット用ストア
export const chatConnectionState = writable('disconnected');
export const chatMessages = writable([]);
export const onlineUsers = writable([]);
export const typingUsers = writable([]);
export const chatErrors = writable(null);

class ChatStore {
  constructor() {
    this.appPath = `/circle/${circle_id}/chat/`;
    this.setupEventListeners();
  }

  setupEventListeners() {
    console.log('[ChatStore] Setting up event listeners for:', this.appPath);
    
    // アプリ固有のイベントリスナー設定
    djangoWsClient.onApp(this.appPath, 'open', () => {
      console.log('[ChatStore] WebSocket opened event triggered');
      chatConnectionState.set('connected');
      chatErrors.set(null);
    });

    djangoWsClient.onApp(this.appPath, 'close', (event) => {
      console.log('[ChatStore] WebSocket closed:', event);
      chatConnectionState.set('disconnected');
      // 接続が切断された場合のクリーンアップ
      onlineUsers.set([]);
      typingUsers.set([]);
    });

    djangoWsClient.onApp(this.appPath, 'error', (error) => {
      console.error('[ChatStore] WebSocket error:', error);
      chatConnectionState.set('error');
      chatErrors.set(error.message || 'Chat connection error');
    });

    djangoWsClient.onApp(this.appPath, 'message', (data) => {
      console.log('[ChatStore] Received message:', data);
      this.handleMessage(data);
    });
  }

  handleMessage(data) {
    switch (data.type) {
      case 'chat_message':
        this.addMessage(data);
        break;
      case 'user_joined':
        this.handleUserJoined(data);
        break;
      case 'user_left':
        this.handleUserLeft(data);
        break;
      case 'user_typing':
        this.handleUserTyping(data);
        break;
      case 'user_stop_typing':
        this.handleUserStopTyping(data);
        break;
      case 'error':
        chatErrors.set(data.message);
        break;
    }
  }

  addMessage(messageData) {
    const message = {
      id: messageData.message_id || Date.now(),
      user_id: messageData.user_id,
      username: messageData.username,
      message: messageData.message,
      timestamp: new Date(messageData.timestamp || Date.now())
    };

    chatMessages.update(messages => [...messages, message]);
  }

  handleUserJoined(data) {
    onlineUsers.update(users => {
      const userExists = users.some(user => user.user_id === data.user_id);
      if (!userExists) {
        return [...users, { user_id: data.user_id, username: data.username }];
      }
      return users;
    });

    // システムメッセージとして追加
    this.addMessage({
      username: 'System',
      message: `${data.username} joined the chat`,
      timestamp: Date.now()
    });
  }

  handleUserLeft(data) {
    onlineUsers.update(users => users.filter(user => user.user_id !== data.user_id));
    
    this.addMessage({
      username: 'System',
      message: `${data.username} left the chat`,
      timestamp: Date.now()
    });
  }

  handleUserTyping(data) {
    typingUsers.update(users => {
      const userExists = users.some(user => user.user_id === data.user_id);
      if (!userExists) {
        return [...users, { user_id: data.user_id, username: data.username }];
      }
      return users;
    });
  }

  handleUserStopTyping(data) {
    typingUsers.update(users => users.filter(user => user.user_id !== data.user_id));
  }

  // パブリックメソッド（コンポーネントから呼び出し）
  async connect(username) {
    chatConnectionState.set('connecting');
    chatErrors.set(null);
    
    try {
      console.log('[ChatStore] Attempting to connect with username:', username);
      console.log('[ChatStore] App path:', this.appPath);
      
      // タイムアウト処理を追加
      const connectPromise = djangoWsClient.connectApp(this.appPath, { username });
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Connection timeout after 10 seconds')), 10000);
      });
      
      await Promise.race([connectPromise, timeoutPromise]);
      console.log('[ChatStore] Connection successful');
      
      // 接続成功時に状態を明示的に更新
      chatConnectionState.set('connected');
      chatErrors.set(null);
      
    } catch (error) {
      console.error('[ChatStore] Connection failed:', error);
      chatConnectionState.set('error');
      chatErrors.set(error.message || 'Connection failed');
      throw error;
    }
  }

  disconnect() {
    console.log('[ChatStore] Disconnecting from:', this.appPath);
    djangoWsClient.disconnect(this.appPath);
    
    // 強制的に状態をリセット
    setTimeout(() => {
      if (chatConnectionState) {
        chatConnectionState.set('disconnected');
        chatErrors.set(null);
        onlineUsers.set([]);
        typingUsers.set([]);
      }
    }, 1000);
  }

  // 強制リセット機能を追加
  forceReset() {
    console.log('[ChatStore] Force resetting connection state');
    chatConnectionState.set('disconnected');
    chatErrors.set(null);
    onlineUsers.set([]);
    typingUsers.set([]);
    chatMessages.set([]);
  }

  sendMessage(message) {
    if (!djangoWsClient.isConnected(this.appPath)) {
      chatErrors.set('Not connected to chat');
      return false;
    }

    return djangoWsClient.send(this.appPath, {
      type: 'chat_message',
      message: message
    });
  }

  sendTyping() {
    if (!djangoWsClient.isConnected(this.appPath)) {
      return false;
    }

    return djangoWsClient.send(this.appPath, {
      type: 'typing'
    });
  }

  sendStopTyping() {
    if (!djangoWsClient.isConnected(this.appPath)) {
      return false;
    }

    return djangoWsClient.send(this.appPath, {
      type: 'stop_typing'
    });
  }

  clearMessages() {
    chatMessages.set([]);
  }

  clearErrors() {
    chatErrors.set(null);
  }

  isConnected() {
    return djangoWsClient.isConnected(this.appPath);
  }
}

// 派生ストア
export const isChatConnected = derived(chatConnectionState, $state => $state === 'connected');
export const isChatConnecting = derived(chatConnectionState, $state => $state === 'connecting');
export const hasChatError = derived(chatConnectionState, $state => $state === 'error');

// タイピング中のユーザー名リスト
export const typingUsernames = derived(typingUsers, $users => 
  $users.map(user => user.username)
);

// 未読メッセージ数（例）
export const unreadCount = derived(chatMessages, $messages => {
  // 実装は要件に応じて
  return $messages.length;
});

// チャットストアインスタンス
const chatStore = new ChatStore();

export default chatStore;