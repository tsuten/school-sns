<script>
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    let { user } = $props();
    let affiliation = $state(null);
    let isLoading = $state(false);
    let error = $state(null);

    onMount(async () => {
        try {
            isLoading = true;
            error = null;
            
            const response = await apiClient.get('/users/affiliation');
            
            // レスポンスを状態に設定
            affiliation = response;

            console.log(affiliation);
            
        } catch (err) {
            console.error('Error fetching affiliation:', err);
            error = 'データの取得に失敗しました: ' + (err.message || 'Unknown error');
        } finally {
            isLoading = false;
        }
    });

</script>

<BaseCard>
    <div class="flex flex-col gap-2">
        <h2 class="text-md font-bold">所属情報</h2>
        {#if affiliation}
            {#each affiliation.classes as class_}
                <p>{class_.name}</p>
            {/each}
            {#each affiliation.schools as school_}
                <p>{school_.name}</p>
            {/each}
        {/if}
    </div>
</BaseCard>