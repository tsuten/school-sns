// django channelsの接続設定を記述

class SocketClient {
    constructor() {
        this.connections = new Map(); // 複数の接続を管理
        this.reconnectAttempts = new Map(); // 再接続試行回数
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // 1秒
        this.baseUrl = 'ws://localhost:8000/ws';
    }

    /**
     * サークルチャットに接続
     * @param {string} circleId - サークルID
     * @param {object} callbacks - イベントコールバック
     * @returns {WebSocket} WebSocket接続
     */
    connectToCircleChat(circleId, callbacks = {}) {
        const connectionKey = `circle_chat_${circleId}`;
        
        // 既存の接続があれば返す
        if (this.connections.has(connectionKey)) {
            const existingSocket = this.connections.get(connectionKey);
            if (existingSocket.readyState === WebSocket.OPEN || 
                existingSocket.readyState === WebSocket.CONNECTING) {
                return existingSocket;
            }
        }

        const socketUrl = `${this.baseUrl}/circle/${circleId}/chat/`;
        const socket = new WebSocket(socketUrl);

        // デフォルトコールバック
        const defaultCallbacks = {
            onOpen: () => console.log(`Connected to circle chat: ${circleId}`),
            onMessage: (data) => console.log('Received message:', data),
            onClose: () => console.log(`Disconnected from circle chat: ${circleId}`),
            onError: (error) => console.error('WebSocket error:', error),
            onUserJoined: (data) => console.log('User joined:', data),
            onUserLeft: (data) => console.log('User left:', data),
            onUserTyping: (data) => console.log('User typing:', data),
            onUserStopTyping: (data) => console.log('User stopped typing:', data),
            ...callbacks
        };

        // イベントリスナー設定
        socket.onopen = (event) => {
            console.log(`WebSocket connected: ${socketUrl}`);
            this.reconnectAttempts.set(connectionKey, 0);
            defaultCallbacks.onOpen(event);
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                switch (data.type) {
                    case 'chat_message':
                        defaultCallbacks.onMessage(data);
                        break;
                    case 'user_joined':
                        defaultCallbacks.onUserJoined(data);
                        break;
                    case 'user_left':
                        defaultCallbacks.onUserLeft(data);
                        break;
                    case 'user_typing':
                        defaultCallbacks.onUserTyping(data);
                        break;
                    case 'user_stop_typing':
                        defaultCallbacks.onUserStopTyping(data);
                        break;
                    case 'error':
                        console.error('Server error:', data.message);
                        defaultCallbacks.onError(data);
                        break;
                    default:
                        console.log('Unknown message type:', data.type);
                }
            } catch (error) {
                console.error('Error parsing message:', error);
                defaultCallbacks.onError(error);
            }
        };

        socket.onclose = (event) => {
            console.log(`WebSocket closed: ${socketUrl}`, event);
            this.connections.delete(connectionKey);
            defaultCallbacks.onClose(event);
            
            // 異常終了の場合は再接続を試行
            if (event.code !== 1000) {
                this.attemptReconnect(connectionKey, circleId, defaultCallbacks);
            }
        };

        socket.onerror = (error) => {
            console.error(`WebSocket error: ${socketUrl}`, error);
            defaultCallbacks.onError(error);
        };

        // 接続を保存
        this.connections.set(connectionKey, socket);
        
