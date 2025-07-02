<script lang="ts">
    // ロケールを定義
    import emojis from "emojibase-data/ja/data.json";
    import groupsSubgroups from "emojibase-data/ja/messages.json";
    import { 
        Smile, 
        Hand, 
        Dog, 
        Apple, 
        Map, 
        Zap, 
        Glasses 
    } from "lucide-svelte";

    let emoji_group = {
        "0": Smile,
        "1": Hand,
        "3": Dog,
        "4": Apple,
        "5": Map,
        "6": Zap,
        "7": Glasses,
    };

    // 除外するキーを定義
    const excludedKeys = ["component", "flags"];

    // グループを適切にフィルタリング
    let filteredGroups: Array<{ id: number; name: string }> = [];

    $: {
        filteredGroups = [];
        if (groupsSubgroups.groups) {
            Object.entries(groupsSubgroups.groups).forEach(([key, value]) => {
                const groupId = parseInt(key);
                // 数値のgroupIdで、除外キーに含まれず、対応する絵文字データが存在するもののみ
                if (
                    !isNaN(groupId) &&
                    !excludedKeys.includes(key) &&
                    emoji_group[groupId.toString()]
                ) {
                    filteredGroups.push({
                        id: groupId,
                        name:
                            typeof value === "string"
                                ? value
                                : value.message || `Group ${groupId}`,
                    });
                }
            });
        }
    }

    // グループごとに絵文字を分類
    let groupedEmojis: Record<number, Record<number, typeof emojis>> = {};

    $: {
        groupedEmojis = {};
        for (const emoji of emojis) {
            if (emoji.group == null || emoji.subgroup == null) continue;

            // 除外されたグループをスキップ（文字列と数値の両方をチェック）
            if (
                excludedKeys.includes(emoji.group.toString()) ||
                excludedKeys.includes(String(emoji.group))
            )
                continue;

            // emoji_groupに定義されていないグループもスキップ
            if (!emoji_group[emoji.group.toString()]) continue;

            if (!groupedEmojis[emoji.group]) groupedEmojis[emoji.group] = {};
            if (!groupedEmojis[emoji.group][emoji.subgroup])
                groupedEmojis[emoji.group][emoji.subgroup] = [];
            groupedEmojis[emoji.group][emoji.subgroup].push(emoji);
        }
    }

    let selectedGroup: number = 0;
    let selectedSubgroup: number | null = null;

    // 初期選択グループを利用可能な最初のグループに設定
    $: if (
        filteredGroups.length > 0 &&
        !filteredGroups.find((g) => g.id === selectedGroup)
    ) {
        selectedGroup = filteredGroups[0].id;
    }
</script>

<div id="emoji-picker" class="w-80 flex flex-col items-center p-4 box-border border border-gray-300 rounded-sm">
    <h2 class="mb-2 text-sm font-semibold text-gray-600">絵文字カテゴリ</h2>
    <div class="flex gap-2 overflow-x-auto pb-2">
        {#each filteredGroups as group}
            <button
                on:click={() => {
                    selectedGroup = group.id;
                    selectedSubgroup = null;
                }}
                class={`w-8 h-8 flex items-center justify-center rounded-md transition-colors select-none ${selectedGroup === group.id ? 'bg-blue-500 text-white' : 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 hover:cursor-pointer'}`}
                title={group.name}
            >
                <svelte:component this={emoji_group[group.id.toString()]} strokeWidth={1.5} />
            </button>
        {/each}
    </div>

    <div id="emoji-list" class="overflow-y-auto h-52 w-full">
        <div class="grid grid-cols-7 gap-2">
            {#if selectedSubgroup !== null}
                {#each groupedEmojis[selectedGroup][selectedSubgroup] as emoji}
                    <span class="text-2xl flex items-center justify-center hover:cursor-pointer select-none">
                        {emoji.emoji}
                    </span>
                {/each}
            {:else}
                {#each Object.values(groupedEmojis[selectedGroup] || {}) as emojis}
                    {#each emojis as emoji}
                        <span class="text-2xl flex items-center justify-center hover:cursor-pointer select-none">
                            {emoji.emoji}
                        </span>
                    {/each}
                {/each}
            {/if}
        </div>
    </div>
</div>