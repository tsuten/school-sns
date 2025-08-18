<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import { Button } from 'flowbite-svelte';

    const dispatch = createEventDispatcher();

    let title = $state('');
    let content = $state('');

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

<div class="flex flex-col gap-4">
    <div class="bg-white rounded-lg border border-gray-300 p-4">
        <div class="space-y-4">
            <div>
                <label for="title" class="block text-sm font-medium text-gray-700 mb-2">タイトル</label>
                <input 
                    id="title" 
                    type="text" 
                    placeholder="タイトルを入力" 
                    bind:value={title}
                    class="w-full px-3 py-2 bg-transparent text-gray-900 placeholder-gray-500 border-none focus:border-none focus:outline-none focus:ring-0"
                />
            </div>
            
            <div class="border-t border-gray-100 pt-4">
                <label for="content" class="block text-sm font-medium text-gray-700 mb-2">メモ内容</label>
                <textarea 
                    id="content" 
                    placeholder="メモの内容を入力" 
                    rows="4" 
                    bind:value={content}
                    class="w-full px-3 py-2 bg-transparent text-gray-900 placeholder-gray-500 resize-y min-h-[100px] border-none focus:border-none focus:outline-none focus:ring-0"
                ></textarea>
            </div>
            
            <div class="border-t border-gray-100 pt-4">
                <Button onclick={handleSend} class="w-full">送信</Button>
            </div>
        </div>
    </div>
</div>