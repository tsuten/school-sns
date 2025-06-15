<script>
    import { User, Camera, Save, Edit3, Calendar, Mail, MapPin, Link as LinkIcon } from "lucide-svelte";
    
    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    // ダミープロフィールデータ
    let profileData = {
        username: "user123",
        displayName: "山田太郎",
        email: "yamada@example.com",
        bio: "こんにちは！SNSを楽しんでいます。趣味は読書と映画鑑賞です。\nよろしくお願いします！",
        birthday: "1990-01-01",
        location: "東京都",
        website: "https://example.com",
        joinDate: "2023-06-15",
        avatarUrl: "https://via.placeholder.com/150/4A90E2/FFFFFF?text=YT"
    };

    // 編集モード管理
    let isEditing = false;
    let editedData = { ...profileData };

    // 統計データ
    let stats = {
        posts: 142,
        followers: 1205,
        following: 387,
        likes: 2847
    };

    function toggleEdit() {
        if (isEditing) {
            // 保存処理
            profileData = { ...editedData };
            console.log("プロフィールを保存しました:", profileData);
        } else {
            // 編集開始
            editedData = { ...profileData };
        }
        isEditing = !isEditing;
    }

    function cancelEdit() {
        editedData = { ...profileData };
        isEditing = false;
    }

    function handleAvatarChange() {
        console.log("プロフィール画像を変更");
        // 実際の実装ではファイル選択ダイアログを表示
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ja-JP', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    }
</script>

<div class="max-w-4xl mx-auto p-6 space-y-8 h-full overflow-y-auto">
    <!-- ページタイトル -->
    <div class="border-b pb-4">
        <h1 class="text-3xl font-bold text-gray-900">プロフィール</h1>
        <p class="text-gray-600 mt-2">あなたのプロフィール情報を管理</p>
    </div>

    <!-- プロフィールヘッダー -->
    <div class="flex flex-col gap-2">
        <h1 class="text-2xl font-bold">あなたのプロフィールカード</h1>
    </div>
    <div class="bg-white rounded-lg border border-gray-200 p-6">
        <div class="flex flex-col md:flex-row items-start md:items-center gap-6">
            <!-- プロフィール画像 -->
            <div class="relative">
                <img 
                    src={profileData.avatarUrl} 
                    alt="プロフィール画像" 
                    class="w-24 h-24 rounded-full object-cover border-4 border-gray-100"
                >
                <button 
                    class="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                    on:click={handleAvatarChange}
                >
                    <Camera class="w-4 h-4" />
                </button>
            </div>

            <!-- 基本情報 -->
            <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                    <h2 class="text-2xl font-bold text-gray-900">{profileData.displayName}</h2>
                    <span class="text-gray-500">@{profileData.username}</span>
                </div>
                <p class="text-gray-600 whitespace-pre-wrap">{profileData.bio}</p>
                
                <!-- メタ情報 -->
                <div class="flex flex-wrap gap-4 mt-3 text-sm text-gray-500">
                    <div class="flex items-center gap-1">
                        <Calendar class="w-4 h-4" />
                        {formatDate(profileData.joinDate)}に参加
                    </div>
                    {#if profileData.location}
                        <div class="flex items-center gap-1">
                            <MapPin class="w-4 h-4" />
                            {profileData.location}
                        </div>
                    {/if}
                    {#if profileData.website}
                        <div class="flex items-center gap-1">
                            <LinkIcon class="w-4 h-4" />
                            <a href={profileData.website} class="text-blue-600 hover:underline" target="_blank">
                                ウェブサイト
                            </a>
                        </div>
                    {/if}
                </div>
            </div>

            <!-- 編集ボタン -->
            <div class="flex gap-2">
                {#if isEditing}
                    <button 
                        class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                        on:click={toggleEdit}
                    >
                        <Save class="w-4 h-4" />
                        保存
                    </button>
                    <button 
                        class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        on:click={cancelEdit}
                    >
                        キャンセル
                    </button>
                {:else}
                    <button 
                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                        on:click={toggleEdit}
                    >
                        <Edit3 class="w-4 h-4" />
                        編集
                    </button>
                {/if}
            </div>
        </div>
    </div>

    <!-- 統計情報 -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h3 class="text-lg font-semibold mb-4">統計</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center">
                <div class="text-2xl font-bold text-blue-600">{stats.posts.toLocaleString()}</div>
                <div class="text-sm text-gray-500">投稿</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-green-600">{stats.followers.toLocaleString()}</div>
                <div class="text-sm text-gray-500">フォロワー</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-purple-600">{stats.following.toLocaleString()}</div>
                <div class="text-sm text-gray-500">フォロー中</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-red-600">{stats.likes.toLocaleString()}</div>
                <div class="text-sm text-gray-500">いいね</div>
            </div>
        </div>
    </div>

    <!-- 編集フォーム -->
    {#if isEditing}
        <div class="bg-white rounded-lg border border-gray-200 p-6">
            <h3 class="text-lg font-semibold mb-4 flex items-center gap-2">
                <User class="w-5 h-5" />
                プロフィール編集
            </h3>
            <form class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">表示名</label>
                        <input 
                            type="text" 
                            bind:value={editedData.displayName}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="表示名を入力"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">ユーザー名</label>
                        <input 
                            type="text" 
                            bind:value={editedData.username}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="ユーザー名を入力"
                        >
                    </div>
                </div>

                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">自己紹介</label>
                    <textarea 
                        bind:value={editedData.bio}
                        rows="4"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="自己紹介を入力"
                    ></textarea>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">メールアドレス</label>
                        <input 
                            type="email" 
                            bind:value={editedData.email}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="メールアドレスを入力"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">生年月日</label>
                        <input 
                            type="date" 
                            bind:value={editedData.birthday}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">場所</label>
                        <input 
                            type="text" 
                            bind:value={editedData.location}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="場所を入力"
                        >
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">ウェブサイト</label>
                        <input 
                            type="url" 
                            bind:value={editedData.website}
                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            placeholder="https://example.com"
                        >
                    </div>
                </div>
            </form>
        </div>
    {/if}

    <!-- プライバシー設定 -->
    <div class="bg-white rounded-lg border border-gray-200 p-6">
        <h3 class="text-lg font-semibold mb-4">プライバシー設定</h3>
        <div class="space-y-4">
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-medium text-gray-900">プロフィールを公開</p>
                    <p class="text-sm text-gray-500">他のユーザーがあなたのプロフィールを見ることができます</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" checked class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
            </div>
            
            <div class="flex items-center justify-between">
                <div>
                    <p class="font-medium text-gray-900">フォローを承認制にする</p>
                    <p class="text-sm text-gray-500">新しいフォロワーを手動で承認します</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer">
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
            </div>
        </div>
    </div>
</div>