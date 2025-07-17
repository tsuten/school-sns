<script>
    import { testWSStore, connectTestWS } from '$lib/stores/testWSStore.js';
    import { onMount } from 'svelte';

    onMount(() => {
        console.log('onMount');
        connectTestWS();
    });

    $effect(() => {
        console.log($testWSStore);
    });
</script>

<div>
    {#each $testWSStore as message}
        <p>{message.message}</p>
    {/each}
</div>
