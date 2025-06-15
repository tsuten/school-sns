<script>
	import '../app.css';
	import SidebarButton from './sidebar-botton.svelte';
	import { House, Bell, User, Settings, MessageCircle, Calendar, LogOut, Crown, TrendingUp, Tickets, ChartGantt, Bookmark, Vote, Heart, Key, NotebookPen} from 'lucide-svelte';
	import State from './state.svelte';
	import Modal from '../lib/components/utils/modal.svelte';
	import UserInfo from '../lib/components/utils/userInfo.svelte';
	let { children } = $props();
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
		{
			icon: Vote,
			href: "/polls",
			label: "投票"
		},
		{
			icon: NotebookPen,
			href: "/post",
			label: "投稿する"
		},
		{
			icon: User,
			href: "/profile",
			label: "プロフィール"
		},
		{
			icon: Settings,
			href: "/settings",
			label: "設定"
		},
	]

</script>

<div class="flex justify-between h-screen">
	<div class="flex items-start flex-col justify-between">
		<div class="flex flex-col gap-1 p-2">
			{#each services as service}
				<SidebarButton icon={service.icon} href={service.href} label={service.label} />
			{/each}
			<a href="/" class="flex flex-row items-center w-40 justify-end gap-2 group" onclick={() => show_logout_modal = true}> <p class="text-sm text-gray-500">ログアウト</p>
				<div class="w-13 h-13 hover:bg-gray-200 rounded-full flex items-center justify-center hover:cursor-pointer">
					<LogOut />
				</div>
			</a>
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
			<div class="border border-gray-300 rounded-lg m-3 w-full">
				<h2 class="text-gray-500 text-sm font-bold text-center py-2">通知</h2>
				<div class="flex flex-col gap-1 p-2 items-center w-full">
					<ul class="flex flex-col gap-1 p-2 w-full">
						<li class="flex items-center gap-1"><MessageCircle class="w-4 h-4" />人間: 調子はどう？</li>
						<li class="flex items-center gap-1 whitespace-nowrap"><Heart class="w-4 h-4" /><p class="overflow-hidden text-ellipsis w-full">あなたの投稿がいいねされましたよん</p></li>
						<li class="flex items-center gap-1"><Vote class="w-4 h-4" />投票が終了しました</li>
						<li class="flex items-center gap-1"><Calendar class="w-4 h-4" />イベントが開催されます</li>
						<li class="flex items-center gap-1"><Key class="w-4 h-4" />パスワードが変更されました</li>
					</ul>
					<div class="flex flex-col text-gray-500 text-sm font-bold text-center">
						<a href="/notifications" class="border border-gray-300 rounded-lg p-2 text-gray-500 text-sm font-bold text-center">更に通知を見る</a>
					</div>
				</div>
			</div>
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
					onclick={() => show_logout_modal = false}
				>
					ログアウト
				</button>
			</div>
		{/snippet}
	</Modal>
</div>