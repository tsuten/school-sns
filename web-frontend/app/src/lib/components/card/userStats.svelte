<script>
    import BaseCard from '$lib/components/utils/baseCard.svelte';
    let { user } = $props();
</script>

<BaseCard>
    <div class="flex flex-col gap-4">
        <h1>ユーザー統計</h1>
        <div class="flex flex-row gap-4">
            <div class="flex flex-col gap-2">
                <h2>投稿数</h2>
                <p>{user.posts_count || 0}</p>
            </div>
            <div class="flex flex-col gap-2">
                <h2>フォロワー数</h2>
                <p>{user.followers_count || 0}</p>
            </div>
            <div class="flex flex-col gap-2">
                <h2>フォロー数</h2>
                <p>{user.following_count || 0}</p>
            </div>
            <div class="flex flex-col gap-2">
                <h2>いいね数</h2>
                <p>{user.likes_count || 0}</p>
            </div>
        </div>
    </div>
</BaseCard>