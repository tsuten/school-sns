import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { authService } from '$lib/services/auth.js';
import { apiClient } from '$lib/services/django.js';

// 認証状態のストア
export const isAuthenticated = writable(false);
export const currentUser = writable(null);
export const isLoading = writable(false);
export const authError = writable(null);

// サーバーから取得したユーザーデータをストアに設定
export function setUserFromServerData(userData, authenticated) {
    if (browser) {
        console.log('setUserFromServerData called with:', { userData, authenticated });
        
        isAuthenticated.set(authenticated);
        
        if (authenticated && userData) {
            // データ構造を統一する
            const normalizedUserData = {
                user: userData,
                authenticated: authenticated
            };
            
            currentUser.set(normalizedUserData);
            console.log('User data set in store:', normalizedUserData);
            
            // 認証されている場合、ローカルストレージのトークンとの整合性を確認
            const token = authService.getAccessToken();
            if (token) {
                // トークンをクッキーに同期
                document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
                console.log('Token synchronized with cookie');
            }
        } else {
            currentUser.set(null);
            console.log('User data cleared from store');
        }
    }
}

// クライアントサイドでユーザー情報を取得
export async function fetchCurrentUser() {
    if (!browser) return null;
    
    try {
        isLoading.set(true);
        authError.set(null);
        
        // apiClientを使用してユーザープロフィールを取得
        const response = await apiClient.get('/users/profile');
        
        if (response) {
            // レスポンスの形式を確認してからセット
            const userData = response.user ? response : { user: response };
            currentUser.set(userData);
            isAuthenticated.set(true);
            console.log('User data fetched successfully:', userData);
            return userData;
        } else {
            throw new Error('ユーザー情報の取得に失敗しました');
        }
    } catch (error) {
        console.error('Error fetching user:', error);
        authError.set(error.message || 'ユーザー情報の取得に失敗しました');
        
        // 認証エラーまたは401エラーの場合はログアウト
        if (error.message.includes('認証') || error.message.includes('401') || error.status === 401) {
            console.log('Authentication error detected, logging out...');
            logout();
        }
        return null;
    } finally {
        isLoading.set(false);
    }
}

// ログイン関数
export async function login(username, password) {
    try {
        isLoading.set(true);
        authError.set(null);
        
        const result = await authService.login(username, password);
        isAuthenticated.set(true);
        
        // トークンをクッキーに設定
        document.cookie = `access_token=${result.access}; path=/; max-age=86400; SameSite=Lax`;
        
        // ユーザー情報を取得
        await fetchCurrentUser();
        
        return result;
    } catch (error) {
        isAuthenticated.set(false);
        authError.set(error.message);
        throw error;
    } finally {
        isLoading.set(false);
    }
}

// ログアウト関数
export function logout() {
    authService.logout();
    isAuthenticated.set(false);
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    currentUser.set(null);
    authError.set(null);
} 