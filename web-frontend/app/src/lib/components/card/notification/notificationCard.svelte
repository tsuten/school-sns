<script>
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    import { getCurrentDateNormalized } from '$lib/utils/datetimeNormalize';
    import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation, HeartHandshake, Grip} from 'lucide-svelte';

    const nowDate = getCurrentDateNormalized();
    const time = new Date();
    

</script>

<BaseCard>
    <MessageCircle />
    <div>
        mashiko100% さんが あなたにチャットしました
    </div>
    <div>
        {nowDate} {time.getHours()}:{time.getMinutes()}
    </div>

</BaseCard>