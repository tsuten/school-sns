<script>
    import { Bell } from "lucide-svelte";
    import { Notifications as wsNotifications } from "$lib/stores/notificationWSStore.js";
</script>

<div class="flex flex-col gap-2 w-80 p-4">
    <div class="flex items-center gap-2">
        <Bell class="w-4 h-4" />
        <span class="text-sm font-medium">Notifications</span>
    </div>
    <div class="flex flex-col gap-2 h-40 overflow-y-auto">
        {#each $wsNotifications as notification}
            <div class="flex items-center gap-2">
                <Bell class="w-4 h-4" />
                <span class="text-sm font-medium whitespace-nowrap overflow-hidden text-ellipsis">{notification.content}</span>
            </div>
        {/each}
    </div>
</div>