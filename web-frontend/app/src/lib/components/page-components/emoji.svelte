<script lang="ts">
    // ロケールを定義
    import emojis from "emojibase-data/ja/data.json";
    import groupsSubgroups from "emojibase-data/ja/messages.json";

    // グループIDからグループ名を取得
    function getGroupName(groupId: number) {
        return groupsSubgroups.groups?.[groupId] || `Group ${groupId}`;
    }
    const excludedKeys = ['component', 'flags'];
    const filteredGroups = groupsSubgroups.groups.filter(group => 
  !excludedKeys.includes(group.key)
);

    // グループごとに絵文字を分類
    let groupedEmojis: Record<number, Record<number, typeof emojis>> = {};

    $: {
        groupedEmojis = {};
        for (const emoji of emojis) {
            if (emoji.group == null || emoji.subgroup == null) continue;
            if (!groupedEmojis[emoji.group]) groupedEmojis[emoji.group] = {};
            if (!groupedEmojis[emoji.group][emoji.subgroup])
                groupedEmojis[emoji.group][emoji.subgroup] = [];
            groupedEmojis[emoji.group][emoji.subgroup].push(emoji);
        }
    }

    let selectedGroup: number = 0;
    let selectedSubgroup: number | null = null;
    
</script>

<div>
    <h2>絵文字カテゴリ</h2>
    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        {#each Object.entries(filteredGroups || {}) as [groupId, groupName]}
            <button
                on:click={() => {
                    selectedGroup = +groupId;
                    selectedSubgroup = null;
                }}
                class:selected={selectedGroup === +groupId}
            >
                {groupName.message}
            </button>
        {/each}
    </div>

    <div style="margin-top: 1em;">
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            {#if selectedSubgroup !== null}
                {#each groupedEmojis[selectedGroup][selectedSubgroup] as emoji}
                    <span style="font-size: 2rem; cursor: pointer;">
                        <!-- title={emoji.annotation} -->
                        {emoji.emoji}
                    </span>
                {/each}
            {:else}
                {#each Object.values(groupedEmojis[selectedGroup] || {}) as emojis}
                    {#each emojis as emoji}
                        <span style="font-size: 2rem; cursor: pointer;">
                            <!-- title={emoji.annotation} -->
                            {emoji.emoji}
                        </span>
                    {/each}
                {/each}
            {/if}
        </div>
    </div>
</div>

<style>
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
</style>
