<script>
	import UserInfoCard from '$lib/components/page-components/userInfoCard.svelte';
	
	const user = {
		id: '123',
		username: 'john_doe',
		display_name: '田中太郎',
		bio: 'プログラマーです。\nよろしくお願いします！',
		location: '東京都',
		birth_place: '大阪府',
		birthday: '1990-05-15',
		pfp: '/path/to/image.jpg',
		created_at: '2023-01-01T00:00:00Z',
		posts_count: 42,
		followers_count: 150,
		following_count: 89
	};
</script>

<!-- 自分のプロフィール -->
<UserInfoCard 
	{user} 
	isOwnProfile={true}
	showEditButton={true}
	onEdit={() => console.log('編集')}
/>