<script>
    import { messages } from "$lib/stores/unifiedBaseWSStore.js";
    import Page from "$lib/components/utils/page.svelte";
</script>

<Page>
<table class="table-auto w-full border-collapse border border-gray-300">
    <thead>
        <tr class="bg-gray-100">
            <th class="border border-gray-300 px-4 py-2 text-left">メッセージタイプ</th>
            <th class="border border-gray-300 px-4 py-2 text-left">内容</th>
            <th class="border border-gray-300 px-4 py-2 text-left">タイムスタンプ</th>
            <th class="border border-gray-300 px-4 py-2 text-left">データ詳細</th>
        </tr>
    </thead>
    <tbody>
        {#each $messages as message, index}
            <tr class="hover:bg-gray-50 {index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}">
                <td class="border border-gray-300 px-4 py-2 font-medium">
                    <span class="px-2 py-1 text-xs rounded {
                        message.type === 'announcement' ? 'bg-blue-100 text-blue-800' :
                        message.type === 'class_message' ? 'bg-green-100 text-green-800' :
                        message.type === 'group_joined' ? 'bg-yellow-100 text-yellow-800' :
                        message.type === 'group_left' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                    }">
                        {message.type}
                    </span>
                </td>
                <td class="border border-gray-300 px-4 py-2">
                    {#if message.data.content}
                        {message.data.content}
                    {:else if message.data.title}
                        <strong>{message.data.title}</strong>
                        {#if message.data.content}
                            <br><span class="text-sm text-gray-600">{message.data.content}</span>
                        {/if}
                    {:else if message.data.group_name}
                        グループ: {message.data.group_name}
                    {:else}
                        -
                    {/if}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-sm text-gray-500">
                    {message.timestamp}
                </td>
                <td class="border border-gray-300 px-4 py-2 text-xs">
                    <details>
                        <summary class="cursor-pointer text-blue-600 hover:text-blue-800">詳細表示</summary>
                        <pre class="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto max-h-32">{JSON.stringify(message.data, null, 2)}</pre>
                    </details>
                </td>
            </tr>
        {:else}
            <tr>
                <td colspan="4" class="border border-gray-300 px-4 py-2 text-center text-gray-500">
                    メッセージがありません
                </td>
            </tr>
        {/each}
    </tbody>
</table>
</Page>