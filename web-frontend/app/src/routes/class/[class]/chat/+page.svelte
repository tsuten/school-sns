<script>
    import { InitializeMessages, messages, disconnectFromChatWS } from "$lib/stores/chatWSStore.js";
    import Page from "$lib/components/utils/page.svelte";
    import { page } from "$app/stores";
    import { browser } from '$app/environment';
    import ChatCore from "$lib/components/shared/chat/chatCore.svelte";
    import Input from "$lib/components/utils/chat/input.svelte";
    let classId = $derived($page.params?.class);

    $inspect("messages", $messages);
    
    $effect(() => {
        if (browser && classId) {
            InitializeMessages("/chat/class-messages/" + classId, "/class/" + classId);
            
            return () => {
                disconnectFromChatWS("/class/" + classId);
            };
        }
    });
</script>

<Page class="flex flex-col h-full">
    <ChatCore messages={$messages} />
    <Input />
</Page>
