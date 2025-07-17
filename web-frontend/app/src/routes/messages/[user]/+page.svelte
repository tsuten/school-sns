<script>
    import { Button, Avatar, Input, Textarea } from 'flowbite-svelte';
    import { Send, ArrowLeft, User } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { authService } from '$lib/services/auth.js';
    import { apiClient, getMediaURL } from '$lib/services/django.js';
    import { page } from '$app/stores';
    import { chatMessages } from "$lib/stores/messageStore.js";
    import InPageSideBar from "$lib/components/page-components/inPageSideBar.svelte";
    import ChatCore from "$lib/components/shared/chat/chatCore.svelte";
    import ChatInput from "$lib/components/shared/chat/chatInput.svelte";
    import { initialize } from "$lib/stores/messageStore.js";
    
    let targetUser = $state(null);
    let userId = $state('');
    let users = $state([]);
    let isLoading = $state(true);
    let error = $state(null);

    // ヘルパー関数
    function getProfileImage(user) {
        return user?.pfp ? getMediaURL(user.pfp) : null;
    }

    function getDisplayName(user) {
        return user?.display_name || user?.user_username || 'Unknown User';
    }

    // ユーザーリストを取得する関数
    async function loadUsers() {
        try {
            isLoading = true;
            error = null;
            const response = await apiClient.get('/chat/users-have-history-with-user');
            users = response.users || [];
        } catch (err) {
            console.error('ユーザーリストの取得に失敗しました:', err);
            error = 'ユーザーリストの読み込みに失敗しました。';
            users = [];
        } finally {
            isLoading = false;
        }
    }

    // URLパラメータの変更を監視
    $effect(() => {
        const targetUserId = $page.params.user;
        if (targetUserId && targetUserId !== userId) {
            userId = targetUserId;
            initialize(targetUserId);
        }
    });

    // コンポーネントマウント時にユーザーリストを読み込み
    onMount(() => {
        loadUsers();
    });

</script>

<div class="flex flex-row h-full w-full">
<InPageSideBar>
    <div class="flex flex-col">
        {#if isLoading}
            <div class="p-4 text-gray-500">読み込み中...</div>
        {:else if error}
            <div class="p-4 text-red-500">{error}</div>
            <Button on:click={loadUsers} class="m-2" size="sm">再試行</Button>
        {:else if users.length === 0}
            <div class="p-4 text-gray-500">会話履歴がありません</div>
        {:else}
            {#each users as user}
                <div class="group flex flex-col p-3 border-b border-gray-200 hover:bg-blue-50 cursor-pointer transition-colors duration-200"
                     role="button"
                     tabindex="0"
                     onclick={() => goto(`/messages/${user.user_id}`)}
                     onkeydown={(e) => e.key === 'Enter' && goto(`/messages/${user.user_id}`)}>
                    <div class="flex items-start gap-3">
                        <!-- アイコンプレースホルダー -->
                        <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 {userId === user.user_id ? 'bg-blue-200' : ''}">
                            <User class="w-4 h-4 text-blue-600" />
                        </div>
                        
                        <!-- 詳細情報 -->
                        <div class="flex-1 min-w-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
                            <div class="flex items-center gap-2">
                                <h3 class="font-medium text-gray-800 truncate whitespace-nowrap">{getDisplayName(user.user)}</h3>
                                {#if user.latest_message && !user.latest_message.is_read && !user.latest_message.is_sent_by_me}
                                    <div class="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0"></div>
                                {/if}
                            </div>
                            {#if user.latest_message}
                                <p class="text-xs text-gray-500 truncate">
                                    {user.latest_message.content}
                                </p>
                                <p class="text-xs text-gray-400">
                                    {new Date(user.latest_message.created_at).toLocaleDateString()}
                                </p>
                            {/if}
                        </div>
                    </div>
                </div>
            {/each}
        {/if}
    </div>
</InPageSideBar>
<div class="flex flex-col h-full w-full relative">
    <!-- ヘッダー -->
    <div class="flex items-center gap-3 p-4 border-b border-gray-200 bg-white">
        {#if targetUser}
            <Avatar src={getProfileImage(targetUser)} size="sm" />
            <div class="flex flex-col">
                <h2 class="text-lg font-semibold">{getDisplayName(targetUser)}</h2>
                <p class="text-sm text-gray-500">@{targetUser.user_username}</p>
            </div>
        {:else}
            <div class="flex flex-col">
                <h2 class="text-lg font-semibold">ユーザー</h2>
                <p class="text-sm text-gray-500">読み込み中...</p>
            </div>
        {/if}
    </div>
    <ChatCore messages={$chatMessages} />
    <ChatInput apiPath="/chat/messages/" />
</div>
</div>