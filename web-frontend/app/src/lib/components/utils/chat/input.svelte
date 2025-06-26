<script>
    import { Button, Input } from 'flowbite-svelte';
    import { Plus, Smile, ArrowUp } from 'lucide-svelte';

    let { 
        value = $bindable(''), 
        onKeydown,
        onSend,
        disabled = false, 
        placeholder = 'メッセージを入力...',
        ...restProps 
    } = $props();

    function handleSend() {
        if (onSend && value.trim()) {
            onSend();
        }
    }

    $inspect(value);
</script>

<div class="bg-white border-t border-gray-300 p-4">
    <div class="flex items-center gap-2">
        <!-- ファイル添付ボタン -->
        <Button 
            pill={true} 
            color="light" 
            class="p-2! hover:cursor-pointer flex-shrink-0"
            {disabled}
        >
            <Plus class="h-5 w-5 text-gray-500" />
        </Button>
        
        <!-- テキスト入力エリア -->
        <Input 
            bind:value
            on:keydown={onKeydown}
            {placeholder}
            {disabled}
            class="rounded-sm bg-white border-gray-300"
            {...restProps}
        />
        
        <!-- 絵文字ボタン -->
        <Button 
            pill={true} 
            color="light" 
            class="p-2! hover:cursor-pointer flex-shrink-0"
            {disabled}
        >
            <Smile class="h-5 w-5 text-gray-500" />
        </Button>
        
        <!-- 送信ボタン -->
        <Button 
            pill={true}
            color="blue" 
            class="p-2! hover:cursor-pointer flex-shrink-0"
            on:click={handleSend}
            disabled={!value?.trim() || disabled}
        >
            <ArrowUp class="h-5 w-5" />
        </Button>
    </div>
</div>