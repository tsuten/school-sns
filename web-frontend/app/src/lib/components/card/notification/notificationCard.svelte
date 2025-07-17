<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import { getCurrentDateNormalized } from "$lib/utils/datetimeNormalize";
    import {
        MessageCircle,
        OctagonAlert,
        Clock,
        X,
    } from "lucide-svelte";
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";
    import { datetimeNormalize } from "$lib/utils/datetimeNormalize";
    import { Button } from "flowbite-svelte";
    let { notification } = $props()

    function getNotificationIcon(type) {
        switch (type) {
            case "message":
                return MessageCircle;
            case "announcement":
                return OctagonAlert;
            default:
                return MessageCircle;
        }
    }

    function getNotificationType(type) {
        switch (type) {
            case "message":
                return "メッセージ";
            case "announcement":
                return "お知らせ";
            default:
                return "メッセージ";
        }
    }
</script>
<BaseCard>
    <div class="flex flex-row justify-between">
        <div class="flex flex-row gap-2">
            <svelte:component this={getNotificationIcon(notification.type)} class="w-12 h-12" />
            <div class="flex flex-col gap-1">
                <div class="text-sm text-gray-500">
                    <p class="">{getNotificationType(notification.type)}</p>
                </div>
                <p class="max-w-[60ch] break-words whitespace-normal leading-relaxed">{notification.content}</p>
            </div>
        </div>
        <div class="flex flex-col gap-1 justify-between">
            <div class="flex flex-row gap-1 items-center self-end">
                <Button color="light" size="sm" pill class="!p-1 hover:cursor-pointer">
                    <X class="w-6 h-6" />
                </Button>
            </div>
            <div class="flex flex-row gap-1 items-center self-end text-sm text-gray-500">
                <Clock class="w-4 h-4" />
                {datetimeNormalize(notification.created_at)}
            </div>
        </div>
    </div>
</BaseCard>
