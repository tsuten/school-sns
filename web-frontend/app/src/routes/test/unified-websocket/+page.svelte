<script>
    import { messages } from "$lib/stores/unifiedBaseWSStore.js";

    $inspect($messages);
</script>

<div>
    {#each $messages as message}
        <p>{message.data}</p>
        <p>{message.timestamp}</p>
    {/each}
</div>