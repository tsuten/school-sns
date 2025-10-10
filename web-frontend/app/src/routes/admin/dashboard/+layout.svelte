<script>
    import '../../../app.css';
    import { Shield, LogOut, Settings, Users, FileText, MessageSquare } from 'lucide-svelte';
    import { goto } from "$app/navigation";
    
    let currentPath = $state('');
    
    function handleLogout() {
        // アドミントークンを削除
        document.cookie = 'admin_access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        goto('/admin/login');
    }
    
    function navigateTo(path) {
        goto(path);
    }
    
    // 現在のパスを取得
    $effect(() => {
        if (typeof window !== 'undefined') {
            currentPath = window.location.pathname;
        }
    });
</script>

<div class="min-h-screen bg-gray-50">
    <!-- ヘッダー -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="px-6 py-4">
            <div class="flex items-center justify-between">
                <!-- ロゴとナビゲーション -->
                <div class="flex items-center space-x-8">
                    <div class="flex items-center space-x-3">
                        <Shield class="h-8 w-8 text-red-600" />
                        <span class="text-xl font-bold text-gray-900">Admin Panel</span>
                    </div>
                    
                    <!-- ナビゲーションメニュー -->
                    <nav class="flex items-center space-x-6">
                        <button 
                            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {currentPath === '/admin/dashboard' ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}"
                            onclick={() => navigateTo('/admin/dashboard')}
                        >
                            <Shield class="h-4 w-4" />
                            <span>ダッシュボード</span>
                        </button>
                        
                        <button 
                            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {currentPath === '/admin/users' ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}"
                            onclick={() => navigateTo('/admin/users')}
                        >
                            <Users class="h-4 w-4" />
                            <span>ユーザー管理</span>
                        </button>
                        
                        <button 
                            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {currentPath === '/admin/posts' ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}"
                            onclick={() => navigateTo('/admin/posts')}
                        >
                            <FileText class="h-4 w-4" />
                            <span>投稿管理</span>
                        </button>
                        
                        <button 
                            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {currentPath === '/admin/circles' ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}"
                            onclick={() => navigateTo('/admin/circles')}
                        >
                            <MessageSquare class="h-4 w-4" />
                            <span>サークル管理</span>
                        </button>
                        
                        <button 
                            class="flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 {currentPath === '/admin/settings' ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'}"
                            onclick={() => navigateTo('/admin/settings')}
                        >
                            <Settings class="h-4 w-4" />
                            <span>設定</span>
                        </button>
                    </nav>
                </div>
                
                <!-- ユーザーメニュー -->
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <p class="text-sm font-medium text-gray-900">管理者</p>
                        <p class="text-xs text-gray-500">admin@example.com</p>
                    </div>
                    <button 
                        class="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors duration-200"
                        onclick={handleLogout}
                    >
                        <LogOut class="h-4 w-4" />
                        <span>ログアウト</span>
                    </button>
                </div>
            </div>
        </div>
    </header>
    
    <!-- メインコンテンツ -->
    <main class="flex h-full p-6 justify-center items-center">
        <slot />
    </main>
</div>