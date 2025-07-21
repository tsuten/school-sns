<script>
    import { Button } from 'flowbite-svelte';
    import { Siren, Ellipsis, Ban, BellOff } from 'lucide-svelte';
    import { onDestroy } from 'svelte';
    import { apiClient, getMediaURL } from '$lib/services/django.js';
    import { page } from '$app/stores';
    import { chatMessages, chatConfig } from "$lib/stores/messageStore.js";
    import ChatCore from "$lib/components/shared/chat/chatCore.svelte";
    import ChatInput from "$lib/components/shared/chat/chatInput.svelte";
    import { initialize } from "$lib/stores/messageStore.js";
    import ChatHeader from "$lib/components/shared/chat/chatHeader.svelte";
    
    let targetUser = $state(null);
    let userId = $state('');
    let showMenu = $state(false);

    // ヘルパー関数
    function getProfileImage(user) {
        return user?.pfp ? getMediaURL(user.pfp) : null;
    }

    function getDisplayName(user) {
        return user?.display_name || user?.user_username || 'Unknown User';
    }

    // 対象ユーザー情報を取得する関数（APIから直接取得）
    async function loadTargetUser(targetUserId) {
        try {
            // TODO: 個別ユーザー情報取得のAPIエンドポイントを実装
            // 現在は基本的な情報のみ設定
            targetUser = {
                id: targetUserId,
                user_username: 'User',
                display_name: 'ユーザー',
                pfp: null
            };
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
            
            // chatConfigを更新
            chatConfig.set({
                type: 'private',
                room_id: targetUserId
            });
        }
    });

    // コンポーネント破棄時にchatConfigをクリア
    onDestroy(() => {
        chatConfig.set({
            type: null,
            room_id: null
        });
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