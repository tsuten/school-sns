<script>
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    import { Calendar, MapPin, LinkIcon, Camera, Edit3, Save, MoreVertical, Cake, AlertTriangle, Trash2, Siren, User } from 'lucide-svelte';
    import { Button, Dropdown, DropdownItem } from 'flowbite-svelte';
    import { apiClient, getMediaURL } from '$lib/services/django';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { dateNormalize } from '$lib/utils/datetimeNormalize';
    import { browser } from '$app/environment';
    import DateBadge from '$lib/components/badge/dateBadge.svelte';
    import { theme } from '$lib/theme.js';
    
    let isEditing = $state(false);
    let isLoading = $state(false);
    let error = $state(null);
    
    let { user } = $props();

    onMount(() => {
        if (browser && user?.id) {
            fetchUser();
        }
    });

    async function fetchUser() {
        if (!browser) return;
        
        try {
            isLoading = true;
            error = null;
            const response = await apiClient.get(`/users/profile/${user.id}`);
            user = response;
        } catch (err) {
            console.error('Error fetching user profile:', err);
            error = 'ユーザー情報の取得に失敗しました';
        } finally {
            isLoading = false;
        }
    }

    // プロフィール画像のURL処理（サーバーサイドレンダリング時は安全にアクセス）
    const profileImageUrl = $derived(
        browser && user?.pfp ? 
            (user.pfp.startsWith('http') ? user.pfp : getMediaURL(user.pfp)) : 
            null
    );

    // ユーザー名の処理（複数の形式に対応）
    const username = $derived(user?.user_username || user?.username);

    // ダミー関数（何もしない）
    function handleAvatarChange() {
        console.log("アバター変更（ダミー）");
    }

    function toggleEdit() {
        isEditing = !isEditing;
        console.log("編集モード切り替え（ダミー）");
    }

    function cancelEdit() {
        isEditing = false;
        console.log("編集キャンセル（ダミー）");
    }
</script>

{#if isLoading}
    <BaseCard>
        <div class="flex items-center justify-center p-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <span class="ml-2 {$theme.text.tertiary}">読み込み中...</span>
        </div>
    </BaseCard>
{:else if error}
    <BaseCard>
        <div class="flex items-center justify-center p-8 text-red-600">
            <AlertTriangle class="w-5 h-5 mr-2" />
            <span>{error}</span>
        </div>
    </BaseCard>
{:else if user}
    <BaseCard>
        <div class="flex flex-col md:flex-row items-start md:items-center gap-6">
            <!-- プロフィール画像 -->
            <div class="relative">
                {#if profileImageUrl}
                    <img 
                        src={profileImageUrl} 
                        alt="プロフィール画像" 
                        class="w-24 h-24 rounded-full object-cover border-4 {$theme.border.secondary}"
                        onerror={() => {
                            console.error('Failed to load profile image:', profileImageUrl);
                        }}
                    />
                {:else}
                    <div class="w-24 h-24 rounded-full {$theme.tertiary} flex items-center justify-center border-4 {$theme.border.secondary}">
                        <User class="w-12 h-12 {$theme.text.quinary}" />
                    </div>
                {/if}
            </div>

            <!-- 基本情報 -->
            <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                    <h2 class="text-2xl font-bold {$theme.text.primary}">{user.display_name || username || 'ユーザー'}</h2>
                    {#if username}
                        <span class="{$theme.text.tertiary}">@{username}</span>
                    {/if}
                </div>
                {#if user.bio}
                    <p class="whitespace-pre-wrap line-clamp-3 {$theme.text.secondary}">{user.bio}</p>
                {/if}
                
                <!-- メタ情報 -->
                <div class="flex flex-wrap gap-4 mt-3 text-sm {$theme.text.tertiary}">
                    {#if user.created_at && dateNormalize(user.created_at)}
                        <div class="flex items-center gap-1">
                            参加日: <DateBadge date={user.created_at} />
                        </div>
                    {/if}
                    {#if user.birthday && dateNormalize(user.birthday)}
                        <div class="flex items-center gap-1">
                            <Cake class="w-4 h-4" />
                            {dateNormalize(user.birthday)}
                        </div>
                    {/if}
                    {#if user.location}
                        <div class="flex items-center gap-1">
                            <MapPin class="w-4 h-4" />
                            {user.location}
                        </div>
                    {/if}
                    {#if user.website}
                        <div class="flex items-center gap-1">
                            <LinkIcon class="w-4 h-4" />
                            <a href={user.website} class="text-blue-600 hover:underline" target="_blank">
                                ウェブサイト
                            </a>
                        </div>
                    {/if}
                </div>
            </div>

            <!-- 編集ボタン -->
            <!--
            <div class="flex gap-2 justify-start items-start">
                <Button color="light" size="xs" class="p-1 hover:cursor-pointer">
                    <MoreVertical class="w-4 h-4" />
                </Button>
                <Dropdown placement="bottom-end" simple>
                    <DropdownItem onclick={() => console.log('通報しました')} class="w-full hover:cursor-pointer flex items-center gap-2">
                        <Siren class="w-4 h-4" />
                        <span>通報する</span>
                    </DropdownItem>
                </Dropdown>
            </div>
            -->
        </div>
    </BaseCard>
{:else}
    <BaseCard>
        <div class="flex items-center justify-center p-8 {$theme.text.tertiary}">
            <User class="w-8 h-8 mr-2" />
            <span>ユーザー情報がありません</span>
        </div>
    </BaseCard>
{/if}