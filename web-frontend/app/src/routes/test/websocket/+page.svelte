<!-- Authenticated Circle Chat Test Page -->
<script>
  import { onMount, onDestroy } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import chatStore, { 
    isChatConnected, 
    isChatConnecting, 
    hasChatError,
    chatMessages, 
    onlineUsers,
    typingUsers,
    typingUsernames,
    chatErrors 
  } from '$lib/stores/chatStore.js';
  import { userInfo, setUserInfo } from '$lib/stores/userInfo.js';
  import { isAuthenticated } from '$lib/stores/auth.js';

  // レスポンシブ表示制御
  let showSidebar = true;
  let isMobile = false;
  let chatMessage = '';
  let typingTimeout = null;
  let messagesContainer;
  let autoConnect = false;

  // 認証状態とユーザー情報の管理
  let authChecked = false;
  let authInitialized = false;
  
  // 初期化時の認証状態保護
  $: if (browser && !authInitialized && $page.data) {
    console.log('[WebSocket Page] Initializing auth state protection');
    
    // ページデータが認証済みの場合、認証ストアの不適切な変更を防ぐ
    if ($page.data.authenticated === true && $page.data.user) {
      console.log('[WebSocket Page] Page data shows authenticated user, preventing auth store changes');
      
      // ユーザー情報を設定
      setUserInfo($page.data.user);
      
      // 認証ストアを明示的にtrueに設定（cookie削除を防ぐ）
      isAuthenticated.set(true);
      
      authInitialized = true;
      authChecked = true;
    } else if ($page.data.authenticated === false) {
      console.log('[WebSocket Page] Page data shows unauthenticated, allowing normal flow');
      authInitialized = true;
    }
  }

  // 認証確認（初期化後のみ実行）
  $: if (browser && authInitialized && !authChecked) {
    if ($page.data?.authenticated === false && !$page.data?.user) {
      console.log('[WebSocket Page] Authentication failed, redirecting to login');
      goto('/login');
    } else if ($page.data?.authenticated === true) {
      console.log('[WebSocket Page] User is authenticated');
      authChecked = true;
    }
  }

  // 認証済みユーザー情報
  $: authenticatedUser = $userInfo.username || $page.data?.user?.user_username;
  $: displayName = $userInfo.display_name || $page.data?.user?.display_name || authenticatedUser;
  
  // デバッグ情報
  $: if (browser) {
    console.log('[WebSocket Page] Auth states:', {
      pageAuthenticated: $page.data?.authenticated,
      hasPageUser: !!$page.data?.user,
      userInfoUsername: $userInfo.username,
      isAuthenticatedStore: $isAuthenticated,
      authenticatedUser,
      authChecked
    });
  }

  // 接続機能
  async function connectToChat() {
    if (!authenticatedUser) {
      console.error('No authenticated user found');
      return;
    }
    
    try {
      console.log('Connecting with authenticated user:', authenticatedUser);
      await chatStore.connect(authenticatedUser);
      console.log('Connection completed, states:', { 
        connected: $isChatConnected, 
        connecting: $isChatConnecting, 
        error: $hasChatError 
      });
    } catch (error) {
      console.error('Connection failed:', error);
    }
  }

  function disconnectFromChat() {
    chatStore.disconnect();
  }

  // メッセージ機能
  function sendMessage() {
    if (chatMessage.trim() && $isChatConnected) {
      chatStore.sendMessage(chatMessage.trim());
      chatMessage = '';
      chatStore.sendStopTyping();
    }
  }

  function handleTyping() {
    if ($isChatConnected && chatMessage.trim()) {
      chatStore.sendTyping();
      
      if (typingTimeout) clearTimeout(typingTimeout);
      typingTimeout = setTimeout(() => {
        chatStore.sendStopTyping();
      }, 2000);
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  // 自動スクロール
  $: if ($chatMessages && messagesContainer && browser) {
    setTimeout(() => {
      if (messagesContainer && messagesContainer.scrollHeight) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 10);
  }

  // レスポンシブ対応
  function handleResize() {
    if (!browser) return;
    isMobile = window.innerWidth < 768;
    if (isMobile) showSidebar = false;
  }

  function toggleSidebar() {
    showSidebar = !showSidebar;
  }

  // 時刻フォーマット
  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('ja-JP', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  // ユーザーアバターの色生成
  function getUserColor(username) {
    const colors = [
      'from-blue-500 to-purple-600',
      'from-green-500 to-teal-600', 
      'from-yellow-500 to-orange-600',
      'from-pink-500 to-red-600',
      'from-indigo-500 to-blue-600',
      'from-purple-500 to-pink-600'
    ];
    const hash = username.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }

  // Cookieトークンチェック関数
  function checkCookieToken() {
    if (!browser) return null;
    
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'access_token') {
        return value;
      }
    }
    return null;
  }

  onMount(() => {
    if (browser) {
      // Cookieの状態を確認
      const cookieToken = checkCookieToken();
      console.log('[WebSocket Page] Initial cookie token:', cookieToken ? 'Present' : 'Missing');
      
      handleResize();
      window.addEventListener('resize', handleResize);
      
      // 認証状態の監視を開始（初期化後のみ）
      let unsubscribeAuth;
      
      // 少し遅延して監視を開始（初期化の競合を避ける）
      setTimeout(() => {
        unsubscribeAuth = isAuthenticated.subscribe((authenticated) => {
          console.log('[WebSocket Page] Auth store changed:', authenticated);
          
          // 認証状態が予期せずfalseになった場合の保護
          if (!authenticated && $page.data?.authenticated === true && authInitialized) {
            console.warn('[WebSocket Page] Unexpected auth state change detected, restoring...');
            // 認証状態を復元
            isAuthenticated.set(true);
          }
        });
      }, 500);
      
      // クリーンアップ関数を保存
      return () => {
        if (unsubscribeAuth) {
          unsubscribeAuth();
        }
      };
    }
    
    // 認証済みユーザーが存在する場合、自動接続を検討
    if (authenticatedUser && autoConnect) {
      setTimeout(connectToChat, 1000);
    }
  });

  onDestroy(() => {
    if (browser) {
      window.removeEventListener('resize', handleResize);
    }
    disconnectFromChat();
    if (typingTimeout) clearTimeout(typingTimeout);
  });
</script>

<svelte:head>
  <title>Circle Chat - {displayName || 'Test'}</title>
</svelte:head>

<div class="h-screen bg-gray-50 flex flex-col">
  
  <!-- ヘッダー -->
  <header class="bg-white shadow-sm border-b border-gray-200 px-4 sm:px-6 py-3 flex-shrink-0">
    <div class="flex items-center justify-between">
      
      <!-- 左側: タイトルとユーザー情報 -->
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-3">
          <!-- ユーザーアバター -->
          <div class="w-10 h-10 rounded-full bg-gradient-to-br {getUserColor(authenticatedUser || 'unknown')} flex items-center justify-center shadow-md">
            <span class="text-white text-sm font-semibold">
              {(displayName || authenticatedUser || 'U').charAt(0).toUpperCase()}
            </span>
          </div>
          
          <div>
            <h1 class="text-lg font-semibold text-gray-900">Circle Chat</h1>
            <p class="text-sm text-gray-600">{displayName || authenticatedUser}</p>
          </div>
        </div>

        <!-- 接続状態 -->
        <div class="hidden sm:flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full {$isChatConnected ? 'bg-green-500' : $isChatConnecting ? 'bg-yellow-500' : 'bg-red-500'}"></div>
          <span class="text-xs text-gray-500">
            {$isChatConnecting ? 'Connecting...' : $isChatConnected ? 'Connected' : 'Disconnected'}
          </span>
          {#if browser}
            <button 
              on:click={() => {
                const token = checkCookieToken();
                console.log('Debug Info:', { 
                  chatStates: { connected: $isChatConnected, connecting: $isChatConnecting, error: $hasChatError },
                  authStates: { 
                    pageAuth: $page.data?.authenticated, 
                    storeAuth: $isAuthenticated, 
                    hasUser: !!$page.data?.user,
                    cookieToken: token ? 'Present' : 'Missing'
                  },
                  userInfo: { username: $userInfo.username, authenticated: $userInfo.authenticated }
                });
              }}
              class="text-xs text-blue-500 hover:text-blue-700"
            >
              Debug
            </button>
            <span class="text-xs text-gray-500">
              Token: {checkCookieToken() ? '✓' : '✗'}
            </span>
          {/if}
        </div>
      </div>

      <!-- 右側: 操作ボタン -->
      <div class="flex items-center space-x-3">
        
        <!-- オンライン数 -->
        {#if $isChatConnected && $onlineUsers.length > 0}
          <span class="hidden sm:inline text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
            {$onlineUsers.length} online
          </span>
        {/if}

        <!-- サイドバー切り替え -->
        <button
          on:click={toggleSidebar}
          class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors md:hidden"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>

                 <!-- トークン状態確認・復元 -->
         {#if browser && !checkCookieToken() && $page.data?.authenticated}
           <button
             on:click={() => {
               // ページデータが認証済みなのにcookieがない場合の復元処理
               console.log('[WebSocket Page] Attempting to restore token from page data');
               if ($page.data?.user) {
                 setUserInfo($page.data.user);
               }
             }}
             class="px-3 py-1 bg-yellow-600 text-white text-xs rounded-lg hover:bg-yellow-700 transition-colors"
           >
             Restore Token
           </button>
         {/if}

         <!-- 接続制御 -->
         {#if !$isChatConnected && !$isChatConnecting}
           <button
             on:click={connectToChat}
             class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
           >
             Connect
           </button>
         {:else if $isChatConnecting}
           <button
             disabled
             class="px-4 py-2 bg-gray-400 text-white text-sm rounded-lg cursor-not-allowed"
           >
             Connecting...
           </button>
         {:else}
           <button
             on:click={disconnectFromChat}
             class="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
           >
             Disconnect
           </button>
         {/if}
      </div>
    </div>

    <!-- モバイル向け接続状態 -->
    <div class="sm:hidden mt-2 flex items-center justify-between">
      <div class="flex items-center space-x-2">
        <div class="w-2 h-2 rounded-full {$isChatConnected ? 'bg-green-500' : $isChatConnecting ? 'bg-yellow-500' : 'bg-red-500'}"></div>
        <span class="text-xs text-gray-500">
          {$isChatConnecting ? 'Connecting...' : $isChatConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      
      {#if $isChatConnected && $onlineUsers.length > 0}
        <span class="text-xs text-gray-500">{$onlineUsers.length} online</span>
      {/if}
    </div>

    <!-- エラー表示 -->
    {#if $chatErrors}
      <div class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800 text-sm">{$chatErrors}</p>
      </div>
    {/if}
  </header>

  <!-- メインコンテンツ -->
  <div class="flex-1 flex overflow-hidden">
    
    <!-- チャットエリア -->
    <main class="flex-1 flex flex-col min-w-0">
      
      <!-- メッセージエリア -->
      <div 
        bind:this={messagesContainer}
        class="flex-1 overflow-y-auto p-4 space-y-4"
      >
        {#if $chatMessages.length === 0}
          <div class="text-center text-gray-500 mt-8">
            <div class="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.99 8.99 0 01-4.7-1.289L3 21l2.3-5.7A7.97 7.97 0 013 12a8 8 0 018-8c4.418 0 8 3.582 8 8z" />
              </svg>
            </div>
            <p class="text-lg font-medium">Welcome to Circle Chat!</p>
            <p class="text-sm mt-1">Connect to start chatting with your circle members</p>
          </div>
        {/if}
        
        {#each $chatMessages as message (message.id)}
          <div class="flex space-x-3 group">
            <div class="flex-shrink-0">
              <div class="w-9 h-9 rounded-full bg-gradient-to-br {getUserColor(message.username)} flex items-center justify-center shadow-sm">
                <span class="text-white text-xs font-semibold">
                  {message.username.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline space-x-2">
                <span class="text-sm font-medium text-gray-900">{message.username}</span>
                <span class="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
              </div>
              <div class="mt-1 bg-white rounded-lg px-3 py-2 shadow-sm border border-gray-100 group-hover:border-gray-200 transition-colors">
                <p class="text-sm text-gray-800 whitespace-pre-wrap">{message.message}</p>
              </div>
            </div>
          </div>
        {/each}
      </div>

      <!-- タイピングインジケーター -->
      {#if $typingUsernames.length > 0}
        <div class="px-4 py-2 border-t bg-gray-50">
          <div class="flex items-center space-x-2">
            <div class="flex space-x-1">
              <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
              <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
              <div class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            </div>
            <span class="text-sm text-gray-600">
              {$typingUsernames.join(', ')} {$typingUsernames.length === 1 ? 'is' : 'are'} typing...
            </span>
          </div>
        </div>
      {/if}

      <!-- メッセージ入力 -->
      <div class="border-t bg-white p-4">
        <div class="flex space-x-3">
          <input
            bind:value={chatMessage}
            on:keypress={handleKeyPress}
            on:input={handleTyping}
            placeholder="Type your message..."
            disabled={!$isChatConnected}
            class="flex-1 px-4 py-3 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
          />
          <button
            on:click={sendMessage}
            disabled={!$isChatConnected || !chatMessage.trim()}
            class="px-6 py-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </main>

    <!-- サイドバー -->
    <aside class="w-64 bg-white border-l border-gray-200 flex-col {showSidebar ? 'flex' : 'hidden'} md:flex">
      
      <!-- オンラインユーザー -->
      <div class="p-4 border-b border-gray-200 flex-1">
        <h3 class="text-sm font-semibold text-gray-900 mb-3 flex items-center">
          <div class="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          Online ({$onlineUsers.length})
        </h3>
        <div class="space-y-2 max-h-48 overflow-y-auto">
          {#each $onlineUsers as user (user.user_id)}
            <div class="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors">
              <div class="w-8 h-8 rounded-full bg-gradient-to-br {getUserColor(user.username)} flex items-center justify-center">
                <span class="text-white text-xs font-semibold">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <span class="text-sm text-gray-700 truncate flex-1">{user.username}</span>
              {#if user.username === authenticatedUser}
                <span class="text-xs text-blue-600 font-medium">You</span>
              {/if}
            </div>
          {:else}
            <div class="text-sm text-gray-500 italic text-center py-4">
              No users online
            </div>
          {/each}
        </div>
      </div>

      <!-- タイピング中のユーザー -->
      {#if $typingUsers.length > 0}
        <div class="p-4 border-b border-gray-200">
          <h3 class="text-sm font-semibold text-gray-900 mb-3 flex items-center">
            <div class="w-2 h-2 bg-yellow-500 rounded-full animate-pulse mr-2"></div>
            Typing...
          </h3>
          <div class="space-y-2">
            {#each $typingUsers as user (user.user_id)}
              <div class="flex items-center space-x-3 p-2">
                <div class="w-6 h-6 rounded-full bg-gradient-to-br {getUserColor(user.username)} flex items-center justify-center">
                  <span class="text-white text-xs">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span class="text-sm text-gray-700">{user.username}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <!-- 統計 -->
      <div class="p-4 mt-auto">
        <h3 class="text-sm font-semibold text-gray-900 mb-3">Chat Stats</h3>
        <div class="space-y-2 text-sm text-gray-600">
          <div class="flex justify-between">
            <span>Messages:</span>
            <span class="font-medium">{$chatMessages.length}</span>
          </div>
          <div class="flex justify-between">
            <span>Online:</span>
            <span class="font-medium">{$onlineUsers.length}</span>
          </div>
          {#if $typingUsers.length > 0}
            <div class="flex justify-between">
              <span>Typing:</span>
              <span class="font-medium">{$typingUsers.length}</span>
            </div>
          {/if}
        </div>
      </div>
    </aside>
  </div>
</div>

<!-- モバイル サイドバー オーバーレイ -->
{#if showSidebar && isMobile}
  <div 
    class="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
    on:click={toggleSidebar}
  ></div>
{/if}