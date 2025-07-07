<script>
    import ProfileCard from '$lib/components/page-components/profileCard.svelte';
    import UserStats from '$lib/components/card/userStats.svelte';
    import Page from '$lib/components/utils/page.svelte';
    let user = $state({
            id: 1,
            display_name: 'John Doe',
            email: 'john.doe@example.com',
            profileImage: 'https://via.placeholder.com/150',
            bio: 'I am a software engineer',
        });
</script>

<Page>
    <ProfileCard user={user} />
    <UserStats user={user} />
</Page>