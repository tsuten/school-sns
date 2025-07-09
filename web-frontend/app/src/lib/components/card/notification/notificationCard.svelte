<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import { getCurrentDateNormalized } from "$lib/utils/datetimeNormalize";
    import {
        MessageCircle,
        OctagonAlert
    } from "lucide-svelte";
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";
    import { datetimeNormalize } from "$lib/utils/datetimeNormalize";

    let { notification } = $props()
</script>
<BaseCard>
    <div class="">
        {#if notification.type == "message"}
            <MessageCircle />
        {:else if notification.type == "announcement"}
            <OctagonAlert />
        {/if}

    </div>
    <div class="">
        {datetimeNormalize(notification.created_at)}
    </div>
    <div>
        {notification.content}
    </div>
</BaseCard>
