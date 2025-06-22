<script>
    import { Avatar, Button, Input } from 'flowbite-svelte';
    import { Pin, Clock, Ellipsis, Search } from 'lucide-svelte';

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

    // サーバーから取得したユーザーデータを使用
    let users = data.users || [];
    let searchQuery = $state('');
    
    // プロフィール画像のフォールバック用関数
    function getProfileImage(user) {
        if (user.pfp) {
            return `http://127.0.0.1:8000${user.pfp}`;
        }
    }
</script>

<div class="flex flex-row gap-2 h-full w-full">
    <div class="flex flex-col gap-2 h-full p-2 w-full">
        <div class="flex flex-col gap-2">
            <div class="relative">
                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <Search class="w-5 h-5 text-gray-500" />
                </div>
                <Input
                    bind:value={searchQuery}
                    placeholder="ユーザーを検索..."
                    class="pl-10"
                />
            </div>
        </div>
        <div class="flex flex-col gap-2 h-full w-full">
            {#each users as user}
                <a href={`/messages/${user.user_id}`}>
                    <Button class="flex flex-row justify-between items-center gap-2 border border-gray-300 hover:cursor-pointer p-3 w-full relative" color="light">
                        <!-- 左側：ユーザー情報 -->
                        <div class="flex flex-row gap-2 items-start">
                            <Avatar src={getProfileImage(user)} />
                            <div class="flex flex-col justify-between">
                                <div class="flex flex-row justify-start items-start gap-1">
                                    <p class="">{user.display_name}</p>
                                    <p class="text-gray-500">@{user.user_username}</p>
                                </div>
                                <div class="flex flex-row justify-center items-center gap-1">
                                    <p class="text-gray-500">最後のメッセージ</p>
                                    <div class="flex items-center gap-1">
                                        <Clock class="w-3 h-3 text-gray-400" />
                                        <p class="text-xs text-gray-400">
                                            {new Date(user.created_at).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 右側：アイコン -->
                        <div class="flex flex-row gap-2">
                            <!-- アイコン（右側） -->
                            <Pin class="w-6 h-6 text-gray-500" />
                            <Ellipsis class="w-6 h-6 text-gray-500" />
                        </div>
                    </Button>
                </a>
            {/each}
            
            <!-- ユーザーが見つからない場合の表示 -->
            {#if users.length === 0}
                <div class="flex flex-col items-center justify-center p-4 text-gray-500">
                    <p class="text-sm">ユーザーが見つかりませんでした</p>
                    <p class="text-xs">サーバーとの接続を確認してください</p>
                </div>
            {/if}
        </div>
    </div>
    {@render children()}
</div>