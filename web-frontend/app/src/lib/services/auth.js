import { browser } from '$app/environment';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

class AuthService {
    constructor() {
        this.tokenKey = 'access_token';
        this.refreshTokenKey = 'refresh_token';
    }

    // ローカルストレージからトークンを取得
    getAccessToken() {
        if (!browser) return null;
        return localStorage.getItem(this.tokenKey);
    }

    getRefreshToken() {
        if (!browser) return null;
        return localStorage.getItem(this.refreshTokenKey);
    }

    // トークンを保存
    setTokens(accessToken, refreshToken) {
        if (!browser) return;
        localStorage.setItem(this.tokenKey, accessToken);
        if (refreshToken) {
            localStorage.setItem(this.refreshTokenKey, refreshToken);
        }
    }

    // トークンを削除
    clearTokens() {
        if (!browser) return;
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
    }

    // ログイン
    async login(username, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/token/pair`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });

            if (!response.ok) {
                throw new Error('ログインに失敗しました');
            }

            const data = await response.json();
            this.setTokens(data.access, data.refresh);
            return data;
        } catch (error) {
            console.error('Login error:', error);
            throw error;
        }
    }

    // トークンリフレッシュ
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            throw new Error('リフレッシュトークンがありません');
        }

        try {
            const response = await fetch(`${API_BASE_URL}/token/refresh`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    refresh: refreshToken
                })
            });

            if (!response.ok) {
                throw new Error('トークンのリフレッシュに失敗しました');
            }

            const data = await response.json();
            this.setTokens(data.access, data.refresh || refreshToken);
            return data.access;
        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearTokens();
            throw error;
        }
    }

    // 認証付きFetch
    async authenticatedFetch(url, options = {}) {
        let accessToken = this.getAccessToken();
        
        if (!accessToken) {
            throw new Error('アクセストークンがありません');
        }

        // 最初の試行
        let response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            }
        });

        // 401エラーの場合、トークンをリフレッシュして再試行
        if (response.status === 401) {
            try {
                accessToken = await this.refreshAccessToken();
                response = await fetch(url, {
                    ...options,
                    headers: {
                        ...options.headers,
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    }
                });
            } catch (refreshError) {
                // リフレッシュに失敗した場合はログアウト
                this.clearTokens();
                throw new Error('認証が必要です');
            }
        }

        return response;
    }

    // ログアウト
    logout() {
        this.clearTokens();
    }

    // 認証状態をチェック
    isAuthenticated() {
        return !!this.getAccessToken();
    }
}

export const authService = new AuthService(); 