/** @type {import('./$types').PageServerLoad} */
export async function load({ params, cookies, url }) {
    const userId = params.user;
    
    // URLが変更されるたびに再読み込みを強制するため、URLをキーとして使用
    const cacheKey = url.pathname;
    
    // デバッグ情報
    console.log('Params:', params);
    console.log('User ID:', userId);
    
    // userIdが無効な場合は早期リターン
    if (!userId || userId === 'undefined') {
        console.error('Invalid user ID:', userId);
        return {
            messages: [],
            targetUser: null,
            userId: userId,
            error: 'Invalid user ID'
        };
    }
    
    try {
        // クッキーからアクセストークンを取得
        const accessToken = cookies.get('access_token');
        
        if (!accessToken) {
            return {
                messages: [],
                targetUser: null,
                userId: userId,
                needsAuth: true
            };
        }

        // メッセージ履歴を取得
        const response = await fetch(`http://127.0.0.1:8000/api/chat/messages/${userId}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                return {
                    messages: [],
                    targetUser: null,
                    userId: userId,
                    needsAuth: true
                };
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // ユーザー情報も取得
        const userResponse = await fetch(`http://127.0.0.1:8000/api/users/profile/${userId}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        let targetUser = null;
        
        if (userResponse.ok) {
            targetUser = await userResponse.json();
        }
        
        return {
            messages: data.messages || [],
            targetUser: targetUser,
            userId: userId,
            needsAuth: false,
            cacheKey: cacheKey  // キャッシュ無効化のためのキー
        };
        
    } catch (error) {
        console.error('メッセージの取得に失敗しました:', error);
        return {
            messages: [],
            targetUser: null,
            userId: userId,
            needsAuth: false
        };
    }
} 