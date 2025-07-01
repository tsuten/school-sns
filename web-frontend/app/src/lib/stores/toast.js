import { writable } from 'svelte/store';

export const toasts = writable([]);

let toastId = 0;

export function addToast(message, type = 'info', duration = 5000) {
    const id = toastId++;
    const toast = {
        id,
        message,
        type,
        duration
    };
    
    toasts.update(items => [...items, toast]);
    
    if (duration > 0) {
        setTimeout(() => {
            removeToast(id);
        }, duration);
    }
    
    return id;
}

export function removeToast(id) {
    toasts.update(items => items.filter(item => item.id !== id));
}

export function clearToasts() {
    toasts.set([]);
} 