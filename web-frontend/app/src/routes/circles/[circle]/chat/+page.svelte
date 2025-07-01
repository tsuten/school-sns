<script>
    import { Send, ArrowLeft, MoreVertical, Smile, Paperclip, Crown, User, Settings, UserMinus, Flag, Info, Reply, Copy, Trash2, Edit, Clock } from 'lucide-svelte';
    import { Button, Badge, Card, Dropdown, DropdownItem, DropdownDivider} from 'flowbite-svelte';
    import { apiClient } from '$lib/services/django';
    import { page } from '$app/stores';
    import { userInfo } from '$lib/stores/userInfo';
    import Input from '$lib/components/utils/chat/input.svelte';
    import { goto } from '$app/navigation';
    import { onMount, onDestroy } from 'svelte';
    import toast from '$lib/utils/toast.js';
    import socketClient from '$lib/services/socket.js';
    import { browser } from '$app/environment';
    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let circle = $state(null);
    let loading = $state(true);
    let messageInput = $state('');
    let messagesContainer;
    let webSocket = $state(null);
    let onlineUsers = $state(new Set());
    let typingUsers = $state(new Set());
    let circleId = $state(null);

    let messages = $state([]);
    let hasNextPage = $state(false);
    let nextUntil = $state(null);
    let loadingMore = $state(false);

    $effect(() => {
        if (browser) {
            circleId = $page.params.circle;
            if (circleId) {
                fetchCircleDetail(circleId);
            }
        }
    });

    onMount(async () => {
        if (browser) {
            const currentCircleId = $page.params.circle;
            circleId = currentCircleId;
            await fetchIsMember(currentCircleId);
            
            // WebSocket接続を初期化
            if (currentCircleId) {
                initWebSocket(currentCircleId);
            }
        }
    });

    onDestroy(() => {
        // コンポーネント破棄時にWebSocket接続を切断
        if (browser && circleId) {
            socketClient.disconnectFromCircleChat(circleId);
        }
    });

    async function fetchIsMember(circleId) {
        try {
            const response = await apiClient.get(`/circle/${circleId}/is-member`);
            if (!response.is_member) {
                toast.error('あなたはこのサークルのメンバーではありません');
                goto(`/circles/${circleId}`);
            }
        } catch (error) {
            toast.error('メンバーシップの確認に失敗しました');
            goto(`/circles/${circleId}`);
        }
    }

    $effect(() => {
        // メッセージが更新されたら自動スクロール（最下部へ）
        if (messagesContainer && messages.length > 0) {
            // 少し遅延させてDOMの更新を待つ
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 10);
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

    async function fetchMessages(circleId, until = null, append = false) {
        try {
            if (!append) {
                loading = true;
            } else {
                loadingMore = true;
            }
            
            let url = `/circle/${circleId}/activity`;
            if (until) {
                url += `?until=${encodeURIComponent(until)}`;
            }
            
            const response = await apiClient.get(url);
            console.log('Activity response:', response);
            
            // 現在のユーザー名とIDを取得
            const currentUsername = $userInfo.username;
            const currentUserId = $userInfo.id;
            console.log('Current user:', currentUsername, currentUserId);
            
            // アクティビティを処理（メッセージと通知を含む）
            const newMessages = response.activities.map(activity => ({
                id: activity.id,
                content: activity.content,
                user: activity.username || activity.user,
                created_at: activity.timestamp,
                timestamp: activity.timestamp,
                type: activity.type, // 'message' または 'notification'
                isOwn: activity.type === 'message' && (activity.user_id === currentUserId || activity.username === currentUsername),
                isNotification: activity.type === 'notification'
            }));
            
            if (append) {
                // 重複チェックして追加
                const currentMessages = messages.filter(msg => !msg.isDateNotification);
                const existingIds = new Set(currentMessages.map(msg => msg.id));
                const uniqueNewMessages = newMessages.filter(msg => !existingIds.has(msg.id));
                const allMessages = [...currentMessages, ...uniqueNewMessages];
                messages = insertDateNotifications(allMessages);
            } else {
                messages = insertDateNotifications(newMessages);
            }
            
            // ページネーション情報を更新
            hasNextPage = response.has_next;
            nextUntil = response.next_until;
            
            console.log('Processed messages:', messages);
            console.log('Has next page:', hasNextPage, 'Next until:', nextUntil);
        } catch (err) {
            console.error('Error fetching activity:', err);
            if (!append) {
                messages = [];
            }
        } finally {
            loading = false;
            loadingMore = false;
        }
    }

    async function loadMoreMessages() {
        if (hasNextPage && !loadingMore && nextUntil) {
            await fetchMessages(circleId, nextUntil, true);
        }
    }

    $effect(() => {
        if (circle) {
            fetchMessages(circle.id);
        }
    });

    function initWebSocket(circleId) {
        console.log('Initializing WebSocket for circle:', circleId);
        
        webSocket = socketClient.connectToCircleChat(circleId, {
            onOpen: () => {
                console.log('WebSocket connected to circle chat');
                toast.success('チャットに接続しました');
            },
            
            onMessage: (data) => {
                console.log('Received message via WebSocket:', data);
                
                // 新しいメッセージを追加
                const newMessage = {
                    id: data.message_id,
                    content: data.message,
                    user: data.username,
                    created_at: data.timestamp,
                    type: 'message',
                    isOwn: data.user_id === $userInfo.id,
                    isNotification: false
                };
                
                // 重複チェック（同じIDのメッセージが既に存在しないか）
                const existingMessage = messages.find(msg => msg.id === newMessage.id);
                if (!existingMessage) {
                    // 日付通知以外のメッセージのみを取得
                    const currentMessages = messages.filter(msg => !msg.isDateNotification);
                    const updatedMessages = [...currentMessages, newMessage];
                    messages = insertDateNotifications(updatedMessages);
                }
            },
            
            onUserJoined: (data) => {
                console.log('User joined:', data);
                onlineUsers.add(data.username);
                onlineUsers = new Set(onlineUsers); // リアクティブ更新のため
                
                // 自分以外のユーザー参加を通知
                if (data.user_id !== $userInfo.id) {
                    toast.info(`${data.username}さんがチャットに参加しました`);
                }
            },
            
            onUserLeft: (data) => {
                console.log('User left:', data);
                onlineUsers.delete(data.username);
                onlineUsers = new Set(onlineUsers); // リアクティブ更新のため
                
                // 自分以外のユーザー退出を通知
                if (data.user_id !== $userInfo.id) {
                    toast.info(`${data.username}さんがチャットから退出しました`);
                }
            },
            
            onUserTyping: (data) => {
                console.log('User typing:', data);
                typingUsers.add(data.username);
                typingUsers = new Set(typingUsers); // リアクティブ更新のため
            },
            
            onUserStopTyping: (data) => {
                console.log('User stopped typing:', data);
                typingUsers.delete(data.username);
                typingUsers = new Set(typingUsers); // リアクティブ更新のため
            },
            
            onClose: () => {
                console.log('WebSocket disconnected from circle chat');
                toast.warning('チャットから切断されました');
            },
            
            onError: (error) => {
                console.error('WebSocket error:', error);
                toast.error('チャット接続でエラーが発生しました');
            }
        });
    }

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
</script>

{#if loading}
    <div class="flex justify-center items-center h-64">
        <div class="text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p class="text-gray-600">読み込み中...</p>
        </div>
    </div>
{:else if circle}
    <div class="flex flex-col h-screen">
        <!-- ヘッダー -->
        <div class="bg-white border-b border-gray-300 px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <a href="/circles/{circleId}">
                    <Button pill={true} color="light" class="p-2! hover:cursor-pointer">
                        <ArrowLeft class="h-5 w-5 text-gray-500" />
                    </Button>
                </a>
                <div>
                    <h1 class="text-lg font-bold text-gray-800">{circle.name}</h1>
                    <div class="flex items-center gap-2 text-sm text-gray-600">
                        <span>{circle.members.length} メンバー</span>
                        {#if onlineUsers.size > 0}
                            <span class="text-green-600">• {onlineUsers.size} オンライン</span>
                        {/if}
                    </div>
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
        <div class="flex-1 overflow-y-auto space-y-2 p-4" bind:this={messagesContainer}>
            <!-- もっと読み込むボタン -->
            {#if hasNextPage}
                <div class="flex justify-center py-4">
                    <Button 
                        color="light" 
                        size="sm"
                        disabled={loadingMore}
                        onclick={loadMoreMessages}
                    >
                        {#if loadingMore}
                            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-500 mr-2"></div>
                            読み込み中...
                        {:else}
                            過去のメッセージを読み込む
                        {/if}
                    </Button>
                </div>
            {/if}
            
            {#each messages as message, index (message.id)}
                {@const shouldShowTime = (() => {
                    if (index === 0) return true;
                    
                    const currentTime = new Date(message.created_at || message.timestamp);
                    const prevMessage = messages[index - 1];
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
                    if (message.isOwn) return false;
                    
                    // 最初のメッセージの場合は常に表示
                    if (index === 0) return true;
                    
                    const prevMessage = messages[index - 1];
                    
                    // 前のメッセージが自分のメッセージまたは通知の場合は表示
                    if (prevMessage.isOwn || prevMessage.isNotification) return true;
                    
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
                    <div class="flex {message.isOwn ? 'justify-end' : 'justify-start'} group gap-2">
                        <div class="flex flex-col {message.isOwn ? 'items-end' : 'items-start'} max-w-sm lg:max-w-md">
                        {#if !message.isOwn && shouldShowUserInfo}
                            <div class="flex items-center gap-2 mb-1 ml-10">
                                <a href="/profile/{message.user?.id}" class="hover:underline">
                                    <span class="text-xs font-medium text-gray-700">{message.user?.username || message.user || 'Unknown'}</span>
                                </a>
                                {#if (message.user?.username || message.user) === circle.founder.username}
                                    <Crown class="w-3 h-3 text-yellow-500" />
                                {/if}
                                {#if shouldShowTime}
                                    <span class="text-xs text-gray-500">
                                        {formatTime(message.created_at || message.timestamp)}
                                    </span>
                                {/if}
                            </div>
                        {:else if message.isOwn && shouldShowTime}
                            <span class="text-xs text-gray-500 mb-1">
                                {formatTime(message.created_at || message.timestamp)}
                            </span>
                        {/if}
                        
                        <div class="flex items-center gap-2">
                            {#if !message.isOwn}
                                <div class="flex flex-col items-center">
                                    {#if shouldShowUserInfo}
                                        <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                            {#if (message.user?.username || message.user) === circle.founder.username}
                                                <Crown class="w-4 h-4 text-yellow-600" />
                                            {:else}
                                                <User class="w-4 h-4 text-blue-600" />
                                            {/if}
                                        </div>
                                    {:else}
                                        <!-- アイコンのスペースを確保 -->
                                        <div class="w-8 h-8 flex-shrink-0"></div>
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

