<script>
    import Page from "$lib/components/utils/page.svelte";
    import AnnouncementCard from "$lib/components/card/announcement/announcement.svelte";
    import { apiClient } from "$lib/services/django";
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    let { data } = $props();
    let path = $page.params;

    let announcements = $state([]);

    onMount(async () => {
        const response = await apiClient.get(`/announcement/announcements/class/${path.class}`);
        announcements = response;
    });
</script>

<Page>
    {#each announcements as announcement}
        <AnnouncementCard announcement={announcement} />
    {/each}
</Page>