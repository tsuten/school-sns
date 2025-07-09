<script>
    /** @type {{ data: import('./$types').PageData }} */
    import NotificationCard from "$lib/components/card/notification/notificationCard.svelte";
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { MessageCircle, OctagonAlert } from "lucide-svelte";
    import Page from "$lib/components/utils/page.svelte";
    let { data } = $props();

    let notifications = $state();
    let filterType = $state();

    const filtered = $derived(() => {
        return filterType
            ? notifications.filter((n) => n.type === filterType)
            : notifications;
    });

    onMount(async () => {
        const response = await apiClient.get(
            "/notifications/notifications",
            {},
        );

        notifications = response;

        // for (let i = 0; i < response.length; i++) {
        //     console.log(response[i].id);
        //     console.log(response[i].content);
        //     console.log(response[i].is_read);
        //     console.log(response[i].created_at);
        //     console.log(response[i].type);
        //     console.log(
        //         "--------------------------------------------------------------",
        //     );
        // }
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
        {#each notifications as i}
            <NotificationCard notification={i} />
        {/each}
        {:else}
        {#each filtered as i}
            <NotificationCard notification={i} />
        {/each}
        {/if}
    </div>
</Page>
