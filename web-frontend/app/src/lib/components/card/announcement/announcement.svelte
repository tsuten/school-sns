<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import { Button, Popover } from "flowbite-svelte";
    import { Check, Star, User, Clock } from "lucide-svelte";
    import { datetimeNormalize } from "$lib/utils/datetimeNormalize";
    import { apiClient } from "$lib/services/django";
    import { onMount } from "svelte";
    import { currentUser } from "$lib/stores/auth";
    import { browser } from "$app/environment";
    import UserChip from "../chips/userChip.svelte";
    import UserPopover from "$lib/components/popover/userPopover.svelte";
    let { announcement } = $props();

    const user = $derived(browser ? ($currentUser?.user || null) : null);

    let isRead = $state(false);

    onMount(() => {
        if (user && user.user_username && announcement.users_read.includes(user.user_username)) {
            isRead = true;
        }
    });

    function handleRead() {
        if (isRead) return; // 既読の場合は何もしない
        
        apiClient.post(`/announcement/announcement/${announcement.id}/read`)
            .then(response => {
                isRead = true;
            })
            .catch(error => {
                console.error('既読処理に失敗しました:', error);
            });
    }
    
    function TranslatePriority(priority) {
        switch (priority) {
            case "high":
                return "高";
            case "medium":
                return "中";
            case "low":
                return "低";
            default:
                return "不明";
        }
    }

    function GetPriorityColor(priority) {
        switch (priority) {
            case "high":
                return "text-red-500 w-4 h-4";
            case "medium":
                return "text-yellow-500 w-4 h-4";
            case "low":
                return "text-green-500 w-4 h-4";
            default:
                return "text-gray-500 w-4 h-4";
        }
    }
</script>

<BaseCard>
    <div class="flex flex-col gap-2 text-center">
        <div class="flex flex-row gap-2 justify-between">
            <div class="flex flex-row gap-2">
                <div class="flex flex-row gap-2 items-center">
                    <h1 class="text-lg font-bold">{announcement.title}</h1>
                </div>
                <div class="flex flex-row gap-2 items-center text-center justify-center text-gray-500 text-sm select-none">
                    <Clock class="w-4 h-4"/>
                    <p class="text-sm">{datetimeNormalize(announcement.created_at)}</p>
                </div>
            </div>
            <div class="flex flex-row gap-1 items-center text-sm text-gray-500">
                <Star class={GetPriorityColor(announcement.priority)} />
                <p>{TranslatePriority(announcement.priority)}</p>
            </div>
        </div>
        <div class="flex flex-row gap-2">
            <p>{announcement.content}</p>
        </div>
        <div class="flex flex-row gap-2 justify-between items-end">
            <div class="flex flex-row gap-2 items-center text-gray-500 text-sm text-center">
                <UserChip user={announcement.posted_by} />
                <UserPopover user_id={announcement.posted_by_id} />
            </div>
            <div class="flex flex-row gap-2 items-center items-end">
                {#if announcement.users_read.length > 0}
                    <div class="flex flex-row gap-2 items-center hover:cursor-pointer hover:bg-gray-100 rounded-sm p-1 select-none">
                        <p class="text-gray-500 text-sm">既読: {announcement.users_read.length}</p>
                    </div>
                    <Popover placement="bottom-start" trigger="click">
                        {#each announcement.users_read as user}
                            <p>{user}</p>
                        {/each}
                    </Popover>
                {/if}
                {#if isRead}
                    <Button class="bg-green-300 hover:bg-green-300 gap-2 items-center self-end rounded-sm">
                        <Check size="16" />
                        <span class="text-sm">既読</span>
                    </Button>
                {:else}
                    <Button color="green" class="gap-2 w-auto self-end hover:cursor-pointer rounded-sm" onclick={handleRead}>
                        <Check />
                        <span>既読にする</span>
                    </Button>
                {/if}
            </div>
        </div>
    </div>
</BaseCard>