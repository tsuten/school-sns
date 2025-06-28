<script>
    import { Send, ArrowLeft, MoreVertical, Smile, Paperclip, Crown, User, Settings, UserMinus, Flag, Info, Reply, Copy, Trash2, Edit } from 'lucide-svelte';
    import { Button, Badge, Card, Dropdown, DropdownItem, DropdownDivider} from 'flowbite-svelte';
    import { apiClient } from '$lib/services/django';
    import { page } from '$app/stores';
    import { userInfo } from '$lib/stores/userInfo';
    import Input from '$lib/components/utils/chat/input.svelte';

    import { onMount } from 'svelte';
    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let circle = $state(null);
    let loading = $state(true);
    let messageInput = $state('');
    let messagesContainer;

    let messages = $state([]);

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
        try {
            const response = await apiClient.get(`/circle/${circleId}/messages`);
            console.log('Messages response:', response);
            
            // 現在のユーザー名を取得
            const currentUsername = $userInfo.username;
            console.log('Current username:', currentUsername);
            
            // APIレスポンスを適切に処理
            messages = response.map(message => ({
                ...message,
                timestamp: message.created_at,
                isOwn: message.user === currentUsername // 現在のユーザーのメッセージかどうか判定
            }));
        } catch (err) {
            console.error('Error fetching messages:', err);
            messages = [];
        }
    }

    $effect(() => {
        if (circle) {
            fetchMessages(circle.id);
        }
    });

    async function sendMessage() {
        console.log('sendMessage called, messageInput:', messageInput);
        console.log('circle:', circle);
        
        if (messageInput.trim() && circle) {
            const messageContent = messageInput.trim();
            messageInput = ''; // 先に入力をクリア
            
            try {
                console.log('Sending message to API...');
                const response = await apiClient.post(`/circle/${circle.id}/messages`, {
                    content: messageContent
                });
                
                console.log('API response:', response);
                
                // 送信成功後、メッセージリストを再取得
                await fetchMessages(circle.id);
                console.log('Message sent successfully');
            } catch (err) {
                console.error('Error sending message:', err);
                // エラー時は入力を復元
                messageInput = messageContent;
                alert('メッセージの送信に失敗しました: ' + err.message);
            }
        } else {
            console.log('Message not sent - messageInput or circle is null');
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
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer" id="chat-menu-button">
                <MoreVertical class="h-5 w-5 text-gray-500" />
            </Button>
            <Dropdown triggeredBy="#chat-menu-button" class="w-44" simple>
                <DropdownItem class="flex items-center gap-2">
                    <Info class="w-4 h-4" />
                    サークル情報
                </DropdownItem>
                <DropdownItem class="flex items-center gap-2">
                    <Settings class="w-4 h-4" />
                    チャット設定
                </DropdownItem>
                <DropdownDivider />
                <DropdownItem class="flex items-center gap-2">
                    <UserMinus class="w-4 h-4" />
                    サークルを退会
                </DropdownItem>
                <DropdownItem class="flex items-center gap-2 text-red-600">
                    <Flag class="w-4 h-4" />
                    サークルを報告
                </DropdownItem>
            </Dropdown>
        </div>

        <!-- メッセージエリア -->
        <div class="flex-1 overflow-y-auto space-y-4 p-4" bind:this={messagesContainer}>
            {#each messages as message, index (message.id)}
                {@const shouldShowTime = index === 0 || 
                    (new Date(message.created_at || message.timestamp) - new Date(messages[index - 1].created_at || messages[index - 1].timestamp)) >= 300000}
                <div class="flex {message.isOwn ? 'justify-end' : 'justify-start'} group items-center gap-2">
                    {#if !message.isOwn}
                            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                {#if (message.user?.username || message.user) === circle.founder.username}
                                    <Crown class="w-4 h-4 text-yellow-600" />
                                {:else}
                                    <User class="w-4 h-4 text-blue-600" />
                                {/if}
                            </div>
                        {/if}
                    
                    <div class="flex {message.isOwn ? 'flex-row-reverse' : 'flex-row'} items-end gap-2 max-w-sm lg:max-w-md relative">

                        <!-- メッセージバブル -->
                        <div class="flex flex-col {message.isOwn ? 'items-end' : 'items-start'}">
                            {#if !message.isOwn}
                                <div class="flex items-center gap-1 mb-1">
                                    <span class="text-xs font-medium text-gray-700">{message.user?.username || message.user || 'Unknown'}</span>
                                    {#if (message.user?.username || message.user) === circle.founder.username}
                                        <Crown class="w-3 h-3 text-yellow-500" />
                                    {/if}
                                </div>
                            {/if}
                            
                            <div class="
                                {message.isOwn 
                                    ? 'bg-blue-500 text-white rounded-sm' 
                                    : 'bg-white text-gray-800 rounded-sm border border-gray-200'
                                } 
                                px-4 py-2 max-w-full break-words
                            ">
                                <p class="text-sm whitespace-pre-wrap">{message.content}</p>
                            </div>
                            
                            {#if shouldShowTime}
                                <span class="text-xs text-gray-500 mt-1">
                                    {formatTime(message.created_at || message.timestamp)}
                                </span>
                            {/if}
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

