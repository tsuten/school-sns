# SvelteのWebSocket接続ハンドリングガイド

## 概要

SvelteはWebSocket接続を効率的にハンドリングするための複数のアプローチを提供しています。このガイドでは、Svelteアプリケーションにおけるリアルタイム通信の実装パターンと最適な実践方法について説明します。

## 主要な実装パターン

### 1. 基本的なWebSocket実装

```javascript
// lib/services/socket.js
class SocketClient {
    constructor() {
        this.connections = new Map(); // 複数の接続を管理
        this.reconnectAttempts = new Map();
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.baseUrl = 'ws://localhost:8000/ws';
    }

    connectToCircleChat(circleId, callbacks = {}) {
        const connectionKey = `circle_chat_${circleId}`;
        
        // 既存の接続チェック
        if (this.connections.has(connectionKey)) {
            const existingSocket = this.connections.get(connectionKey);
            if (existingSocket.readyState === WebSocket.OPEN || 
                existingSocket.readyState === WebSocket.CONNECTING) {
                return existingSocket;
            }
        }

        const socketUrl = `${this.baseUrl}/circle/${circleId}/chat/`;
        const socket = new WebSocket(socketUrl);

        // イベントリスナーの設定
        socket.onopen = (event) => {
            console.log(`WebSocket connected: ${socketUrl}`);
            callbacks.onOpen?.(event);
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // メッセージタイプに応じた処理
            switch (data.type) {
                case 'chat_message':
                    callbacks.onMessage?.(data);
                    break;
                case 'user_joined':
                    callbacks.onUserJoined?.(data);
                    break;
                // その他のタイプ...
            }
        };

        // 接続を保存
        this.connections.set(connectionKey, socket);
        return socket;
    }
}
```

### 2. Svelteコンポーネントでの使用

```svelte
<!-- +page.svelte -->
<script>
    import { onMount, onDestroy } from 'svelte';
    import { browser } from '$app/environment';
    import socketClient from '$lib/services/socket.js';
    import { userInfo } from '$lib/stores/userInfo';

    let webSocket = $state(null);
    let messages = $state([]);
    let onlineUsers = $state(new Set());
    let circleId = $state(null);

    onMount(async () => {
        if (browser && circleId) {
            initWebSocket(circleId);
        }
    });

    onDestroy(() => {
        // コンポーネント破棄時にWebSocket接続を切断
        if (browser && circleId) {
            socketClient.disconnectFromCircleChat(circleId);
        }
    });

    function initWebSocket(circleId) {
        webSocket = socketClient.connectToCircleChat(circleId, {
            onOpen: () => {
                console.log('WebSocket connected');
            },
            
            onMessage: (data) => {
                // 新しいメッセージを追加
                const newMessage = {
                    id: data.message_id,
                    content: data.message,
                    user: data.username,
                    timestamp: data.timestamp,
                    isOwn: data.user_id === $userInfo.id
                };
                
                // 重複チェック
                const existingMessage = messages.find(msg => msg.id === newMessage.id);
                if (!existingMessage) {
                    messages = [...messages, newMessage];
                }
            },
            
            onUserJoined: (data) => {
                onlineUsers.add(data.username);
                onlineUsers = new Set(onlineUsers); // リアクティブ更新
            },
            
            onClose: () => {
                console.log('WebSocket disconnected');
            }
        });
    }
</script>
```

## Svelteストアを使ったWebSocket管理

### 1. WebSocketストアパターン

