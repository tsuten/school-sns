<script>
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { dateNormalize, datetimeNormalize } from "$lib/utils/datetimeNormalize";
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import MemoInput from "$lib/components/input/memoInput.svelte";
    import DatetimeBadge from "$lib/components/badge/datetimeBadge.svelte";
    import DateBadge from "$lib/components/badge/dateBadge.svelte";
    import { Clock } from "lucide-svelte";
    import { Button, Modal, P } from "flowbite-svelte";
    import { theme } from "$lib/theme.js";
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

<div class="p-6 h-full overflow-y-scroll relative {$theme.card.background}">
    <h1 class="text-2xl font-bold mb-6 {$theme.text.primary}">メモ</h1>
    <div 
        bind:this={memoContainer}
        class="relative w-full"
        style="min-height: 400px;"
    >
        {#if isLoading}
            <p class="text-center py-8 {$theme.text.secondary}">メモを読み込み中...</p>
        {:else}
            {#each memos as memo, index}
                <div
                    class="memo-card absolute p-4 rounded-lg cursor-pointer transition-all duration-200 {$theme.card.background} {$theme.border.primary}"
                    role="button"
                    tabindex="0"
                    onkeydown={(e) => e.key === 'Enter' && openMemo(memo)}
                    onclick={() => openMemo(memo)}
                >
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="text-lg font-semibold line-clamp-2 {$theme.text.primary}">{memo.title}</h3>
                        <span class="text-xs px-2 py-1 rounded-full {$theme.text.tertiary} {$theme.card.background}">
                            <DateBadge date={memo.created_at} />
                        </span>
                    </div>
                    <div class="whitespace-pre-wrap max-h-32 overflow-hidden {$theme.text.secondary}">
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

<Modal title="メモを編集" form bind:open={showModal} on:close={() => { showModal = false; selectedMemo = null; }}>
    {#if selectedMemo}
        <P>
            <div class="flex flex-col gap-2">
                <label for="modal-title" class="text-sm {$theme.text.tertiary}">タイトル</label>
                <input 
                    id="modal-title" 
                    type="text" 
                    bind:value={selectedMemo.title}
                    class="w-full px-3 py-2 rounded-md {$theme.input.background} {$theme.input.border} {$theme.input.text}"
                />
            </div>
        </P>
        <P>
            <hr class="{$theme.border.secondary}" />
        </P>
        <P>
            <div class="flex flex-col gap-2">
                <label for="modal-content" class="text-sm {$theme.text.tertiary}">内容</label>
                <div class="rounded-md {$theme.background.secondary} {$theme.border.primary}">
                    <textarea 
                        id="modal-content" 
                        bind:value={selectedMemo.content}
                        rows="10"
                        class="w-full px-3 py-2 border-none resize-none min-h-[160px] focus:outline-none focus:ring-0 {$theme.input.text}"
                    ></textarea>
                </div>
            </div>
        </P>
        <P>
            <hr class="{$theme.border.secondary}" />
        </P>
        <P>
            <div class="flex flex-row gap-3 justify-between items-center">
                <div class="flex flex-row gap-2 items-center {$theme.text.tertiary}">
                    <DatetimeBadge date={selectedMemo.created_at} />
                </div>
                <div class="flex flex-row gap-2">
                    <Button color="light" class="hover:cursor-pointer" onclick={() => { showModal = false; selectedMemo = null; }}>
                        閉じる
                    </Button>
                    <Button onclick={() => updateMemo(selectedMemo)} color="blue" class="hover:cursor-pointer">
                        更新
                    </Button>
                </div>
            </div>
        </P>
    {/if}
</Modal>

<style>
    .memo-card {
        break-inside: avoid;
        page-break-inside: avoid;
    }
    
    .line-clamp-2 {
        display: -webkit-box;
        line-clamp: 2;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
</style>