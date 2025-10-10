<script>
    import { createEventDispatcher } from 'svelte';
    import { apiClient } from '$lib/services/django.js';
    import { Button } from 'flowbite-svelte';
    
    const dispatch = createEventDispatcher();
    
    let title = $state('');
    let description = $state('');
    let isAllDay = $state(false);
    let startTime = $state('');
    let endTime = $state('');
    let isLoading = $state(false);
    let error = $state(null);
    let success = $state(false);
    
    // 現在の日時をデフォルト値として設定
    $effect(() => {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        startTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        endTime = `${year}-${month}-${day}T${hours}:${minutes}`;
    });
    
    // フォーム送信処理
    async function handleSubmit() {
        if (!title.trim()) {
            error = 'タイトルは必須です';
            return;
        }
        
        try {
            isLoading = true;
            error = null;
            success = false;
            
            const scheduleData = {
                title: title.trim(),
                description: description.trim(),
                is_all_day: isAllDay,
                start_time: isAllDay ? null : startTime,
                end_time: isAllDay ? null : endTime
            };
            
            console.log('スケジュール作成データ:', scheduleData);
            
            const response = await apiClient.post('/calendar/new-schedules', scheduleData);
            
            console.log('作成されたスケジュール:', response);
            
            // 成功時の処理
            success = true;
            resetForm();
            
            // 親コンポーネントに作成完了を通知
            dispatch('scheduleCreated', response);
            
        } catch (err) {
            console.error('スケジュール作成エラー:', err);
            error = err.message || 'スケジュールの作成に失敗しました';
        } finally {
            isLoading = false;
        }
    }
    
    // フォームリセット
    function resetForm() {
        title = '';
        description = '';
        isAllDay = false;
        startTime = '';
        endTime = '';
        error = null;
        success = false;
    }
    
    // 全日スケジュールの切り替え
    function toggleAllDay() {
        isAllDay = !isAllDay;
        if (isAllDay) {
            startTime = '';
            endTime = '';
        } else {
            // 現在時刻を設定
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            startTime = `${year}-${month}-${day}T${hours}:${minutes}`;
            endTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
    }
</script>

<div class="bg-white rounded-lg border border-gray-300 p-6 w-80">
    <h3 class="text-lg font-semibold mb-4 text-gray-800">新しいスケジュール</h3>
    
    <form onsubmit={handleSubmit} class="space-y-4">
        <!-- タイトル -->
        <div>
            <label for="title" class="block text-sm font-medium text-gray-700 mb-1">
                タイトル
            </label>
            <input
                id="title"
                type="text"
                bind:value={title}
                placeholder="スケジュールのタイトル"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
            />
        </div>
        
        <!-- 説明 -->
        <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-1">
                説明
            </label>
            <textarea
                id="description"
                bind:value={description}
                placeholder="スケジュールの詳細説明"
                rows="3"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
        </div>
        
        <!-- 開始時刻 -->
        {#if !isAllDay}
            <div>
                <label for="startTime" class="block text-sm font-medium text-gray-700 mb-1">
                    開始時刻
                </label>
                <input
                    id="startTime"
                    type="datetime-local"
                    bind:value={startTime}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>
        {/if}
        
        <!-- 終了時刻 -->
        {#if !isAllDay}
            <div>
                <label for="endTime" class="block text-sm font-medium text-gray-700 mb-1">
                    終了時刻
                </label>
                <input
                    id="endTime"
                    type="datetime-local"
                    bind:value={endTime}
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
            </div>
        {/if}
        
        <!-- エラーメッセージ -->
        {#if error}
            <div class="text-red-600 text-sm bg-red-50 p-3 rounded-md">
                {error}
            </div>
        {/if}
        
        <!-- 成功メッセージ -->
        {#if success}
            <div class="text-green-600 text-sm bg-green-50 p-3 rounded-md">
                スケジュールが正常に作成されました！
            </div>
        {/if}
        
        <!-- 送信ボタン -->
        <Button
            type="submit"
            disabled={isLoading}
            class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
            {isLoading ? '作成中...' : 'スケジュール作成'}
        </Button>
    </form>
</div>
