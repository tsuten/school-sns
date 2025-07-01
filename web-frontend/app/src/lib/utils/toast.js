import { addToast } from '$lib/stores/toast.js';

export const toast = {
    success: (message, duration = 5000) => addToast(message, 'success', duration),
    error: (message, duration = 5000) => addToast(message, 'error', duration),
    warning: (message, duration = 5000) => addToast(message, 'warning', duration),
    info: (message, duration = 5000) => addToast(message, 'info', duration)
};

export default toast; 