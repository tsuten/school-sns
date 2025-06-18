<script>
    // カレンダーの基盤
    import dayjs from 'dayjs';
    import 'dayjs/locale/ja';
    import { ChevronLeft, ChevronRight } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django.js';
    import { getSchedules, getSchedulesFromMultipleCalendars } from './getSchedules.js';
    
    dayjs.locale('ja');

    const { data } = $props();

    let currentDate = $state(dayjs());
    let calendars = $state([]);
    let schedules = $state([]);
    let isLoading = $state(true);
    let isLoadingSchedules = $state(false);
    let error = $state(null);
    
    // 現在表示中の月の情報を計算
    const startOfMonth = $derived(currentDate.startOf('month'));
    const endOfMonth = $derived(currentDate.endOf('month'));
    const startOfWeek = $derived(startOfMonth.startOf('week'));
    const endOfWeek = $derived(endOfMonth.endOf('week'));
    
    // カレンダーに表示する全ての日（前月末・当月・翌月初を含む）
    const totalDays = $derived(endOfWeek.diff(startOfWeek, 'day') + 1);
    const calendarDays = $derived(Array.from({ length: totalDays }, (_, i) => startOfWeek.add(i, 'day')));
    
    // カレンダーデータを取得する関数
    async function fetchCalendars() {
        try {
            isLoading = true;
            error = null;
            
            const response = await apiClient.get('/calendar/calendars');
            calendars = response || [];
            
            console.log('カレンダーデータを取得しました:', calendars);
        } catch (err) {
            console.error('カレンダーデータの取得に失敗しました:', err);
            error = err.message || 'カレンダーデータの取得に失敗しました';
            
            // フォールバックデータ
            calendars = [
                {
                    id: '1',
                    name: 'デフォルトカレンダー',
                    description: 'APIエラー時のフォールバックカレンダー',
                    created_at: '2021-01-01T00:00:00Z',
                    updated_at: '2021-01-01T00:00:00Z'
                }
            ];
        } finally {
            isLoading = false;
        }
    }
    
    // スケジュールデータを取得する関数
    async function fetchSchedules() {
        if (!calendars.length) {
            console.log('カレンダーが設定されていないため、スケジュール取得をスキップします');
            return;
        }
        
        try {
            isLoadingSchedules = true;
            console.log('=== スケジュール取得開始 ===');
            
            const year = currentDate.year();
            const month = currentDate.month() + 1; // dayjs の month() は 0-based なので +1
            
            console.log(`対象年月: ${year}年${month}月`);
            console.log('対象カレンダー:', calendars.map(cal => ({ id: cal.id, name: cal.name })));
            
            // 全てのカレンダーからスケジュールを取得
            const calendarIds = calendars.map(cal => cal.id);
            const fetchedSchedules = await getSchedulesFromMultipleCalendars(calendarIds, year, month);
            
            schedules = fetchedSchedules;
            console.log('=== スケジュール取得完了 ===');
            
        } catch (err) {
            console.error('スケジュール取得中にエラーが発生しました:', err);
        } finally {
            isLoadingSchedules = false;
        }
    }
    
    // コンポーネントマウント時にカレンダーデータを取得
    onMount(() => {
        fetchCalendars();
    });
    
    // 副作用：カレンダーが取得されたらスケジュールを取得
    $effect(() => {
        if (calendars.length > 0) {
            console.log('カレンダーが取得されたので、スケジュールを取得します');
            fetchSchedules();
        }
    });
    
    // 副作用：月が変更されたらスケジュールを再取得
    $effect(() => {
        console.log('表示月が変更されました:', currentDate.format('YYYY年MM月'));
        if (calendars.length > 0) {
            fetchSchedules();
        }
    });
    
    // 副作用：状態変更時のログ出力
    $effect(() => {
        console.log('currentDate changed:', currentDate.format('YYYY-MM-DD'));
    });
    
    $effect(() => {
        console.log('startOfMonth changed:', startOfMonth.format('YYYY-MM-DD'));
    });
    
    $effect(() => {
        console.log('endOfMonth changed:', endOfMonth.format('YYYY-MM-DD'));
    });
    
    $effect(() => {
        console.log('startOfWeek changed:', startOfWeek.format('YYYY-MM-DD'));
    });
    
    $effect(() => {
        console.log('endOfWeek changed:', endOfWeek.format('YYYY-MM-DD'));
    });
    
    $effect(() => {
        console.log('totalDays changed:', totalDays);
    });
    
    $effect(() => {
        console.log('calendarDays changed:', calendarDays.map(day => day.format('YYYY-MM-DD')));
    });
    
    // 曜日のヘッダー
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    
    // 月を変更する関数
    function previousMonth() {
        currentDate = currentDate.subtract(1, 'month');
    }
    
    function nextMonth() {
        currentDate = currentDate.add(1, 'month');
    }
    
    // 今日の日付
    const today = dayjs();
    
    // 日付のスタイルを判定する関数
    function getDayClass(day) {
        let classes = 'w-10 h-10 flex items-center justify-center rounded-lg text-sm cursor-pointer hover:bg-gray-100 ';
        
        // 今日の日付
        if (day.isSame(today, 'day')) {
            classes += 'bg-blue-500 text-white hover:bg-blue-600 ';
        }
        // 当月以外の日付
        else if (!day.isSame(currentDate, 'month')) {
            classes += 'text-gray-400 ';
        }
        // 当月の日付
        else {
            classes += 'text-gray-900 ';
        }
        
        return classes;
    }
