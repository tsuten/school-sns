<script>
    import WidgetBase from './widgetBase.svelte';
    import { MessageCircle, Heart, Vote, Calendar, Key, Bell } from 'lucide-svelte';
    import { Badge } from 'flowbite-svelte';
</script>

<WidgetBase title="通知" icon={Bell} href="/notifications">
    {#snippet snippet()}
        <ul class="flex flex-col gap-1 w-full">
            <li class="flex items-center justify-between gap-1">
                <div class="flex items-center gap-1">
                    <MessageCircle class="w-4 h-4" />
                    <p>人間: 調子はどう？</p>
                </div>
                <Badge color="gray">10:00</Badge>
            </li>
            <li class="flex items-center gap-1 whitespace-nowrap"><Heart class="w-4 h-4" /><p class="overflow-hidden text-ellipsis w-full">あなたの投稿がいいねされましたよん</p></li>
            <li class="flex items-center gap-1"><Vote class="w-4 h-4" />投票が終了しました</li>
            <li class="flex items-center gap-1"><Calendar class="w-4 h-4" />イベントが開催されます</li>
            <li class="flex items-center gap-1"><Key class="w-4 h-4" />パスワードが変更されました</li>
        </ul>
    {/snippet}
</WidgetBase>