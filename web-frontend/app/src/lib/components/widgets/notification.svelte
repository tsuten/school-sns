<!-- TODO: 横幅の表示制限を親コンポーネントの幅に沿って動的に変える -->

<script>
    import WidgetBase from "./widgetBase.svelte";
    import {
        MessageCircle,
        Heart,
        Vote,
        Calendar,
        Key,
        Bell,
    } from "lucide-svelte";
    import { Badge } from "flowbite-svelte";
    import { Notifications } from "$lib/stores/notificationWSStore.js";
    import dayjs from "dayjs";
    import relativeTime from "dayjs/plugin/relativeTime";
    import "dayjs/locale/ja";

    dayjs.extend(relativeTime);
    dayjs.locale("ja");

    let reversedNotifications = $derived([...$Notifications].reverse());
</script>

<WidgetBase title="通知" icon={Bell} href="/notifications">
    {#snippet snippet()}
        <ul class="flex flex-col gap-1 w-full">
            {#each reversedNotifications.slice(0, 5) as notification}
                <a href={`/notifications/${notification.id}`} class="hover:cursor-pointer hover:bg-gray-100 rounded-sm p-1 px-2">
                    <li class="flex items-center justify-between gap-1">
                        <div class="flex items-center gap-1">
                            <MessageCircle class="w-4 h-4" />
                            <p class="whitespace-nowrap overflow-hidden text-ellipsis max-w-[10ch]">
                                {notification.content}
                            </p>
                        </div>
                        <Badge color="gray"
                            >{dayjs().to(
                                dayjs(notification.created_at),
                            )}
                        </Badge>
                    </li>
                </a>
            {/each}
        </ul>
    {/snippet}
</WidgetBase>