        return socket;
    }

    /**
     * 通知システムに接続
     * @param {object} callbacks - イベントコールバック
     * @returns {WebSocket} WebSocket接続
     */
    connectToNotifications(callbacks = {}) {
        const connectionKey = 'notifications';
        
        // 既存の接続があれば返す
        if (this.connections.has(connectionKey)) {
            const existingSocket = this.connections.get(connectionKey);
            if (existingSocket.readyState === WebSocket.OPEN || 
                existingSocket.readyState === WebSocket.CONNECTING) {
                return existingSocket;
            }
        }

        const socketUrl = `${this.baseUrl}/notifications/`;
        const socket = new WebSocket(socketUrl);

        // デフォルトコールバック
        const defaultCallbacks = {
            onOpen: () => console.log('Connected to notifications'),
            onNotification: (data) => console.log('Received notification:', data),
            onClose: () => console.log('Disconnected from notifications'),
            onError: (error) => console.error('Notification WebSocket error:', error),
            ...callbacks
        };

        // イベントリスナー設定
        socket.onopen = (event) => {
            console.log(`Notification WebSocket connected: ${socketUrl}`);
            this.reconnectAttempts.set(connectionKey, 0);
            defaultCallbacks.onOpen(event);
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                switch (data.type) {
                    case 'circle_notification':
                        defaultCallbacks.onNotification(data);
                        break;
                    case 'error':
                        console.error('Notification server error:', data.message);
                        defaultCallbacks.onError(data);
                        break;
                    default:
                        console.log('Unknown notification type:', data.type);
                }
            } catch (error) {
                console.error('Error parsing notification:', error);
                defaultCallbacks.onError(error);
            }
        };

        socket.onclose = (event) => {
            console.log(`Notification WebSocket closed: ${socketUrl}`, event);
            this.connections.delete(connectionKey);
            defaultCallbacks.onClose(event);
            
            // 異常終了の場合は再接続を試行
            if (event.code !== 1000) {
                this.attemptReconnect(connectionKey, null, defaultCallbacks);
            }
        };

        socket.onerror = (error) => {
            console.error(`Notification WebSocket error: ${socketUrl}`, error);
            defaultCallbacks.onError(error);
        };

        // 接続を保存
        this.connections.set(connectionKey, socket);
        
        return socket;
    }

    /**
     * 再接続を試行
     * @param {string} connectionKey - 接続キー
     * @param {string} circleId - サークルID（チャットの場合）
     * @param {object} callbacks - コールバック
     */
    attemptReconnect(connectionKey, circleId, callbacks) {
        const attempts = this.reconnectAttempts.get(connectionKey) || 0;
        
        if (attempts < this.maxReconnectAttempts) {
            const delay = this.reconnectDelay * Math.pow(2, attempts); // 指数バックオフ
            
            console.log(`Attempting to reconnect (${attempts + 1}/${this.maxReconnectAttempts}) in ${delay}ms...`);
            
            setTimeout(() => {
                this.reconnectAttempts.set(connectionKey, attempts + 1);
                
                if (connectionKey.startsWith('circle_chat_')) {
                    this.connectToCircleChat(circleId, callbacks);
                } else if (connectionKey === 'notifications') {
                    this.connectToNotifications(callbacks);
                }
            }, delay);
        } else {
            console.error(`Max reconnection attempts reached for ${connectionKey}`);
            this.reconnectAttempts.delete(connectionKey);
        }
    }

    /**
     * チャットメッセージを送信
     * @param {string} circleId - サークルID
     * @param {string} message - メッセージ内容
     */
    sendChatMessage(circleId, message) {
        const connectionKey = `circle_chat_${circleId}`;
        const socket = this.connections.get(connectionKey);
        
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'chat_message',
                message: message
            }));
        } else {
            console.error('Chat socket not connected');
        }
    }

    /**
     * タイピング状態を送信
     * @param {string} circleId - サークルID
     * @param {boolean} isTyping - タイピング中かどうか
     */
    sendTypingStatus(circleId, isTyping) {
        const connectionKey = `circle_chat_${circleId}`;
        const socket = this.connections.get(connectionKey);
        
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: isTyping ? 'typing' : 'stop_typing'
            }));
        }
    }

    /**
     * 特定の接続を切断
     * @param {string} connectionKey - 接続キー
     */
    disconnect(connectionKey) {
        const socket = this.connections.get(connectionKey);
        if (socket) {
            socket.close(1000, 'Client disconnect');
            this.connections.delete(connectionKey);
            this.reconnectAttempts.delete(connectionKey);
        }
    }

    /**
     * サークルチャットから切断
     * @param {string} circleId - サークルID
     */
    disconnectFromCircleChat(circleId) {
        this.disconnect(`circle_chat_${circleId}`);
    }

    /**
     * 通知システムから切断
     */
    disconnectFromNotifications() {
        this.disconnect('notifications');
    }

    /**
     * すべての接続を切断
     */
    disconnectAll() {
        for (const [key, socket] of this.connections) {
            socket.close(1000, 'Client disconnect all');
        }
        this.connections.clear();
        this.reconnectAttempts.clear();
    }

    /**
     * 接続状態を取得
     * @param {string} connectionKey - 接続キー
     * @returns {number} WebSocket.readyState
     */
    getConnectionState(connectionKey) {
        const socket = this.connections.get(connectionKey);
        return socket ? socket.readyState : WebSocket.CLOSED;
    }

    /**
     * サークルチャットの接続状態を取得
     * @param {string} circleId - サークルID
     * @returns {number} WebSocket.readyState
     */
    getCircleChatState(circleId) {
        return this.getConnectionState(`circle_chat_${circleId}`);
    }

    /**
     * 通知システムの接続状態を取得
     * @returns {number} WebSocket.readyState
     */
    getNotificationState() {
        return this.getConnectionState('notifications');
    }
}

// シングルトンインスタンスを作成してエクスポート
const socketClient = new SocketClient();

export default socketClient;

