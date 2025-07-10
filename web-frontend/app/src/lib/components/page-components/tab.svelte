<script>
    // propで親からタブで切り替える先のデータを受け取る
    // それを基にボタンでタブを切り替える処理を書く
    let { tabsData } = $props();
</script>
<div class="flex justify-around">
    {#each tabsData as t}
        <a href="{t.href}"><button>{t.label}</button></a>
    {/each}

    
</div>