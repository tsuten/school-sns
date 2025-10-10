<script>
	import ProfileCard from '$lib/components/card/profileCard.svelte';
	import { currentUser, isAuthenticated } from '$lib/stores/auth';
	import { browser } from '$app/environment';
	import Page from '$lib/components/utils/page.svelte';
	import AffiliationInfo from '$lib/components/card/user/affiliationInfo.svelte';
	import CircleAffiliationInfo from '$lib/components/card/user/circleAffiliationInfo.svelte';
	import ActivityCard from '$lib/components/card/activityCard.svelte';
	import FriendManagementCard from '$lib/components/card/friendManagementCard.svelte';
	// サーバーサイドレンダリング時の安全なアクセス
	const user = $derived(browser ? ($currentUser?.user || null) : null);


</script>

<Page>
	<div class="flex flex-row gap-4 w-full max-w-7xl mx-auto h-full">
		<div class="flex flex-col gap-4 w-full h-full">
		{#if user}
			<!-- 自分のプロフィール -->
			<ProfileCard {user} />
		{:else}
			<div class="flex items-center justify-center p-8 text-gray-500">
				<p>ユーザー情報を読み込み中...</p>
			</div>
		{/if}
			<AffiliationInfo {user} />
			<div class="flex-1 min-h-0">
				<ActivityCard limit={50} showRefreshButton={true} />
			</div>
		</div>
		<div class="h-full w-full">
			<FriendManagementCard />
		</div>
	</div>
</Page>

<!-- 表示する内容：
・ユーザー情報
・ユーザーの所属情報
・ユーザーの友達
・ユーザーへの招待 -->