<script>
    import { User, Lock, Mail, LogOut, Trash2, Bell, Palette, Shield } from "lucide-svelte";

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    // ダミーユーザーデータ
    let userInfo = {
        username: "user123",
        displayName: "山田太郎",
        email: "yamada@example.com",
        bio: "こんにちは！よろしくお願いします。",
        birthday: "1990-01-01",
        joinDate: "2023-06-15"
    };

    let settingsItems = [
        {
            title: "プロフィール設定",
            icon: User,
            description: "ユーザー名、表示名、自己紹介を編集"
        },
        {
            title: "パスワード変更",
            icon: Lock,
            description: "アカウントのパスワードを変更"
        },
        {
            title: "メールアドレス",
            icon: Mail,
            description: "メールアドレスの変更・確認"
        },
        {
            title: "通知設定",
            icon: Bell,
            description: "通知の受け取り方法を設定"
        },
        {
            title: "プライバシー",
            icon: Shield,
            description: "プライバシーとセキュリティ設定"
        },
        {
            title: "テーマ設定",
            icon: Palette,
            description: "ダークモード・ライトモード"
        }
    ];

    let dangerousActions = [
        {
            title: "ログアウト",
            icon: LogOut,
            description: "現在のセッションからログアウト",
            color: "text-orange-600"
        },
        {
            title: "アカウント削除",
            icon: Trash2,
            description: "アカウントを完全に削除（復元不可）",
            color: "text-red-600"
        }
    ];

    function handleSettingClick(item) {
        console.log(`${item.title}がクリックされました`);
        // 実際の実装では各設定画面に遷移
    }

    function handleDangerousAction(item) {
        console.log(`${item.title}がクリックされました`);
        // 実際の実装では確認ダイアログを表示
    }
</script>

<div class="max-w-4xl mx-auto p-6 space-y-8 h-full overflow-y-auto">
    <!-- ページタイトル -->
    <div class="border-b pb-4">
        <h1 class="text-3xl font-bold text-gray-900">設定</h1>
        <p class="text-gray-600 mt-2">アカウントとアプリケーションの設定を管理</p>
    </div>

    <!-- ユーザー情報概要 -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
            <User class="w-5 h-5" />
            ユーザー情報
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700">ユーザー名</label>
                <p class="text-gray-900">{userInfo.username}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">表示名</label>
                <p class="text-gray-900">{userInfo.displayName}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">メールアドレス</label>
                <p class="text-gray-900">{userInfo.email}</p>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">登録日</label>
                <p class="text-gray-900">{userInfo.joinDate}</p>
            </div>
            <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700">自己紹介</label>
                <p class="text-gray-900">{userInfo.bio}</p>
            </div>
        </div>
    </div>

    <!-- 設定項目 -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h2 class="text-xl font-semibold mb-4">アカウント設定</h2>
        <div class="space-y-3">
            {#each settingsItems as item}
                <button 
                    class="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    on:click={() => handleSettingClick(item)}
                >
                    <div class="flex items-center gap-3">
                        <svelte:component this={item.icon} class="w-5 h-5 text-gray-600" />
                        <div class="text-left">
                            <p class="font-medium text-gray-900">{item.title}</p>
                            <p class="text-sm text-gray-500">{item.description}</p>
                        </div>
                    </div>
                    <div class="text-gray-400">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </button>
            {/each}
        </div>
    </div>

    <!-- 危険な操作 -->
    <div class="bg-white rounded-lg border border-red-200 p-6">
        <h2 class="text-xl font-semibold mb-4 text-red-700">危険な操作</h2>
        <div class="space-y-3">
            {#each dangerousActions as item}
                <button 
                    class="w-full flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-red-50 transition-colors"
                    on:click={() => handleDangerousAction(item)}
                >
                    <div class="flex items-center gap-3">
                        <svelte:component this={item.icon} class="w-5 h-5 {item.color}" />
                        <div class="text-left">
                            <p class="font-medium {item.color}">{item.title}</p>
                            <p class="text-sm text-gray-500">{item.description}</p>
                        </div>
                    </div>
                    <div class="{item.color}">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </div>
                </button>
            {/each}
        </div>
    </div>

    <!-- フッター情報 -->
    <div class="bg-gray-50 rounded-lg p-4 text-center text-sm text-gray-600">
        <p>何か問題がございましたら、サポートまでお問い合わせください。</p>
        <p class="mt-1">バージョン 1.0.0</p>
    </div>
</div>