<script>
    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let polls = [];

    for (let i = 0; i < 10; i++) {
        polls.push({
            id: i + 1,
            title: "投票" + (i + 1),
            description: "投票" + (i + 1) + "の説明",
            until: "2025-06-09 12:00:00",
            emoji: "🍣",
            options: [
                {
                    id: 1,
                    title: "オプション1",
                },
                {
                    id: 2,
                    title: "オプション2",
                },
                {
                    id: 3,
                    title: "オプション3",
                },
                {
                    id: 4,
                    title: "オプション4",
                },
            ],
        });
    }
</script>

<div class="flex flex-col gap-2">
    {#each polls as poll}
        <div class="flex flex-row w-full bg-white rounded-lg p-2 gap-4 border border-gray-300">
            <div class="flex flex-col gap-2">
                <p class="text-lg font-bold">{poll.title}</p>
                <p class="text-2xl text-gray-500">{poll.emoji}</p>
            </div>
            <p class="text-sm text-gray-500">{poll.description}</p>
            <p class="text-sm text-gray-500">{poll.until}</p>
            <div class="flex flex-row gap-2">
                {#each poll.options as option}
                    <p class="text-sm text-gray-500">{option.title}</p>
                {/each}
            </div>
        </div>
    {/each}
</div>