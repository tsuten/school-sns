import type { Writable } from 'svelte/store';

export interface DataStoreConfig {
  type: string;
  room_id: string | number;
}

export interface DataStoreEntry {
  id: string | number;
  // その他の共通プロパティがあればここに追加
}

export interface DataStore<T extends DataStoreEntry> {
  config: Writable<DataStoreConfig>;
  data: Writable<T[]>;
  initialize: (param: any) => void;
  addEntry: (entry: T) => void;
  deleteEntry: (id: string | number) => void;
  restoreEntry?: (entry: T) => void;
  fetchInitialData: (param: any) => Promise<void>;
  fetchMoreData?: () => Promise<void>;
  subscribeToWebSocket?: (latestMessageStore: Writable<any>) => void;
} 