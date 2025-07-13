<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";

    let { user } = $props();
</script>

<BaseCard>
    <div class="flex flex-col items-center gap-2">
        <img src={user.profile_image} alt="Profile Image" class="w-10 h-10 rounded-full" />
        <span class="text-sm font-medium">{user.display_name}</span>
        <span class="text-sm text-gray-500">{user.username}</span>
    </div>
</BaseCard>

