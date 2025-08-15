<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import DatetimeBadge from "$lib/components/badge/datetimeBadge.svelte";
    let { poll } = $props();

    let options = $state([
        {
            id: 1,
            name: "ピザ",
        },
        {
            id: 2,
            name: "ハンバーグ",
        },
        {
            id: 3,
            name: "カレー",
        },
    ]);

</script>

<BaseCard>
    <div class="flex flex-col gap-2 text-center">
        <div class="flex flex-row gap-2 items-center text-center justify-start">
            <h1 class="text-lg font-bold flex">何を食べたい？</h1>
            <DatetimeBadge date={new Date()} />
        </div>
        <div class="grid grid-cols-3 gap-2">
            <div class="flex flex-row gap-2 items-center text-center justify-start">
                <p>ヴェグヴェグヴェグチって話なの</p>
            </div>

            <div class="flex flex-col gap-2 col-span-2">
                {#each options as option}
                    <button class="bg-white text-black px-4 py-2 rounded-sm border-1 border-gray-300 hover:cursor-pointer">{option.name}</button>
                {/each}
            </div>
        </div>
    </div>
</BaseCard>