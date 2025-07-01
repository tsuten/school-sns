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
    let isCalendarOpen = $state();
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

    // カレンダーポップアップの開閉を切り替える
    function toggleCalendar() {
        isCalendarOpen = !isCalendarOpen;
    }

    function changeMonth(offset) {
        currentCalendarDate = new Date(
            // 表示月を指定されたオフセット分移動
            currentCalendarDate.getFullYear(),
            currentCalendarDate.getMonth() + offset,
            1,
        );
        // 日、時、分は現在の選択値を維持して選択されている日時も月を合わせて更新
        startDateTime = new Date(
            currentCalendarDate.getFullYear(),
            currentCalendarDate.getMonth(),
            startDateTime.getDate(),
            hour,
            minute,
        );
        endDateTime = new Date(
            currentCalendarDate.getFullYear(),
            currentCalendarDate.getMonth(),
            endDateTime.getDate(),
            hour,
            minute,
        );
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
        const y = currentCalendarDate.getFullYear();
        const m = currentCalendarDate.getMonth() + 1;
        const d = calendarMode === "start" ? startDateTime.getDate() : endDateTime.getDate();
        const w = weekdays[currentCalendarDate.getDay()];
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
        updateSelectedDisplay();
        isCalendarOpen = false;
        if (calendarMode === "start") {
            startDateTime.setHours(hour, minute);
            updateSelectedDisplay();
        } else {
            endDateTime.setHours(hour, minute);
            updateSelectedDisplay();
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

    // カレンダーに表示するセル数を取得（6週間 × 7日 = 42セル）
    function getCalendarCells() {
        return 42;
    }

    // カレンダーを開く関数
    // modeは"start"または"end"を指定
    function openCalendar(mode) {
        calendarMode = mode;
        isCalendarOpen = true;
        if (mode === "start") {
            currentCalendarDate = new Date(startDateTime);
            hour = startDateTime.getHours();
            minute = startDateTime.getMinutes();
        } else {
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
        // console.log("イベント名:", eventName);
        // console.log("概要:", content);
        // console.log("開始日時:", startDateTime);
        // console.log("終了日時:", endDateTime);
        // console.log("Location:", postalCode+prefecture+city+street+banti+building);
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

<Child on:added={handleDataAdded} />

{#if valuesError_1 === true}
        <p>建物名・部屋番号以外の項目は全て入力してください</p>
    {/if}

<form onsubmit={(e) => e.preventDefault()}>
    <div class="overlay" onclick={() => onClose?.()} />
    <div class="bottom-sheet open">
        <button class="close-button" onclick={() => onClose?.()}>✕</button>

        <div>
            <label>イベント名</label>
            <input
                bind:value={eventName}
                placeholder="例: ドキドキマヤ文明鎮魂祭"
            />
        </div>

        <div>
            <label>概要</label>
            <input
                bind:value={content}
                placeholder="例: マヤ文明の魂を鎮魂します"
            />
        </div>

        <div class="calendar-container">
            <label>日時</label>
            <input
                class="calendar-input"
                readonly
                value={startDate}
                onclick={() => openCalendar("start")}
                placeholder="日時を選択してください"
            />

            <input type="hidden" name="start_datetime" value={startDate} required />

            {#if isCalendarOpen}
                <div class="calendar-popup">
                    <div class="calendar-header">
                        <button
                            type="button"
                            class="calendar-nav-btn"
                            onclick={() => changeMonth(-1)}>‹</button
                        >
                        <div class="calendar-title">
                            {currentCalendarDate.getFullYear()}年 {currentCalendarDate.getMonth() +
                                1}月
                        </div>
                        <button
                            type="button"
                            class="calendar-nav-btn"
                            onclick={() => changeMonth(1)}>›</button
                        >
                    </div>

                    <div class="calendar-weekdays">
                        {#each weekdays as day}
                            <div class="calendar-weekday">{day}</div>
                        {/each}
                    </div>

                    <div class="calendar-days">
                        {#each Array(getCalendarCells()) as _, index}
                            {#key index}
                                    <!-- svelte-ignore a11y_consider_explicit_label -->
                                    <!-- svelte-ignore a11y_consider_explicit_label -->
                                {#if index < getFirstDayOfMonth()}
                                    <button
                                        disabled
                                        class="calendar-day other-month"
                                    >
                                    </button>
                                {:else if index < getFirstDayOfMonth() + getDaysInMonth()}
                                    <button
                                        class="calendar-day"
                                        onclick={() =>
                                            selectDay(
                                                index -
                                                    getFirstDayOfMonth() +
                                                    1,
                                            )}
                                    >
                                        {index - getFirstDayOfMonth() + 1}
                                    </button>
                                {:else}
                                    <button
                                        disabled
                                        class="calendar-day other-month"
                                    >
                                    </button>
                                {/if}
                            {/key}
                        {/each}
                    </div>

                    <div class="time-selectors">
                            <!-- svelte-ignore a11y_label_has_associated_control -->
                            <!-- svelte-ignore a11y_label_has_associated_control -->
                        <div class="time-selector">
                            <label>時</label>
                            <select
                                bind:value={hour}
                                onchange={updateSelectedDisplay}
                            >
                                {#each Array(24) as _, h}
                                    <option value={h}
                                        >{String(h).padStart(2, "0")}時</option
                                    >
                                {/each}
                            </select>
                        </div>

                            <!-- svelte-ignore a11y_label_has_associated_control -->
                            <!-- svelte-ignore a11y_label_has_associated_control -->
                        <div class="time-selector">
                            <label>分</label>
                            <select
                                bind:value={minute}
                                onchange={updateSelectedDisplay}
                            >
                                {#each Array(12) as _, i}
                                    <option value={i * 5}
                                        >{String(i * 5).padStart(
                                            2,
                                            "0",
                                        )}分</option
                                    >
                                {/each}
                            </select>
                        </div>
                    </div>

                    <div class="calendar-confirmation">
                        <div class="selected-datetime">
                            選択中: {startDate}
                        </div>

                        <div class="calendar-buttons">
                            <button
                                type="button"
                                class="calendar-btn primary"
                                onclick={toggleCalendar}>キャンセル</button
                            >
                            <button
                                type="button"
                                class="calendar-btn primary"
                                onclick={confirmDate}>決定</button
                            >
                        </div>
                    </div>
                </div>
            {/if}
        </div>
        <hr />
        <br>
        <div class="calendar-container">
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label>終了日時</label>
            <input
                class="calendar-input"
                readonly
                value={endDate}
                onclick={() => openCalendar("end")}
                placeholder="日時を選択してください"
            />

            <input type="hidden" name="end_datetime" value={endDate} required />

            {#if isCalendarOpen}
                <div class="calendar-popup">
                    <div class="calendar-header">
                        <button
                            type="button"
                            class="calendar-nav-btn"
                            onclick={() => changeMonth(-1)}>‹</button
                        >
                        <div class="calendar-title">
                            {currentCalendarDate.getFullYear()}年 {currentCalendarDate.getMonth() +
                                1}月
                        </div>
                        <button
                            type="button"
                            class="calendar-nav-btn"
                            onclick={() => changeMonth(1)}>›</button
                        >
                    </div>

                    <div class="calendar-weekdays">
                        {#each weekdays as day}
                            <div class="calendar-weekday">{day}</div>
                        {/each}
                    </div>

                    <div class="calendar-days">
                        {#each Array(getCalendarCells()) as _, index}
                            {#key index}
                                {#if index < getFirstDayOfMonth()}
                                    <button
                                        disabled
                                        class="calendar-day other-month"
                                    >
                                    </button>
                                {:else if index < getFirstDayOfMonth() + getDaysInMonth()}
                                    <button
                                        class="calendar-day"
                                        onclick={() =>
                                            selectDay(
                                                index -
                                                    getFirstDayOfMonth() +
                                                    1,
                                            )}
                                    >
                                        {index - getFirstDayOfMonth() + 1}
                                    </button>
                                {:else}
                                    <button
                                        disabled
                                        class="calendar-day other-month"
                                    >
                                    </button>
                                {/if}
                            {/key}
                        {/each}
                    </div>

                    <div class="time-selectors">
                        <div class="time-selector">
                            <label>時</label>
                            <select
                                bind:value={hour}
                                onchange={updateSelectedDisplay}
                            >
                                {#each Array(24) as _, h}
                                    <option value={h}
                                        >{String(h).padStart(2, "0")}時</option
                                    >
                                {/each}
                            </select>
                        </div>

                        <div class="time-selector">
                            <label>分</label>
                            <select
                                bind:value={minute}
                                onchange={updateSelectedDisplay}
                            >
                                {#each Array(12) as _, i}
                                    <option value={i * 5}
                                        >{String(i * 5).padStart(
                                            2,
                                            "0",
                                        )}分</option
                                    >
                                {/each}
                            </select>
                        </div>
                    </div>

                    <div class="calendar-confirmation">
                        <div class="selected-datetime">
                            選択中: {endDate}
                        </div>

                        <div class="calendar-buttons">
                            <button
                                type="button"
                                class="calendar-btn primary"
                                onclick={toggleCalendar}>キャンセル</button
                            >
                            <button
                                type="button"
                                class="calendar-btn primary"
                                onclick={confirmDate}>決定</button
                            >
                        </div>
                    </div>
                </div>
            {/if}
        </div>
        <hr />
        <br>
        <PostalSearch bind:postalCode bind:prefecture bind:city bind:street />

        <div>
            <label>番地</label>
            <input bind:value={banti} required placeholder="例: 1-19-11" />
        </div>

        <div>
            <label>建物名・部屋番号</label>
            <input
                bind:value={building}
                placeholder="例: パークウェルビル5F（任意）"
            />
            <small>マンション名や部屋番号がある場合は入力してください</small>
        </div>

        <button type="button" id="submitBtn" onclick={() => HandleEvent?.()}>送信</button>
    </div>
</form>

<style>
    /* カレンダー用スタイル */
    .calendar-confirmation {
        margin-top: 12px;
        border-top: 1px solid #ddd;
        padding-top: 12px;
    }

    .calendar-container {
        position: fixed;
        display: inline-block;
        width: 100%;
        justify-content: flex-end;
    }

    .calendar-input {
        position: absolute;
        background-color: #f8f9fa;
    }

    .calendar-popup {
        position: fixed;
        top: 0;
        right: 0;
        z-index: 1000;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 16px;
        width: 320px;
    }

    .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }

    .calendar-nav-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 8px;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }

    .calendar-nav-btn:hover {
        background-color: #f0f0f0;
    }

    .calendar-title {
        font-size: 16px;
        font-weight: bold;
    }

    .calendar-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
        margin-bottom: 8px;
    }

    .calendar-weekday {
        text-align: center;
        font-size: 12px;
        font-weight: bold;
        color: #666;
        padding: 8px 4px;
    }

    .calendar-days {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 2px;
        margin-bottom: 16px;
    }

    .calendar-day {
        width: 36px;
        height: 36px;
        border: none;
        background: none;
        cursor: pointer;
        border-radius: 4px;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
    }

    .calendar-day:hover {
        background-color: #e3f2fd;
    }

    .calendar-day.other-month {
        color: #ccc;
    }

    .calendar-day.selected {
        background-color: #2196f3;
        color: white;
    }

    .calendar-day.today {
        background-color: #e1f5fe;
        color: #0277bd;
        font-weight: bold;
    }

    .time-selectors {
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
    }

    .time-selector {
        flex: 1;
    }

    .time-selector label {
        display: block;
        margin-bottom: 4px;
        font-size: 12px;
        font-weight: bold;
    }

    .time-selector select {
        width: 100%;
        padding: 4px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    .selected-datetime {
        background-color: #f5f5f5;
        padding: 12px;
        border-radius: 4px;
        margin-bottom: 16px;
        font-size: 14px;
    }

    .calendar-buttons {
        display: flex;
        gap: 8px;
        justify-content: flex-end;
    }

    .calendar-btn {
        padding: 6px 12px;
        border: 1px solid #ddd;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
    }

    .calendar-btn.primary {
        background-color: #2196f3;
        color: white;
        border-color: #2196f3;
    }

    .calendar-btn:hover {
        background-color: #f0f0f0;
    }

    .calendar-btn.primary:hover {
        background-color: #1976d2;
    }

    /* フォーム用スタイル(あとで消す) */

    .overlay {
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 40;
    }

    .bottom-sheet {
        position: fixed;
        bottom: -100%;
        left: 0;
        width: 100%;
        height: 47vh;
        margin: 0 auto;
        background: white;
        transition: bottom 0.3s ease;
        z-index: 50;
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
    }
</style>