```javascript
// lib/stores/websocket.js
import { writable, readable } from 'svelte/store';

let _websocket = undefined;
let _message = writable(undefined);

// WebSocket接続ストア
export const websocket = readable(undefined, (set) => {
    const ws = new WebSocket('ws://localhost:8080');
    
    ws.onopen = () => {
        _websocket = ws;
        set(ws);
        
        ws.onmessage = (event) => {
            _message.set(event.data);
        };
        
        ws.onclose = () => {
            _websocket = undefined;
            set(undefined);
            _message.set(undefined);
        };
    };
    
    return () => {
        _websocket?.close();
        _websocket = undefined;
        _message.set(undefined);
    };
});

// メッセージストア
export const message = {
    subscribe: _message.subscribe,
    send: (data) => {
        if (_websocket && _websocket.readyState === WebSocket.OPEN) {
            _websocket.send(JSON.stringify(data));
        }
    }
};
```

### 2. 型安全なメッセージルーティング

```typescript
// lib/websocket/router.ts
import { derived, writable } from 'svelte/store';

type WebSocketRoutes = {
    "userSignedIn": { userId: number, username: string };
    "userMessage": { userId: number, message: string, timestamp: number };
    "userSignedOut": { userId: number };
};

type SimpleMessage<T> = {
    topic: string;
    data: T;
};

export type MessageReader<RouteMap> = {
    read: <RouteKey extends Extract<keyof RouteMap, string>>(
        topic: RouteKey
    ) => Readable<RouteMap[RouteKey] | undefined>;
};

export function createMessageReader<T extends {}>(): MessageReader<T> {
    return {
        read<RouteKey extends Extract<keyof T, string>>(topic: RouteKey) {
            return derived(message, ($message, set) => {
                if ($message) {
                    const data: SimpleMessage<T[RouteKey]> = JSON.parse($message);
                    if (data.topic === topic) {
                        set(data.data);
                    }
                }
            });
        }
    };
}

// 使用例
const reader = createMessageReader<WebSocketRoutes>();
const userMessages = reader.read("userMessage");
```

## 高度な機能とベストプラクティス

### 1. 自動再接続機能

```javascript
class WebSocketService {
    attemptReconnect(connectionKey, circleId, callbacks) {
        const attempts = this.reconnectAttempts.get(connectionKey) || 0;
        
        if (attempts < this.maxReconnectAttempts) {
            // 指数バックオフ
            const delay = this.reconnectDelay * Math.pow(2, attempts);
            
            setTimeout(() => {
                this.reconnectAttempts.set(connectionKey, attempts + 1);
                this.connectToCircleChat(circleId, callbacks);
            }, delay);
        }
    }
}
```

### 2. ハートビート機能

```javascript
startHeartbeat(socket) {
    const heartbeatInterval = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'ping' }));
        } else {
            clearInterval(heartbeatInterval);
        }
    }, 30000); // 30秒間隔
    
    return heartbeatInterval;
}
```

### 3. メッセージキューイング

```javascript
class WebSocketService {
    constructor() {
        this.messageQueue = new Map();
    }
    
    sendMessage(connectionKey, message) {
        const socket = this.connections.get(connectionKey);
        
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(message));
            
            // キューにあるメッセージも送信
            const queue = this.messageQueue.get(connectionKey) || [];
            while (queue.length > 0) {
                const queuedMessage = queue.shift();
                socket.send(JSON.stringify(queuedMessage));
            }
        } else {
            // 接続が利用できない場合はキューに追加
            if (!this.messageQueue.has(connectionKey)) {
                this.messageQueue.set(connectionKey, []);
            }
            this.messageQueue.get(connectionKey).push(message);
        }
    }
}
```

## SvelteKitでのWebSocket統合

### 1. サーバーサイド統合

```typescript
// lib/server/webSocketUtils.ts
import { WebSocketServer } from 'ws';

const WEBSOCKET_SYMBOL = Symbol.for('sveltekit.websocket');

export function createWebSocketServer() {
    if (!globalThis[WEBSOCKET_SYMBOL]) {
        const wss = new WebSocketServer({ port: 3001 });
        globalThis[WEBSOCKET_SYMBOL] = wss;
        
        wss.on('connection', (ws) => {
            console.log('New WebSocket connection');
            
            ws.on('message', (message) => {
                // メッセージ処理
                const data = JSON.parse(message.toString());
                handleWebSocketMessage(ws, data);
            });
        });
    }
    
    return globalThis[WEBSOCKET_SYMBOL];
}

export function getWebSocketServer() {
    return globalThis[WEBSOCKET_SYMBOL];
}
```

