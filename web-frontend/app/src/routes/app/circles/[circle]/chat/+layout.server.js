import { api } from '$lib/services/django.js';

export async function load({ cookies }) {
    try {
        // クッキーからトークンを取得
        const accessToken = cookies.get('access_token');
        
        if (!accessToken) {
            return {
                circles: []
            };
        }

        // ユーザーが参加しているサークル一覧を取得
        const response = await fetch('http://localhost:8000/api/circle/you', {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const circles = await response.json();
            return {
                circles
            };
        } else {
            console.error('Failed to fetch user circles:', response.status);
            return {
                circles: []
            };
        }
    } catch (error) {
        console.error('Error fetching user circles:', error);
        return {
            circles: []
        };
    }
} 