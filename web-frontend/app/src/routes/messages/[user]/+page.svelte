<script>
    import { Button, Avatar, Input, Textarea } from 'flowbite-svelte';
    import { Send, ArrowLeft } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { authService } from '$lib/services/auth.js';
    import { page } from '$app/stores';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let messages = $state([]);
    let targetUser = $state(null);
    let userId = $state('');
    let newMessage = $state('');
    let messagesContainer;

    // dataの変更を監視してstateを更新
    $effect(() => {
        const newUserId = data.userId;
        const oldUserId = userId;
        
        messages = data.messages || [];
        targetUser = data.targetUser;
        userId = newUserId;
        
        // ユーザーが変更された場合のみ、メッセージ入力をリセット
        if (oldUserId && oldUserId !== newUserId) {
            newMessage = '';
        }
        
        // メッセージが更新されたらスクロールを最下部に移動
        if (messages.length > 0) {
            setTimeout(() => {
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            }, 100);
        }
    });

    // URLパラメータの変更を監視（初回読み込み時は実行しない）
    let isInitialLoad = true;
    $effect(() => {
        const currentUserId = $page.params.user;
        if (!isInitialLoad && currentUserId !== userId && currentUserId) {
            // URLが変更されたらメッセージを一時的にクリア
            messages = [];
            targetUser = null;
            newMessage = ''; // URL変更時のみ入力をクリア
        }
        isInitialLoad = false;
    });

    // プロフィール画像のフォールバック用関数
    function getProfileImage(user) {
        if (user?.pfp) {
            return `http://127.0.0.1:8000${user.pfp}`;
        }
        return `https://picsum.photos/seed/${user?.user_id || 'default'}/40/40`;
    }

    // 表示名のフォールバック用関数
    function getDisplayName(user) {
        return user?.display_name || user?.user_username || 'ユーザー';
    }

    // メッセージ送信関数
    async function sendMessage() {
        if (!newMessage.trim()) return;

        // 認証チェック
        if (!authService.isAuthenticated()) {
            alert('ログインが必要です');
            goto('/login');
            return;
        }

        try {
            const response = await authService.authenticatedFetch('http://127.0.0.1:8000/api/chat/messages', {
                method: 'POST',
                body: JSON.stringify({
                    recipient_id: $page.params.user,  // 現在のURLパラメータを使用
                    content: newMessage.trim()
                })
            });

            if (response.ok) {
                const sentMessage = await response.json();
                // 新しいメッセージを配列に追加
                messages = [...messages, {
                    id: sentMessage.id,
                    sent_by: 'request_user',  // Django側の値に合わせる
                    content: newMessage.trim(),
                    is_read: false,
                    created_at: new Date().toISOString()
                }];
                newMessage = '';
                // スクロールを最下部に移動
                setTimeout(() => {
                    if (messagesContainer) {
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                }, 100);
            }
        } catch (error) {
            console.error('メッセージの送信に失敗しました:', error);
            if (error.message === '認証が必要です') {
                alert('認証が切れました。再度ログインしてください。');
                goto('/login');
            }
        }
    }

    // Enterキーでメッセージ送信
    function handleKeydown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

    // 日時フォーマット関数
    function formatMessageTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);

        if (diffInHours < 24) {
            return date.toLocaleTimeString('ja-JP', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } else {
            return date.toLocaleDateString('ja-JP', { 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit', 
                minute: '2-digit' 
            });
        }
    }

    // コンポーネントマウント時の処理
    onMount(() => {
        // 認証が必要な場合はログインページにリダイレクト
        if (data.needsAuth) {
            alert('ログインが必要です');
            goto('/login');
            return;
        }
    });
</script>

<div class="flex flex-col h-full w-full">
    <!-- ヘッダー -->
    <div class="flex items-center gap-3 p-4 border-b border-gray-200 bg-white">
        <a href="/messages">
            <Button 
                color="light" 
                size="sm" 
                class="p-2" 
                on:click={() => goto('/messages')}
            >
                <ArrowLeft class="w-4 h-4" />
            </Button>
        </a>
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

    <!-- メッセージ一覧 -->
    <div 
        bind:this={messagesContainer}
        class="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50"
    >
        {#if messages.length === 0}
            <div class="flex flex-col items-center justify-center h-full text-gray-500">
                <p class="text-lg">まだメッセージがありません</p>
                <p class="text-sm">最初のメッセージを送ってみましょう！</p>
            </div>
        {:else}
            {#each messages as message}
                <div class="flex {message.sent_by === 'request_user' ? 'justify-end' : 'justify-start'}">
                    <div class="flex max-w-xs lg:max-w-md {message.sent_by === 'request_user' ? 'flex-row-reverse' : 'flex-row'} items-end gap-2">
                        <!-- アバター（相手のメッセージの場合のみ表示） -->
                        {#if message.sent_by !== 'request_user'}
                            <Avatar src={getProfileImage(targetUser)} size="xs" />
                        {/if}
                        
                        <!-- メッセージバブル -->
                        <div class="flex flex-col {message.sent_by === 'request_user' ? 'items-end' : 'items-start'}">
                            <div class="px-4 py-2 rounded-lg {
                                message.sent_by === 'request_user' 
                                    ? 'bg-blue-500 text-white' 
                                    : 'bg-white border border-gray-200'
                            }">
                                <p class="text-sm whitespace-pre-wrap">{message.content}</p>
                            </div>
                            
                            <!-- 時刻とステータス -->
                            <div class="flex items-center gap-1 mt-1 px-1">
                                <span class="text-xs text-gray-400">
                                    {formatMessageTime(message.created_at)}
                                </span>
                                {#if message.sent_by === 'request_user'}
                                    <span class="text-xs text-gray-400">
                                        {message.is_read ? '既読' : '未読'}
                                    </span>
                                {/if}
                            </div>
                        </div>
                    </div>
                </div>
            {/each}
        {/if}
    </div>

    <!-- メッセージ入力欄 -->
    <div class="p-4 border-t border-gray-200 bg-white">
        <div class="flex gap-2 items-end">
            <div class="flex-1">
                <Textarea
                    bind:value={newMessage}
                    placeholder="メッセージを入力..."
                    rows="1"
                    class="resize-none"
                    on:keydown={handleKeydown}
                />
            </div>
            <Button 
                color="blue" 
                size="sm" 
                class="p-3"
                disabled={!newMessage.trim()}
                on:click={sendMessage}
            >
                <Send class="w-4 h-4" />
            </Button>
        </div>
    </div>
</div>