/**
 * Django WebSocket Client for Django Channels
 * 
 * 使い方:
 * import djangoWsClient from '$lib/services/djangoWS.js';
 * 
 * // 接続
 * await djangoWsClient.connectApp('/circle/123/chat/', { username: 'user123' });
 * 
 * // イベント監視
 * djangoWsClient.onApp('/circle/123/chat/', 'message', (data) => console.log(data));
 * 
 * // メッセージ送信
 * djangoWsClient.send('/circle/123/chat/', { type: 'chat_message', message: 'Hello' });
 * 
 * // 切断
 * djangoWsClient.disconnect('/circle/123/chat/');
 * 
 * イベント: 'open', 'close', 'message', 'error'
 */
class DjangoWebSocketClient {
    constructor(baseUrl, options = {}) {
      this.baseUrl = baseUrl.replace(/\/$/, '');
      this.options = {
        reconnectInterval: 1000,
        maxReconnectInterval: 30000,
        reconnectDecay: 1.5,
        maxReconnectAttempts: 10,
        timeoutInterval: 5000,
        enableLogging: true,
        ...options
      };
  
      this.connections = new Map(); // path -> connection info
      this.eventListeners = new Map(); // global events
      this.reconnectTimers = new Map(); // path -> timer
      this.messageQueues = new Map(); // path -> queued messages
    }
  
    // グローバルイベントリスナー
    on(event, callback) {
      if (!this.eventListeners.has(event)) {
        this.eventListeners.set(event, []);
      }
      this.eventListeners.get(event).push(callback);
    }
  
    off(event, callback) {
      if (this.eventListeners.has(event)) {
        const listeners = this.eventListeners.get(event);
        const index = listeners.indexOf(callback);
        if (index > -1) listeners.splice(index, 1);
      }
    }
  
    emit(event, data) {
      if (this.eventListeners.has(event)) {
        this.eventListeners.get(event).forEach(callback => {
          try {
            callback(data);
          } catch (error) {
            this.log('error', `Event listener error: ${error.message}`);
          }
        });
      }
    }
  
    // ログ出力
    log(level, message) {
      if (this.options.enableLogging) {
        console[level](`[Django WS] ${message}`);
      }
    }
  
    // アプリ接続作成
    async connectApp(appPath, options = {}) {
      const cleanPath = appPath.startsWith('/') ? appPath : `/${appPath}`;
      
      if (this.connections.has(cleanPath)) {
        this.log('warn', `Already connected to ${cleanPath}`);
        return this.connections.get(cleanPath);
      }
  
      const wsUrl = `${this.baseUrl}${cleanPath}`;
      const connection = {
        path: cleanPath,
        wsUrl: wsUrl,
        ws: null,
        isConnected: false,
        isConnecting: false,
        reconnectAttempts: 0,
        eventListeners: new Map(),
        options: { autoReconnect: true, queueMessages: true, ...options }
      };
  
      this.connections.set(cleanPath, connection);
      this.messageQueues.set(cleanPath, []);
  
      return this.connect(cleanPath);
    }
  
    // 特定アプリに接続
    async connect(appPath, additionalParams = {}) {
      const connection = this.connections.get(appPath);
      if (!connection) {
        throw new Error(`App not registered: ${appPath}`);
      }
  
      if (connection.isConnected || connection.isConnecting) {
        return Promise.resolve();
      }
  
      return new Promise((resolve, reject) => {
        connection.isConnecting = true;
        
        const params = new URLSearchParams(additionalParams);
        const finalUrl = params.toString() ? 
          `${connection.wsUrl}?${params}` : connection.wsUrl;
  
        this.log('info', `Connecting to ${finalUrl}`);
  
        try {
          const ws = new WebSocket(finalUrl);
          connection.ws = ws;
  
          ws.onopen = (event) => {
            connection.isConnected = true;
            connection.isConnecting = false;
            connection.reconnectAttempts = 0;
            
            this.log('info', `Connected to ${appPath}`);
            this.sendQueuedMessages(appPath);
            this.emitAppEvent(appPath, 'open', event);
            this.emit('app_connected', { path: appPath, event });
            resolve();
          };
  
          ws.onclose = (event) => {
            connection.isConnected = false;
            connection.isConnecting = false;
            
            this.log('info', `Disconnected from ${appPath}: ${event.code}`);
            this.emitAppEvent(appPath, 'close', event);
            this.emit('app_disconnected', { path: appPath, event });
            
            if (event.code !== 1000 && connection.options.autoReconnect && 
                connection.reconnectAttempts < this.options.maxReconnectAttempts) {
              this.scheduleReconnect(appPath);
            }
          };
  
          ws.onmessage = (event) => {
            try {
              const data = JSON.parse(event.data);
              this.log('info', `Message from ${appPath}: ${event.data.substring(0, 100)}...`);
              this.emitAppEvent(appPath, 'message', data);
              this.emit('app_message', { path: appPath, data });
            } catch (error) {
              this.emitAppEvent(appPath, 'message', event.data);
            }
          };
  
          ws.onerror = (error) => {
            this.log('error', `Error on ${appPath}: ${error.message || error}`);
            this.emitAppEvent(appPath, 'error', error);
            this.emit('app_error', { path: appPath, error });
            
            if (connection.isConnecting) {
              reject(error);
            }
          };
  
          setTimeout(() => {
            if (connection.isConnecting && !connection.isConnected) {
              ws.close();
              reject(new Error(`Connection timeout: ${appPath}`));
            }
          }, this.options.timeoutInterval);
  
        } catch (error) {
          connection.isConnecting = false;
          reject(error);
        }
      });
    }
  
