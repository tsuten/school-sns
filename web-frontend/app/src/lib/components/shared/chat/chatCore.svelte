<script>
    import { Crown, User, Info, Reply, Copy, Trash2, Edit, Clock, Ellipsis, MoreVertical } from 'lucide-svelte';
    import { Badge, Button, Dropdown, DropdownItem, DropdownDivider } from 'flowbite-svelte';
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    import { getMediaURL, apiClient } from '$lib/services/django';

    // プロパティ（外部から受け取るデータ）
    let {
        messages = [],
        currentUser = null,
        loading = false,
        hasNextPage = false,
        loadMoreMessages = null,
        onMessageAction = null,
        showUserInfo = true,
        allowActions = false,
        typingUsers = new Set(),
        onlineUsers = new Set(),
        getUserIcon = null, // (user) => iconComponent のような関数
        targetUserId = null, // 相手ユーザーのID
        targetUser = null // 相手ユーザーの情報
    } = $props();

    let messagesContainer = $state();
    let profileImages = $state(new Map()); // プロフィール画像のキャッシュ

    // メッセージが更新されたら自動スクロール（最下部へ）
    $effect(() => {
        if (messagesContainer && messages.length > 0) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 10);
        }
    });

    async function getPfpFromId(id) {
        if (!id) return null;
        
        // キャッシュに既にある場合はそれを返す
        if (profileImages.has(id)) {
            return profileImages.get(id);
        }
        
        try {
            console.log(`Fetching profile for user: ${id}`); // デバッグ用
            const response = await apiClient.get(`/users/profile/${id}`);
            console.log(`Profile response:`, response); // デバッグ用
            const pfp = response.pfp;
            // キャッシュに保存
            profileImages.set(id, pfp);
            return pfp;
        } catch (error) {
            console.error(`Error fetching profile for user ${id}:`, error);
            // エラーの場合はデフォルト画像のパスを返す
            return null;
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

    function insertDateNotifications(messageList) {
        if (messageList.length === 0) return messageList;
        
        // メッセージを時系列順（古い順）にソート
        const sortedMessages = [...messageList].sort((a, b) => {
            const timeA = new Date(a.created_at || a.timestamp);
            const timeB = new Date(b.created_at || b.timestamp);
            return timeA - timeB; // 古い順
        });
        
        const result = [];
        let lastDate = null;
        
        for (let i = 0; i < sortedMessages.length; i++) {
            const message = sortedMessages[i];
            const messageDate = new Date(message.created_at || message.timestamp);
            const currentDateString = messageDate.toLocaleDateString('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
            
            // 日付が変わった場合、または最初のメッセージの場合
            if (lastDate === null || lastDate !== currentDateString) {
                // 日付通知を挿入
                const dateNotification = {
                    id: `date-${messageDate.getTime()}`,
                    content: currentDateString,
                    user: 'System',
                    created_at: message.created_at || message.timestamp,
                    timestamp: message.created_at || message.timestamp,
                    type: 'date',
                    isOwn: false,
                    isNotification: true,
                    isDateNotification: true
                };
                
                result.push(dateNotification);
                lastDate = currentDateString;
            }
            
            result.push(message);
        }
        
        return result;
    }

    function handleMessageAction(action, message) {
        if (onMessageAction) {
            onMessageAction(action, message);
        }
    }

    async function handleLoadMore() {
        if (loadMoreMessages && hasNextPage) {
            await loadMoreMessages();
        }
    }

    function getMessageUserIcon(message) {
        if (getUserIcon) {
            return getUserIcon(message.user || message);
        }
        // メッセージオブジェクトに直接アイコン情報がある場合
        if (message.userIcon) {
            return message.userIcon;
        }
        // ユーザーオブジェクトにアイコン情報がある場合
        if (message.user && message.user.icon) {
            return message.user.icon;
        }
        // デフォルトのユーザーアイコン
        return User;
    }

    function getMessageUserBadge(message) {
        // メッセージオブジェクトに直接バッジ情報がある場合
        if (message.userBadge) {
            return message.userBadge;
        }
        // ユーザーオブジェクトにバッジ情報がある場合
        if (message.user && message.user.badge) {
            return message.user.badge;
        }
        return null;
    }

    // ユーザーIDを取得する関数
    function getUserId(message) {
        console.log('getUserId called with message:', message); // デバッグ用
        
        // メッセージのsent_byフィールドに基づいてユーザーIDを判定
        if (message.sent_by === 'target_user') {
            // 相手ユーザーのメッセージの場合
            console.log('Message is from target_user, using targetUserId:', targetUserId); // デバッグ用
            return targetUserId;
        } else if (message.sent_by === 'request_user') {
            // 自分のメッセージの場合
            console.log('Message is from request_user, using currentUser:', currentUser); // デバッグ用
            console.log('currentUser.user:', currentUser?.user); // デバッグ用
            return currentUser?.user?.id || currentUser?.user?.user_id;
        }
        
        // フォールバック: 古い形式のメッセージに対応
        if (message.user?.id) return message.user.id;
        if (message.user?.user_id) return message.user.user_id;
        if (message.sender?.id) return message.sender.id;
        if (message.sender?.user_id) return message.sender.user_id;
        
        console.log('No user ID found for message'); // デバッグ用
        return null;
    }

    // 処理されたメッセージ（日付通知を含む）
    let processedMessages = $derived.by(() => {
        console.log('Processing messages:', messages); // デバッグ用
        console.log('targetUserId:', targetUserId); // デバッグ用
        console.log('currentUser:', currentUser); // デバッグ用
        console.log('currentUser.user:', currentUser?.user); // デバッグ用
        console.log('currentUser.user.id:', currentUser?.user?.id); // デバッグ用
        console.log('currentUser.user.user_id:', currentUser?.user?.user_id); // デバッグ用
        console.log('targetUser:', targetUser); // デバッグ用
        console.log('targetUser.display_name:', targetUser?.display_name); // デバッグ用
        console.log('targetUser.user_username:', targetUser?.user_username); // デバッグ用
        return insertDateNotifications(messages);
    });
</script>

    <div class="flex-1 overflow-y-auto space-y-2 p-4 h-full" bind:this={messagesContainer}>
        {#if loading && messages.length === 0}
            <div class="flex justify-center items-center h-64">
                <div class="text-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p class="text-gray-600">読み込み中...</p>
                </div>
            </div>
        {:else if processedMessages.length === 0}
            <div class="flex justify-center items-center h-64">
                <div class="text-center">
                    <p class="text-gray-500">メッセージがありません</p>
                </div>
            </div>
        {:else}
            <!-- もっと読み込むボタン -->
            {#if hasNextPage}
                <div class="flex justify-center py-4">
                    <Button 
                        color="light" 
                        size="sm"
                        disabled={loading}
                        onclick={handleLoadMore}
                    >
                        {#if loading}
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500 mr-2"></div>
                            読み込み中...
                        {:else}
                            過去のメッセージを読み込む
                        {/if}
                    </Button>
                </div>
            {/if}
            
            {#each processedMessages as message, index (message.id)}
                {@const shouldShowTime = (() => {
                    if (index === 0) return true;
                    
                    const currentTime = new Date(message.created_at || message.timestamp);
                    const prevMessage = processedMessages[index - 1];
                    const prevTime = new Date(prevMessage.created_at || prevMessage.timestamp);
                    
                    // 時間差が5分以上の場合は常に表示
                    const timeDiff = currentTime - prevTime;
                    if (timeDiff >= 300000) return true;
                    
                    // 送信者が異なる場合は表示
                    const currentSender = message.isOwn ? 'own' : message.isNotification ? 'notification' : (message.user?.username || message.user);
                    const prevSender = prevMessage.isOwn ? 'own' : prevMessage.isNotification ? 'notification' : (prevMessage.user?.username || prevMessage.user);
                    
                    return currentSender !== prevSender;
                })()}
                {@const shouldShowUserInfo = (() => {
                    // 通知の場合は常にfalse（アイコンと名前は表示しない）
                    if (message.isNotification) return false;
                    
                    // 自分のメッセージの場合は常にfalse（アイコンと名前は表示しない）
                    if (message.isOwn || message.sent_by === 'request_user') return false;
                    
                    // 最初のメッセージの場合は常に表示
                    if (index === 0) return true;
                    
                    const prevMessage = processedMessages[index - 1];
                    
                    // 前のメッセージが自分のメッセージまたは通知の場合は表示
                    if (prevMessage.isOwn || prevMessage.sent_by === 'request_user' || prevMessage.isNotification) return true;
                    
                    const currentTime = new Date(message.created_at || message.timestamp);
                    const prevTime = new Date(prevMessage.created_at || prevMessage.timestamp);
                    const timeDiff = currentTime - prevTime;
                    
                    // 時間差が5分以上の場合は表示
                    if (timeDiff >= 300000) return true;
                    
                    // 送信者が異なる場合は表示
                    const currentSender = message.user?.username || message.user;
                    const prevSender = prevMessage.user?.username || prevMessage.user;
                    
                    return currentSender !== prevSender;
                })()}
                {@const userIcon = getMessageUserIcon(message)}
                {@const userBadge = getMessageUserBadge(message)}
                {@const userId = getUserId(message)}
                {@const debugInfo = console.log('Displaying user icon for message:', message, 'userId:', userId)}
                
                <!-- 通知の場合は中央表示 -->
                {#if message.isNotification}
                    <div class="flex justify-center group">
                        {#if message.isDateNotification}
                            <!-- 日付通知 -->
                            <Badge border color="gray" class="flex items-center gap-2 px-2 py-1 rounded-full text-xs font-medium border-gray-300 bg-white text-gray-500 select-none">
                                <span>{message.content}</span>
                            </Badge>
                        {:else}
                            <!-- 通常の通知 -->
                            <Badge border color="gray" class="flex items-center gap-2 px-2 py-1 rounded-full text-xs font-medium border-gray-300 bg-white text-gray-500 select-none">
                                <Info class="w-3 h-3" />
                                <span>{message.content}</span>
                                {#if shouldShowTime}
                                    <span class="text-gray-500 flex items-center gap-1">
                                        <Clock class="w-3 h-3" />
                                        {formatTime(message.created_at || message.timestamp)}
                                    </span>
                                {/if}
                            </Badge>
                        {/if}
                    </div>
                {:else}
                    <!-- 通常のメッセージ表示 -->
                    <div class="flex {(message.isOwn || message.sent_by === 'request_user') ? 'justify-end' : 'justify-start'} group gap-2">
                        <div class="flex flex-col {(message.isOwn || message.sent_by === 'request_user') ? 'items-end' : 'items-start'} max-w-sm lg:max-w-md">
                            {#if !(message.isOwn || message.sent_by === 'request_user') && shouldShowUserInfo && showUserInfo}
                                <div class="flex items-center gap-2 mb-1 ml-10">
                                    <span class="text-xs font-medium text-gray-700">
                                        {#if message.sent_by === 'target_user'}
                                            {targetUser?.display_name || targetUser?.user_username || `User ${targetUserId?.slice(0, 8)}...`}
                                        {:else if message.sent_by === 'request_user'}
                                            {currentUser?.user?.display_name || currentUser?.user?.user_username || 'You'}
                                        {:else}
                                            {message.user?.username || message.user || message.sender?.user_username || message.sender || 'Unknown'}
                                        {/if}
                                    </span>
                                    {#if userBadge}
                                        <svelte:component this={userBadge} class="w-3 h-3 text-yellow-500" />
                                    {/if}
                                    {#if shouldShowTime}
                                        <span class="text-xs text-gray-500">
                                            {formatTime(message.created_at || message.timestamp)}
                                        </span>
                                    {/if}
                                </div>
                            {:else if (message.isOwn || message.sent_by === 'request_user') && shouldShowTime}
                                <span class="text-xs text-gray-500 mb-1">
                                    {formatTime(message.created_at || message.timestamp)}
                                </span>
                            {/if}
                            
                            <div class="flex items-center gap-2 relative">
                                {#if !(message.isOwn || message.sent_by === 'request_user') && showUserInfo}
                                    <div class="flex flex-col items-center">
                                        {#if shouldShowUserInfo}
                                            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden">
                                                {#await getPfpFromId(userId)}
                                                    <div class="w-8 h-8 bg-blue-100 animate-pulse"></div>
                                                {:then pfp}
                                                    {#if pfp}
                                                        <img src={getMediaURL(pfp)} alt={message.user?.username || message.user || 'User'} class="w-8 h-8 object-cover" />
                                                    {:else}
                                                        <svelte:component this={userIcon} class="w-4 h-4 text-blue-600" />
                                                    {/if}
                                                {:catch}
                                                    <svelte:component this={userIcon} class="w-4 h-4 text-blue-600" />
                                                {/await}
                                            </div>
                                        {:else}
                                            <!-- アイコンのスペースを確保 -->
                                            <div class="w-8 h-8 flex-shrink-0"></div>
                                        {/if}
                                    </div>
                                {/if}
                                
                                <div class="
                                    {(message.isOwn || message.sent_by === 'request_user')
                                        ? 'bg-blue-500 text-white rounded-sm' 
                                        : 'bg-white text-gray-800 rounded-sm border border-gray-200'
                                    } 
                                    px-4 py-2 max-w-full break-words
                                ">
                                    <p class="text-sm whitespace-pre-wrap">{message.content}</p>
                                </div>
                                
                                <!-- メッセージアクション -->
                                {#if allowActions}
                                    <div class="opacity-0 group-hover:opacity-100 transition-opacity">
                                        <Dropdown placement="right-start" triggeredBy="#message-actions-{message.id}" simple={true}>
                                            <DropdownItem class="hover:cursor-pointer w-full flex items-center" onclick={() => handleMessageAction('reply', message)}>
                                                <Reply class="w-4 h-4 mr-2" />返信
                                            </DropdownItem>
                                            <DropdownItem class="hover:cursor-pointer w-full flex items-center" onclick={() => handleMessageAction('copy', message)}>
                                                <Copy class="w-4 h-4 mr-2" />コピー
                                            </DropdownItem>
                                            {#if (message.isOwn || message.sent_by === 'request_user') || (currentUser && currentUser.is_admin)}
                                                <DropdownDivider />
                                                <DropdownItem class="hover:cursor-pointer w-full flex items-center" onclick={() => handleMessageAction('edit', message)}>
                                                    <Edit class="w-4 h-4 mr-2" />編集
                                                </DropdownItem>
                                                <DropdownItem class="hover:cursor-pointer w-full flex items-center" onclick={() => handleMessageAction('delete', message)}>
                                                    <Trash2 class="w-4 h-4 mr-2" />削除
                                                </DropdownItem>
                                            {/if}
                                        </Dropdown>
                                        <button 
                                            id="message-actions-{message.id}"
                                            class="p-1 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors hover:cursor-pointer"
                                        >
                                            <MoreVertical class="w-4 h-4" />
                                        </button>
                                    </div>
                                {/if}
                            </div>
                        </div>
                    </div>
                {/if}
            {/each}
            
            <!-- タイピング中のユーザー表示 -->
            {#if typingUsers.size > 0}
                <div class="flex justify-start">
                    <div class="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
                        <div class="flex space-x-1">
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                            <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        </div>
                        <span class="text-sm text-gray-600">
                            {Array.from(typingUsers).join(', ')}が入力中...
                        </span>
                    </div>
                </div>
            {/if}
        {/if}
    </div>
