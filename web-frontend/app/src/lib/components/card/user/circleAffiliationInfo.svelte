<script>
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    import { apiClient } from '$lib/services/django';
    import { onMount } from 'svelte';

    let { user } = $props();
    let circles = $state(null);
    
    onMount(async () => {
        const response = await apiClient.get(`/circle/user/${user.user_id}`);
        circles = response;
    });
</script>

<BaseCard>
    <div class="flex flex-col gap-2">
        <h2 class="text-md font-bold">所属サークル</h2>
        {#if circles}
            {#each circles as circle}
                <p>{circle.name}</p>
            {/each}
        {/if}
    </div>
</BaseCard>