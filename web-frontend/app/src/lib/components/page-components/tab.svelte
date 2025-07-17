<script>
    // propで親からタブで切り替える先のデータを受け取る
    // それを基にボタンでタブを切り替える処理を書く
    let { tabsData } = $props();
</script>

<div class="flex justify-around border-b border-gray-300">
    {#each tabsData as t}
        <a href={t.href} class="flex items-center w-full">
            <button class="flex gap-2 hover:bg-gray-200 w-full hover:cursor-pointer justify-center h-10 items-center transition-all duration-300">
                <t.icon />
                {t.label}
            </button>
        </a>
    {/each}
</div>
