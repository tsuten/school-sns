<script>
    import { Calendar, User, MapPin, Bookmark, ChevronDown, ChevronUp, DoorOpen } from "lucide-svelte";
    
    /** @type {{ event: { title: string, description: string, organizer: string, location: string, start_datetime: string } }} */
    let { event } = $props();
    
    // 展開状態の管理
    let isExpanded = $state(false);
    
    // 日時をフォーマットする関数
    function formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        return date.toLocaleString('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    // 説明文が3行を超えるかどうかを判定
    function shouldShowButton(text) {
        // 改行の数をカウント + 文字数で判定（大まかな推定）
        const lineBreaks = (text.match(/\n/g) || []).length;
        const estimatedLines = Math.ceil(text.length / 50) + lineBreaks; // 50文字を1行として推定
        return estimatedLines > 3;
    }
    
    // 展開/縮小の切り替え
    function toggleExpanded() {
        isExpanded = !isExpanded;
    }
    
    // 3行を超える場合のみフェード効果を適用
    const shouldApplyFade = $derived(shouldShowButton(event.description));
</script>

<style>
    .description-fade {
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        position: relative;
        line-height: 1.5;
        max-height: 4.5em; /* 3行 × 1.5 line-height */
        white-space: pre-wrap; /* 改行を保持 */
    }
    
    .description-fade.apply-fade::after {
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 100%;
        height: 1.5em; /* 1行分の高さ */
        background: linear-gradient(to bottom, transparent, white);
        pointer-events: none;
    }
    
    .description-expanded {
        line-height: 1.5;
        white-space: pre-wrap;
    }
</style>

<div class="flex flex-row w-full p-2 gap-4 bg-white rounded-lg border border-gray-300">
    <div class="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center">
        <Calendar class="w-8 h-8 text-gray-400" />
    </div>
    <div class="flex flex-row justify-between w-full">
        <div class="flex flex-col justify-center">
            <p class="text-lg font-bold">{event.title}</p>
            <div class="mt-1">
                <p class="text-sm text-gray-600 {isExpanded ? 'description-expanded' : 'description-fade'} {shouldApplyFade && !isExpanded ? 'apply-fade' : ''}">{event.description}</p>
                {#if shouldShowButton(event.description)}
                    <button 
                        class="text-xs text-blue-500 hover:text-blue-700 mt-1 flex items-center gap-1 hover:cursor-pointer"
                        onclick={toggleExpanded}
                    >
                        {isExpanded ? '閉じる' : '更に見る'}
                        {#if isExpanded}
                            <ChevronUp class="w-3 h-3" />
                        {:else}
                            <ChevronDown class="w-3 h-3" />
                        {/if}
                    </button>
                {/if}
            </div>
        </div>
        <div class="flex flex-col gap-2 items-end justify-between">
            <div class="flex flex-row gap-2 items-center">
                <div class="flex gap-2 items-center hover:cursor-pointer">
                    <DoorOpen class="w-6 h-6 text-gray-500" />
                </div>
                <div class="flex gap-2 items-center hover:cursor-pointer">
                    <Bookmark class="w-6 h-6 text-gray-500" />
                </div>
            </div>
            <div class="flex flex-row gap-2 items-center text-xs text-gray-500">
                <MapPin class="w-4 h-4" />
                <span>{event.location}</span>
                <User class="w-4 h-4" />
                <span>{event.organizer}</span>
                <Calendar class="w-4 h-4" />
                <span>{formatDateTime(event.start_datetime)}</span>
            </div>
        </div>
    </div>
</div>