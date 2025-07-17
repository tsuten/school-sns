<script>
    import { Button, Avatar, Input, Textarea } from 'flowbite-svelte';
    import { Send, ArrowLeft, User, LogOut, Siren, DoorOpen, Ellipsis, Ban, BellOff } from 'lucide-svelte';
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
    import ChatHeader from "$lib/components/shared/chat/chatHeader.svelte";
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
    let showMenu = $state(false);

    // 対象ユーザー情報を取得する関数
    async function loadTargetUser(targetUserId) {
        try {
            // ユーザーリストから対象ユーザーを探す
            const userEntry = users.find(u => u.user_id === targetUserId);
            if (userEntry) {
                targetUser = userEntry.user;
            } else {
                // ユーザーリストにない場合は直接APIで取得
                // 今回はユーザーリストから取得するのみとする
                targetUser = null;
            }
        } catch (err) {
            console.error('対象ユーザー情報の取得に失敗しました:', err);
            targetUser = null;
        }
    }

    // URLパラメータの変更を監視
    $effect(() => {
        const targetUserId = $page.params.user;
        if (targetUserId && targetUserId !== userId) {
            userId = targetUserId;
            initialize(targetUserId);
            loadTargetUser(targetUserId);
        }
    });

    // コンポーネントマウント時にユーザーリストを読み込み
    onMount(() => {
        loadUsers();
    });

    // ユーザーリストが更新されたときに対象ユーザーを設定
    $effect(() => {
        if (users.length > 0 && userId && !targetUser) {
            loadTargetUser(userId);
        }
    });

    // メッセージ送信処理
    async function handleMessageSend(content) {
        if (!userId) {
            console.error('送信先ユーザーが指定されていません');
            return;
        }

        console.log("メッセージを送信します", content, userId);

        try {
            const response = await apiClient.post('/chat/messages', {
                content: content,
                receiver_id: userId
            });
            console.log('メッセージが送信されました:', response);
        } catch (error) {
            console.error('メッセージの送信に失敗しました:', error);
            throw error; // エラーを再スローして chatInput でハンドリング
        }
    }

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
                        <!-- ユーザーアイコン -->
                        <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden {userId === user.user_id ? 'ring-2 ring-blue-300' : ''}">
                            {#if getProfileImage(user.user)}
                                <img 
                                    src={getProfileImage(user.user)} 
                                    alt={getDisplayName(user.user)}
                                    class="w-full h-full object-cover"
                                />
                            {:else}
                                <div class="w-full h-full bg-blue-100 flex items-center justify-center">
                                    <User class="w-4 h-4 text-blue-600" />
                                </div>
                            {/if}
                        </div>
                        
                        <!-- 詳細情報 -->
                        <div class="flex-1 min-w-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
                            <div class="flex items-center gap-2">
                                <h3 class="font-medium text-gray-800 truncate whitespace-nowrap">{getDisplayName(user.user)}</h3>
                                <p class="text-xs text-gray-500 truncate whitespace-nowrap">@{user.user.user_username}</p>
                            </div>
                            {#if user.latest_message}
                                <p class="text-xs text-gray-500 truncate">
                                    {user.latest_message.content}
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
    <ChatHeader 
        logo={targetUser ? getProfileImage(targetUser) : null} 
        title={targetUser ? getDisplayName(targetUser) : 'ユーザー'} 
        subtitle={targetUser ? `@${targetUser.user_username}` : '読み込み中...'} 
    >
        <div class="flex flex-row items-center gap-2">
            {#if showMenu}
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer" id="chat-menu-button">
                <Siren class="h-5 w-5 text-gray-500" />
            </Button>
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer" id="chat-menu-button">
                <Ban class="h-5 w-5 text-gray-500" />
            </Button>
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer" id="chat-menu-button">
                <BellOff class="h-5 w-5 text-gray-500" />
            </Button>
            {/if}
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer" id="chat-menu-button" onclick={() => showMenu = !showMenu}>
                <Ellipsis class="h-5 w-5 text-gray-500" />
            </Button>
        </div>
    </ChatHeader>
    <ChatCore messages={$chatMessages} />
    <ChatInput onSend={handleMessageSend} />
</div>
</div>