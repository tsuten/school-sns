import { writable } from 'svelte/store';
import { apiClient } from '$lib/services/django';

export const settingsStore = writable({});

export const initialize = () => {
    apiClient.get('/users/settings').then(response => {
        settingsStore.set(response.data);
        console.log("settings Data :", response)
    });
};