<script>
    import WidgetBase from '../../utils/widgetBase.svelte';
    import { Calendar, ChevronLeft, ChevronRight } from 'lucide-svelte';

    let currentDate = $state(new Date());
    
    // 現在の年月を取得
    const year = $derived(currentDate.getFullYear());
    const month = $derived(currentDate.getMonth());
    
    // 月の名前
    const monthNames = [
        '1月', '2月', '3月', '4月', '5月', '6月',
        '7月', '8月', '9月', '10月', '11月', '12月'
    ];
    
    // 曜日
    const dayNames = ['日', '月', '火', '水', '木', '金', '土'];
    
    // 今日の日付
    const today = new Date();
    
    // カレンダーの日付を生成
    const calendarDays = $derived(generateCalendarDays(year, month));
    
    function generateCalendarDays(year, month) {
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startDate = new Date(firstDay);
        startDate.setDate(startDate.getDate() - firstDay.getDay());
        
        const days = [];
        const current = new Date(startDate);
        
        // 6週間分の日付を生成
        for (let week = 0; week < 6; week++) {
            for (let day = 0; day < 7; day++) {
                days.push(new Date(current));
                current.setDate(current.getDate() + 1);
            }
        }
        
        return days;
    }
    
    function isToday(date) {
        return date.toDateString() === today.toDateString();
    }
    
    function isCurrentMonth(date) {
        return date.getMonth() === month;
    }
    
    function prevMonth() {
        currentDate = new Date(year, month - 1, 1);
    }
    
    function nextMonth() {
        currentDate = new Date(year, month + 1, 1);
    }
</script>

<WidgetBase title="カレンダー" icon={Calendar} href="/calendar">
    <div class="flex flex-col gap-3">
        <!-- カレンダーヘッダー -->
        <div class="flex items-center justify-between">
            <button 
                class="p-1 hover:bg-gray-100 rounded transition-colors"
                on:click={prevMonth}
            >
                <ChevronLeft class="w-4 h-4" />
            </button>
            
            <h3 class="font-semibold text-sm">
                {year}年 {monthNames[month]}
            </h3>
            
            <button 
                class="p-1 hover:bg-gray-100 rounded transition-colors"
                on:click={nextMonth}
            >
                <ChevronRight class="w-4 h-4" />
            </button>
        </div>
        
        <!-- 曜日ヘッダー -->
        <div class="grid grid-cols-7 gap-1 text-xs text-gray-500 text-center">
            {#each dayNames as dayName}
                <div class="py-1">{dayName}</div>
            {/each}
        </div>
        
        <!-- カレンダーグリッド -->
        <div class="grid grid-cols-7 gap-1">
            {#each calendarDays as day}
                <div 
                    class="aspect-square flex items-center justify-center text-xs rounded cursor-pointer transition-colors
                           {isCurrentMonth(day) 
                               ? isToday(day) 
                                   ? 'bg-blue-500 text-white font-semibold' 
                                   : 'text-gray-900 hover:bg-gray-100' 
                               : 'text-gray-300'}"
                >
                    {day.getDate()}
                </div>
            {/each}
        </div>
        
        <!-- 今日の日付表示 -->
        <div class="text-xs text-gray-500 text-center border-t pt-2">
            今日: {today.getFullYear()}年{today.getMonth() + 1}月{today.getDate()}日
        </div>
    </div>
</WidgetBase>