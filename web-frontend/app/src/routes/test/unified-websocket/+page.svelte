<script>
    import { announcements } from "$lib/stores/announcementStore.js";

    $inspect($announcements);
</script>

<div>
    {#each $announcements as announcement}
        <p>{announcement.message}</p>
        <p>{announcement.timestamp}</p>
    {/each}
</div>