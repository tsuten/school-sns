<script>
    import WidgetBase from './widgetBase.svelte';
    import { MessageCircle, Heart, Vote, Calendar, Key, Bell } from 'lucide-svelte';
    import { Badge } from 'flowbite-svelte';
    import { Notifications } from '$lib/stores/notificationWSStore.js';
    import { timeNormalize } from '$lib/utils/datetimeNormalize';
</script>

<WidgetBase title="通知" icon={Bell} href="/notifications">
    {#snippet snippet()}
        <ul class="flex flex-col gap-1 w-full">
            {#each $Notifications.slice(0, 5) as notification}
            <li class="flex items-center justify-between gap-1">
                <div class="flex items-center gap-1">
                    <MessageCircle class="w-4 h-4" />
                    <p>{notification.content}</p>
                </div>
                <Badge color="gray">{timeNormalize(notification.created_at)}</Badge>
            </li>
            {/each}
            <li class="flex items-center gap-1 whitespace-nowrap"><Heart class="w-4 h-4" /><p class="overflow-hidden text-ellipsis w-full">あなたの投稿がいいねされましたよん</p></li>
            <li class="flex items-center gap-1"><Vote class="w-4 h-4" />投票が終了しました</li>
            <li class="flex items-center gap-1"><Calendar class="w-4 h-4" />イベントが開催されます</li>
            <li class="flex items-center gap-1"><Key class="w-4 h-4" />パスワードが変更されました</li>
        </ul>
    {/snippet}
</WidgetBase>