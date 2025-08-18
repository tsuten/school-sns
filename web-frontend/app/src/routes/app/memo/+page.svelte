<script>
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { dateNormalize, datetimeNormalize } from "$lib/utils/datetimeNormalize";
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import MemoInput from "$lib/components/input/memoInput.svelte";
    import DatetimeBadge from "$lib/components/badge/datetimeBadge.svelte";
    import DateBadge from "$lib/components/badge/dateBadge.svelte";
    import { Clock } from "lucide-svelte";
    import { Button } from "flowbite-svelte";
    /** @type {import('./$types').PageProps} */
    let { data } = $props();

    let selectedMemo = $state(null);
    let showModal = $state(false);
    let memoContainer;

    let memos = $state([]);
    let isLoading = $state(true);

    const fetchMemos = async () => {
        try {
            isLoading = true;
            const response = await apiClient.get("/memo/");
            console.log(response);
            memos = response;
        } catch (error) {
            console.error("メモの取得に失敗しました:", error);
            memos = [];
        } finally {
            isLoading = false;
        }
    };

    $inspect("memos", memos);

    // memosの変更を監視してmasonryを再初期化
    $effect(() => {
        if (memos.length > 0 && memoContainer && !isLoading) {
            setTimeout(() => {
                initMasonry();
            }, 100);
        }
    });

    function openMemo(memo) {
        selectedMemo = memo;
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        selectedMemo = null;
    }

    async function updateMemo(memo) {
        await apiClient.put(`/memo/${memo.id}`, {
            title: memo.title,
            content: memo.content
        });
        fetchMemos();
        closeModal();
    }

    // Masonryレイアウトの初期化
    onMount(async () => {
        // まずデータを取得
        await fetchMemos();
        
        // データが読み込まれた後にmasonryを初期化
        if (memoContainer && memos.length > 0) {
            // DOMの更新を待ってから初期化
            setTimeout(() => {
                initMasonry();
            }, 100);
            
            // 100ms毎にレイアウトをリセット
            const interval = setInterval(() => {
                if (memoContainer && memos.length > 0) {
                    initMasonry();
                }
            }, 100);
            
            // コンポーネントのアンマウント時にインターバルをクリア
            return () => {
                clearInterval(interval);
            };
        }
    });

    function initMasonry() {
        const container = memoContainer;
        const items = container.children;
        const columns = 4;
        const columnHeights = new Array(columns).fill(0);
        
        // 各メモカードを最も短い列に配置
        Array.from(items).forEach((item, index) => {
            const shortestColumn = columnHeights.indexOf(Math.min(...columnHeights));
            const left = shortestColumn * (100 / columns);
            
            item.style.position = 'absolute';
            item.style.left = `${left}%`;
            item.style.top = `${columnHeights[shortestColumn]}px`;
            item.style.width = `${100 / columns - 2}%`;
            
            // 次のカードの位置を計算
            columnHeights[shortestColumn] += item.offsetHeight + 16; // 16pxはgap
        });
        
        // コンテナの高さを設定
        container.style.height = `${Math.max(...columnHeights)}px`;
    }

    // ウィンドウリサイズ時にmasonryを再計算
    function handleResize() {
        if (memoContainer) {
            initMasonry();
        }
    }
</script>

<svelte:window on:resize={handleResize} />

<div class="p-6 h-full overflow-y-scroll relative">
    <h1 class="text-2xl font-bold mb-6">メモ</h1>
    <div 
        bind:this={memoContainer}
        class="relative w-full"
        style="min-height: 400px;"
    >
        {#if isLoading}
            <p class="text-center py-8">メモを読み込み中...</p>
        {:else}
            {#each memos as memo, index}
                <div
                    class="memo-card absolute p-4 rounded-lg border border-gray-300 cursor-pointer transition-all duration-200"
                    role="button"
                    tabindex="0"
                    onkeydown={(e) => e.key === 'Enter' && openMemo(memo)}
                    onclick={() => openMemo(memo)}
                >
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-lg font-semibold text-gray-800 line-clamp-2">{memo.title}</h3>
                        <span class="text-xs text-gray-600 bg-white bg-opacity-50 px-2 py-1 rounded-full">
                            <DateBadge date={memo.created_at} />
                        </span>
                    </div>
                    <div class="text-gray-700 whitespace-pre-wrap max-h-32 overflow-hidden">
                        {memo.content}
                    </div>
                </div>
            {/each}
        {/if}
    </div>
    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 max-w-xl w-full">
        <MemoInput on:memoSent={fetchMemos} />
    </div>
</div>

{#if showModal && selectedMemo}
    <!-- オーバーレイ背景 -->
    <div class="fixed inset-0 z-40" style="background-color: rgba(0, 0, 0, 0.3);" onclick={() => showModal = false}></div>
    
    <!-- モーダル -->
    <div class="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50">
        <div class="p-6 bg-white rounded-lg border border-gray-300 w-xl max-h-xl overflow-y-auto flex flex-col gap-4 justify-between">
            <div class="flex flex-col gap-4">
                <div>
                    <input 
                        id="modal-title" 
                        type="text" 
                        bind:value={selectedMemo.title}
                        class="w-full px-3 py-2 bg-transparent text-gray-900 placeholder-gray-500 border-none focus:border-none focus:outline-none focus:ring-0"
                    />
                </div>
                
                <div>
                    <textarea 
                        id="modal-content" 
                        bind:value={selectedMemo.content}
                        rows="6"
                        class="w-full px-3 py-2 bg-transparent text-gray-900 placeholder-gray-500 resize-y min-h-[100px] border-none focus:border-none focus:outline-none focus:ring-0"
                    ></textarea>
                </div>
            </div>
            
            <div class="flex flex-row gap-2 justify-between items-center pt-4 border-t border-gray-200">
                <div class="flex flex-row gap-2 items-center text-gray-500">
                    <DatetimeBadge date={selectedMemo.created_at} />
                </div>
                <Button onclick={() => updateMemo(selectedMemo)} color="blue" class="hover:cursor-pointer">
                    更新
                </Button>
            </div>
        </div>
    </div>
{/if}

<style>
    .memo-card {
        break-inside: avoid;
        page-break-inside: avoid;
    }
    
    .line-clamp-2 {
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>