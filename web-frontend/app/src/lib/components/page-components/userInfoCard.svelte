<script>
	import { User, MapPin, Calendar, Edit3, Settings } from 'lucide-svelte';
	
	/**
	 * @typedef {Object} UserData
	 * @property {string} id - ユーザーID
	 * @property {string} username - ユーザー名
	 * @property {string} [display_name] - 表示名
	 * @property {string} [bio] - 自己紹介
	 * @property {string} [location] - 居住地
	 * @property {string} [birth_place] - 出身地
	 * @property {string} [birthday] - 誕生日
	 * @property {string} [pfp] - プロフィール画像URL
	 * @property {string} created_at - 作成日時
	 * @property {number} [posts_count] - 投稿数
	 * @property {number} [followers_count] - フォロワー数
	 * @property {number} [following_count] - フォロー数
	 */
	
	let { 
		user,
		isOwnProfile = false,
		showEditButton = false,
		onEdit = () => {},
		onFollow = () => {},
		isFollowing = false
	} = $props();
	
	// 日付フォーマット関数
	function formatDate(dateString) {
		if (!dateString) return '';
		const date = new Date(dateString);
		return date.toLocaleDateString('ja-JP', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}
	
	// 参加日フォーマット関数
	function formatJoinDate(dateString) {
		if (!dateString) return '';
		const date = new Date(dateString);
		return date.toLocaleDateString('ja-JP', {
			year: 'numeric',
			month: 'long'
		});
	}
</script>

<div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
	<!-- ヘッダー部分（背景色） -->
	<div class="h-32 bg-gradient-to-r from-blue-500 to-purple-600"></div>
	
	<!-- プロフィール情報 -->
	<div class="px-6 pb-6">
		<!-- プロフィール画像とボタン -->
		<div class="flex justify-between items-start -mt-16 mb-4">
			<div class="relative">
				{#if user.pfp}
					<img 
						src={user.pfp} 
						alt="{user.display_name || user.username}のプロフィール画像"
						class="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover"
					/>
				{:else}
					<div class="w-32 h-32 rounded-full border-4 border-white shadow-lg bg-gray-200 flex items-center justify-center">
						<User class="w-16 h-16 text-gray-400" />
					</div>
				{/if}
			</div>
			
			<!-- アクションボタン -->
			<div class="flex gap-2 mt-4">
				{#if isOwnProfile}
					{#if showEditButton}
						<button 
							onclick={onEdit}
							class="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors duration-200 font-medium"
						>
							<Edit3 class="w-4 h-4" />
							プロフィール編集
						</button>
					{/if}
					<button class="p-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors duration-200">
						<Settings class="w-5 h-5" />
					</button>
				{:else}
					<button 
						onclick={onFollow}
						class="px-6 py-2 {isFollowing ? 'bg-gray-100 hover:bg-gray-200 text-gray-700' : 'bg-blue-500 hover:bg-blue-600 text-white'} rounded-full transition-colors duration-200 font-medium"
					>
						{isFollowing ? 'フォロー中' : 'フォロー'}
					</button>
				{/if}
			</div>
		</div>
		
		<!-- ユーザー名と表示名 -->
		<div class="mb-4">
			<h1 class="text-2xl font-bold text-gray-900 mb-1">
				{user.display_name || user.username}
			</h1>
			{#if user.display_name}
				<p class="text-gray-500">@{user.username}</p>
			{/if}
		</div>
		
		<!-- 自己紹介 -->
		{#if user.bio}
			<div class="mb-4">
				<p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{user.bio}</p>
			</div>
		{/if}
		
		<!-- 詳細情報 -->
		<div class="flex flex-wrap gap-4 mb-4 text-sm text-gray-600">
			{#if user.location}
				<div class="flex items-center gap-1">
					<MapPin class="w-4 h-4" />
					<span>{user.location}</span>
				</div>
			{/if}
			
			{#if user.birth_place && user.birth_place !== user.location}
				<div class="flex items-center gap-1">
					<span class="text-gray-400">出身:</span>
					<span>{user.birth_place}</span>
				</div>
			{/if}
			
			{#if user.birthday}
				<div class="flex items-center gap-1">
					<Calendar class="w-4 h-4" />
					<span>誕生日: {formatDate(user.birthday)}</span>
				</div>
			{/if}
			
			<div class="flex items-center gap-1">
				<Calendar class="w-4 h-4" />
				<span>{formatJoinDate(user.created_at)}に参加</span>
			</div>
		</div>
		
		<!-- 統計情報 -->
		<div class="flex gap-6 text-sm">
			{#if user.posts_count !== undefined}
				<div class="flex gap-1">
					<span class="font-semibold text-gray-900">{user.posts_count.toLocaleString()}</span>
					<span class="text-gray-600">投稿</span>
				</div>
			{/if}
			
			{#if user.following_count !== undefined}
				<div class="flex gap-1">
					<span class="font-semibold text-gray-900">{user.following_count.toLocaleString()}</span>
					<span class="text-gray-600">フォロー中</span>
				</div>
			{/if}
			
			{#if user.followers_count !== undefined}
				<div class="flex gap-1">
					<span class="font-semibold text-gray-900">{user.followers_count.toLocaleString()}</span>
					<span class="text-gray-600">フォロワー</span>
				</div>
			{/if}
		</div>
	</div>
</div>