    // アプリ切断
    disconnect(appPath) {
      const connection = this.connections.get(appPath);
      if (!connection) return false;
  
      this.clearReconnectTimer(appPath);
      connection.reconnectAttempts = this.options.maxReconnectAttempts;
  
      if (connection.ws) {
        connection.ws.close(1000, 'Manual disconnect');
      }
      return true;
    }
  
    // 全アプリ切断
    disconnectAll() {
      for (const appPath of this.connections.keys()) {
        this.disconnect(appPath);
      }
    }
  
    // メッセージ送信
    send(appPath, data) {
      const connection = this.connections.get(appPath);
      if (!connection) {
        this.log('error', `App not found: ${appPath}`);
        return false;
      }
  
      const message = typeof data === 'string' ? data : JSON.stringify(data);
  
      if (connection.isConnected && connection.ws.readyState === WebSocket.OPEN) {
        try {
          connection.ws.send(message);
          return true;
        } catch (error) {
          this.log('error', `Send error on ${appPath}: ${error.message}`);
          this.queueMessage(appPath, message);
          return false;
        }
      } else {
        if (connection.options.queueMessages) {
          this.queueMessage(appPath, message);
        }
        return false;
      }
    }
  
    // メッセージキューイング
    queueMessage(appPath, message) {
      const queue = this.messageQueues.get(appPath);
      if (queue) {
        queue.push(message);
        if (queue.length > 100) queue.shift();
      }
    }
  
    sendQueuedMessages(appPath) {
      const queue = this.messageQueues.get(appPath);
      const connection = this.connections.get(appPath);
      
      if (!queue || !connection || !connection.isConnected) return;
  
      while (queue.length > 0) {
        const message = queue.shift();
        if (!this.send(appPath, message)) {
          queue.unshift(message);
          break;
        }
      }
    }
  
    // アプリ固有イベントリスナー
    onApp(appPath, event, callback) {
      const connection = this.connections.get(appPath);
      if (!connection) return false;
  
      if (!connection.eventListeners.has(event)) {
        connection.eventListeners.set(event, []);
      }
      connection.eventListeners.get(event).push(callback);
      return true;
    }
  
    offApp(appPath, event, callback) {
      const connection = this.connections.get(appPath);
      if (!connection) return false;
  
      if (connection.eventListeners.has(event)) {
        const listeners = connection.eventListeners.get(event);
        const index = listeners.indexOf(callback);
        if (index > -1) listeners.splice(index, 1);
      }
      return true;
    }
  
    emitAppEvent(appPath, event, data) {
      const connection = this.connections.get(appPath);
      if (!connection) return;
  
      if (connection.eventListeners.has(event)) {
        connection.eventListeners.get(event).forEach(callback => {
          try {
            callback(data);
          } catch (error) {
            this.log('error', `App event listener error on ${appPath}: ${error.message}`);
          }
        });
      }
    }
  
    // 再接続スケジュール
    scheduleReconnect(appPath) {
      const connection = this.connections.get(appPath);
      if (!connection) return;
  
      this.clearReconnectTimer(appPath);
  
      const timeout = Math.min(
        this.options.reconnectInterval * Math.pow(this.options.reconnectDecay, connection.reconnectAttempts),
        this.options.maxReconnectInterval
      );
  
      this.log('info', `Reconnecting ${appPath} in ${timeout}ms (attempt ${connection.reconnectAttempts + 1})`);
  
      const timer = setTimeout(() => {
        connection.reconnectAttempts++;
        this.connect(appPath).catch(() => {});
      }, timeout);
  
      this.reconnectTimers.set(appPath, timer);
    }
  
    clearReconnectTimer(appPath) {
      const timer = this.reconnectTimers.get(appPath);
      if (timer) {
        clearTimeout(timer);
        this.reconnectTimers.delete(appPath);
      }
    }
  
    // ユーティリティ
    isConnected(appPath) {
      const connection = this.connections.get(appPath);
      return connection && connection.isConnected && 
             connection.ws && connection.ws.readyState === WebSocket.OPEN;
    }
  
    getConnectedApps() {
      return Array.from(this.connections.entries())
        .filter(([_, conn]) => conn.isConnected)
        .map(([path, _]) => path);
    }
  
    getStats() {
      const stats = {};
      for (const [path, connection] of this.connections) {
        stats[path] = {
          isConnected: connection.isConnected,
          isConnecting: connection.isConnecting,
          reconnectAttempts: connection.reconnectAttempts,
          queuedMessages: this.messageQueues.get(path)?.length || 0
        };
      }
      return stats;
    }
  
    // クリーンアップ
    destroy() {
      for (const appPath of this.connections.keys()) {
        this.clearReconnectTimer(appPath);
        this.disconnect(appPath);
      }
      this.connections.clear();
      this.messageQueues.clear();
      this.eventListeners.clear();
    }
  }
  
  // シングルトンインスタンス（アプリ全体で使用）
  const djangoWsClient = new DjangoWebSocketClient('ws://localhost:8000/ws');
  
  export default djangoWsClient;