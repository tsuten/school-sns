import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { authService } from '$lib/services/auth.js';

// 認証状態のストア
export const isAuthenticated = writable(false);
export const currentUser = writable(null);

// 初期化
if (browser) {
    // ページロード時に認証状態をチェック
    isAuthenticated.set(authService.isAuthenticated());
    
    // トークンをクッキーに同期
    const syncTokenToCookie = () => {
        const token = authService.getAccessToken();
        if (token) {
            document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Lax`;
        } else {
            document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        }
    };
    
    // 初期同期
    syncTokenToCookie();
    
    // 認証状態の変更を監視
    isAuthenticated.subscribe((authenticated) => {
        if (!authenticated) {
            authService.clearTokens();
            document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
            currentUser.set(null);
        } else {
            syncTokenToCookie();
        }
    });
}

// ログイン関数
export async function login(username, password) {
    try {
        const result = await authService.login(username, password);
        isAuthenticated.set(true);
        
        // トークンをクッキーに設定
        document.cookie = `access_token=${result.access}; path=/; max-age=86400; SameSite=Lax`;
        
        return result;
    } catch (error) {
        isAuthenticated.set(false);
        throw error;
    }
}

// ログアウト関数
export function logout() {
    authService.logout();
    isAuthenticated.set(false);
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    currentUser.set(null);
} 