<script>
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    import { Calendar, MapPin, LinkIcon, Camera, Edit3, Save, MoreVertical, Cake, AlertTriangle, Trash2, Siren } from 'lucide-svelte';
    import { Button, Dropdown, DropdownItem } from 'flowbite-svelte';
    import { apiClient } from '$lib/services/django';
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { dateNormalize } from '$lib/utils/datetimeNormalize';
    let isEditing = $state(false);
    
    let user = $state([]);
    const userId = $page.params.user;

    onMount(() => {
        fetchUser();
    });

    async function fetchUser() {
        const response = await apiClient.get(`/users/profile/${userId}`);
        user = response;
        console.log(user);
    }
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

<BaseCard>
    <div class="flex flex-col md:flex-row items-start md:items-center gap-6">
        <!-- プロフィール画像 -->
        <div class="relative">
            <img 
                src={`http://localhost:8000${user.pfp}`} 
                alt="プロフィール画像" 
                class="w-24 h-24 rounded-full object-cover border-4 border-gray-100"
            >
        </div>

        <!-- 基本情報 -->
        <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
                <h2 class="text-2xl font-bold text-gray-900">{user.display_name}</h2>
                <span class="text-gray-500">@{user.user_username}</span>
            </div>
            <p class="text-gray-600 whitespace-pre-wrap line-clamp-3">{user.bio}</p>
            
            <!-- メタ情報 -->
            <div class="flex flex-wrap gap-4 mt-3 text-sm text-gray-500">
                {#if user.created_at && dateNormalize(user.created_at)}
                    <div class="flex items-center gap-1">
                        <Calendar class="w-4 h-4" />
                        {dateNormalize(user.created_at)}に参加
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
    </div>
</BaseCard>