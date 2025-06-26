<script>
    import { Send, Smile, Paperclip, Crown, User } from 'lucide-svelte';
    import { Button } from 'flowbite-svelte';
    import { createEventDispatcher } from 'svelte';

    // Props
    let { 
        messages = [],
        currentUserId = null,
        founderIds = [],
        placeholder = "メッセージを入力...",
        disabled = false,
        showAvatar = true,
        showTimestamp = true,
        enableInput = true
    } = $props();

    // State
    let messageInput = $state('');
    let messagesContainer;
    
    // Event dispatcher for sending messages
    const dispatch = createEventDispatcher();

    // Auto-scroll when messages update
    $effect(() => {
        if (messagesContainer && messages.length > 0) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 10);
        }
    });

    $inspect(messages);
    $inspect(messageInput);

    function sendMessage() {
        if (messageInput.trim() && !disabled) {
            dispatch('sendMessage', {
                content: messageInput.trim()
            });
            messageInput = '';
        }
    }

    function handleKeyPress(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }

    function formatTime(timestamp) {
        return new Date(timestamp).toLocaleTimeString('ja-JP', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function isOwnMessage(message) {
        return message.user_id === currentUserId;
    }

    function isFounder(userId) {
        return founderIds.includes(userId);
    }
</script>

<div class="flex flex-col h-full bg-gray-50">
    <!-- メッセージエリア -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4" bind:this={messagesContainer}>
        {#each messages as message (message.id || message.timestamp)}
            <div class="flex {isOwnMessage(message) ? 'justify-end' : 'justify-start'}">
                <div class="flex {isOwnMessage(message) ? 'flex-row-reverse' : 'flex-row'} items-end gap-2 max-w-sm lg:max-w-md">
                    <!-- アバター -->
                    {#if showAvatar && !isOwnMessage(message)}
                        <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                            {#if isFounder(message.user_id)}
                                <Crown class="w-4 h-4 text-yellow-600" />
                            {:else}
                                <User class="w-4 h-4 text-blue-600" />
                            {/if}
                        </div>
                    {/if}

                    <!-- メッセージバブル -->
                    <div class="flex flex-col {isOwnMessage(message) ? 'items-end' : 'items-start'}">
                        <!-- 表示名 -->
                        {#if !isOwnMessage(message) && message.display_name}
                            <div class="flex items-center gap-1 mb-1">
                                <span class="text-xs font-medium text-gray-700">{message.display_name}</span>
                                {#if isFounder(message.user_id)}
                                    <Crown class="w-3 h-3 text-yellow-500" />
                                {/if}
                            </div>
                        {/if}
                        
                        <!-- メッセージ内容 -->
                        <div class="
                            {isOwnMessage(message)
                                ? 'bg-blue-500 text-white rounded-l-lg rounded-tr-lg' 
                                : 'bg-white text-gray-800 rounded-r-lg rounded-tl-lg border border-gray-200'
                            } 
                            px-4 py-2 max-w-full break-words
                        ">
                            <p class="text-sm whitespace-pre-wrap">{message.content}</p>
                        </div>
                        
                        <!-- タイムスタンプ -->
                        {#if showTimestamp && message.sent_at}
                            <span class="text-xs text-gray-500 mt-1">
                                {formatTime(message.sent_at)}
                            </span>
                        {/if}
                    </div>
                </div>
            </div>
        {/each}

        <!-- メッセージがない場合 -->
        {#if messages.length === 0}
            <div class="text-center py-8 text-gray-500">
                <div class="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Send class="w-8 h-8 text-gray-400" />
                </div>
                <p>まだメッセージがありません</p>
                <p class="text-xs mt-1">最初のメッセージを送信してみましょう</p>
            </div>
        {/if}
    </div>

    <!-- メッセージ入力エリア -->
    {#if enableInput}
        <div class="bg-white border-t border-gray-300 p-4">
            <div class="flex items-end gap-2">
                <!-- ファイル添付ボタン -->
                <Button 
                    pill={true} 
                    color="light" 
                    class="p-2! hover:cursor-pointer flex-shrink-0"
                    on:click={() => dispatch('attachFile')}
                    {disabled}
                >
                    <Paperclip class="h-5 w-5 text-gray-500" />
                </Button>
                
                <!-- テキスト入力エリア -->
                <div class="flex-1 relative">
                    <textarea
                        bind:value={messageInput}
                        on:keydown={handleKeyPress}
                        {placeholder}
                        {disabled}
                        class="w-full px-4 py-2 border border-gray-300 rounded-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 max-h-24 disabled:bg-gray-100 disabled:cursor-not-allowed"
                        rows="1"
                    ></textarea>
                </div>
                
                <!-- 絵文字ボタン -->
                <Button 
                    pill={true} 
                    color="light" 
                    class="p-2! hover:cursor-pointer flex-shrink-0"
                    on:click={() => dispatch('openEmoji')}
                    {disabled}
                >
                    <Smile class="h-5 w-5 text-gray-500" />
                </Button>
                
                <!-- 送信ボタン -->
                <Button 
                    color="blue" 
                    class="px-4 py-2 rounded-sm hover:cursor-pointer flex-shrink-0"
                    on:click={sendMessage}
                    disabled={!messageInput.trim() || disabled}
                >
                    <Send class="h-4 w-4" />
                </Button>
            </div>
        </div>
    {/if}
</div>
