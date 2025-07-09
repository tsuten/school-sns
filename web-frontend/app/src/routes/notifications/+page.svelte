<script>
    /** @type {{ data: import('./$types').PageData }} */
    import NotificationCard from '$lib/components/card/notification/notificationCard.svelte';
    let { data } = $props();
</script>

<div class="flex flex-col gap-4">
    <div class="flex flex-col gap-2">
        <h1 class="text-2xl font-bold">通知</h1>
    </div>
    <NotificationCard />
</div>