<script>
    import { Modal } from "flowbite-svelte";
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { dateNormalize } from "$lib/utils/datetimeNormalize";
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import MemoInput from "$lib/components/input/memoInput.svelte";
    /** @type {import('./$types').PageProps} */
    let { data } = $props();

    let selectedMemo = null;
    let showModal = false;
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
    <h1 class="text-2xl font-bold mb-6">メモギャラリー</h1>
    
    <div 
        bind:this={memoContainer}
        class="relative w-full"
        style="min-height: 400px;"
    >
        {#if isLoading}
            <p class="text-center py-8">メモを読み込み中...</p>
        {:else}
            {#each memos as memo, index}
                <BaseCard 
                    class="memo-card absolute p-4 rounded-lg border border-gray-300 cursor-pointer transition-all duration-200"
                    role="button"
                    tabindex="0"
                    onclick={() => openMemo(memo)}
                    onkeydown={(e) => e.key === 'Enter' && openMemo(memo)}
                >
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-lg font-semibold text-gray-800 line-clamp-2">{memo.title}</h3>
                        <span class="text-xs text-gray-600 bg-white bg-opacity-50 px-2 py-1 rounded-full">
                            {dateNormalize(memo.created_at)}
                        </span>
                    </div>
                    <div class="text-sm text-gray-700 whitespace-pre-wrap max-h-32 overflow-hidden">
                        {memo.content}
                    </div>
                </BaseCard>
            {/each}
        {/if}
    </div>
    <div class="absolute bottom-4 left-1/2 transform -translate-x-1/2 max-w-xl w-full">
        <MemoInput />
    </div>
</div>

{#if showModal && selectedMemo}
    <Modal bind:open={showModal} on:close={closeModal} size="2xl">
        <div class="p-6">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-xl font-bold text-gray-800">{selectedMemo.title}</h2>
                <div class="flex items-center space-x-2">
                    <span class="text-sm text-gray-500">{dateNormalize(selectedMemo.created_at)}</span>
                </div>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
                <div class="whitespace-pre-wrap text-gray-700 font-sans">{selectedMemo.content}</div>
            </div>
            <div class="flex justify-end mt-6">
                <button 
                    class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                    onclick={closeModal}
                >
                    閉じる
                </button>
            </div>
        </div>
    </Modal>
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