</script>

<div class="flex flex-col gap-4 p-4">
    <div class="flex flex-col gap-2">
        <h1 class="text-2xl font-bold">カレンダー</h1>
    </div>
    
    <!-- カレンダーヘッダー -->
    <div class="flex items-center justify-between bg-white rounded-lg p-4 border border-gray-300">
        <button 
            class="p-2 hover:bg-gray-100 rounded-lg hover:cursor-pointer"
            onclick={previousMonth}
            aria-label="前の月"
        >
            <ChevronLeft class="w-5 h-5" />
        </button>
        
        <h2 class="text-xl font-semibold">
            {currentDate.format('YYYY年MM月')}
        </h2>
        
        <button 
            class="p-2 hover:bg-gray-100 rounded-lg hover:cursor-pointer "
            onclick={nextMonth}
            aria-label="次の月"
        >
            <ChevronRight class="w-5 h-5" />
        </button>
    </div>
    
    <!-- カレンダー本体 -->
    <div class="bg-white rounded-lg p-4 border border-gray-300">
        <!-- 曜日ヘッダー -->
        <div class="grid grid-cols-7 gap-1 mb-2">
            {#each weekdays as weekday}
                <div class="w-10 h-10 flex items-center justify-center text-sm font-semibold text-gray-600">
                    {weekday}
                </div>
            {/each}
        </div>
        
        <!-- 日付グリッド -->
        <div class="grid grid-cols-7 gap-1">
            {#each calendarDays as day}
                <div class={getDayClass(day)}>
                    {day.format('D')}
                </div>
            {/each}
        </div>
    </div>

    <!-- カレンダー一覧 -->
    <div class="bg-white rounded-lg p-4 border border-gray-300">
        <h3 class="text-lg font-semibold mb-4">カレンダー一覧</h3>
        
        {#if isLoading}
            <div class="flex items-center justify-center py-8">
                <p class="text-gray-500">カレンダーを読み込み中...</p>
            </div>
        {:else if error}
            <div class="flex flex-col items-center justify-center py-8">
                <p class="text-red-500 mb-2">エラー: {error}</p>
                <button 
                    class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                    onclick={fetchCalendars}
                >
                    再試行
                </button>
            </div>
        {:else}
            <div class="flex flex-col gap-4">
                {#each calendars as calendar}
                    <div class="border border-gray-300 rounded-lg p-4 hover:bg-gray-50 w-1/4 hover:cursor-pointer">
                        <h4 class="font-semibold text-lg">{calendar.initial}</h4>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
    
    <!-- スケジュール情報（デバッグ用） -->
    {#if schedules.length > 0}
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-300">
            <h3 class="text-lg font-semibold mb-2">取得したスケジュール（{schedules.length}件）</h3>
            <p class="text-sm text-gray-600 mb-2">※ 詳細はブラウザのコンソールをご確認ください</p>
            <div class="text-xs text-gray-500">
                {schedules.map(s => s.title).join(', ')}
            </div>
        </div>
    {/if}
</div>

