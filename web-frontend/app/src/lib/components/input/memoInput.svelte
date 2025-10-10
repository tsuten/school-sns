<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import { Button } from 'flowbite-svelte';
    import { theme } from '$lib/theme.js';
    import { ChevronsUp, ChevronsDown } from 'lucide-svelte';

    const dispatch = createEventDispatcher();

    let title = $state('');
    let content = $state('');
    let showInput = $state(true);

    async function handleSend() {
        try {
            await apiClient.post('/memo/', {
                title: title,
                content: content,
            });
            
            // 送信完了後に親コンポーネントに通知
            dispatch('memoSent');
            
            // 入力フィールドをクリア
            title = '';
            content = '';
        } catch (error) {
            console.error('メモの送信に失敗しました:', error);
        }
    }
</script>

<div class="flex flex-col">
    {#if showInput}
        <div class="rounded-lg {$theme.card.background} {$theme.border.primary}">
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
            <div class="p-4">
                <div class="space-y-4">
                    <div>
                        <label for="title" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">タイトル</label>
                        <input 
                            id="title" 
                            type="text" 
                            placeholder="タイトルを入力" 
                            bind:value={title}
                            class="w-full px-3 py-2 rounded-md focus:outline-none focus:ring-0 {$theme.input.background} {$theme.input.border} {$theme.input.text}"
                        />
                    </div>
                    
                    <div>
                        <hr class="{$theme.border.secondary}" />
                    </div>
                    
                    <div>
                        <label for="content" class="block text-sm font-medium mb-2 {$theme.text.tertiary}">メモ内容</label>
                        <div class="rounded-md {$theme.background.secondary} {$theme.border.primary}">
                            <textarea 
                                id="content" 
                                placeholder="メモの内容を入力" 
                                rows="6" 
                                bind:value={content}
                                class="w-full px-3 py-2 border-none resize-none min-h-[120px] focus:outline-none focus:ring-0 {$theme.input.text}"
                            ></textarea>
                        </div>
                    </div>
                    
                    <div>
                        <hr class="{$theme.border.secondary}" />
                    </div>
                    
                    <div class="flex flex-row gap-2 justify-end">
                        <Button onclick={handleSend} color="blue" class="hover:cursor-pointer">メモを作成</Button>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="rounded-lg {$theme.card.background} {$theme.border.primary}">
            <button 
                color="light" 
                class="w-full flex items-center justify-center gap-2 h-10 {$theme.background.secondary} hover:cursor-pointer"
                onclick={() => { showInput = true; }}
            >
                <ChevronsUp class="w-4 h-4 transition-transform duration-200" />
                <span>メモを追加</span>
            </button>
        </div>
    {/if}
</div>