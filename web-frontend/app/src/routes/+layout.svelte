<script>
	import '../app.css';
	import SidebarButton from './sidebar-botton.svelte';
	import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen, School, University, Presentation} from 'lucide-svelte';
	import State from './state.svelte';
	import Modal from '../lib/components/utils/modal.svelte';
	import UserInfo from '../lib/components/utils/userInfo.svelte';
	import WidgetBase from '../lib/components/widgets/widgetBase.svelte';
	import Notification from '../lib/components/widgets/notification.svelte';
	import { setUserInfo, clearUserInfo } from '../lib/stores/userInfo.js';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '../lib/services/django.js';
	
	let { children, data } = $props();
	
	// サーバーから取得したデータをストアに設定
	onMount(() => {
		if (data?.user && data?.authenticated) {
			console.log('Setting user info from server data:', data.user);
			setUserInfo(data.user);
		} else {
			console.log('No authenticated user data, clearing user info');
			clearUserInfo();
		}
	});
	
	// ログアウト処理
	async function handleLogout() {
		try {
			// APIクライアントのログアウト（トークンをクリア）
			api.auth.logout();
			
			// ユーザー情報ストアをクリア
			clearUserInfo();
			
			// Cookieもクリア（サーバーサイドで設定されている場合）
			document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
			document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
			
			// ログインページにリダイレクト
			goto('/login');
		} catch (error) {
			console.error('Logout error:', error);
			// エラーが発生してもログアウト処理は続行
			clearUserInfo();
			goto('/login');
		}
		
		show_logout_modal = false;
	}
	
	let trending = ["すげえ祭り", "やべえ祭り", "しょぼい祭り", "キモい祭り", "おもろい祭り"]
	let trend_updated_at = new Date().toLocaleString();

	let editing_widget = $state(false);
	let show_logout_modal = $state(false);


	let services = [
		{
			icon: House,
			href: "/",
			label: "ver 0.0.1"
		},
		{
			icon: Bell,
			href: "/notifications",
			label: "通知"
		},
		{
			icon: ChartGantt,
			href: "/timeline",
			label: "タイムライン"
		},
		{
			icon: MessageCircle,
			href: "/messages",
			label: "メッセージ"
		},
		{
			icon: Bookmark,
			href: "/bookmark",
			label: "ブックマーク"
		},
		{
			icon: TrendingUp,
			href: "/trending",
			label: "トレンド"
		},
		{
			icon: Tickets,
			href: "/events",
			label: "イベント"
		},
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
		{
			icon: User,
			href: "/profile",
			label: "あなた"
		},
		{
			icon: Settings,
			href: "/settings",
			label: "設定"
		},
	]

	let enrollment_services = [
		{
			icon: University,
			href: "/institution",
			label: "全体"
		},
		{
			icon: School,
			href: "/school",
			label: "学校"
		},
		{
			icon: Presentation,
			href: "/class",
			label: "クラス"
		},
	]

</script>

<div class="flex justify-between h-screen">
	<div class="flex items-start flex-col justify-between">
		<div class="flex flex-col gap-1 p-2">
			{#each services as service}
				<SidebarButton icon={service.icon} href={service.href} label={service.label} />
			{/each}
			<div class="flex flex-col gap-1 p-2 border border-gray-300 rounded-lg w-full">
				{#each enrollment_services as service}
					<SidebarButton icon={service.icon} href={service.href} label={service.label} />
				{/each}
			</div>
			<button class="flex flex-row items-center w-40 justify-end gap-2 group" onclick={() => show_logout_modal = true}> <p class="text-sm text-gray-500">ログアウト</p>
				<div class="w-13 h-13 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
					<LogOut />
				</div>
			</button>
		</div>
		<div class="flex flex-col gap-1 p-2 pb-6">
			<UserInfo />
		</div>
	</div>

	<div class="w-full border-x border-gray-300 h-screen">
		{@render children()}
	</div>
	<div class="flex flex-col w-3/7 w-70 h-full justify-between">
		<div>
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
			<Notification />
			<State />
		</div>
		<button class="border border-gray-300 rounded-lg m-3 py-2 w-full text-center text-gray-500 text-sm font-bold hover:cursor-pointer hover:bg-gray-200" onclick={() => editing_widget = !editing_widget}>
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