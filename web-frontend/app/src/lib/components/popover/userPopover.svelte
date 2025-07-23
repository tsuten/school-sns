<script>
    import { Popover } from "flowbite-svelte";
    import { apiClient, getMediaURL } from "$lib/services/django";
    import { Calendar } from "lucide-svelte";
    import { Avatar } from "flowbite-svelte";
    import { datetimeNormalize } from "$lib/utils/datetimeNormalize";
    let { user_id } = $props();

    let user = $state()

    $effect(() => {
        apiClient.get(`/users/profile/${user_id}`).then((res) => {
            user = res;
        }).catch((err) => {
            console.error(err);
        });
    });

    function getProfileImage(user) {
        return user?.pfp ? getMediaURL(user.pfp) : null;
    }
</script>

<Popover placement="bottom-start" trigger="click" class="p-2">
    <div class="flex flex-row gap-2">
        <Avatar src={getProfileImage(user)} />
    <p>{user.display_name}</p>
    <p>@{user.user_username}</p>
    </div>
    <div class="flex flex-row gap-2 items-center">
        <Calendar size="16" />
        <p>{datetimeNormalize(user.created_at)}</p>
    </div>
</Popover>