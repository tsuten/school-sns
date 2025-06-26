<script>
    import Emoji from '$lib/components/page-components/emoji.svelte'; 
</script>
<div>
    <h1> ログイン </h1>
    <form>
        <div> 
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label>ユーザーネームを入力</label>
            <input 
                type="text"
                required
                placeholder="例: 武田信玄"
            />

        </div>
        <br>
        <div>
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label>パスワードを入力</label>
            <input 
                type="password"
                required
            />            
        </div>
        <button type="submit" id="submitBtn">送信</button>
    </form>
</div>
<Emoji />