<script>
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    //
    let password = $state();
    let username = $state();

    // $inspect(username);
    // $inspect(password);

    function onSend() {
        // ここでAPIに送信する処理を追加
        let getIsLogin;
        let response = apiClient.post("/token/pair", {
            password: password,
            username: username,
        });
        response
            .then((result) => {
                // fulfilled のときの処理
                console.log("成功:", result);
                console.log(result.access)
            })
            .catch((error) => {
                // rejected のときの処理
                console.error("失敗:", error);
            })
            .finally(() => {
                // どちらでも共通で実行する処理
                console.log("完了");
            });
    }
</script>

<div>
    <h1>ログイン</h1>
    <form>
        <div>
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label>ユーザーネームを入力</label>
            <input
                type="text"
                id="username"
                bind:value={username}
                required
                placeholder="例: 武田信玄"
            />
        </div>
        <br />
        <div>
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label>パスワードを入力</label>
            <input
                type="password"
                id="password"
                bind:value={password}
                required
            />
        </div>
        <button type="submit" id="submitBtn" onclick={() => onSend?.()}
            >送信</button
        >
    </form>
</div>
