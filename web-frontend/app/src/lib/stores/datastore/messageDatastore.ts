import { writable, get, type Writable } from 'svelte/store';
import { latestMessage } from '$lib/stores/unifiedBaseWSStore';
import { apiClient } from '$lib/services/django';
import type { DataStore, DataStoreConfig, DataStoreEntry } from './baseDatastore';

interface Message extends DataStoreEntry {
  content: string;
  created_at: string;
  sender: any; // TODO: 適切な Sender インターフェースを定義
  type: string;
}

class MessageDataStoreInternal implements DataStore<Message> {
  public config: Writable<DataStoreConfig>;
  public data: Writable<Message[]>;

  constructor() {
    this.config = writable<DataStoreConfig>({
      type: null,
      room_id: null,
    });
    this.data = writable<Message[]>([]);

    this.subscribeToWebSocket(latestMessage);
  }

  public initialize(user_id: any): void {
    this.fetchInitialData(user_id);
  }

  public addEntry(newMessage: Message): void {
    const currentConfig = get(this.config);
    if (currentConfig.type === 'private' && currentConfig.room_id == newMessage.sender.id) {
      this.data.update((messages) => [...messages, newMessage]);
    }
  }

  public deleteEntry(messageId: string | number): void {
    this.data.update((messages) => messages.filter(message => message.id !== messageId));
  }

  public restoreEntry(restoredMessage: Message): void {
    const currentConfig = get(this.config);
    if (currentConfig.type === 'private' && currentConfig.room_id == restoredMessage.sender.id) {
      this.data.update((messages) => [...messages, restoredMessage]);
    }
  }

  public async fetchInitialData(user_id: any): Promise<void> {
    try {
      const response = await apiClient.get(`/pm/messages/${user_id}`);
      this.data.set(response.data.messages);
    } catch (error) {
      console.error('初期メッセージの取得に失敗しました:', error);
    }
  }

  public async fetchMoreData(): Promise<void> {
    // TODO: カーソルページネーションの実装
    console.log("Fetch more messages...");
  }

  public subscribeToWebSocket(latestMessageStore: Writable<any>): void {
    latestMessageStore.subscribe((data) => {
      try {
        if (data.type === 'message') {
          if (data.operation === 'delete' && data.data && data.data.id) {
            this.deleteEntry(data.data.id);
            return;
          }
          if (data.operation === 'restore' && data.data) {
            this.restoreEntry(data.data);
            return;
          }
          const newMessage: Message = {
            id: data.data.id || crypto.randomUUID(),
            content: data.data.content,
            created_at: data.data.created_at,
            sender: data.data.sender,
            type: 'message'
          };
          this.addEntry(newMessage);
        }
      } catch (error) {
        console.error('WebSocketデータの解析に失敗しました:', error);
      }
    });
  }
}

const internalMessageStore = new MessageDataStoreInternal();

export const chatConfig = internalMessageStore.config;
export const chatMessages = internalMessageStore.data;
export const initializeMessageStore = (userId: any) => internalMessageStore.initialize(userId);
export const addMessageEntry = (entry: Message) => internalMessageStore.addEntry(entry);
export const deleteMessageEntry = (id: string | number) => internalMessageStore.deleteEntry(id);
export const restoreMessageEntry = (entry: Message) => internalMessageStore.restoreEntry!(entry);
export const fetchInitialMessageData = (userId: any) => internalMessageStore.fetchInitialData(userId);
export const fetchMoreMessageData = () => internalMessageStore.fetchMoreData!(); 