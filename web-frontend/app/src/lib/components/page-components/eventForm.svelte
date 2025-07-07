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
    <p>建物名・部屋番号以外の項目は全て入力してください</p>
{/if}

<div class="w-full max-w-md mx-auto bg-white rounded shadow p-4 mt-4">
    <form onsubmit={(e) => e.preventDefault()}>
        <!-- フォーム本体ここから -->
        <div class="flex items-center gap-2 mb-3 mt-2">
            <label class="block text-sm font-semibold min-w-[5.5rem]">イベント名</label>
            <input
                class="px-3 py-0.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-gray-400 text-left text-sm w-[calc(92%-2.5rem)] min-w-0"
                bind:value={eventName}
                placeholder="例: ドキドキマヤ文明鎮魂祭"
            />
        </div>
        <div class="flex items-center gap-2 mb-3">
            <label class="block text-sm font-semibold min-w-[5.5rem]">概要</label>
            <input
                class="px-3 py-0.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-gray-400 text-left text-sm w-[calc(92%-2.5rem)] min-w-0"
                bind:value={content}
                placeholder="例: マヤ文明の魂を鎮魂します"
            />
        </div>
        <div class="flex gap-2 mb-2 ml-[5.5rem] w-[calc(100%-5.5rem-1.5rem)] min-w-0 pr-6">
            <div class="flex-1">
                <label class="block text-sm font-semibold">日時</label>
                <input
                    class="px-3 py-0.5 border border-gray-300 rounded bg-gray-50 text-left text-sm w-full min-w-0 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder-gray-400"
                    readonly
                    value={startDate}
                    onclick={() => openCalendar("start")}
                    placeholder="日時を選択してください"
                />
                <input type="hidden" name="start_datetime" value={startDate} required />
                {#if isStartCalendarOpen}
                    <div class="fixed bottom-0 right-2 z-[1000] bg-white border border-gray-300 rounded-lg shadow-lg p-3 w-64">
                        <div class="flex justify-between items-center mb-3">
                            <button
                                type="button"
                                class="bg-transparent border-none cursor-pointer p-1 rounded-full w-6 h-6 flex items-center justify-center text-base hover:bg-gray-100"
                                onclick={() => changeMonth(-1)}>‹</button
                            >
                            <div class="text-sm font-bold">
                                {currentCalendarDate.getFullYear()}年 {currentCalendarDate.getMonth() + 1}月
                            </div>
                            <button
                                type="button"
                                class="bg-transparent border-none cursor-pointer p-1 rounded-full w-6 h-6 flex items-center justify-center text-base hover:bg-gray-100"
                                onclick={() => changeMonth(1)}>›</button
                            >
                        </div>

                        <div class="grid grid-cols-7 gap-0.5 mb-2">
                            {#each weekdays as day}
                                <div class="text-center text-xs font-bold text-gray-600 py-1 px-0.5">{day}</div>
                            {/each}
                        </div>

                        <div class="grid grid-cols-7 gap-0.5 mb-3">
                            {#each Array(getCalendarCells()) as _, index}
                                {#key index}
                                    {@const cellData = getCalendarCellData(index)}
                                    <button
                                        class="w-6 h-6 border-none bg-transparent cursor-pointer rounded text-xs flex items-center justify-center transition-all hover:bg-blue-50 {cellData.isPrevMonth || cellData.isNextMonth ? 'text-gray-400' : 'text-black'}"
                                        onclick={() => selectDay(cellData.day, cellData.isPrevMonth || cellData.isNextMonth)}
                                    >
                                        {cellData.day}
                                    </button>
                                {/key}
                            {/each}
                        </div>

                        <div class="flex gap-2 mb-3">
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                            <div class="flex-1">
                                <label class="block mb-1 text-xs font-bold">時</label>
                                <select
                                    class="w-full p-1 border border-gray-300 rounded text-xs"
                                    bind:value={hour}
                                    onchange={updateSelectedDisplay}
                                >
                                    {#each Array(24) as _, h}
                                        <option value={h}>{String(h).padStart(2, "0")}時</option>
                                    {/each}
                                </select>
                            </div>
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                            <div class="flex-1">
                                <label class="block mb-1 text-xs font-bold">分</label>
                                <select
                                    class="w-full p-1 border border-gray-300 rounded text-xs"
                                    bind:value={minute}
                                    onchange={updateSelectedDisplay}
                                >
                                    {#each Array(12) as _, i}
                                        <option value={i * 5}>{String(i * 5).padStart(2, "0")}分</option>
                                    {/each}
                                </select>
                            </div>
                        </div>

                        <div class="mt-2 border-t border-gray-300 pt-2">
                            <div class="bg-gray-100 p-2 rounded mb-3 text-xs">
                                選択中: {startDate}
                            </div>
                            <div class="flex gap-2 justify-end">
                                <button
                                    type="button"
                                    class="py-1 px-2 border border-gray-300 rounded cursor-pointer text-xs bg-gray-500 text-white hover:bg-gray-600"
                                    onclick={() => isStartCalendarOpen = false}>キャンセル</button
                                >
                                <button
                                    type="button"
                                    class="py-1 px-2 border border-gray-300 rounded cursor-pointer text-xs bg-blue-500 text-white hover:bg-blue-700"
                                    onclick={confirmDate}>決定</button
                                >
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
            <div class="flex-1">
                <label class="block text-sm font-semibold">終了日時</label>
                <input
                    class="px-3 py-0.5 border border-gray-300 rounded bg-gray-50 text-left text-sm w-full min-w-0 cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder-gray-400"
                    readonly
                    value={endDate}
                    onclick={() => openCalendar("end")}
                    placeholder="日時を選択してください"
                />
                <input type="hidden" name="end_datetime" value={endDate} required />
                {#if isEndCalendarOpen}
                    <div class="fixed top-0 right-2 z-[1000] bg-white border border-gray-300 rounded-lg shadow-lg p-3 w-64">
                        <div class="flex justify-between items-center mb-3">
                            <button
                                type="button"
                                class="bg-transparent border-none cursor-pointer p-1 rounded-full w-6 h-6 flex items-center justify-center text-base hover:bg-gray-100"
                                onclick={() => changeMonth(-1)}>‹</button
                            >
                            <div class="text-sm font-bold">
                                {currentCalendarDate.getFullYear()}年 {currentCalendarDate.getMonth() + 1}月
                            </div>
                            <button
                                type="button"
                                class="bg-transparent border-none cursor-pointer p-1 rounded-full w-6 h-6 flex items-center justify-center text-base hover:bg-gray-100"
                                onclick={() => changeMonth(1)}>›</button
                            >
                        </div>

                        <div class="grid grid-cols-7 gap-0.5 mb-2">
                            {#each weekdays as day}
                                <div class="text-center text-xs font-bold text-gray-600 py-1 px-0.5">{day}</div>
                            {/each}
                        </div>

                        <div class="grid grid-cols-7 gap-0.5 mb-3">
                            {#each Array(getCalendarCells()) as _, index}
                                {#key index}
                                    {@const cellData = getCalendarCellData(index)}
                                    <button
                                        class="w-6 h-6 border-none bg-transparent cursor-pointer rounded text-xs flex items-center justify-center transition-all hover:bg-blue-50 {cellData.isPrevMonth || cellData.isNextMonth ? 'text-gray-400' : 'text-black'}"
                                        onclick={() => selectDay(cellData.day, cellData.isPrevMonth || cellData.isNextMonth)}
                                    >
                                        {cellData.day}
                                    </button>
                                {/key}
                            {/each}
                        </div>

                        <div class="flex gap-2 mb-3">
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                            <div class="flex-1">
                                <label class="block mb-1 text-xs font-bold">時</label>
                                <select
                                    class="w-full p-1 border border-gray-300 rounded text-xs"
                                    bind:value={hour}
                                    onchange={updateSelectedDisplay}
                                >
                                    {#each Array(24) as _, h}
                                        <option value={h}>{String(h).padStart(2, "0")}時</option>
                                    {/each}
                                </select>
                            </div>
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                                <!-- svelte-ignore a11y_label_has_associated_control -->
                            <div class="flex-1">
                                <label class="block mb-1 text-xs font-bold">分</label>
                                <select
                                    class="w-full p-1 border border-gray-300 rounded text-xs"
                                    bind:value={minute}
                                    onchange={updateSelectedDisplay}
                                >
                                    {#each Array(12) as _, i}
                                        <option value={i * 5}>{String(i * 5).padStart(2, "0")}分</option>
                                    {/each}
                                </select>
                            </div>
                        </div>

                        <div class="mt-2 border-t border-gray-300 pt-2">
                            <div class="bg-gray-100 p-2 rounded mb-3 text-xs">
                                選択中: {endDate}
                            </div>
                            <div class="flex gap-2 justify-end">
                                <button
                                    type="button"
                                    class="py-1 px-2 border border-gray-300 rounded cursor-pointer text-xs bg-gray-500 text-white hover:bg-gray-600"
                                    onclick={() => isEndCalendarOpen = false}>キャンセル</button
                                >
                                <button
                                    type="button"
                                    class="py-1 px-2 border border-gray-300 rounded cursor-pointer text-xs bg-blue-500 text-white hover:bg-blue-700"
                                    onclick={confirmDate}>決定</button
                                >
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        </div>
        <PostalSearch bind:postalCode bind:prefecture bind:city bind:street />
        <div class="flex items-center gap-2 mb-3">
            <label class="block text-sm font-semibold min-w-[5.5rem]">番地</label>
            <input 
                class="px-3 py-0.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-gray-400 text-left text-sm w-[calc(92%-2.5rem)] min-w-0"
                bind:value={banti} 
                placeholder="例: 1-19-11" 
            />
        </div>
        <div class="flex items-center gap-2 mb-3">
            <label class="block text-sm font-semibold min-w-[5.5rem]">建物名/<br>部屋番号</label>
            <input
                class="px-3 py-0.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-gray-400 text-left text-sm w-[calc(92%-2.5rem)] min-w-0"
                bind:value={building}
                placeholder="例: パークウェルビル5F（任意）"
            />
        </div>
        <div class="flex items-center mb-1 -mt-2">
            <div class="min-w-[5.5rem]"></div>
            <small class="block text-xs text-gray-500 mt-1">マンション名や部屋番号がある場合は入力してください</small>
        </div>
        <div class="flex justify-end mb-2 pr-6">
            <button type="button" id="submitBtn" class="px-4 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 transition" onclick={() => HandleEvent?.()}>送信</button>
        </div>
    </form>
</div>

<style>
    /* フォーム用スタイル(あとで消す) */
    .bottom-sheet {
        position: fixed;
        bottom: -100%;
        left: 0;
        width: 100%;
        height: 76vh;
        margin: 0 auto;
        background: white;
        transition: bottom 0.3s ease;
        z-index: 800;
    }
    .bottom-sheet.open {
        bottom: 0;
    }
    .close-button {
        position: absolute;
        top: 10px;
        right: 16px;
        background: none;
        border: none;
        font-size: 20px;
        cursor: pointer;
        z-index: 1000;
    }
</style>