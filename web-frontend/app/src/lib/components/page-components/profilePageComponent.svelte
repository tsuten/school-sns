<script>
    import { apiClient, getMediaURL } from '$lib/services/django';
    import { onMount } from 'svelte';
    import { User, Calendar, MapPin, School } from 'lucide-svelte';
    import DateBadge from '$lib/components/badge/dateBadge.svelte';
    
    let { user } = $props();
    let userProfile = $state(null);

    onMount(() => {
        fetchUser();
    });

    async function fetchUser() {
        const response = await apiClient.get(`/users/profile/${user.user_id}`);
        userProfile = response;
        console.log(userProfile);
    }

    // ヘルパー関数
    function getProfileImage(user) {
        return user?.pfp ? getMediaURL(user.pfp) : null;
    }

    function getDisplayName(user) {
        return user?.display_name || user?.user_username || "Unknown User";
    }

</script>

<div class="w-full h-full">
    {#if userProfile}
        <!-- プロフィールヘッダー -->
        <div class="relative w-full border-b border-gray-300 h-full">
            <!-- バナー背景 -->
            <div class="h-48 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 w-full">
                <!-- バナー画像があれば表示 -->
                <!-- <img src={getBannerImage(userProfile)} alt="Banner" class="w-full h-full object-cover" /> -->
            </div>
            
            <!-- プロフィール情報エリア -->
            <div class="relative px-6 pb-6">
                <!-- プロフィールアイコン（バナーに重なる位置・中央） -->
                <div class="absolute -top-16 left-1/2 transform -translate-x-1/2">
                    <div class="w-32 h-32 rounded-full border-5 border-white bg-white overflow-hidden">
                        {#if getProfileImage(userProfile)}
                            <img 
                                src={getProfileImage(userProfile)} 
                                alt={getDisplayName(userProfile)}
                                class="w-full h-full object-cover"
                            />
                        {:else}
                            <div class="w-full h-full bg-gray-200 flex items-center justify-center">
                                <User class="w-16 h-16 text-gray-400" />
                            </div>
                        {/if}
                    </div>
                </div>
                
                <!-- ユーザー情報 -->
                <div class="pt-18">
                    <div class="flex justify-between items-start">
                        <div class="flex-1">
                            <!-- 名前とユーザー名（中央寄せ） -->
                            <div class="text-center mb-4">
                                <h1 class="text-3xl font-bold text-gray-900 mb-1">
                                    {getDisplayName(userProfile)}
                                </h1>
                                <p class="text-gray-600 text-lg mb-3">
                                    @{userProfile.user_username}
                                </p>
                                
                                <!-- バイオ（中央寄せ） -->
                                {#if userProfile.bio}
                                    <p class="text-gray-800 mb-4 leading-relaxed max-w-md mx-auto">
                                        {userProfile.bio}
                                    </p>
                                {/if}
                            </div>
                            
                            <!-- 詳細情報 -->
                            <div class="flex flex-wrap gap-4 text-gray-600 justify-center">
                                {#if userProfile.birthday}
                                    <div class="flex items-center gap-1">
                                        <Calendar class="w-4 h-4" />
                                        <span class="text-sm">{formatDate(userProfile.birthday)}</span>
                                    </div>
                                {/if}
                                
                                {#if userProfile.location}
                                    <div class="flex items-center gap-1">
                                        <MapPin class="w-4 h-4" />
                                        <span class="text-sm">{userProfile.location}</span>
                                    </div>
                                {/if}
                                
                                {#if userProfile.birth_place}
                                    <div class="flex items-center gap-1">
                                        <School class="w-4 h-4" />
                                        <span class="text-sm">出身: {userProfile.birth_place}</span>
                                    </div>
                                {/if}
                                
                                <div class="flex items-center gap-1">
                                    <Calendar class="w-4 h-4" />
                                    <span class="text-sm flex flex-row gap-1 items-center">参加日: <DateBadge date={userProfile.created_at} showClock={false} /></span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- 右側のアクションボタンエリア -->
                        <div class="ml-4">
                            <!-- フォローボタンやその他のアクションボタンを追加可能 -->
                            <!-- 
                            <button class="px-6 py-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors">
                                フォロー
                            </button>
                            -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <!-- ローディング状態 -->
        <div class="w-full h-64 flex items-center justify-center">
            <div class="text-gray-500">プロフィールを読み込み中...</div>
        </div>
    {/if}
</div>