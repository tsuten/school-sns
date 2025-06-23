/** @type {import('./$types').LayoutServerLoad} */
export async function load({ cookies }) {
    try {
        // クッキーからアクセストークンを取得
        const accessToken = cookies.get('access_token');
        
        if (!accessToken) {
            return {
                users: [],
                needsAuth: true
            };
        }

        // Django APIからランダムユーザーを10人取得
        const response = await fetch('http://127.0.0.1:8000/api/users/random/10', {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                return {
                    users: [],
                    needsAuth: true
                };
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const users = await response.json();
        
        return {
            users: users,
            needsAuth: false
        };
    } catch (error) {
        console.error('ユーザーデータの取得に失敗しました:', error);
        return {
            users: [],
            needsAuth: false
        };
    }
}