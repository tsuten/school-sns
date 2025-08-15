<script>
	import '../../app.css';
	import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation, HeartHandshake, Grip, PanelLeftOpen, PanelLeftClose, Search } from 'lucide-svelte';
	import State from './state.svelte';
	import Modal from '$lib/components/utils/modal.svelte';
	import UserInfo from '$lib/components/utils/userInfo.svelte';
	import WidgetBase from '$lib/components/widgets/widgetBase.svelte';
	import Notification from '$lib/components/widgets/notification.svelte';
	import ToastContainer from '$lib/components/utils/ToastContainer.svelte';
	import { setUserFromServerData, logout as authLogout, isAuthenticated, currentUser } from '$lib/stores/auth.js';
	import { onMount } from 'svelte';
	import { apiClient } from '$lib/services/django.js';
	import CalendarWidget from '$lib/components/widgets/prototype/calendarWidget.svelte';
	import EventsWidget from '$lib/components/widgets/prototype/eventsWidget.svelte';
	import { Button, Input, Dropdown, DropdownItem } from 'flowbite-svelte';
	import ServicesGridMenu from '$lib/components/card/topbar/servicesGridMenu.svelte';
	import UserIcon from '$lib/components/utils/userIcon.svelte';
	import NotificationDropdown from '$lib/components/card/topbar/notificationDropdown.svelte';
	import Sidebar from '$lib/components/layout/sidebar/sidebar.svelte';
	import { settingsStore } from '$lib/stores/serverSettingsStore.js';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	let { children, data } = $props();
	
	// サーバーから取得したデータをストアに設定
	onMount(async () => {
		console.log('Layout onMount - data:', data);
		if (data?.user && data?.authenticated) {
			console.log('Setting user info from server data:', data.user);
			// サーバーデータの構造を確認してからストアに設定
			setUserFromServerData(data.user, data.authenticated);
		} else {
			console.log('No authenticated user data, clearing user info');
			setUserFromServerData(null, false);
		}

		try {
			const setup_response = await apiClient.get('/setup/completion-rate');
			console.log('Setup response:', setup_response);
			if (setup_response.is_system_ready === false && !page.url.pathname.includes('/setup')) {
				goto('/setup');
			}
		} catch (error) {
			console.error('Setup error:', error);
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
	let showSidebar = $state(true);
</script>

<div class="flex flex-col h-screen w-full">
	<div name="topbar" class="text-center flex flex-row items-center justify-between border-gray-300 p-2 border-b flex-shrink- relative">
		<div>
			<Button color="light" class="hover:cursor-pointer border-none !p-2" pill onclick={() => showSidebar = !showSidebar}>
				{#if showSidebar}
					<PanelLeftClose class="w-6 h-6 text-gray-500" />
				{:else}
					<PanelLeftOpen class="w-6 h-6 text-gray-500" />
				{/if}
			</Button>
		</div>
		<div class="flex flex-row items-center gap-2 absolute left-1/2 transform -translate-x-1/2 w-96">
			<div class="relative w-full">
				<Search class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
				<Input type="text" placeholder="検索" class="rounded-sm pl-9" />
			</div>
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
	<div class="flex justify-between flex-1 min-h-0 overflow-hidden">
		<Sidebar bind:showSidebar={showSidebar} />

		<div class="w-full border-x border-gray-300 h-full">	
			<div class="page-transition page-transition-in h-full">
				{@render children()}
			</div>
		</div>
		<!--
		<div class="flex flex-col w-3/7 w-80 h-full justify-between p-4">
			<div class="h-full">
				<div class="border border-gray-300 rounded-lg m-3">
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
				</div>
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
		-->
	</div>
</div>

<!-- Toast Container -->
<ToastContainer />