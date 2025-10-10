<script>
    import SidebarButton from "$lib/components/layout/sidebar/sidebar-button.svelte";
    import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation, HeartHandshake, Grip, BookOpen, Rss, Clock, MessageSquareText} from 'lucide-svelte';
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";
    import { fade } from 'svelte/transition';
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";
    let { showSidebar } = $props();
    let show_logout_modal = $state(false);

    let your_classes = $state([]);


    let services = [
		{
			icon: House,
			href: "/app",
			label: "あなた"
		},
		{
			icon: Rss,
			href: "/app/feed",
			label: "フィード"
		},
/*
		{
			icon: Bell,
			href: "/app/notifications",
			label: "通知"
		},
*/
/*		{
			icon: ChartGantt,
			href: "/timeline",
			label: "タイムライン"
		},*/
		{
			icon: MessageCircle,
			href: "/app/messages",
			label: "メッセージ"
		},
/*
		{
			icon: HeartHandshake,
			href: "/app/circles",
			label: "サークル"
		},
*/
/*		{
			icon: Bookmark,
			href: "/bookmark",
			label: "ブックマーク"
		},*/
/*		{
			icon: TrendingUp,
			href: "/trending",
			label: "トレンド"
		},*/
/*
		{
			icon: School,
			href: "/app/school",
			label: "学校"
		},
*/
/*		{
			icon: Tickets,
			href: "/events",
			label: "イベント"
		},*/
		{
			icon: NotebookPen,
			href: "/app/memo",
			label: "メモ"
		},
		{
			icon: BookOpen,
			href: "/app/assignments",
			label: "課題"
		},
		{
			icon: Calendar,
			href: "/app/calendar",
			label: "カレンダー"
		},
		{
			icon: Clock,
			href: "/app/events",
			label: "イベント"
		},
		{
			icon: MessageSquareText,
			href: "/app/forum",
			label: "掲示板"
		},
/*		{
			icon: Vote,
			href: "/polls",
			label: "投票"
		},*/
/*		{
			icon: NotebookPen,
			href: "/post",
			label: "投稿する"
		},*/
/*		{
			icon: User,
			href: "/profile",
			label: "あなた"
		},*/
	]

	let enrollment_services = [
/*		{
			icon: Presentation,
			href: "/class",
			label: "クラス"
		},*/
	]

    let bottom_services = [
		{
			icon: Settings,
			href: "/app/settings",
			label: "設定"
		},
	]

    onMount(async () => {
		const response = await apiClient.get("/organizations/my_classes");
		your_classes = response.map(class_obj => ({
			icon: School,
			href: `/class/${class_obj.id}`,
			label: class_obj.name
		}));
	});

	function navigateToSettings(href) {
		// 現在のパスに「settings」が含まれている場合は遷移しない
		if ($page.url.pathname.includes('settings')) {
			return;
		}
		goto(href);
	}
</script>

<!-- <div class="flex items-start flex-col justify-between">
    <button class="border border-gray-300 rounded-lg py-2 w-full text-center text-gray-500 text-sm font-bold hover:cursor-pointer hover:bg-gray-200" onclick={() => showSidebar = !showSidebar}>
        サイドバーを{showSidebar ? "閉じる" : "開く"}
    </button>
</div> -->
<div>
{#if showSidebar}
<div class="flex items-center flex-col justify-between h-full min-w-40">
    <div class="flex flex-col gap-1 p-2 justify-start w-full">
        {#each services as service}
            <a href={service.href} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
				<p class="text-sm text-gray-500">{service.label}</p>
            </a>
        {/each}
        <div class="border-t border-gray-300 my-2"></div>
        {#each your_classes as service}
            <a href={service.href} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
            </a>
        {/each}
    </div>
    <div class="flex flex-col gap-1 p-2 justify-end w-full">
        {#each bottom_services as service}
            <button onclick={() => navigateToSettings(service.href)} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
				<p class="text-sm text-gray-500">{service.label}</p>
            </button>
        {/each}
    </div>
</div>
{:else}
<div class="flex items-center flex-col justify-between h-full">
    <div class="flex flex-col gap-1 p-2">
        {#each services as service}
            <a href={service.href} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
            </a>
        {/each}
        <div class="border-t border-gray-300 my-2"></div>
        {#each your_classes as service}
            <a href={service.href} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
            </a>
        {/each}
    </div>
    <div class="flex flex-col gap-1 p-2">
        {#each bottom_services as service}
            <button onclick={() => navigateToSettings(service.href)} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
            </button>
        {/each}
    </div>
</div>
{/if}
</div>