### 2. 開発環境での設定

```javascript
// vite.config.js
import { sveltekit } from '@sveltejs/kit/vite';

export default {
    plugins: [
        sveltekit(),
        {
            name: 'websocket',
            configureServer(server) {
                server.middlewares.use('/ws', (req, res, next) => {
                    if (req.headers.upgrade === 'websocket') {
                        // WebSocket接続処理
                        handleWebSocketUpgrade(req, res);
                    } else {
                        next();
                    }
                });
            }
        }
    ]
};
```

## リアクティビティとパフォーマンス

### 1. Svelte 5の新しいリアクティビティシステム

```svelte
<script>
    import { onMount } from 'svelte';
    
    let messages = $state([]);
    let connectionStatus = $state('disconnected');
    
    // エフェクトを使用したWebSocket管理
    $effect(() => {
        if (browser && circleId) {
            const ws = new WebSocket(`ws://localhost:8000/chat/${circleId}`);
            
            ws.onopen = () => {
                connectionStatus = 'connected';
            };
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                messages = [...messages, data];
            };
            
            ws.onclose = () => {
                connectionStatus = 'disconnected';
            };
            
            // クリーンアップ
            return () => {
                ws.close();
            };
        }
    });
</script>
```

### 2. メモリリークの防止

```javascript
// クリーナブルストアパターン
import { writable } from 'svelte/store';

export function cleanableWebSocket(url) {
    const { subscribe, set } = writable(null);
    
    return {
        subscribe,
        connect() {
            const ws = new WebSocket(url);
            set(ws);
            
            // クリーンアップ関数を返す
            return () => {
                ws.close();
                set(null);
            };
        }
    };
}
```

## エラーハンドリングとデバッグ

### 1. 包括的なエラーハンドリング

```javascript
class WebSocketService {
    handleError(error, connectionKey) {
        console.error(`WebSocket error for ${connectionKey}:`, error);
        
        // エラータイプに応じた処理
        if (error.code === 1006) {
            // 異常終了 - 再接続を試行
            this.attemptReconnect(connectionKey);
        } else if (error.code === 1008) {
            // ポリシー違反 - 再接続しない
            console.error('WebSocket policy violation');
        }
        
        // ユーザーへの通知
        this.notifyError(error.message);
    }
}
```

### 2. デバッグ支援機能

```javascript
class WebSocketService {
    constructor(debug = false) {
        this.debug = debug;
        this.connectionLogs = new Map();
    }
    
    log(connectionKey, message, data = null) {
        if (this.debug) {
            const timestamp = new Date().toISOString();
            console.log(`[${timestamp}] ${connectionKey}: ${message}`, data);
            
            if (!this.connectionLogs.has(connectionKey)) {
                this.connectionLogs.set(connectionKey, []);
            }
            this.connectionLogs.get(connectionKey).push({
                timestamp,
                message,
                data
            });
        }
    }
    
    getConnectionLogs(connectionKey) {
        return this.connectionLogs.get(connectionKey) || [];
    }
}
```

## まとめ

SvelteのWebSocket実装の主要な利点：

1. **リアクティブストア**: Svelteのストアシステムを活用した状態管理
2. **ライフサイクル管理**: `onMount`と`onDestroy`による適切なリソース管理
3. **型安全性**: TypeScriptを使用した型安全なメッセージルーティング
4. **再接続機能**: 堅牢な自動再接続とエラーハンドリング
5. **パフォーマンス**: 効率的なリアクティビティシステム

これらのパターンを組み合わせることで、Svelteアプリケーションにおいて信頼性の高いリアルタイム機能を実装できます。