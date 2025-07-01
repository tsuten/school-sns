<script lang="ts">
    // ロケールを定義
    import emojis from "emojibase-data/ja/data.json";
    import groupsSubgroups from "emojibase-data/ja/messages.json";

    let emoji_group = {
        "0": "😊",
        "1": "✌️",
        "3": "🐶",
        "4": "🍉",
        "5": "🗾",
        "6": "🥎",
        "7": "🕶",
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

<div id="emoji-picker">
    <h2>絵文字カテゴリ</h2>
    <div>
        {#each filteredGroups as group}
            <button
                on:click={() => {
                    selectedGroup = group.id;
                    selectedSubgroup = null;
                }}
                class:selected={selectedGroup === group.id}
                title={group.name}
            >
                {emoji_group[group.id.toString()]}
            </button>
        {/each}
    </div>

    <div id="emoji-list">
        <div>
            {#if selectedSubgroup !== null}
                {#each groupedEmojis[selectedGroup][selectedSubgroup] as emoji}
                    <span class="emoji">
                        {emoji.emoji}
                    </span>
                {/each}
            {:else}
                {#each Object.values(groupedEmojis[selectedGroup] || {}) as emojis}
                    {#each emojis as emoji}
                        <span class="emoji">
                            {emoji.emoji}
                        </span>
                    {/each}
                {/each}
            {/if}
        </div>
    </div>
</div>

<style>
    #emoji-list {
        overflow-y: auto;
        height: 200px;
        align-content: flex-start;
    }

    #emoji-list > div {
        display: flex;
        flex-wrap: wrap;
    }

    .emoji {
        font-size: 1.5rem;
        display: inline-block;
        margin: 0.2rem;
        line-height: 1;
    }
    #emoji-picker {
        width: 40%;
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1em;
        box-sizing: border-box;
    }
    button.selected {
        background: #0078d4;
        color: white;
    }
    button {
        border: 1px solid #ccc;
        background: #f9f9f9;
        padding: 0.3em 0.8em;
        border-radius: 4px;
        cursor: pointer;
    }
    button:not(.selected):hover {
        background: #eee;
    }

    #emoji-list::-webkit-scrollbar {
        width: 10px;
        background: #f1f1f1;
    }

    #emoji-list::-webkit-scrollbar-thumb {
        background: #bdbdbd;
        border-radius: 0; /* ← 角丸をなくして四角に */
    }

    #emoji-list::-webkit-scrollbar-thumb:hover {
        background: #888;
    }
</style>
