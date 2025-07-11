<script>
    // svelte系の定義
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { createEventDispatcher } from 'svelte';
    import PostalSearch from "$lib/components/page-components/postalSearch.svelte";

   // 使う変数
    let eventName = $state();
    let content = $state();
    let selectedDate = $state();
    let postalCode = $state();
    let prefecture = $state();
    let city = $state();
    let street = $state();
    let banti = $state();
    let building = $state();

    let startDate = $state();
    let endDate = $state();  

    let startDateTime = new Date();
    let endDateTime = new Date(); 
    
    let selectedDateTime = new Date();
    
    // カレンダーの表示状態を個別に管理
    let isStartCalendarOpen = $state(false);
    let isEndCalendarOpen = $state(false);
    
    let currentCalendarDate = $state();
    let minute = $state();

    minute = Math.floor(selectedDateTime.getMinutes() / 5) * 5;
    let hour = $state()
    hour = selectedDateTime.getHours();

    let calendarMode = "start";

    let valuesError_1 = $state();

    const dispatch = createEventDispatcher();

    // 表示の制御用の関数
    const { onClose } = $props();

    const weekdays = ["日", "月", "火", "水", "木", "金", "土"];

    // マウントされた時に実行
    onMount(() => {
        initializeCalendar();
    });

    // カレンダーの初期位置の関数
    function initializeCalendar() {
        // 現在の時刻を取得
        const now = new Date();
        // 5分刻みにする
        now.setMinutes(Math.floor(now.getMinutes() / 5) * 5);

        // 各変数を現在時刻で初期化
        startDateTime = now;

        // 終了時刻は開始時刻の3日後
        endDateTime = new Date(now);
        endDateTime.setDate(endDateTime.getDate() + 3);

        currentCalendarDate = new Date(now);
        hour = now.getHours();
        minute = now.getMinutes();

        // update関数を呼び出し
        updateSelectedDisplay();
    }

    // カレンダーポップアップの開閉を切り替える（廃止予定）
    function toggleCalendar() {
        if (calendarMode === "start") {
            isStartCalendarOpen = false;
        } else {
            isEndCalendarOpen = false;
        }
    }

    function changeMonth(offset) {
        currentCalendarDate = new Date(
            // 表示月を指定されたオフセット分移動
            currentCalendarDate.getFullYear(),
            currentCalendarDate.getMonth() + offset,
            1,
        );
        // 日、時、分は現在の選択値を維持して選択されている日時も月を合わせて更新
        if (calendarMode === "start") {
            startDateTime = new Date(
                currentCalendarDate.getFullYear(),
                currentCalendarDate.getMonth(),
                startDateTime.getDate(),
                hour,
                minute,
            );
        } else {
            endDateTime = new Date(
                currentCalendarDate.getFullYear(),
                currentCalendarDate.getMonth(),
                endDateTime.getDate(),
                hour,
                minute,
            );
        }
        // update関数を呼び出し
        updateSelectedDisplay();
    }

    // カレンダーから日付を選択する関数
    function selectDay(day, fromOtherMonth = false) {
        // 他の月の日付が選択された場合、月を移動
        if (fromOtherMonth) {
            // 日付が15より大きい場合は前月、小さい場合は翌月
            currentCalendarDate.setMonth(
                currentCalendarDate.getMonth() + (day > 15 ? -1 : 1),
            );
        }
        if (calendarMode === "start") {
            startDateTime = new Date(
                currentCalendarDate.getFullYear(),
                currentCalendarDate.getMonth(),
                day,
                hour,
                minute,
            );
        } else {
            endDateTime = new Date(
                currentCalendarDate.getFullYear(),
                currentCalendarDate.getMonth(),
                day,
                hour,
                minute,
            );
        }
        // update関数を呼び出し
        updateSelectedDisplay();
    }

    //updateする関数
    function updateSelectedDisplay() {
        const targetDateTime = calendarMode === "start" ? startDateTime : endDateTime;
        const y = targetDateTime.getFullYear();
        const m = targetDateTime.getMonth() + 1;
        const d = targetDateTime.getDate();
        const w = weekdays[targetDateTime.getDay()];
        const h = hour.toString().padStart(2, "0");
        const min = minute.toString().padStart(2, "0");
        const dateStr = `${y}年${m}月${d}日(${w}) ${h}:${min}`;
        
        if (calendarMode === "start") {
            startDate = dateStr;
        } else {
            endDate = dateStr;
        }
    }

    function confirmDate() {
        if (calendarMode === "start") {
            startDateTime.setHours(hour, minute);
            updateSelectedDisplay();
            isStartCalendarOpen = false;
        } else {
            endDateTime.setHours(hour, minute);
            updateSelectedDisplay();
            isEndCalendarOpen = false;
        }
    }

    // 日を取得
    function getDaysInMonth() {
        const y = currentCalendarDate.getFullYear();
        const m = currentCalendarDate.getMonth();
        return new Date(y, m + 1, 0).getDate();
    }

    // 曜日を取得
    function getFirstDayOfMonth() {
        const y = currentCalendarDate.getFullYear();
        const m = currentCalendarDate.getMonth();
        return new Date(y, m, 1).getDay();
    }

    // 前月の日数を取得
    function getDaysInPrevMonth() {
        const y = currentCalendarDate.getFullYear();
        const m = currentCalendarDate.getMonth();
        return new Date(y, m, 0).getDate();
    }

    // カレンダーに表示するセル数を取得（6週間 × 7日 = 42セル）
    function getCalendarCells() {
        return 42;
    }

    // カレンダーセルの日付と月情報を取得する関数
    function getCalendarCellData(index) {
        const firstDay = getFirstDayOfMonth();
        const daysInMonth = getDaysInMonth();
        const daysInPrevMonth = getDaysInPrevMonth();
        
        if (index < firstDay) {
            // 前月の日付
            const day = daysInPrevMonth - (firstDay - index - 1);
            return { day, isPrevMonth: true, isNextMonth: false };
        } else if (index < firstDay + daysInMonth) {
            // 現在の月の日付
            const day = index - firstDay + 1;
            return { day, isPrevMonth: false, isNextMonth: false };
        } else {
            // 翌月の日付
            const day = index - (firstDay + daysInMonth) + 1;
            return { day, isPrevMonth: false, isNextMonth: true };
        }
    }

    // カレンダーを開く関数
    // modeは"start"または"end"を指定
    function openCalendar(mode) {
        // 他のカレンダーを閉じる
        isStartCalendarOpen = false;
        isEndCalendarOpen = false;
        
        calendarMode = mode;
        
        if (mode === "start") {
            isStartCalendarOpen = true;
            currentCalendarDate = new Date(startDateTime);
            hour = startDateTime.getHours();
            minute = startDateTime.getMinutes();
        } else {
            isEndCalendarOpen = true;
            currentCalendarDate = new Date(endDateTime);
            hour = endDateTime.getHours();
            minute = endDateTime.getMinutes();
        }
        updateSelectedDisplay();
    }

    // イベントを登録する関数
    // すべてのフィールドが入力されているか確認し、APIにPOSTリクエストを送信
    // 成功したらonCloseを呼び出す
    async function HandleEvent() {
        if (!eventName || !content || !startDateTime || !endDateTime || !postalCode || !prefecture || !city || !street || !banti) {
            valuesError_1 = true;   
            return;
        }
        if (building == undefined) {
            building = " ";
        }
        try {
            const response = await apiClient.post("/events/create", {
                title: eventName,
                description: content,
                start_datetime: startDateTime.toISOString(),
                end_datetime: endDateTime.toISOString(),
                location: postalCode + prefecture + city + street + banti + (building || ""),
                published: true
            });
            
            dispatch('added');
            onClose?.();
        } catch (e) {
            alert("登録に失敗しました: " + (e?.message || ""));
            console.log("APIエラー詳細", e);
        }
    }
