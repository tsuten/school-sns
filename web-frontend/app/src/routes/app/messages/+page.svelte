<script>
    import { MessageSquare, ArrowLeft } from 'lucide-svelte';
    import { Button } from 'flowbite-svelte';
</script>

<div class="flex flex-col items-center justify-center h-full w-full bg-gray-50">
    <div class="max-w-md mx-auto text-center p-8">
        <div class="mb-6">
            <MessageSquare class="w-16 h-16 text-gray-400 mx-auto mb-4" />
        </div>
        
        <h2 class="text-2xl font-bold text-gray-800 mb-2">メッセージ</h2>
        <p class="text-gray-600 mb-6">
            左側のサイドバーからユーザーを選択して<br />
            会話を開始してください
        </p>
        
        <div class="text-sm text-gray-500">
            <p>💡 ヒント: 過去にメッセージを交換したユーザーが表示されます</p>
        </div>
    </div>
</div>