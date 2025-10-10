<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import { Button } from 'flowbite-svelte';
    import { theme } from '$lib/theme.js';
    import { ChevronsUp, ChevronsDown } from 'lucide-svelte';

    const dispatch = createEventDispatcher();

    let title = $state('');
    let description = $state('');
    let start_datetime = $state('');
    let end_datetime = $state('');
    let location = $state('');
    let showInput = $state(true);

    async function handleSend() {
        try {
            await apiClient.post('/events/create', {
                title: title,
                description: description,
                start_datetime: start_datetime,
                end_datetime: end_datetime,
                location: location,
            });
            
            // 送信完了後に親コンポーネントに通知
            dispatch('eventSent');
            
            // 入力フィールドをクリア
            title = '';
            description = '';
            start_datetime = '';
            end_datetime = '';
            location = '';
        } catch (error) {
            console.error('イベントの送信に失敗しました:', error);
        }
    }
</script>

<div class="fixed bottom-0 left-0 right-0 z-50">
    {#if showInput}
        <div class="mx-auto max-w-2xl rounded-lg {$theme.card.background} {$theme.border.primary} shadow-lg">
            <!-- 開閉ボタン -->
            <div class="border-b {$theme.border.secondary}">
                <button 
                    class="w-full flex items-center justify-center gap-2 hover:cursor-pointer {$theme.background.secondary}"
                    onclick={() => { showInput = !showInput; }}
                >
                    <ChevronsDown class="w-4 h-4 transition-transform duration-200" />
                    <span>{showInput ? 'フォームを閉じる' : 'フォームを開く'}</span>
                </button>
            </div>
            
            <!-- フォーム部分 -->
            <div class="max-h-[60vh] overflow-y-auto">
                <div class="p-4 space-y-4">
                    <div>
                        <label for="title" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">イベントタイトル</label>
                        <input 
                            id="title" 
                            type="text" 
                            placeholder="イベントのタイトルを入力" 
                            bind:value={title}
                            class="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-0 {$theme.input.background} {$theme.input.border} {$theme.input.text}"
                        />
                    </div>
                    
                    <div>
                        <hr class="{$theme.border.secondary}" />
                    </div>
                    
                    <div>
                        <label for="description" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">イベント詳細</label>
                        <div class="rounded-md {$theme.background.secondary} {$theme.border.primary}">
                            <textarea 
                                id="description" 
                                placeholder="イベントの詳細を入力" 
                                rows="3" 
                                bind:value={description}
                                class="w-full px-3 py-2 border-none resize-none min-h-[60px] focus:outline-none focus:ring-0 {$theme.input.text}"
                            ></textarea>
                        </div>
                    </div>
                    
                    <div>
                        <hr class="{$theme.border.secondary}" />
                    </div>
                    
                    <div class="grid grid-cols-2 gap-4">
                        <div>
                            <label for="start_datetime" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">開始日時</label>
                            <input 
                                id="start_datetime" 
                                type="datetime-local" 
                                bind:value={start_datetime}
                                class="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-0 {$theme.input.background} {$theme.input.border} {$theme.input.text}"
                            />
                        </div>
                        
                        <div>
                            <label for="end_datetime" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">終了日時</label>
                            <input 
                                id="end_datetime" 
                                type="datetime-local" 
                                bind:value={end_datetime}
                                class="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-0 {$theme.input.background} {$theme.input.border} {$theme.input.text}"
                            />
                        </div>
                    </div>
                    
                    <div>
                        <hr class="{$theme.border.secondary}" />
                    </div>
                    
                    <div>
                        <label for="location" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">開催場所</label>
                        <input 
                            id="location" 
                            type="text" 
                            placeholder="開催場所を入力" 
                            bind:value={location}
                            class="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-0 {$theme.input.background} {$theme.input.border} {$theme.input.text}"
                        />
                    </div>
                    
                    <div>
                        <hr class="{$theme.border.secondary}" />
                    </div>
                    
                    <div class="flex flex-row gap-2 justify-end pb-2">
                        <Button onclick={handleSend} color="blue" class="hover:cursor-pointer">イベントを作成</Button>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="mx-auto max-w-2xl rounded-lg {$theme.card.background} {$theme.border.primary} shadow-lg">
            <button 
                color="light" 
                class="w-full flex items-center justify-center gap-2 h-10 {$theme.background.secondary} hover:cursor-pointer"
                onclick={() => { showInput = true; }}
            >
                <ChevronsUp class="w-4 h-4 transition-transform duration-200" />
                <span>イベントを追加</span>
            </button>
        </div>
    {/if}
</div>
