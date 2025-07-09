<script>
    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();
</script>

<div class="flex flex-col gap-4">
    <h1 class="text-2xl font-bold">クラス</h1>
    <div class="flex flex-row gap-4">
        <li class="flex flex-col gap-2">
            <span>お知らせ</span>
        </li>
        <li class="flex flex-col gap-2">
            <span>チャット</span>
        </li>
        <li class="flex flex-col gap-2">
            <span>メンバー</span>
        </li>
        <li class="flex flex-col gap-2">
            <span>ファイル</span>
        </li>
    </div>
    {@render children()}
</div>