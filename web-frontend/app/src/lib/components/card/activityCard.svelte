<script>
	import { onMount } from 'svelte';
	import { apiClient, getMediaURL } from '$lib/services/django';
	import { theme } from '$lib/theme.js';
	import { Button, Spinner } from 'flowbite-svelte';
	import { User, RefreshCcw } from 'lucide-svelte';
	
	let { limit = 10, showRefreshButton = true } = $props();

	let activities = $state([]);
	let loadingActivities = $state(true);
	let profileImages = $state(new Map()); // プロフィール画像のキャッシュ

	onMount(() => {
		fetchActivities();
	});

	async function fetchActivities() {
		try {
			loadingActivities = true;
			const response = await apiClient.get(`/activity/feed?limit=${limit}`);
			activities = response || [];
		} catch (err) {
			console.error('Error fetching activities:', err);
			activities = [];
		} finally {
			loadingActivities = false;
		}
	}

	async function getPfpFromId(id) {
		// キャッシュに既にある場合はそれを返す
		if (profileImages.has(id)) {
			return profileImages.get(id);
		}
		
		try {
			const response = await apiClient.get(`/users/profile/${id}`);
			const pfp = response.pfp;
			// キャッシュに保存
			profileImages.set(id, pfp);
			return pfp;
		} catch (error) {
			console.error(`Error fetching profile for user ${id}:`, error);
			// エラーの場合はデフォルト画像のパスを返す
			return null;
		}
	}

	function formatActivityTime(createdAt) {
		const now = new Date();
		const created = new Date(createdAt);
		const diff = now - created;
		
		const minutes = Math.floor(diff / (1000 * 60));
		const hours = Math.floor(diff / (1000 * 60 * 60));
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));
		
		if (minutes < 1) return '今';
		if (minutes < 60) return `${minutes}分前`;
		if (hours < 24) return `${hours}時間前`;
		if (days < 7) return `${days}日前`;
		
		return created.toLocaleDateString('ja-JP');
	}
</script>

<div class="h-full flex flex-col border {$theme.border.primary} rounded-lg {$theme.background.primary} p-4">
	<div class="flex flex-row gap-2 items-center justify-between mb-4">
		<h2 class="text-lg font-bold {$theme.text.primary} flex-shrink-0">最近のアクティビティ</h2>
		<Button 
			color="light" 
			size="xs"
			onclick={fetchActivities}
			class="p-2 hover:cursor-pointer"
		>
			<RefreshCcw class="w-4 h-4" />
		</Button>
	</div>
	{#if loadingActivities}
		<div class="text-center py-4 flex-1 flex items-center justify-center">
			<div class="text-center">
				<Spinner size="6" class="mx-auto" />
				<p class="mt-2 {$theme.text.tertiary}">読み込み中...</p>
			</div>
		</div>
	{:else if activities.length === 0}
		<div class="text-center py-4 {$theme.text.tertiary} flex-1 flex items-center justify-center">
			<p>アクティビティがありません</p>
		</div>
	{:else}
		<div class="flex-1 overflow-y-auto space-y-3 pr-2">
			{#each activities as activity}
				<div class="flex items-start space-x-3 p-3 border {$theme.border.secondary} rounded-lg">
					<div class="flex-shrink-0 w-8 h-8 {$theme.background.quaternary} rounded-lg flex items-center justify-center">
						{#await getPfpFromId(activity.user_id)}
							<div class="w-8 h-8 rounded-lg bg-gray-300 animate-pulse"></div>
						{:then pfp}
							{#if pfp}
								<img src={getMediaURL(pfp)} alt={activity.username} class="w-8 h-8 rounded-lg" />
							{:else}
								<div class="w-8 h-8 rounded-lg bg-gray-300 flex items-center justify-center">
									<User class="w-4 h-4 text-gray-500" />
								</div>
							{/if}
						{:catch}
							<div class="w-8 h-8 rounded-lg bg-gray-300 flex items-center justify-center">
								<User class="w-4 h-4 text-gray-500" />
							</div>
						{/await}
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-center space-x-2">
							<span class="text-sm font-medium {$theme.text.primary}">{activity.username}</span>
							<span class="text-xs {$theme.text.tertiary}">{formatActivityTime(activity.created_at)}</span>
						</div>
						<p class="text-sm {$theme.text.secondary} mt-1">{activity.description}</p>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
