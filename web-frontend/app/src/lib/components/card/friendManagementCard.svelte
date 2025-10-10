<script>
	import { onMount } from 'svelte';
	import { apiClient, getMediaURL } from '$lib/services/django';
	import { theme } from '$lib/theme.js';
	import { Button, Input, Modal, P, Spinner } from 'flowbite-svelte';
	import { UserRoundPlus, UserPlus, Check, X, RefreshCcw, MessageCircle, User } from 'lucide-svelte';
	import toast from '$lib/utils/toast';
	import { goto } from '$app/navigation';

	let defaultModal = $state(false);
	let friends = $state([]);
	let searchedInput = $state('');
	let searchedUsers = $state([]);
	let friendRequests = $state([]);
	let loading = $state(true);
	let profileImages = $state(new Map()); // プロフィール画像のキャッシュ

	onMount(() => {
		fetchFriends();
		fetchFriendRequests();
	});

	async function reFetch() {
		fetchFriends();
		fetchFriendRequests();
		toast.success('情報を再取得しました');
	}

	async function fetchFriends() {
		try {
			const response = await apiClient.get('/relations/friends');
			friends = response.data.data;
		} catch (err) {
			console.error('Error fetching friends:', err);
			friends = [];
		} finally {
			loading = false;
		}
	}

	async function fetchFriendRequests() {
		try {
			const response = await apiClient.get('/relations/requests');
			friendRequests = response.data.data;
		} catch (err) {
			console.error('Error fetching friend requests:', err);
			friendRequests = [];
		}
	}

	async function searchUsers() {
		if (searchedInput.length < 3) {
			searchedUsers = [];
		} else {
			try {
				const response = await apiClient.get(`/users/search/${searchedInput}`);
				searchedUsers = response;
			} catch (err) {
				console.error('Error searching users:', err);
				searchedUsers = [];
			}
		}
	}

	async function acceptFriendRequest(requestId) {
		try {
			await apiClient.post(`/relations/request/accept`, {
				friend_request_id: requestId
			});
			fetchFriendRequests();
			fetchFriends();
			toast.success('友達申請を承認しました');
		} catch (err) {
			console.error('Error accepting friend request:', err);
			toast.error('友達申請の承認に失敗しました');
		}
	}

	async function rejectFriendRequest(requestId) {
		try {
			await apiClient.post(`/relations/request/reject`, {
				friend_request_id: requestId
			});
			fetchFriendRequests();
			fetchFriends();
			toast.success('友達申請を拒否しました');
		} catch (err) {
			console.error('Error rejecting friend request:', err);
			toast.error('友達申請の拒否に失敗しました');
		}
	}

	async function sendFriendRequest(userId) {
		try {
			await apiClient.post(`/relations/request/send`, {
				to_user_id: userId
			});
			fetchFriendRequests();
			fetchFriends();
			toast.success('友達申請を送信しました');
		} catch (err) {
			console.error('Error sending friend request:', err);
			toast.error('友達申請の送信に失敗しました');
		}
	}

	async function removeFriend(friendId) {
		// 友達削除機能は実装されていない場合のプレースホルダー
		console.log('Remove friend:', friendId);
		toast.info('友達削除機能は開発中です');
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
</script>

<div class="h-full flex flex-col border {$theme.border.primary} rounded-lg {$theme.background.primary} p-4">
	<div class="flex flex-col gap-4 w-full h-full">
		<!-- 友達申請セクション -->
		<div class="flex flex-col gap-2 flex-shrink-0">
			<div class="flex flex-row gap-2 items-center justify-between">
				<h2 class="text-lg font-bold {$theme.text.primary}">友達申請</h2>
				<Button 
					color="light" 
					size="xs"
					onclick={reFetch}
					class="p-2 hover:cursor-pointer"
				>
					<RefreshCcw class="w-4 h-4" />
				</Button>
			</div>
			
			{#if friendRequests.length === 0}
				<div class="text-center py-4 {$theme.text.tertiary}">
					<p>友達申請はありません</p>
				</div>
			{:else}
				{#each friendRequests as request}
					<div class="flex flex-row justify-between gap-2 border {$theme.border.secondary} rounded-lg p-2 items-center">
						<div class="flex flex-row gap-2 items-center">
							{#await getPfpFromId(request.id)}
								<div class="w-10 h-10 rounded-lg bg-gray-300 animate-pulse"></div>
							{:then pfp}
								{#if pfp}
									<img src={getMediaURL(pfp)} alt={request.username} class="w-10 h-10 rounded-lg" />
								{:else}
									<div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center">
										<User class="w-6 h-6 text-gray-500" />
									</div>
								{/if}
							{:catch}
								<div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center">
									<User class="w-6 h-6 text-gray-500" />
								</div>
							{/await}
							<p class="{$theme.text.primary}">{request.username}</p>
						</div>
						<div class="flex gap-2">
							<Button 
								pill={true} 
								color="light" 
								size="xs"
								class="bg-green-500 text-white hover:bg-green-600 hover:cursor-pointer" 
								onclick={() => acceptFriendRequest(request.request_id)}
							>
								<Check class="w-4 h-4" />
							</Button>
							<Button 
								pill={true} 
								color="light" 
								size="xs"
								class="bg-red-500 text-white hover:bg-red-600" 
								onclick={() => rejectFriendRequest(request.request_id)}
							>
								<X class="w-4 h-4" />
							</Button>
						</div>
					</div>
				{/each}
			{/if}
			
			<hr class="{$theme.border.secondary}" />
		</div>

		<!-- 友達追加セクション -->
		<div class="flex flex-row gap-2 items-center justify-between flex-shrink-0">
			<h2 class="text-lg font-bold {$theme.text.primary}">友達</h2>
			<Button 
				color="light" 
				size="sm"
				onclick={() => (defaultModal = true)}
				class="hover:cursor-pointer"
			>
				<UserRoundPlus class="w-4 h-4" />
				<span>友達を追加</span>
			</Button>
		</div>

		<!-- 友達一覧 -->
		<div class="flex-1 overflow-y-auto space-y-2 pr-2">
			{#if loading}
				<div class="flex items-center justify-center py-8">
					<Spinner size="6" />
				</div>
			{:else if friends.length === 0}
				<div class="text-center py-8 {$theme.text.tertiary}">
					<p>友達がいません</p>
				</div>
			{:else}
				{#each friends as friend}
					<div class="flex flex-row gap-2 justify-between items-center p-2 border {$theme.border.secondary} rounded-lg">
						<div class="flex flex-row gap-2 items-center">
							{#await getPfpFromId(friend.id)}
								<div class="w-10 h-10 rounded-lg bg-gray-300 animate-pulse"></div>
							{:then pfp}
								{#if pfp}
									<img src={getMediaURL(pfp)} alt={friend.username} class="w-10 h-10 rounded-lg" />
								{:else}
									<div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center">
										<User class="w-6 h-6 text-gray-500" />
									</div>
								{/if}
							{:catch}
								<div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center">
									<User class="w-6 h-6 text-gray-500" />
								</div>
							{/await}
							<p class="{$theme.text.primary}">{friend.username}</p>
						</div>
						<div class="flex flex-row gap-2 items-center">
							<Button 
								color="light" 
								pill={true} 
								size="xs"
								class="p-2 hover:cursor-pointer" 
								onclick={() => goto(`/app/messages/${friend.id}`)}
							>
								<MessageCircle class="w-4 h-4" />
							</Button>
						</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>

	<!-- 友達追加モーダル -->
	<Modal title="友達を追加" form bind:open={defaultModal} onaction={({ action }) => alert(`Handle "${action}"`)}>
		<P>
			<Input 
				type="text" 
				placeholder="ユーザー名で検索" 
				bind:value={searchedInput} 
				oninput={searchUsers}
				class="{$theme.input.background} {$theme.input.border} {$theme.input.text}"
			/>
		</P>
		<P>
			{#if searchedUsers.length === 0 && searchedInput.length >= 3}
				<div class="text-center py-4 {$theme.text.tertiary}">
					<p>ユーザーが見つかりません</p>
				</div>
			{:else}
				{#each searchedUsers as user}
					<div class="flex flex-row gap-2 items-center justify-between p-2 border {$theme.border.secondary} rounded-lg">
						<div class="flex flex-row gap-2 items-center">
							{#await getPfpFromId(user.id)}
								<div class="w-10 h-10 rounded-lg bg-gray-300 animate-pulse"></div>
							{:then pfp}
								{#if pfp}
									<img src={getMediaURL(pfp)} alt={user.user_username} class="w-10 h-10 rounded-lg" />
								{:else}
									<div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center">
										<User class="w-6 h-6 text-gray-500" />
									</div>
								{/if}
							{:catch}
								<div class="w-10 h-10 rounded-lg bg-gray-300 flex items-center justify-center">
									<User class="w-6 h-6 text-gray-500" />
								</div>
							{/await}
							<p class="{$theme.text.primary}">{user.user_username}</p>
						</div>
						<Button 
							color="light" 
							size="xs"
							onclick={() => sendFriendRequest(user.user_id)}
							class="hover:cursor-pointer"
						>
							<UserPlus class="w-4 h-4" />
							<span>追加</span>
						</Button>
					</div>
				{/each}
			{/if}
		</P>
	</Modal>
</div>
