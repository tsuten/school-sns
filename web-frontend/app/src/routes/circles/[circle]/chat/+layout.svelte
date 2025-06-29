<script>
    import { page } from '$app/stores';
    import { Crown, Users, Hash } from 'lucide-svelte';
    import { Badge } from 'flowbite-svelte';

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

    // 現在のサークルIDを取得
    let currentCircleId = $derived($page.params.circle);

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

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('ja-JP', {
            month: 'short',
            day: 'numeric'
        });
    }
</script>

<div class="flex h-screen">
    <!-- 左サイドバー: 参加サークル一覧 -->
    <div class="w-16 hover:w-64 bg-gray-50 border-r border-gray-300 flex flex-col transition-all duration-300 ease-in-out group">
        <!-- ヘッダー -->
        <div class="p-4 border-b border-gray-300 bg-white">
            <div class="flex items-center gap-2">
                <Users class="w-5 h-5 text-gray-800 flex-shrink-0" />
                <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
                    <h2 class="text-lg font-bold text-gray-800 whitespace-nowrap">
                        サークルを探す
                    </h2>
                    <p class="text-sm text-gray-600 whitespace-nowrap">{data.circles?.length || 0} サークル</p>
                </div>
            </div>
        </div>

        <!-- サークル一覧 -->
        <div class="flex-1 overflow-y-auto">
            {#if data.circles && data.circles.length > 0}
                {#each data.circles as circle}
                    <a 
                        href="/circles/{circle.id}/chat"
                        class="block p-4 border-b border-gray-200 hover:bg-white transition-colors {currentCircleId === circle.id ? 'bg-blue-50' : ''} relative"
                        title={circle.name}
                    >
                        <!-- 現在のサークルを示す縦線 -->
                        {#if currentCircleId === circle.id}
                            <div class="absolute left-0 top-0 bottom-0 w-1 bg-blue-500"></div>
                        {/if}
                        
                        <div class="flex items-start gap-3">
                            <!-- アイコンプレースホルダー（後でアイコンに置き換え予定） -->
                            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 {currentCircleId === circle.id ? 'bg-blue-200' : ''}">
                                <Hash class="w-4 h-4 text-blue-600" />
                            </div>
                            
                            <!-- 展開時のみ表示される詳細情報 -->
                            <div class="flex-1 min-w-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 overflow-hidden">
                                <!-- サークル名と創設者マーク -->
                                <div class="flex items-center gap-2">
                                    <h3 class="font-medium text-gray-800 truncate whitespace-nowrap">{circle.name}</h3>
                                    {#if circle.founder}
                                        <Crown class="w-4 h-4 text-yellow-500 flex-shrink-0" />
                                    {/if}
                                </div>
                            </div>
                        </div>
                    </a>
                {/each}
            {:else}
                <div class="p-4 text-center text-gray-500">
                    <Users class="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                        <p class="text-sm whitespace-nowrap">参加しているサークルがありません</p>
                    </div>
                </div>
            {/if}
        </div>
    </div>

    <!-- メインコンテンツエリア -->
    <div class="flex-1 flex flex-col">
        {@render children()}
    </div>
</div>

<style>
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>