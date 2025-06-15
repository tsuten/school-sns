// 状態はローカルストレージに保存されているので保持されます
// 開発が進んできたらデータベースに保存することも視野に

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const storageKey = 'activeWidgets';

const storedValue = browser ? window.localStorage.getItem(storageKey) : null;
const initialValue = storedValue ? JSON.parse(storedValue) : [];

const store = writable(initialValue);

store.subscribe((value) => {
	if (browser) {
		window.localStorage.setItem(storageKey, JSON.stringify(value));
	}
});

export const activeWidgets = store;