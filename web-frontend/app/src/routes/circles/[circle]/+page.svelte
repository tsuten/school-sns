<script>
    import { Users, Tag, User, Calendar, Settings, MessageCircle, UserPlus, Crown, ArrowLeft } from 'lucide-svelte';
    import { Button, Badge, Card } from 'flowbite-svelte';
    import { apiClient } from '$lib/services/django';
    import { page } from '$app/stores';
    import toast from '$lib/utils/toast.js';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let circle = $state(null);
    let loading = $state(true);
    let error = $state(null);
    let isMember = $state(null);

    // カテゴリーの日本語表示マッピング
    const categoryLabels = {
        study: '学習',
        hobby: '趣味',
        game: 'ゲーム',
        music: '音楽',
        art: '美術',
        sports: 'スポーツ',
        other: 'その他'
    };

    $effect(() => {
        const circleId = $page.params.circle;
        if (circleId) {
            fetchCircleDetail(circleId);
            fetchIsMember(circleId);
        }
    });

    async function fetchCircleDetail(circleId) {
        try {
            loading = true;
            error = null;
            const response = await apiClient.get(`/circle/${circleId}`);
            circle = response;
        } catch (err) {
            error = err.message || 'サークル情報の取得に失敗しました';
            console.error('Error fetching circle:', err);
        } finally {
            loading = false;
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('ja-JP', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    async function JoinCircle(circleId) {
        try {
            const response = await apiClient.post(`/circle/${circleId}/join`);
            if (response.status === 'success') {
                toast.success('サークルに参加しました');
                // 参加成功後、データを再取得してページを更新
                await fetchCircleDetail(circleId);
                await fetchIsMember(circleId);
            } else {
                toast.error('サークルに参加できませんでした');
            }
        } catch (error) {
            console.error('Error joining circle:', error);
            toast.error('サークルに参加できませんでした');
        }
    }

    async function fetchIsMember(circleId) {
        const response = await apiClient.get(`/circle/${circleId}/is-member`);
        isMember = response.is_member;
    }

    $inspect(circle);
</script>

{#if loading}
    <div class="container mx-auto p-4">
        <div class="flex justify-center items-center h-64">
            <div class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p class="text-gray-600">読み込み中...</p>
            </div>
        </div>
    </div>
{:else if error}
    <div class="container mx-auto p-4">
        <div class="text-center py-12">
            <Users class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 class="text-xl font-bold text-gray-800 mb-2">エラーが発生しました</h2>
            <p class="text-gray-600 mb-4">{error}</p>
            <Button color="blue" size="sm" on:click={() => window.history.back()}>
                戻る
            </Button>
        </div>
    </div>
{:else if circle}
    <div class="container mx-auto p-4 max-w-4xl">
        <!-- ヘッダー部分 -->
        <a href="/circles/discover">
            <Button pill={true} color="light" class="p-2! hover:cursor-pointer mb-4">
                <ArrowLeft class="h-5 w-5 text-gray-500" />
            </Button>
        </a>
        <div class="bg-white rounded-sm border border-gray-300 p-6 mb-6">
            <div class="flex flex-col md:flex-row justify-between items-end gap-4">
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-3">
                        <h1 class="text-3xl font-bold text-gray-800">{circle.name}</h1>
                        <Badge color={circle.is_public ? 'green' : 'gray'} class="text-xs">
                            {circle.is_public ? '公開' : '非公開'}
                        </Badge>
                        <Badge color="blue" class="text-xs">
                            {categoryLabels[circle.category] || circle.category}
                        </Badge>
                    </div>
                    
                    {#if circle.description}
                        <p class="text-gray-600 text-lg mb-4 whitespace-pre-wrap">{circle.description}</p>
                    {/if}

                    <!-- 作成者情報 -->
                    <div class="flex items-center gap-2 mb-4">
                        <Crown class="w-5 h-5 text-yellow-500" />
                        <span class="text-sm text-gray-600">作成者:</span>
                        <span class="text-sm font-medium text-gray-800">{circle.founder.username}</span>
                    </div>

                    <!-- 統計情報 -->
                    <div class="flex items-center gap-6 text-sm text-gray-600">
                        <div class="flex items-center gap-2">
                            <Users class="w-4 h-4" />
                            <span>{circle.members.length} メンバー</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <Calendar class="w-4 h-4" />
                            <span>{formatDate(circle.created_at)} 作成</span>
                        </div>
                    </div>
                </div>

                <!-- アクションボタン -->
                <div class="flex flex-col gap-2">
                    {#if circle.tags && circle.tags.length > 0}
                        <div class="p-4">
                            <h3 class="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
                                <Tag class="w-5 h-5" />
                                タグ
                            </h3>
                            <div class="flex flex-wrap gap-2">
                                {#each circle.tags as tag}
                                    <Badge color="gray" class="text-sm">
                                        {tag.name}
                                    </Badge>
                                {/each}
                            </div>
                        </div>
                    {/if}
                    {#if !isMember}
                        <Button color="blue" size="sm" class="flex items-center gap-2 rounded-sm hover:cursor-pointer" onclick={() => JoinCircle(circle.id)}>
                            <UserPlus class="w-4 h-4" />
                            参加する
                        </Button>
                    {:else}
                    <a href="/circles/{circle.id}/chat">
                        <Button color="light" size="sm" class="flex items-center gap-2 rounded-sm hover:cursor-pointer">
                            <MessageCircle class="w-4 h-4" />
                            チャット
                        </Button>
                    </a>
                    {/if}
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

                <!-- 最近の活動 -->
                <Card class="rounded-sm shadow-none border-gray-300">
                    <div class="p-4">
                        <h3 class="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
                            <MessageCircle class="w-5 h-5" />
                            最近の活動
                        </h3>
                        <div class="text-center py-8 text-gray-500">
                            <MessageCircle class="w-12 h-12 text-gray-300 mx-auto mb-2" />
                            <p>まだ活動がありません</p>
                        </div>
                    </div>
                </Card>

            <!-- サイドバー -->
            <div class="space-y-6">
                <!-- メンバーリスト -->
                <Card class="rounded-sm shadow-none border-gray-300">
                    <div class="p-4">
                        <h3 class="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
                            <Users class="w-5 h-5" />
                            メンバー ({circle.members.length})
                        </h3>
                        <div class="space-y-3 max-h-64 overflow-y-auto">
                            {#each circle.members as member}
                                <div class="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-sm">
                                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                        <User class="w-4 h-4 text-blue-600" />
                                    </div>
                                    <div class="flex-1">
                                        <p class="text-sm font-medium text-gray-800">{member.username}</p>
                                        {#if member.id === circle.founder.id}
                                            <p class="text-xs text-yellow-600 flex items-center gap-1">
                                                <Crown class="w-3 h-3" />
                                                作成者
                                            </p>
                                        {/if}
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                </Card>

                <!-- サークル情報 -->
                <Card class="rounded-sm shadow-none border-gray-300">
                    <div class="p-4">
                        <h3 class="text-lg font-bold text-gray-800 mb-3">サークル情報</h3>
                        <div class="space-y-2 text-sm">
                            <div class="flex justify-between">
                                <span class="text-gray-600">公開設定:</span>
                                <span class="text-gray-800">{circle.is_public ? '公開' : '非公開'}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">カテゴリー:</span>
                                <span class="text-gray-800">{categoryLabels[circle.category] || circle.category}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">作成日:</span>
                                <span class="text-gray-800">{formatDate(circle.created_at)}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">更新日:</span>
                                <span class="text-gray-800">{formatDate(circle.updated_at)}</span>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    </div>
{:else}
    <div class="container mx-auto p-4">
        <div class="text-center py-12">
            <Users class="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p class="text-gray-500">サークルが見つかりませんでした</p>
        </div>
    </div>
{/if}
