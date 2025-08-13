<script>
    import { onMount } from 'svelte';
    import { apiClient } from '$lib/services/django';
    import Announcement from '$lib/components/card/announcement/announcement.svelte';
    import Page from '$lib/components/utils/page.svelte';
    /** @type {import('./$types').PageProps} */
    let { data } = $props();

    let announcements = $state([]);

    onMount(async () => {
        const response = await apiClient.get('/feed/');
        announcements = response.data;
    });
</script>

<Page>
    <div class="flex flex-col gap-4">
    {#each announcements as announcement}
        <Announcement {announcement} />
    {/each}
    </div>
</Page>