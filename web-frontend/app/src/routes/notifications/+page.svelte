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
    let isFilter = $state(false);
    let filterTyped = $state();
    let filteredNotifications = $state([]);

    // 何をしているのかわからない関数
    function notificationsFilter(type){
        if (isFilter == true && filterTyped == type ) {
            isFilter = false;
            return;
        }
        
        // filteredを初期化
        filteredNotifications = []
        for (const notification of notifications) {
            // 気合でフィルタリング
            if (notification.type == type){
                filteredNotifications.push(notification)
            }
         }
        console.log(filteredNotifications)
        // フィルタリングが行われたので表示のためにtrue
        isFilter = true
        filterTyped = type
    }

    onMount(async () => {
        const response = await apiClient.get("/notifications/notifications");

        notifications = response.reverse();
        console.log(notifications)

        connectTestWS();
    });
</script>

<Page>
    <div class="flex flex-col gap-4">
        <div class="flex gap-4 justify-center">
            <button
                class="hover:scale-110 transition text-center"
                onclick={() => (notificationsFilter("message"))}
            >
                <MessageCircle />
            </button>
            <button class="hover:scale-110 transition text-center" onclick={() => (notificationsFilter("announcement"))}>
                <OctagonAlert />
            </button>
        </div>
                 
        {#if isFilter == false}
            {#each wsNotificationsReversed as i}
                <NotificationCard notification={i} />
            {/each}
            {#each notifications as i}
                <NotificationCard notification={i} />
            {/each}
        {:else}
            {#each wsNotificationsReversed as i}
                <NotificationCard notification={i} />
            {/each}
            {#each filteredNotifications as i}
                <NotificationCard notification={i} />
            {/each}
        {/if}
    </div>
</Page>