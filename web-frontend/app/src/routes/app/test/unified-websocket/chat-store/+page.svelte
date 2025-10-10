<script>
    import { classMessages } from "$lib/stores/classChatStore.js";
</script>

<div>
    {#each $classMessages as message}
        <p>{message.content}</p>
    {/each}
</div>