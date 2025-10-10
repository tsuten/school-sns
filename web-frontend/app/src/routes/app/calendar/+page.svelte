<script>
    // カレンダーの基盤
    import dayjs from 'dayjs';
    import 'dayjs/locale/ja';
    import { ChevronLeft, ChevronRight } from 'lucide-svelte';
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django.js';
    import { getNewSchedules } from './getSchedules.js';
    import ScheduleForm from '$lib/components/input/scheduleForm.svelte';
    
    dayjs.locale('ja');

    const { data } = $props();

    let currentDate = $state(dayjs());
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
    
    // スケジュールを取得する関数
    async function fetchSchedules() {
        try {
            isLoading = true;
            error = null;
            
            const year = currentDate.year();
            const month = currentDate.month() + 1; // dayjsは0ベースなので+1
            
            console.log('NewSchedule取得開始:', { year, month });
            
            const fetchedSchedules = await getNewSchedules(year, month);
            schedules = fetchedSchedules;
            
            console.log('取得したNewSchedule:', schedules);
        } catch (err) {
            console.error('NewScheduleの取得に失敗しました:', err);
            error = err.message || 'スケジュールの取得に失敗しました';
            schedules = [];
        } finally {
            isLoading = false;
        }
    }
    
    // スケジュール作成完了時の処理
    function handleScheduleCreated(newSchedule) {
        console.log('新しいスケジュールが作成されました:', newSchedule);
        
        // 作成されたスケジュールを現在のリストに追加（即座に表示）
        if (newSchedule && newSchedule.id) {
            schedules = [...schedules, newSchedule];
        }
        
        // カレンダー情報を再取得して最新状態を保証
        setTimeout(() => {
            fetchSchedules();
        }, 100);
    }
    
    // 指定した日のスケジュールを取得する関数（開始日のスケジュールのみ）
    function getSchedulesForDay(day) {
        return schedules.filter(schedule => {
            if (schedule.start_time) {
                const scheduleStartDate = dayjs(schedule.start_time);
                return scheduleStartDate.isSame(day, 'day');
            }
            return false;
        });
    }
    
    // 指定した日がスケジュールの継続日かどうかを判定する関数
    function isScheduleContinuationDay(day, schedule) {
        if (!schedule.start_time || !schedule.end_time) return false;
        
        const scheduleStartDate = dayjs(schedule.start_time);
        const scheduleEndDate = dayjs(schedule.end_time);
        
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
        if (!schedule.start_time || !schedule.end_time) return 1;
        
        const startDate = dayjs(schedule.start_time);
        const endDate = dayjs(schedule.end_time);
        return endDate.diff(startDate, 'day') + 1;
    }
    
    // スケジュールの位置タイプを判定する関数
    function getSchedulePositionType(day, schedule) {
        if (!schedule.start_time || !schedule.end_time) return 'single';
        
        const scheduleStartDate = dayjs(schedule.start_time);
        const scheduleEndDate = dayjs(schedule.end_time);
        
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
    
    // コンポーネントマウント時にスケジュールを取得
    onMount(() => {
        fetchSchedules();
    });
    
    // 月が変更されたときにスケジュールを再取得
    $effect(() => {
        fetchSchedules();
    });
    
    // 副作用：状態変更時のログ出力
    $effect(() => {
        console.log('currentDate changed:', currentDate.format('YYYY-MM-DD'));
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
        let classes = 'flex flex-col items-center justify-start text-sm hover:bg-gray-100 h-24 w-full';
        
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

<div class="flex flex-col gap-4 p-4 h-full overflow-y-scroll max-w-7xl mx-auto">
    
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
    
    <!-- メインコンテンツ（カレンダー + フォーム） -->
    <div class="flex gap-6">
        <!-- カレンダー本体 -->
        <div class="flex-1 bg-white rounded-lg border border-gray-300">
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
        
        <!-- スケジュール作成フォーム -->
        <div class="w-80">
            <ScheduleForm on:scheduleCreated={handleScheduleCreated} />
        </div>
    </div>

    <!-- スケジュール情報（デバッグ用） -->
    <!--{#if schedules.length > 0}
        <div class="bg-gray-50 rounded-lg p-4 border border-gray-300">
            <h3 class="text-lg font-semibold mb-2">取得したスケジュール（{schedules.length}件）</h3>
            <p class="text-sm text-gray-600 mb-2">※ 詳細はブラウザのコンソールをご確認ください</p>
            <div class="text-xs text-gray-500">
                {schedules.map(s => s.title).join(', ')}
            </div>
        </div>
    {/if} -->
</div>

