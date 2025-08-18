<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import DatetimeBadge from "$lib/components/badge/datetimeBadge.svelte";
    import UserChip from "$lib/components/card/chips/userChip.svelte";
    import { apiClient } from "$lib/services/django";
    let { poll } = $props();

    // 投票者の合計数を計算
    let totalVotes = $derived(poll.choices.reduce((sum, choice) => sum + (choice.vote_count || 0), 0));

    async function vote(choice_id) {
        await apiClient.post(`/polls/choice/${choice_id}/vote`);
        
        // 投票後の状態を更新
        poll.choices.forEach(choice => {
            choice.is_voted_by_user = choice.id === choice_id;
        });
    }

</script>

<BaseCard>
    <div class="flex flex-col gap-2 text-center">
        <div class="flex flex-row gap-2 items-center text-center justify-start">
            <h1 class="text-lg font-bold flex">{poll.question}</h1>
            <div class="text-gray-500">
                <DatetimeBadge date={poll.created_at} />
            </div>
        </div>
        <div class="flex flex-row gap-4">
            <div class="flex flex-col gap-2 justify-between items-start flex-1">
                <p>{poll.description}</p>
                <div class="flex flex-row gap-2 items-center text-center justify-between w-full">
                    <UserChip user={poll.username} />
                    <p class="text-sm text-gray-600">投票数: {totalVotes}</p>
                </div>
            </div>

            <div class="flex flex-col gap-2 flex-1">
                {#each poll.choices as choice}
                    <button 
                        onclick={() => vote(choice.id)} 
                        class="px-4 py-2 rounded-sm border-1 border-gray-300 hover:cursor-pointer {choice.is_voted_by_user ? 'bg-blue-500 text-white' : 'bg-white text-black'}"
                    >
                        {choice.choice_text}
                    </button>
                {/each}
            </div>
        </div>
    </div>
</BaseCard>