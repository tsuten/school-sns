import { apiClient } from '$lib/services/django.js';

export const load = async () => {
    try {
        const response = await apiClient.get('/pm/users-have-history-with-user');
        return {
            users: response.data.users || []
        };
    } catch (err) {
        console.error('ユーザーリストの取得に失敗しました:', err);
        return {
            users: [],
            error: 'ユーザーリストの読み込みに失敗しました。'
        };
    }
}; 