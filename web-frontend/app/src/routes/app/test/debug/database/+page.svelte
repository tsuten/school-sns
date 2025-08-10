<script>
    import { database } from "$lib/stores/simpleWSDBStore.js";
    import Page from "$lib/components/utils/page.svelte";
    import { onMount } from "svelte";

    let selectedType = 'all'; // 選択されたメッセージタイプ
    let displayedMessages = []; // 表示するメッセージ
    let dynamicHeaders = []; // 動的に生成されるテーブルヘッダー

    // databaseストアの変更を監視し、表示メッセージを更新
    $: {
        console.log("Database state:", $database); // ここでinspect
        if ($database) {
            if (selectedType === 'all') {
                displayedMessages = Object.values($database).flat(); // すべてのタイプを平坦化
            } else {
                displayedMessages = $database[selectedType] || []; // 選択されたタイプのメッセージ
            }
            // dynamicHeadersを更新
            const allKeys = new Set();
            displayedMessages.forEach(message => {
                if (message.data && typeof message.data === 'object') {
                    Object.keys(message.data).forEach(key => allKeys.add(key));
                }
            });
            dynamicHeaders = Array.from(allKeys).sort(); // ソートして表示順を一定にする
        } else {
            displayedMessages = [];
            dynamicHeaders = [];
        }
    }

    // onMountは冗長になる可能性もありますが、明示的に記述しておきます。
    // $:ブロックがリアクティブに動作するため、通常は不要です。
    onMount(() => {
        // 初回ロード時に$databaseの内容が利用可能であれば、displayedMessagesとdynamicHeadersを初期化
        // $:ブロックがこれを処理するため、このonMountのロジックはほとんどの場合で省略可能。
        // ここでは念のため残しておきます。
        if ($database) {
            if (selectedType === 'all') {
                displayedMessages = Object.values($database).flat();
            } else {
                displayedMessages = $database[selectedType] || [];
            }
            const allKeys = new Set();
            displayedMessages.forEach(message => {
                if (message.data && typeof message.data === 'object') {
                    Object.keys(message.data).forEach(key => allKeys.add(key));
                }
            });
            dynamicHeaders = Array.from(allKeys).sort();
        }
    });
</script>

<Page>
    <div class="mb-4">
        <label for="messageType" class="block text-sm font-medium text-gray-700">メッセージタイプでフィルタ:</label>
        <select id="messageType" bind:value={selectedType} class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
            <option value="all">すべてのタイプ</option>
            {#each Object.keys($database || {}) as type}
                <option value={type}>{type}</option>
            {/each}
        </select>
    </div>

    <table class="table-auto w-full border-collapse border border-gray-300">
        <thead>
            <tr class="bg-gray-100">
                <th class="border border-gray-300 px-4 py-2 text-left">タイムスタンプ</th>
                {#each dynamicHeaders as header}
                    <th class="border border-gray-300 px-4 py-2 text-left">{header}</th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each displayedMessages as message, index}
                <tr class="hover:bg-gray-50 {index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                    <td class="border border-gray-300 px-4 py-2 text-sm text-gray-500">
                        {message.timestamp}
                    </td>
                    {#each dynamicHeaders as header}
                        <td class="border border-gray-300 px-4 py-2 text-xs">
                            {#if message.data && message.data[header] !== undefined}
                                <!-- dataがオブジェクトでない場合や、文字列、数値などの場合はそのまま表示 -->
                                <!-- オブジェクトや配列の場合はJSON.stringifyで表示 -->
                                {typeof message.data[header] === 'object' && message.data[header] !== null
                                    ? JSON.stringify(message.data[header], null, 2)
                                    : message.data[header]}
                            {:else}
                                <!-- データが存在しない場合は空のセル -->
                            {/if}
                        </td>
                    {/each}
                </tr>
            {:else}
                <tr>
                    <td colspan="{2 + dynamicHeaders.length}" class="border border-gray-300 px-4 py-2 text-center text-gray-500">
                        メッセージがありません
                    </td>
                </tr>
            {/each}
        </tbody>
    </table>
</Page>