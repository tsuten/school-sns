<script>
    import SidebarButton from "$lib/components/layout/sidebar/sidebar-button.svelte";
    import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation, HeartHandshake, Grip} from 'lucide-svelte';
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";

    let showSidebar = $state(false);
    let show_logout_modal = $state(false);

    let your_classes = $state([]);


    let services = [
		{
			icon: House,
			href: "/",
			label: "あなた"
		},
		{
			icon: Bell,
			href: "/notifications",
			label: "通知"
		},
/*		{
			icon: ChartGantt,
			href: "/timeline",
			label: "タイムライン"
		},*/
		{
			icon: MessageCircle,
			href: "/messages",
			label: "メッセージ"
		},
		{
			icon: HeartHandshake,
			href: "/circles",
			label: "サークル"
		},
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
		{
			icon: School,
			href: "/school",
			label: "学校"
		},
/*		{
			icon: Tickets,
			href: "/events",
			label: "イベント"
		},*/
		{
			icon: Calendar,
			href: "/calendar",
			label: "カレンダー"
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
			href: "/settings",
			label: "設定"
		},
	]

    onMount(async () => {
		const response = await apiClient.get("/enrollments/my_classes");
		your_classes = response.map(class_obj => ({
			icon: School,
			href: `/class/${class_obj.id}`,
			label: class_obj.name
		}));
	});
</script>

<!-- <div class="flex items-start flex-col justify-between">
    <button class="border border-gray-300 rounded-lg py-2 w-full text-center text-gray-500 text-sm font-bold hover:cursor-pointer hover:bg-gray-200" onclick={() => showSidebar = !showSidebar}>
        サイドバーを{showSidebar ? "閉じる" : "開く"}
    </button>
</div> -->
<div class="hover:cursor-pointer" onclick={(event) => {
    if (event.target === event.currentTarget) {
        showSidebar = !showSidebar;
    }
}}>
{#if showSidebar}
<div class="flex items-start flex-col justify-between">
    <div class="flex flex-col gap-1 p-2">
        {#each services as service}
            <SidebarButton icon={service.icon} href={service.href} label={service.label} />
        {/each}
        <h2 class="text-gray-500 text-sm font-bold text-center py-2">あなたのクラス</h2>
        {#each your_classes as service}
            <SidebarButton icon={service.icon} href={service.href} label={service.label} />
        {/each}
    </div>
    <div class="flex flex-col gap-1 p-2">
        {#each bottom_services as service}
            <SidebarButton icon={service.icon} href={service.href} label={service.label} />
        {/each}
        <button class="flex flex-row items-center w-40 justify-end gap-2 group" onclick={() => show_logout_modal = true}> <p class="text-sm text-gray-500">ログアウト</p>
            <div class="w-13 h-13 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                <LogOut />
            </div>
        </button>
    </div>
</div>
{:else}
<div class="flex items-start flex-col justify-between">
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
            <a href={service.href} class="flex flex-row gap-2 items-center">
                <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                    <service.icon size="20" />
                </div>
            </a>
        {/each}
        <button class="flex flex-row items-center justify-center gap-2 group" onclick={() => show_logout_modal = true}>
            <div class="w-10 h-10 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
                <LogOut size="20" />
            </div>
        </button>
    </div>
</div>
{/if}
</div>