<script>
    import WidgetBase from '../../utils/widgetBase.svelte';
    import { Calendar, MapPin, Clock } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django.js';
    import { Badge } from 'flowbite-svelte';

    let events = $state([]);
    let loading = $state(true);
    let error = $state(null);

    // イベントデータを取得
    async function fetchEvents() {
        try {
            loading = true;
            error = null;
            events = await apiClient.get('/events/held_events');
        } catch (err) {
            console.error('イベント取得エラー:', err);
            error = `イベントの取得に失敗しました: ${err.message}`;
            events = [];
        } finally {
            loading = false;
        }
    }

    // 日時フォーマット関数
    function formatDateTime(dateString) {
        const date = new Date(dateString);
        const month = date.getMonth() + 1;
        const day = date.getDate();
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${month}/${day} ${hours}:${minutes}`;
    }

    // イベントの状態を取得
    function getEventStatus(event) {
        const now = new Date();
        const startDate = new Date(event.start_datetime);
        const endDate = new Date(event.end_datetime);
        
        if (event.is_cancelled) return 'キャンセル';
        if (now < startDate) return '開催予定';
        if (now > endDate) return '終了';
        return '開催中';
    }

    // イベントの状態に応じたスタイルクラス
    function getStatusClass(event) {
        const status = getEventStatus(event);
        switch (status) {
            case 'キャンセル': return 'text-red-500';
            case '開催予定': return 'text-blue-500';
            case '終了': return 'text-gray-500';
            case '開催中': return 'text-green-500';
            default: return 'text-gray-500';
        }
    }

    onMount(() => {
        fetchEvents();
    });
</script>

<WidgetBase title="開催中のイベント" icon={Calendar} href="/events">
    <div class="flex flex-col gap-3">
        {#if loading}
            <div class="flex items-center justify-center py-4">
                <div class="text-sm text-gray-500">読み込み中...</div>
            </div>
        {:else if error}
            <div class="flex items-center justify-center py-4">
                <div class="text-sm text-red-500">{error}</div>
            </div>
        {:else if events.length === 0}
            <div class="flex items-center justify-center py-4">
                <div class="text-sm text-gray-500">開催中のイベントはありません</div>
            </div>
        {:else}
            {#each events.slice(0, 3) as event (event.id)}
                <div class="border border-gray-300 rounded-sm p-3 hover:bg-gray-50 transition-colors cursor-pointer">
                    <!-- イベントタイトルと状態 -->
                    <div class="flex items-start justify-between mb-2">
                        <h4 class="font-medium text-sm line-clamp-2 flex-1">{event.title}</h4>
                        <Badge color={getStatusClass(event)}>{getEventStatus(event)}</Badge>
                    </div>
                    
                    <!-- イベント詳細 -->
                    <div class="space-y-1">
                        <!-- 開催時間 -->
                        <div class="flex items-center gap-1 text-xs text-gray-600">
                            <Clock class="w-3 h-3" />
                            <span>{formatDateTime(event.start_datetime)} - {formatDateTime(event.end_datetime)}</span>
                        </div>
                        
                        <!-- 場所 -->
                        {#if event.location}
                            <div class="flex items-center gap-1 text-xs text-gray-600">
                                <MapPin class="w-3 h-3" />
                                <span class="line-clamp-1">{event.location}</span>
                            </div>
                        {/if}
                        
                        <!-- 主催者 -->
                        <div class="text-xs text-gray-500">
                            主催: {event.organizer}
                        </div>
                    </div>
                </div>
            {/each}
            
            <!-- 「もっと見る」リンク -->
            {#if events.length > 3}
                <div class="text-center">
                    <a href="/events" class="text-xs text-blue-500 hover:underline">
                        他 {events.length - 3} 件のイベントを見る
                    </a>
                </div>
            {/if}
        {/if}
        
        <!-- 更新ボタン -->
        <div class="border-t pt-2">
            <button 
                class="w-full text-xs text-gray-500 hover:text-gray-700 transition-colors"
                onclick={fetchEvents}
                disabled={loading}
            >
                {loading ? '更新中...' : '更新'}
            </button>
        </div>
    </div>
</WidgetBase>
