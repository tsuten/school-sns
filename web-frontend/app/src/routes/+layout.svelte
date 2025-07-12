<script>
	import '../app.css';
	import SidebarButton from './sidebar-botton.svelte';
	import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation, HeartHandshake, Grip} from 'lucide-svelte';
	import State from './state.svelte';
	import Modal from '../lib/components/utils/modal.svelte';
	import UserInfo from '../lib/components/utils/userInfo.svelte';
	import WidgetBase from '../lib/components/widgets/widgetBase.svelte';
	import Notification from '../lib/components/widgets/notification.svelte';
	import ToastContainer from '../lib/components/utils/ToastContainer.svelte';
	import { setUserFromServerData, logout as authLogout, isAuthenticated, currentUser } from '../lib/stores/auth.js';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { apiClient } from '../lib/services/django.js';
	import CalendarWidget from '../lib/components/widgets/prototype/calendarWidget.svelte';
	import EventsWidget from '../lib/components/widgets/prototype/eventsWidget.svelte';
	import { Button, Input, Dropdown, DropdownItem } from 'flowbite-svelte';
	import ServicesGridMenu from '../lib/components/card/topbar/servicesGridMenu.svelte';
	import UserIcon from '../lib/components/utils/userIcon.svelte';
	import NotificationDropdown from '../lib/components/card/topbar/notificationDropdown.svelte';
	let { children, data } = $props();
	
	// サーバーから取得したデータをストアに設定
	onMount(() => {
		console.log('Layout onMount - data:', data);
		if (data?.user && data?.authenticated) {
			console.log('Setting user info from server data:', data.user);
			// サーバーデータの構造を確認してからストアに設定
			setUserFromServerData(data.user, data.authenticated);
		} else {
			console.log('No authenticated user data, clearing user info');
			setUserFromServerData(null, false);
		}
	});
	
	// ログアウト処理
	async function handleLogout() {
		try {
			// auth.jsストアのログアウト関数を使用
			authLogout();
			
			// ログインページにリダイレクト
			goto('/login');
		} catch (error) {
			console.error('Logout error:', error);
			// エラーが発生してもログアウト処理は続行
			authLogout();
			goto('/login');
		}
		
		show_logout_modal = false;
	}
	
	let trending = ["すげえ祭り", "やべえ祭り", "しょぼい祭り", "キモい祭り", "おもろい祭り"]
	let trend_updated_at = new Date().toLocaleString();

	let editing_widget = $state(false);
	let show_logout_modal = $state(false);

	let showSidebar = $state(false);


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

	let your_classes = $state([]);

	onMount(async () => {
		const response = await apiClient.get("/enrollments/my_classes");
		your_classes = response.map(class_obj => ({
			icon: School,
			href: `/class/${class_obj.id}`,
			label: class_obj.name
		}));
	});

	let bottom_services = [
		{
			icon: Settings,
			href: "/settings",
			label: "設定"
		},
	]

</script>

<div class="flex flex-col h-screen w-full">
	<div name="topbar" class="text-center flex flex-row items-center justify-between border-gray-300 p-4 border-b h-16">
		<div>
		</div>
		<div class="flex flex-row items-center gap-2">
			<Input type="text" placeholder="検索" class="w-full h-8 rounded-sm"/>
		</div>
		<div class="flex flex-row items-center gap-4">
			<Button color="light" class="hover:cursor-pointer border-none !p-2" pill>
				<Grip class="w-6 h-6 text-gray-500" />
			</Button>
			<Dropdown simple>
				<ServicesGridMenu />
			</Dropdown>
			<Button color="light" class="hover:cursor-pointer border-none !p-2" pill>
				<Bell class="w-6 h-6 text-gray-500" />
			</Button>
			<Dropdown simple>
				<NotificationDropdown />
			</Dropdown>
			<UserIcon />
		</div>
	</div>
	<div class="flex justify-between flex-1 h-full">
		<div class="flex items-start flex-col justify-between">
			<button class="border border-gray-300 rounded-lg py-2 w-full text-center text-gray-500 text-sm font-bold hover:cursor-pointer hover:bg-gray-200" onclick={() => showSidebar = !showSidebar}>
				サイドバーを{showSidebar ? "閉じる" : "開く"}
			</button>
		</div>
		<div class="flex items-start flex-col justify-between" class:hidden={showSidebar === false}>
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

		<div class="w-full border-x border-gray-300 h-full">
			{@render children()}
		</div>
		<div class="flex flex-col w-3/7 w-80 h-full justify-between p-4">
			<div class="h-full">
			<!--<div class="border border-gray-300 rounded-lg m-3">
					<h2 class="text-gray-500 text-sm font-bold text-center py-2">トレンド<p>{trend_updated_at}</p></h2>
					<div class="flex flex-col gap-1 p-2 items-center">
						<ul class="flex flex-col gap-1 p-2">
							<li class="flex items-center gap-1"><Crown class="w-4 h-4 text-yellow-500" />{trending[0]}</li>
							<li class="flex items-center gap-1"><Crown class="w-4 h-4 text-gray-500" />{trending[1]}</li>
							<li class="flex items-center gap-1"><Crown class="w-4 h-4 text-amber-800" />{trending[2]}</li>
							<li class="flex items-center gap-1"><Crown class="w-4 h-4 invisible" />{trending[3]}</li>
							<li class="flex items-center gap-1"><Crown class="w-4 h-4 invisible" />{trending[4]}</li>
						</ul>
						<div class="flex flex-col text-gray-500 text-sm font-bold text-center">
							<a href="/trending" class="border border-gray-300 rounded-lg p-2 text-gray-500 text-sm font-bold text-center">更にトレンドを見る</a>
						</div>
					</div>
				</div>-->
				<div class="flex flex-col gap-4 mb-4 h-full overflow-y-auto">
					<Notification />
					<CalendarWidget />
				</div>
			</div>
			<button class="border border-gray-300 rounded-lg py-2 w-full text-center text-gray-500 text-sm font-bold hover:cursor-pointer hover:bg-gray-200" onclick={() => editing_widget = !editing_widget}>
				ウィジェットの設定
			</button>
		</div>

		<Modal 
			isOpen={editing_widget}
			title="ウィジェットの設定"
			on:close={() => editing_widget = false}
		>
			{#snippet children()}
				<div class="p-6">
					<p class="text-center">ウィジェットの設定画面です</p>
					<div class="mt-4 flex justify-end gap-2">
						<button 
							class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
							onclick={() => editing_widget = false}
						>
							キャンセル
						</button>
						<button 
							class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
							onclick={() => editing_widget = false}
						>
							保存
						</button>
					</div>
				</div>
			{/snippet}
		</Modal>

		<Modal 
			isOpen={show_logout_modal}
			title="ログアウト"
			on:close={() => show_logout_modal = false}
		>
			{#snippet children()}
				<div class="p-6">
					<p class="text-center">ログアウトしますか？</p>
				</div>
				<div class="mt-4 flex justify-end gap-2">
					<button 
						class="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
						onclick={() => show_logout_modal = false}
					>
						キャンセル
					</button>
					<button 
						class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
						onclick={handleLogout}
					>
						ログアウト
					</button>
				</div>
			{/snippet}
		</Modal>
	</div>
</div>

<!-- Toast Container -->
<ToastContainer />