</script>

{#if valuesError_1 === true}
    <p class="text-red-500 text-sm mb-3">建物名・部屋番号以外の項目は全て入力してください</p>
{/if}

<div class="w-full w-[68vw] mx-auto rounded-lg shadow-lg p-6 relative">
    <!-- 閉じるボタン -->
    <button
        type="button"
        class="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-500 hover:text-gray-700 transition-colors"
        onclick={() => onClose?.()}
        aria-label="フォームを閉じる"
    >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
    </button>

    <!-- フォームタイトル -->
    <h2 class="text-xl font-bold text-gray-800 mb-6 pr-8">新しいイベントを作成</h2>

    <form onsubmit={(e) => e.preventDefault()}>
        <!-- イベント名 -->
        <div class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-2">イベント名</label>
            <input
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                bind:value={eventName}
                placeholder="例: ドキドキマヤ文明鎮魂祭"
            />
        </div>

        <!-- 概要 -->
        <div class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-2">概要</label>
            <textarea
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                rows="3"
                bind:value={content}
                placeholder="例: マヤ文明の魂を鎮魂します"
            ></textarea>
        </div>

        <!-- 日時選択 -->
        <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">開始日時</label>
                <input
                    class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                    readonly
                    value={startDate}
                    onclick={() => openCalendar("start")}
                    placeholder="日時を選択"
                />
                {#if isStartCalendarOpen}
                    <div class="fixed inset-0 flex items-center justify-center z-[1001]">
                        <div class="bg-white border border-gray-300 rounded-lg shadow-xl p-4 w-80 max-w-[90vw]">
                            <div class="flex justify-between items-center mb-3">
                                <button
                                    type="button"
                                    class="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                    onclick={() => changeMonth(-1)}>‹</button
                                >
                                <div class="text-sm font-bold">
                                    {currentCalendarDate.getFullYear()}年 {currentCalendarDate.getMonth() + 1}月
                                </div>
                                <button
                                    type="button"
                                    class="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                    onclick={() => changeMonth(1)}>›</button
                                >
                            </div>

                            <div class="grid grid-cols-7 gap-1 mb-2">
                                {#each weekdays as day}
                                    <div class="text-center text-xs font-bold text-gray-600 py-1">{day}</div>
                                {/each}
                            </div>

                            <div class="grid grid-cols-7 gap-1 mb-4">
                                {#each Array(getCalendarCells()) as _, index}
                                    {#key index}
                                        {@const cellData = getCalendarCellData(index)}
                                        <button
                                            class="w-8 h-8 rounded text-xs flex items-center justify-center hover:bg-blue-50 transition-colors {cellData.isPrevMonth || cellData.isNextMonth ? 'text-gray-400' : 'text-black'}"
                                            onclick={() => selectDay(cellData.day, cellData.isPrevMonth || cellData.isNextMonth)}
                                        >
                                            {cellData.day}
                                        </button>
                                    {/key}
                                {/each}
                            </div>

                            <div class="flex gap-2 mb-4">
                                <div class="flex-1">
                                    <label class="block mb-1 text-xs font-bold">時</label>
                                    <select
                                        class="w-full p-2 border border-gray-300 rounded text-sm"
                                        bind:value={hour}
                                        onchange={updateSelectedDisplay}
                                    >
                                        {#each Array(24) as _, h}
                                            <option value={h}>{String(h).padStart(2, "0")}時</option>
                                        {/each}
                                    </select>
                                </div>
                                <div class="flex-1">
                                    <label class="block mb-1 text-xs font-bold">分</label>
                                    <select
                                        class="w-full p-2 border border-gray-300 rounded text-sm"
                                        bind:value={minute}
                                        onchange={updateSelectedDisplay}
                                    >
                                        {#each Array(12) as _, i}
                                            <option value={i * 5}>{String(i * 5).padStart(2, "0")}分</option>
                                        {/each}
                                    </select>
                                </div>
                            </div>

                            <div class="border-t pt-3">
                                <div class="bg-gray-100 p-2 rounded mb-3 text-sm">
                                    選択中: {startDate}
                                </div>
                                <div class="flex gap-2 justify-end">
                                    <button
                                        type="button"
                                        class="px-3 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors"
                                        onclick={() => isStartCalendarOpen = false}>キャンセル</button
                                    >
                                    <button
                                        type="button"
                                        class="px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
                                        onclick={confirmDate}>決定</button
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
            
            <div>
                <label class="block text-sm font-semibold text-gray-700 mb-2">終了日時</label>
                <input
                    class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                    readonly
                    value={endDate}
                    onclick={() => openCalendar("end")}
                    placeholder="日時を選択"
                />
                {#if isEndCalendarOpen}
                    <div class="fixed inset-0 flex items-center justify-center z-[1001]">
                        <div class="bg-white border border-gray-300 rounded-lg shadow-xl p-4 w-80 max-w-[90vw]">
                            <div class="flex justify-between items-center mb-3">
                                <button
                                    type="button"
                                    class="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                    onclick={() => changeMonth(-1)}>‹</button
                                >
                                <div class="text-sm font-bold">
                                    {currentCalendarDate.getFullYear()}年 {currentCalendarDate.getMonth() + 1}月
                                </div>
                                <button
                                    type="button"
                                    class="p-2 hover:bg-gray-100 rounded-full transition-colors"
                                    onclick={() => changeMonth(1)}>›</button
                                >
                            </div>

                            <div class="grid grid-cols-7 gap-1 mb-2">
                                {#each weekdays as day}
                                    <div class="text-center text-xs font-bold text-gray-600 py-1">{day}</div>
                                {/each}
                            </div>

                            <div class="grid grid-cols-7 gap-1 mb-4">
                                {#each Array(getCalendarCells()) as _, index}
                                    {#key index}
                                        {@const cellData = getCalendarCellData(index)}
                                        <button
                                            class="w-8 h-8 rounded text-xs flex items-center justify-center hover:bg-blue-50 transition-colors {cellData.isPrevMonth || cellData.isNextMonth ? 'text-gray-400' : 'text-black'}"
                                            onclick={() => selectDay(cellData.day, cellData.isPrevMonth || cellData.isNextMonth)}
                                        >
                                            {cellData.day}
                                        </button>
                                    {/key}
                                {/each}
                            </div>

                            <div class="flex gap-2 mb-4">
                                <div class="flex-1">
                                    <label class="block mb-1 text-xs font-bold">時</label>
                                    <select
                                        class="w-full p-2 border border-gray-300 rounded text-sm"
                                        bind:value={hour}
                                        onchange={updateSelectedDisplay}
                                    >
                                        {#each Array(24) as _, h}
                                            <option value={h}>{String(h).padStart(2, "0")}時</option>
                                        {/each}
                                    </select>
                                </div>
                                <div class="flex-1">
                                    <label class="block mb-1 text-xs font-bold">分</label>
                                    <select
                                        class="w-full p-2 border border-gray-300 rounded text-sm"
                                        bind:value={minute}
                                        onchange={updateSelectedDisplay}
                                    >
                                        {#each Array(12) as _, i}
                                            <option value={i * 5}>{String(i * 5).padStart(2, "0")}分</option>
                                        {/each}
                                    </select>
                                </div>
                            </div>

                            <div class="border-t pt-3">
                                <div class="bg-gray-100 p-2 rounded mb-3 text-sm">
                                    選択中: {endDate}
                                </div>
                                <div class="flex gap-2 justify-end">
                                    <button
                                        type="button"
                                        class="px-3 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50 transition-colors"
                                        onclick={() => isEndCalendarOpen = false}>キャンセル</button
                                    >
                                    <button
                                        type="button"
                                        class="px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
                                        onclick={confirmDate}>決定</button
                                    >
                                </div>
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>

        <!-- 住所情報 -->
        <PostalSearch bind:postalCode bind:prefecture bind:city bind:street />
        
        <div class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-2">番地</label>
            <input 
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                bind:value={banti} 
                placeholder="例: 1-19-11" 
            />
        </div>

        <div class="mb-4">
            <label class="block text-sm font-semibold text-gray-700 mb-2">建物名・部屋番号</label>
            <input
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                bind:value={building}
                placeholder="例: パークウェルビル5F（任意）"
            />
            <p class="text-xs text-gray-500 mt-1">マンション名や部屋番号がある場合は入力してください</p>
        </div>

        <!-- 送信ボタン -->
            <div class="flex justify-end mb-2 pr-6">
            <button type="button" id="submitBtn" class="px-4 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 transition" onclick={() => HandleEvent?.()}>送信</button>
        </div>
    </form>
</div>