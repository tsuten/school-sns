// Django Backend API Client
// btw thanks claude for writing this code as well

export const API_BASE_URL = "http://localhost:8000/api";

class DjangoAPIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL.trim();
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    // トークンを取得（localStorage、sessionStorage、またはCookieから）
    getAuthToken() {
        // JWTトークンの取得ロジック
        return localStorage.getItem('access_token') || 
               sessionStorage.getItem('access_token');
    }

    // 認証ヘッダーを追加
    getHeaders(customHeaders = {}) {
        const headers = { ...this.defaultHeaders, ...customHeaders };
        const token = this.getAuthToken();
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    // 基本的なfetchラッパー
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.getHeaders(options.headers),
            ...options,
        };

        try {
            const response = await fetch(url, config);
            
            // レスポンスの処理
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(response.status, errorData.message || response.statusText, errorData);
            }

            // 204 No Contentの場合はnullを返す
            if (response.status === 204) {
                return null;
            }

            return await response.json();
        } catch (error) {
            if (error instanceof APIError) {
                throw error;
            }
            throw new APIError(0, 'Network Error', { originalError: error });
        }
    }

    // GET リクエスト
    async get(endpoint, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;
        
        return this.request(url, {
            method: 'GET',
        });
    }

    // POST リクエスト
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // PUT リクエスト
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    // PATCH リクエスト
    async patch(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    }

    // DELETE リクエスト
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }

    // ファイルアップロード用
    async uploadFile(endpoint, file, additionalData = {}) {
        const formData = new FormData();
        formData.append('file', file);
        
        Object.keys(additionalData).forEach(key => {
            formData.append(key, additionalData[key]);
        });

        return this.request(endpoint, {
            method: 'POST',
            body: formData,
            headers: {
                // Content-Typeを削除してブラウザに自動設定させる
                ...this.getHeaders(),
                'Content-Type': undefined,
            },
        });
    }

    // 認証関連のメソッド
    async login(credentials) {
        const response = await this.post('/auth/token/pair', credentials);
        
        if (response.access) {
            localStorage.setItem('access_token', response.access);
            localStorage.setItem('refresh_token', response.refresh);
        }
        
        return response;
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new APIError(401, 'No refresh token available');
        }

        try {
            const response = await this.post('/auth/token/refresh', {
                refresh: refreshToken
            });
            
            if (response.access) {
                localStorage.setItem('access_token', response.access);
            }
            
            return response;
        } catch (error) {
            // リフレッシュトークンが無効な場合はログアウト
            this.logout();
            throw error;
        }
    }

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
    }
}

// カスタムエラークラス
class APIError extends Error {
    constructor(status, message, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.data = data;
    }
}

// シングルトンインスタンス
export const apiClient = new DjangoAPIClient();

// 便利な関数をエクスポート
export { DjangoAPIClient, APIError };

// 使用例のための関数
export const api = {
    // 投稿関連
    posts: {
        getLatest: () => apiClient.get('/posts/latest'),
        getRandomWithinLastDay: () => apiClient.get('/posts/random-within-last-day'),
        create: (postData) => apiClient.post('/posts', postData),
        getById: (id) => apiClient.get(`/posts/${id}`),
        update: (id, postData) => apiClient.put(`/posts/${id}`, postData),
        delete: (id) => apiClient.delete(`/posts/${id}`),
    },
    
    // 認証関連
    auth: {
        login: (credentials) => apiClient.login(credentials),
        logout: () => apiClient.logout(),
        refreshToken: () => apiClient.refreshToken(),
        verify: (token) => apiClient.post('/auth/token/verify', { token }),
    },
    
    // ユーザー関連
    users: {
        getProfile: () => apiClient.get('/users/profile'),
        updateProfile: (profileData) => apiClient.patch('/users/profile', profileData),
        uploadAvatar: (file) => apiClient.uploadFile('/users/avatar', file),
    },
};