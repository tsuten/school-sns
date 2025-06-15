import { apiClient, APIError } from '../lib/services/django.js';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ cookies }) {
    // Cookieまたはヘッダーからトークンを取得
    const accessToken = cookies.get('access_token');
    
    if (!accessToken) {
        console.log('user not authenticated');
        return {
            user: null,
            authenticated: false
        };
    }

    try {
        // トークンを一時的にlocalStorageの代わりに設定
        // サーバーサイドではlocalStorageが使えないため、直接ヘッダーに設定
        const response = await fetch(`${apiClient.baseURL}/auth/token/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ token: accessToken })
        });

        if (!response.ok) {
            console.log('user not authenticated - invalid token');
            return {
                user: null,
                authenticated: false
            };
        }

        // ユーザー情報を取得
        const userResponse = await fetch(`${apiClient.baseURL}/users/profile`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            }
        });

        if (userResponse.ok) {
            const userData = await userResponse.json();
            console.log('Authenticated user data:', userData);
            return {
                user: userData,
                authenticated: true
            };
        } else {
            console.log('user not authenticated - failed to fetch user data');
            return {
                user: null,
                authenticated: false
            };
        }

    } catch (error) {
        console.log('user not authenticated - error:', error.message);
        return {
            user: null,
            authenticated: false
        };
    }
}