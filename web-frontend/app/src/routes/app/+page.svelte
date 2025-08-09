<script>
	import ProfileCard from '$lib/components/card/profileCard.svelte';
	import { currentUser, isAuthenticated } from '$lib/stores/auth';
	import { browser } from '$app/environment';
	import Page from '$lib/components/utils/page.svelte';
	import AffiliationInfo from '$lib/components/card/user/affiliationInfo.svelte';
	import CircleAffiliationInfo from '$lib/components/card/user/circleAffiliationInfo.svelte';
	// サーバーサイドレンダリング時の安全なアクセス
	const user = $derived(browser ? ($currentUser?.user || null) : null);
</script>

<Page>
	{#if user}
		<!-- 自分のプロフィール -->
		<ProfileCard {user} />
	{:else}
		<div class="flex items-center justify-center p-8 text-gray-500">
			<p>ユーザー情報を読み込み中...</p>
		</div>
	{/if}
	<div class="grid grid-cols-2 gap-4 h-full">
		<AffiliationInfo {user} />
		<CircleAffiliationInfo {user} />
	</div>
</Page>