<script>
    // カレンダーの基盤
    import dayjs from 'dayjs';
    import 'dayjs/locale/ja';
    import { ChevronLeft, ChevronRight } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django.js';
    import { getSchedulesFromMultipleCalendars } from './getSchedules.js';
    
    dayjs.locale('ja');

    const { data } = $props();

    let currentDate = $state(dayjs());
    let calendars = $state([]);
    let schedules = $state([]);
    let isLoading = $state(true);
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
            
            // カレンダー取得後、スケジュールも取得
            await fetchSchedules();
            
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
    
    // スケジュールを取得する関数
    async function fetchSchedules() {
        try {
            const calendarIds = calendars.map(calendar => calendar.id);
            const year = currentDate.year();
            const month = currentDate.month() + 1; // dayjsは0ベースなので+1
            
            console.log('スケジュール取得開始:', { calendarIds, year, month });
            
            const fetchedSchedules = await getSchedulesFromMultipleCalendars(calendarIds, year, month);
            schedules = fetchedSchedules;
            
            console.log('取得したスケジュール:', schedules);
        } catch (err) {
            console.error('スケジュールの取得に失敗しました:', err);
            schedules = [];
        }
    }
    
    // 指定した日のスケジュールを取得する関数（開始日のスケジュールのみ）
    function getSchedulesForDay(day) {
        return schedules.filter(schedule => {
            const scheduleStartDate = dayjs(schedule.start_time);
            return scheduleStartDate.isSame(day, 'day');
        });
    }
    
    // 指定した日がスケジュールの継続日かどうかを判定する関数
    function isScheduleContinuationDay(day, schedule) {
        const scheduleStartDate = dayjs(schedule.start_time);
        const scheduleEndDate = schedule.end_time ? dayjs(schedule.end_time) : scheduleStartDate;
        
        // 開始日より後で、終了日以前の日かどうか
        return day.isAfter(scheduleStartDate, 'day') && 
               (day.isSame(scheduleEndDate, 'day') || day.isBefore(scheduleEndDate, 'day'));
    }
    
    // 指定した日に継続中のスケジュールを取得する関数
    function getContinuationSchedulesForDay(day) {
        return schedules.filter(schedule => isScheduleContinuationDay(day, schedule));
    }
    
    // 指定した日の全てのスケジュール（開始日+継続中）のインデックスを計算する関数
    function getScheduleIndex(day, targetSchedule) {
        const daySchedules = getSchedulesForDay(day);
        const continuationSchedules = getContinuationSchedulesForDay(day);
        
        // 開始日のスケジュールのインデックスをチェック
        const startIndex = daySchedules.findIndex(schedule => schedule.id === targetSchedule.id);
        if (startIndex !== -1) {
            return startIndex;
        }
        
        // 継続中のスケジュールのインデックスをチェック（開始日スケジュール数を加算）
        const continuationIndex = continuationSchedules.findIndex(schedule => schedule.id === targetSchedule.id);
        if (continuationIndex !== -1) {
            return daySchedules.length + continuationIndex;
        }
        
        return 0;
    }
    
    // スケジュールの表示期間を計算する関数
    function getScheduleDuration(schedule) {
        const startDate = dayjs(schedule.start_time);
        const endDate = schedule.end_time ? dayjs(schedule.end_time) : startDate;
        return endDate.diff(startDate, 'day') + 1;
    }
    
    // スケジュールの位置タイプを判定する関数
    function getSchedulePositionType(day, schedule) {
        const scheduleStartDate = dayjs(schedule.start_time);
        const scheduleEndDate = schedule.end_time ? dayjs(schedule.end_time) : scheduleStartDate;
        
        if (day.isSame(scheduleStartDate, 'day') && day.isSame(scheduleEndDate, 'day')) {
            return 'single'; // 1日のみのスケジュール
        } else if (day.isSame(scheduleStartDate, 'day')) {
            return 'start'; // 開始日
        } else if (day.isSame(scheduleEndDate, 'day')) {
            return 'end'; // 終了日
        } else {
            return 'middle'; // 中間日
        }
    }
    
    // スケジュールバーのスタイルクラスを取得する関数
    function getScheduleBarClass(day, schedule, index = 0) {
        const positionType = getSchedulePositionType(day, schedule);
        let baseClass = 'w-full text-xs text-white px-1 py-0.5 mb-0.5 truncate relative hover:cursor-pointer';
        
        // インデックスに基づいて色の濃淡を決定（偶数は濃い色、奇数は薄い色）
        const isDark = index % 2 === 0;
        
        switch (positionType) {
            case 'single':
                return baseClass + (isDark ? ' bg-blue-500 rounded' : ' bg-blue-300 rounded');
            case 'start':
                return baseClass + (isDark ? ' bg-blue-500 rounded-l' : ' bg-blue-300 rounded-l');
            case 'end':
                return baseClass + (isDark ? ' bg-blue-500 rounded-r' : ' bg-blue-300 rounded-r');
            case 'middle':
                return baseClass + (isDark ? ' bg-blue-500' : ' bg-blue-300');
            default:
                return baseClass + (isDark ? ' bg-blue-500 rounded' : ' bg-blue-300 rounded');
        }
    }
    
    // コンポーネントマウント時にカレンダーデータを取得
    onMount(() => {
        fetchCalendars();
    });
    
    // 月が変更されたときにスケジュールを再取得
    $effect(() => {
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
        let classes = 'flex flex-col items-center justify-start rounded-none text-sm hover:bg-gray-100 h-24 w-full';
        
        // 今日の日付
        if (day.isSame(today, 'day')) {
            classes += ' bg-blue-50 border-blue-300';
        }
        // 当月以外の日付
        else if (!day.isSame(currentDate, 'month')) {
            classes += ' text-gray-400 bg-gray-50';
        }
        // 当月の日付
        else {
            classes += ' text-gray-900 bg-white';
        }
        
        return classes;
    }
</script>

<style>
    .schedule-bar {
        position: relative;
        margin: 0 -1px; /* セル間のギャップを埋める */
    }
    
    .schedule-bar.start::after {
        content: '';
        position: absolute;
        right: -1px;
        top: 0;
        bottom: 0;
        width: 1px;
        background-color: inherit;
    }
    
    .schedule-bar.middle::before {
        content: '';
        position: absolute;
        left: -1px;
        top: 0;
        bottom: 0;
        width: 1px;
        background-color: inherit;
    }
    
    .schedule-bar.middle::after {
        content: '';
        position: absolute;
        right: -1px;
        top: 0;
        bottom: 0;
        width: 1px;
        background-color: inherit;
    }
    
    .schedule-bar.end::before {
        content: '';
        position: absolute;
        left: -1px;
        top: 0;
        bottom: 0;
        width: 1px;
        background-color: inherit;
    }
</style>

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
    <div class="bg-white rounded-lg border border-gray-300">
        <!-- 曜日ヘッダー -->
        <div class="grid grid-cols-7 gap-1 mb-2">
            {#each weekdays as weekday}
                <div class="h-10 flex items-center justify-center text-sm font-semibold text-gray-600">
                    {weekday}
                </div>
            {/each}
        </div>
        
        <!-- 日付グリッド -->
        <div class="grid grid-cols-7 w-full">
            {#each calendarDays as day}
                <div class={getDayClass(day)}>
                    <!-- 日付 -->
                    <div class="font-semibold mb-1 {day.isSame(today, 'day') ? 'text-blue-600' : ''}">
                        {day.format('D')}
                    </div>
                    
                    <!-- 開始日のスケジュール表示 -->
                    {#each getSchedulesForDay(day) as schedule, index}
                        <div class="{getScheduleBarClass(day, schedule, index)} schedule-bar start" title={`${schedule.title} (${getScheduleDuration(schedule)}日間)`}>
                            {schedule.title}
                        </div>
                    {/each}
                    
                    <!-- 継続中のスケジュール表示 -->
                    {#each getContinuationSchedulesForDay(day) as schedule}
                        {@const positionType = getSchedulePositionType(day, schedule)}
                        {@const scheduleIndex = getScheduleIndex(day, schedule)}
                        <div class="{getScheduleBarClass(day, schedule, scheduleIndex)} schedule-bar {positionType}" title={`${schedule.title} (継続中)`}>
                            {#if positionType === 'end'}
                                &nbsp;
                            {:else}
                                &nbsp;
                            {/if}
                        </div>
                    {/each}
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
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {#each calendars as calendar}
                    <div class="border border-gray-300 rounded-lg p-4 hover:bg-gray-50">
                        <h4 class="font-semibold text-lg mb-2">{calendar.name}</h4>
                        <p class="text-gray-600 text-sm mb-2">{calendar.description}</p>
                        <div class="text-xs text-gray-400">
                            <p>作成日: {new Date(calendar.created_at).toLocaleDateString('ja-JP')}</p>
                            <p>更新日: {new Date(calendar.updated_at).toLocaleDateString('ja-JP')}</p>
                        </div>
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

