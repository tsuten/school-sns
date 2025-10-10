<script>
    import { InitializeMessages, messages, disconnectFromChatWS } from "$lib/stores/chatWSStore.js";
    import Page from "$lib/components/utils/page.svelte";
    import { page } from "$app/stores";
    import { browser } from '$app/environment';
    import ChatCore from "$lib/components/shared/chat/chatCore.svelte";
    import ChatInput from "$lib/components/shared/chat/chatInput.svelte";
    import InPageSideBar from "$lib/components/page-components/inPageSideBar.svelte";
    let classId = $derived($page.params?.class);

    $inspect("messages", $messages);
    
    $effect(() => {
        if (browser && classId) {
            InitializeMessages("/room-messages/class/" + classId, "/class/" + classId);
            
            return () => {
                disconnectFromChatWS("/class/" + classId);
            };
        }
    });
</script>

<div class="flex flex-row w-full h-full">
    <InPageSideBar data={$messages} currentCircleId={classId} />
    <div class="flex-1 flex flex-col relative h-full w-full">
        <ChatCore messages={$messages} />
        <ChatInput apiPath="/room-messages/class/" />
    </div>
</div>
