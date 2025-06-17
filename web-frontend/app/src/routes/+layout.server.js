import { apiClient, APIError } from '../lib/services/django.js';

/** @type {import('./$types').LayoutServerLoad} */
export async function load({ cookies }) {
    // Cookieまたはヘッダーからトークンを取得
    const accessToken = cookies.get('access_token');
    
    if (!accessToken) {
        console.log('No access token found in cookies');
        return {
            user: null,
            authenticated: false
        };
    }

    try {
        // トークンを検証
        const verifyResponse = await fetch(`${apiClient.baseURL}/token/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: accessToken })
        });

        if (!verifyResponse.ok) {
            const errorData = await verifyResponse.json().catch(() => ({}));
            console.log('Token verification failed:', verifyResponse.status, errorData);
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
            console.log('Successfully authenticated user:', userData.user_username);
            return {
                user: userData,
                authenticated: true
            };
        } else {
            const errorData = await userResponse.json().catch(() => ({}));
            console.log('Failed to fetch user profile:', userResponse.status, errorData);
            return {
                user: null,
                authenticated: false
            };
        }

    } catch (error) {
        console.log('Authentication error:', error.message);
        return {
            user: null,
            authenticated: false
        };
    }
}