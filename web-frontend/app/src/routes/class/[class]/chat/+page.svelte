<script>
    import { InitializeMessages, messages, disconnectFromChatWS } from "$lib/stores/chatWSStore.js";
    import Page from "$lib/components/utils/page.svelte";
    import { page } from "$app/stores";
    import { browser } from '$app/environment';

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

<Page>
    <div class="flex flex-col gap-4">
        <h1 class="text-2xl font-bold">チャット</h1>
        {#each $messages as message}
            <div class="flex flex-col gap-2">
                <span class="text-sm text-gray-500">{message.content}</span>
            </div>
        {/each}
    </div>
</Page>
