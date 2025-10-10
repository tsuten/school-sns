<script>
    import { Button, Avatar } from 'flowbite-svelte';
    import { User } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { apiClient, getMediaURL } from '$lib/services/django.js';
    import { page } from '$app/stores';
    import InPageSideBar from "$lib/components/page-components/inPageSideBar.svelte";

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

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
            const response = await apiClient.get('/pm/users-have-history-with-user');
            users = response.data.users || [];
        } catch (err) {
            console.error('ユーザーリストの取得に失敗しました:', err);
            error = 'ユーザーリストの読み込みに失敗しました。';
            users = [];
        } finally {
            isLoading = false;
        }
    }

    // コンポーネントマウント時にユーザーリストを読み込み
    onMount(() => {
        loadUsers();
    });
</script>

<div class="flex flex-row h-full w-full">
    <InPageSideBar is_fixed={true}>
        <div class="flex flex-col">
                {#each users as user}
                    <div class="group flex flex-col p-3 border-b border-gray-200 hover:bg-blue-50 cursor-pointer transition-colors duration-200"
                         role="button"
                         tabindex="0"
                         onclick={() => goto(`/app/messages/${user.user_id}`)}
                         onkeydown={(e) => e.key === 'Enter' && goto(`/app/messages/${user.user_id}`)}>
                        <div class="flex items-start gap-3">
                            <!-- ユーザーアイコン -->
                            <div class="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden {$page.params.user === user.user_id ? 'ring-2 ring-blue-300' : ''}">
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
                            <div class="flex-1 min-w-0 duration-300 overflow-hidden">
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
        </div>
    </InPageSideBar>
    
    <!-- メインコンテンツエリア -->
    <div class="flex flex-col h-full w-full">
        {@render children()}
    </div>
</div> 