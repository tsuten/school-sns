<script>
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import Emoji from '$lib/components/page-components/emoji.svelte';
    //
    let password = $state();
    let username = $state();

    let valuesError_1 = $state();
    valuesError_1 = false;
    let valuesError_2 = $state();
    valuesError_2 = false;
    // $inspect(username);
    // $inspect(password);

    function HandleLogin() {
        valuesError_1 = false;
        valuesError_2 = false;
        if (username == null || password == null) {
            valuesError_1 = true;      
            return;
        }
        // ここでAPIに送信する処理を追加
        const response = apiClient.post("/token/pair", {
            password: password,
            username: username,
        });
        response
            .then((result) => {
                // fulfilled のときの処理
                console.log("成功:", result);
                const access_token =result.access;
                document.cookie = `access_token=${access_token}; path=/`;
            })
            .catch((error) => {
                // rejected のときの処理
                console.error("失敗:", error);
                valuesError_2 = true;
                return;
            })
            .finally(() => {
                // どちらでも共通で実行する処理
                console.log("完了");
            });
    }
</script>

<div>
    <h1>ログイン</h1>
    {#if valuesError_1 === true}
        <p>ユーザー名またはパスワードを入力してください</p>
    {/if}
    {#if valuesError_2 === true}
        <p>ログインに失敗しました。ユーザー名とパスワードを再確認してください</p>
    {/if}
    <form>
        <div>
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label>ユーザーネームを入力</label>
            <input
                type="text"
                id="username"
                bind:value={username}
                placeholder="例: 長曾我部元親"
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
            />
        </div>
        <button type="submit" id="submitBtn" onclick={() => HandleLogin?.()}
            >送信</button
        >
    </form>
</div>
<Emoji />
