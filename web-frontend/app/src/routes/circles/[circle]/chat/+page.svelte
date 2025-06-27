<script>
    import { Send, ArrowLeft, MoreVertical, Smile, Paperclip, Crown, User } from 'lucide-svelte';
    import { Button, Badge, Card} from 'flowbite-svelte';
    import { apiClient } from '$lib/services/django';
    import { page } from '$app/stores';
    import Input from '$lib/components/utils/chat/input.svelte';

    import { onMount } from 'svelte';
    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let circle = $state(null);
    let loading = $state(true);
    let messageInput = $state('');
    let messagesContainer;

    // ダミーメッセージデータ
    let messages = $state([
        {
            id: 1,
            user: { id: 'user1', username: 'alice' },
            content: 'みなさん、おつかれさまです！',
            timestamp: '2024-01-15T09:00:00Z',
            isOwn: false
        },
        {
            id: 2,
            user: { id: 'user2', username: 'bob' },
            content: 'おつかれさまです！今日の勉強会の件ですが、資料の共有ありがとうございました。',
            timestamp: '2024-01-15T09:15:00Z',
            isOwn: false
        },
        {
            id: 3,
            user: { id: 'current-user', username: 'you' },
            content: 'どういたしまして！みんなで頑張りましょう！',
            timestamp: '2024-01-15T09:30:00Z',
            isOwn: true
        },
        {
            id: 4,
            user: { id: 'user3', username: 'charlie' },
            content: '次回の予定はいつごろになりそうですか？',
            timestamp: '2024-01-15T10:00:00Z',
            isOwn: false
        },
        {
            id: 5,
            user: { id: 'user1', username: 'alice' },
            content: '来週の土曜日はどうでしょうか？',
            timestamp: '2024-01-15T10:15:00Z',
            isOwn: false
        },
        {
            id: 6,
            user: { id: 'current-user', username: 'you' },
            content: '土曜日いいですね！参加します🙋‍♀️',
            timestamp: '2024-01-15T10:20:00Z',
            isOwn: true
        }
    ]);

    $effect(() => {
        const circleId = $page.params.circle;
        if (circleId) {
            fetchCircleDetail(circleId);
        }
    });

    $effect(() => {
        // メッセージが更新されたら自動スクロール
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    });

    async function fetchCircleDetail(circleId) {
        try {
            loading = true;
            const response = await apiClient.get(`/circle/${circleId}`);
            circle = response;
        } catch (err) {
            console.error('Error fetching circle:', err);
        } finally {
            loading = false;
        }
    }

    async function fetchMessages(circleId) {
        const response = await apiClient.get(`/circle/${circleId}/messages`);
        console.log(response);
        messages = response;
    }

    $effect(() => {
        if (circle) {
            fetchMessages(circle.id);
        }
    });

    function sendMessage() {
        if (messageInput.trim()) {
            const newMessage = {
                id: messages.length + 1,
                user: { id: 'current-user', username: 'you' },
                content: messageInput.trim(),
                timestamp: new Date().toISOString(),
                isOwn: true
            };
            messages = [...messages, newMessage];
            messageInput = '';
        }
    }

    function formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString('ja-JP', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function formatDate(timestamp) {
        return new Date(timestamp).toLocaleDateString('ja-JP', {
            month: 'short',
            day: 'numeric'
        });
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }
</script>

{#if loading}
    <div class="flex justify-center items-center h-64">
        <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p class="text-gray-600">読み込み中...</p>
        </div>
    </div>
{:else if circle}
    <div class="flex flex-col h-screen bg-gray-50">
        <!-- ヘッダー -->
        <div class="bg-white border-b border-gray-300 px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <a href="/circles/{$page.params.circle}">
                    <Button pill={true} color="light" class="p-2! hover:cursor-pointer">
                        <ArrowLeft class="h-5 w-5 text-gray-500" />
                    </Button>
                </a>
                <div>
                    <h1 class="text-lg font-bold text-gray-800">{circle.name}</h1>
                    <p class="text-sm text-gray-600">{circle.members.length} メンバー</p>
                </div>
            </div>
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer">
                <MoreVertical class="h-5 w-5 text-gray-500" />
            </Button>
        </div>

        <!-- メッセージエリア -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4" bind:this={messagesContainer}>
            {#each messages as message (message.id)}
                <div class="flex {message.isOwn ? 'justify-end' : 'justify-start'}">
                    <div class="flex {message.isOwn ? 'flex-row-reverse' : 'flex-row'} items-end gap-2 max-w-sm lg:max-w-md">
                        <!-- アバター -->
                        {#if !message.isOwn}
                            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                {#if message.user.id === circle.founder.id}
                                    <Crown class="w-4 h-4 text-yellow-600" />
                                {:else}
                                    <User class="w-4 h-4 text-blue-600" />
                                {/if}
                            </div>
                        {/if}

                        <!-- メッセージバブル -->
                        <div class="flex flex-col {message.isOwn ? 'items-end' : 'items-start'}">
                            {#if !message.isOwn}
                                <div class="flex items-center gap-1 mb-1">
                                    <span class="text-xs font-medium text-gray-700">{message.user.username}</span>
                                    {#if message.user.id === circle.founder.id}
                                        <Crown class="w-3 h-3 text-yellow-500" />
                                    {/if}
                                </div>
                            {/if}
                            
                            <div class="
                                {message.isOwn 
                                    ? 'bg-blue-500 text-white rounded-l-lg rounded-tr-lg' 
                                    : 'bg-white text-gray-800 rounded-r-lg rounded-tl-lg border border-gray-200'
                                } 
                                px-4 py-2 max-w-full break-words
                            ">
                                <p class="text-sm whitespace-pre-wrap">{message.content}</p>
                            </div>
                            
                            <span class="text-xs text-gray-500 mt-1">
                                {formatTime(message.timestamp)}
                            </span>
                        </div>
                    </div>
                </div>
            {/each}
        </div>

        <!-- メッセージ入力エリア -->
        <Input 
            bind:value={messageInput}
            onKeydown={handleKeyPress}
            onSend={sendMessage}
            placeholder="{circle.name}に送信…"
        />
    </div>
{:else}
    <div class="flex justify-center items-center h-64">
        <div class="text-center">
            <p class="text-gray-500">サークルが見つかりませんでした</p>
        </div>
    </div>
{/if}

