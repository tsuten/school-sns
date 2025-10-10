<script>
    import SidebarButton from "$lib/components/layout/sidebar/sidebar-button.svelte";
    import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation, HeartHandshake, Grip, BookOpen, Rss, Clock, MessageSquareText, Sun, Moon, MessageSquare} from 'lucide-svelte';
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";
    import { fade } from 'svelte/transition';
	import { page } from "$app/stores";
	import { goto } from "$app/navigation";
    import { currentTheme, toggleTheme, theme } from "$lib/theme.js";
    import { Button, Dropdown, DropdownItem } from "flowbite-svelte";
    import NotificationDropdown from "$lib/components/card/topbar/notificationDropdown.svelte";
    let { showSidebar } = $props();
    let show_logout_modal = $state(false);
    let displayType = $state("horizontal");
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
			icon: MessageSquare,
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
/*
		{
			icon: BookOpen,
			href: "/app/assignments",
			label: "課題"
		},
*/
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
/*
		{
			icon: MessageSquareText,
			href: "/app/forum",
			label: "掲示板"
		},
*/
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

    <div class="flex items-center flex-row justify-end w-full relative {$theme.background.primary}">
        <div class="flex flex-row gap-1 p-2 justify-center flex-1 gap-4 absolute left-1/2 transform -translate-x-1/2">
        {#if displayType === "vertical"}
        {#each services as service}
            <a href={service.href} class="w-20 h-15 flex flex-col justify-center items-center hover:cursor-pointer rounded-lg p-2 {$theme.text.primary} hover:{$theme.button.secondary}">
                <div class="flex items-center justify-center">
                    <service.icon size="20" />
                </div>
				<p class="text-sm font-bold">{service.label}</p>
            </a>
        {/each}
        {:else}
        {#each services as service}
            <a href={service.href} class="p-2 gap-2 flex flex-row items-center justify-center hover:cursor-pointer rounded-lg {$theme.text.primary} hover:{$theme.button.secondary} whitespace-nowrap">
                <div class="rounded-full flex items-center justify-center">
                    <service.icon size="20" />
                </div>
				<p class="text-sm font-bold">{service.label}</p>
            </a>
        {/each}
        {/if}
    </div>
    
    <!-- テーマ変更ボタン -->
    <div class="flex items-center p-2 gap-2">
        <Button color="light" class="hover:cursor-pointer border-none !p-2" pill>
            <Bell class="w-6 h-6 text-gray-500" />
        </Button>
        <Dropdown simple>
            <NotificationDropdown />
        </Dropdown>
        <Button color="light" class="hover:cursor-pointer border-none !p-2" pill onclick={toggleTheme}
            title="テーマを切り替え"
        >
            {#if $currentTheme === 'dark'}
                <Sun size="20" class="text-yellow-500" />
            {:else}
                <Moon size="20" class="text-gray-600" />
            {/if}
        </Button>
    </div>
</div>