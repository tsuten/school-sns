<script>
    import { 
        MessageCircle, 
        Calendar, 
        Bell, 
        Settings, 
        School, 
        Tickets, 
        HeartHandshake, 
        User,
        Home,
        BookOpen,
        Users,
        Camera,
        Music,
        Map,
        Heart,
        Bookmark,
        ChartGantt,
        Vote
    } from "lucide-svelte";

    let services = [
        {
            icon: Home,
            label: "ホーム",
            href: "/"
        },
        {
            icon: MessageCircle,
            label: "メッセージ",
            href: "/messages"
        },
        {
            icon: Bell,
            label: "通知",
            href: "/notifications"
        },
        {
            icon: Calendar,
            label: "カレンダー",
            href: "/calendar"
        },
        {
            icon: Tickets,
            label: "イベント",
            href: "/events"
        },
        {
            icon: User,
            label: "プロフィール",
            href: "/profile"
        },
        {
            icon: Users,
            label: "友達",
            href: "/friends"
        },
        {
            icon: Camera,
            label: "写真",
            href: "/photos"
        },
        {
            icon: Music,
            label: "音楽",
            href: "/music"
        },
        {
            icon: Bookmark,
            label: "ブックマーク",
            href: "/bookmark"
        },
        {
            icon: Vote,
            label: "アンケート",
            href: "/survey"
        }
    ]

    // 外部からイベントを受け取るための関数をエクスポート
    export let onServiceClick = () => {};
</script>

<!-- ドロップダウンメニューの内容 -->
<div class="w-80 p-4">
    
    <!-- グリッドレイアウト -->
    <div class="grid grid-cols-3 gap-2">
        {#each services as service}
            <a
                href={service.href}
                class="flex flex-col items-center gap-2 py-2 rounded-sm hover:bg-gray-100 hover:cursor-pointer text-center"
                onclick={() => onServiceClick()}
            >
                <svelte:component this={service.icon} class="w-6 h-6 text-gray-600" />
                <span class="text-xs text-gray-700 font-medium">{service.label}</span>
            </a>
        {/each}
    </div>
</div>