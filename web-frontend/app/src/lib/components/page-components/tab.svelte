<script>
    // propで親からタブで切り替える先のデータを受け取る
    // それを基にボタンでタブを切り替える処理を書く
    let { tabsData } = $props();
</script>

<div class="flex justify-around flex-wrap">
    {#each tabsData as t}
        <a href={t.href} class="flex items-center space-x-2">
            <button class="flex gap-2 hover:bg-red-700 px-20 py-3">
                <t.icon />
                {t.label}
            </button>
        </a>
    {/each}
</div>
