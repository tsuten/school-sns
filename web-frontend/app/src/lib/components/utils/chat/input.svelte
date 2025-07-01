<script>
    import { Button, Input, Dropdown, DropdownItem } from 'flowbite-svelte';
    import { Plus, Smile, ArrowUp, Image, Video, File, Camera } from 'lucide-svelte';

    let { 
        value = $bindable(''), 
        onKeydown,
        onSend,
        onFileSelect,
        disabled = false, 
        placeholder = 'メッセージを入力...',
        ...restProps 
    } = $props();

    let attachDropdown = [
        {
            icon: Image,
            accept: 'image/*',
            label: '画像',
            description: 'JPG, PNG, GIF',
            color: 'text-blue-500'
        },
        {
            icon: Video,
            accept: 'video/*',
            label: '動画',
            description: 'MP4, AVI, MOV',
            color: 'text-green-500'
        },
        {
            icon: Camera,
            accept: 'image/*',
            label: 'カメラ',
            description: '写真を撮影',
            color: 'text-purple-500'
        },
        {
            icon: File,
            accept: '*',
            label: 'ファイル',
            description: 'PDF, DOC, その他',
            color: 'text-gray-500'
        }
    ];

    let fileInput;

    function handleSend() {
        console.log('handleSend called, value:', value);
        console.log('onSend function exists:', !!onSend);
        if (onSend && value.trim()) {
            console.log('Calling onSend function');
            onSend();
        } else if (!value.trim()) {
            console.log('Empty message, not sending');
        } else if (!onSend) {
            console.log('onSend function not provided');
        }
    }

    function handleKeydown(event) {
        console.log('handleKeydown called, key:', event.key);
        if (onKeydown) {
            console.log('Calling onKeydown function');
            onKeydown(event);
        } else {
            console.log('onKeydown function not provided');
        }
    }

    function handleFileSelect(accept) {
        if (fileInput) {
            fileInput.accept = accept;
            fileInput.click();
        }
    }

    function handleFileChange(event) {
        const files = event.target.files;
        if (files && files.length > 0 && onFileSelect) {
            onFileSelect(files[0]);
        }
        // ファイル入力をリセット
        event.target.value = '';
    }
</script>

<div class="bg-white border-t border-gray-300 p-4">
    <div class="flex items-center gap-2">
        <!-- ファイル添付ボタン -->
        <Button 
            pill={true} 
            color="light" 
            class="p-2! hover:cursor-pointer flex-shrink-0"
            {disabled}
            id="file-attach-button"
        >
            <Plus class="h-5 w-5 text-gray-500" />
        </Button>
        
        <!-- ファイル添付ドロップダウン -->
        <Dropdown triggeredBy="#file-attach-button" class="w-48" placement="top" simple>
            {#each attachDropdown as item}
                <DropdownItem class="flex items-center gap-3 w-full px-4 py-3" onclick={() => handleFileSelect(item.accept)}>
                    <item.icon class="w-5 h-5 {item.color} flex-shrink-0" />
                    <div class="flex-1">
                        <div class="font-medium text-left">{item.label}</div>
                        <div class="text-xs text-gray-500 text-left">{item.description}</div>
                    </div>
                </DropdownItem>
            {/each}
        </Dropdown>

        <!-- 隠しファイル入力 -->
        <input 
            bind:this={fileInput}
            type="file" 
            class="hidden" 
            onchange={handleFileChange}
        />
        
        <!-- テキスト入力エリア -->
        <Input 
            bind:value
            onkeydown={handleKeydown}
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
            onclick={handleSend}
            disabled={!value?.trim() || disabled}
        >
            <ArrowUp class="h-5 w-5" />
        </Button>
    </div>
</div>