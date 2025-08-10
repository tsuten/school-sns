<script>
    import Page from "$lib/components/utils/page.svelte";
    import AnnouncementCard from "$lib/components/card/announcement/announcement.svelte";
    import { InitializeAnnouncements } from "$lib/stores/announcementStore.js";
    import { announcements } from "$lib/stores/announcementStore.js";
    import { page } from "$app/stores";
    import { onMount } from "svelte";
    let { data } = $props();
    let path = $page.params;

    onMount(async () => {
        await InitializeAnnouncements(path.class);
    });
</script>

<Page>
    {#each $announcements as announcement}
        <AnnouncementCard announcement={announcement} />
    {/each}
</Page>