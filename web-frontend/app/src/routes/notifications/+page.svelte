<script>
    /** @type {{ data: import('./$types').PageData }} */
    import NotificationCard from "$lib/components/card/notification/notificationCard.svelte";
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { MessageCircle, OctagonAlert } from "lucide-svelte";
    import Page from "$lib/components/utils/page.svelte";
    import { connectTestWS, Notifications as wsNotifications } from "$lib/stores/notificationWSStore.js";
    let { data } = $props();

    let wsNotificationsReversed = $state([]);

    // subscribeの代わりに$effectを使用してリアクティブに監視
    $effect(() => {
        wsNotificationsReversed = $wsNotifications.reverse();
    });

    let notifications = $state([]);
    let filterType = $state();

    // 何をしているのかわからない -> 消していいすか？
    const filtered = $derived(() => {
        return filterType
            ? notifications.filter((n) => n.type === filterType)
            : notifications;
    });

    onMount(async () => {
        const response = await apiClient.get("/notifications/notifications");

        notifications = response.reverse();

        connectTestWS();
    });

</script>

<Page>
    <div class="flex flex-col gap-4">
        <div class="flex gap-4 justify-center">
            <button
                class="hover:scale-110 transition text-center"
                onclick={() => (filterType = "message")}
            >
                <MessageCircle />
            </button>
            <div class="hover:scale-110 transition text-center">
                <OctagonAlert />
            </div>
        </div>
        
        {#if filterType == null}
            {#each wsNotificationsReversed as i}
                <NotificationCard notification={i} />
            {/each}
            {#each notifications as i}
                <NotificationCard notification={i} />
            {/each}
        {/if}
    </div>
</Page>
