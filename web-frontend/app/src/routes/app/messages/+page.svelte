<script>
    import { MessageSquare, ArrowLeft } from 'lucide-svelte';
    import { Button } from 'flowbite-svelte';
    import { theme } from '$lib/theme.js';
</script>

<div class="flex flex-col items-center justify-center h-full w-full {$theme.secondary}">
    <div class="max-w-md mx-auto text-center p-8">
        <div class="">
            <MessageSquare class="w-16 h-16 mx-auto mb-2 {$theme.text.tertiary}" />
        </div>
        
        <h2 class="text-2xl font-bold mb-4 {$theme.text.tertiary}">メッセージ</h2>
        <p class="mb-6 {$theme.text.tertiary}">
            左側のサイドバーからユーザーを選択して<br />
            会話を開始してください
        </p>
    </div>
</div>