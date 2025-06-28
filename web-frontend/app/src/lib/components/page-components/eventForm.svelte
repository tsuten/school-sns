<script>
    // svelte系の定義
    import { onMount } from "svelte";
    import PostalSearch from "$lib/components/page-components/postalSearch.svelte";

    // 使う変数
    let postalCode = "";
    let prefecture = "";
    let city = "";
    let street = "";

    let eventName = "";
    let content = "";
    let selectedDate = "";
    let selectedDateTime = new Date();
    let isCalendarOpen = false;
    let currentCalendarDate = new Date();
    let hour = selectedDateTime.getHours();
    let minute = Math.floor(selectedDateTime.getMinutes() / 5) * 5;
    let banti = "";
    let building = "";

    // 表示の制御用の関数
    export let onClose;

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
        selectedDateTime = now;
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
        selectedDateTime = new Date(
            currentCalendarDate.getFullYear(),
            currentCalendarDate.getMonth(),
            selectedDateTime.getDate(),
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
        // 選択された日付で日時を更新　(時、分は維持)
        selectedDateTime = new Date(
            currentCalendarDate.getFullYear(),
            currentCalendarDate.getMonth(),
            day,
            hour,
            minute,
        );
        // update関数を呼び出し
        updateSelectedDisplay();
    }

    //updateする関数
    function updateSelectedDisplay() {
        // ユーザーが選んだセルに合わせてデータを取得し代入
        const y = selectedDateTime.getFullYear();
        const m = selectedDateTime.getMonth() + 1;
        const d = selectedDateTime.getDate();
        const w = weekdays[selectedDateTime.getDay()];
        const h = hour.toString().padStart(2, "0");
        const min = minute.toString().padStart(2, "0");
        // 表示データに取得したデータを入れて表示
        selectedDate = `${y}年${m}月${d}日(${w}) ${h}:${min}`;
    }

    function confirmDate() {
        updateSelectedDisplay();
        isCalendarOpen = false;
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

</script>

<form onsubmit={(e) => e.preventDefault()}>
    <div class="overlay" onclick={() => onClose?.()} />
    <div class="bottom-sheet open">
        <button class="close-button" onclick={() => onClose?.()}>✕</button>

        <div>
            <label>イベント名</label>
            <input
                bind:value={eventName}
                required
                placeholder="例: ドキドキマヤ文明鎮魂祭"
            />
        </div>

        <div>
            <label>概要</label>
            <input
                bind:value={content}
                required
                placeholder="例: マヤ文明の魂を鎮魂します"
            />
        </div>

        <div class="calendar-container">
            <label>日時</label>
            <input
                class="calendar-input"
                readonly
                value={selectedDate}
                onclick={toggleCalendar}
                placeholder="日時を選択してください"
            />

            <input
                type="hidden"
                name="datetime"
                value={selectedDate}
                required
            />

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
                            選択中: {selectedDate}
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

        <button type="button" id="submitBtn">送信</button>
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
        height: 90vh;
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
