<script>
    import '../../../app.css';
    import { onMount } from "svelte";
    import { apiClient } from "$lib/services/django";
    import { goto } from "$app/navigation";
    import { Button, Input, Label, Alert } from 'flowbite-svelte';
    import { Lock, Shield, AlertCircle, CheckCircle } from 'lucide-svelte';
    
    let password = $state("");
    let username = $state("");
    let isLoading = $state(false);
    let errorMessage = $state("");
    let successMessage = $state("");

    async function handleAdminLogin() {
        // 入力値の検証
        if (!username.trim() || !password.trim()) {
            errorMessage = "ユーザー名とパスワードを入力してください";
            return;
        }

        isLoading = true;
        errorMessage = "";
        successMessage = "";

        try {
            // アドミン認証用のエンドポイント（実際のAPIに合わせて調整が必要）
            const response = await apiClient.post("/admin/login/", {
                username: username.trim(),
                password: password
            });

            if (response.data && response.data.access) {
                // アクセストークンを保存
                document.cookie = `admin_access_token=${response.data.access}; path=/; secure; samesite=strict`;
                
                successMessage = "ログインに成功しました。ダッシュボードにリダイレクトします...";
                
                // 少し待ってからダッシュボードにリダイレクト
                setTimeout(() => {
                    goto("/admin/dashboard");
                }, 1500);
            } else {
                errorMessage = "ログインに失敗しました。認証情報を確認してください。";
            }
        } catch (error) {
            console.error("ログインエラー:", error);
            
            if (error.response?.status === 401) {
                errorMessage = "ユーザー名またはパスワードが正しくありません";
            } else if (error.response?.status === 403) {
                errorMessage = "アドミン権限がありません";
            } else if (error.response?.status >= 500) {
                errorMessage = "サーバーエラーが発生しました。しばらく待ってから再試行してください。";
            } else {
                errorMessage = "ログインに失敗しました。ネットワーク接続を確認してください。";
            }
        } finally {
            isLoading = false;
        }
    }

    function handleSubmit(event) {
        event.preventDefault();
        handleAdminLogin();
    }

    // エラーメッセージをクリア
    function clearError() {
        errorMessage = "";
    }

    // 成功メッセージをクリア
    function clearSuccess() {
        successMessage = "";
    }
</script>

<div class="min-w-screen w-full flex flex-col items-center justify-center">
    <div class="text-center">
        <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-red-100 mb-4">
            <Shield class="h-6 w-6 text-red-600" />
        </div>
        <h2 class="text-3xl font-extrabold text-gray-900 mb-2">
            管理者ログイン
        </h2>
        <p class="text-sm text-gray-600 mb-10">
            管理者アカウントを使用してください
        </p>
    </div>

    <!-- エラーメッセージ -->
    {#if errorMessage}
        <Alert color="red" dismissable on:close={clearError} class="mb-6">
            <AlertCircle class="w-4 h-4" />
            <span class="font-medium">{errorMessage}</span>
        </Alert>
    {/if}

    <!-- 成功メッセージ -->
    {#if successMessage}
        <Alert color="green" dismissable on:close={clearSuccess} class="mb-6">
            <CheckCircle class="w-4 h-4" />
            <span class="font-medium">{successMessage}</span>
        </Alert>
    {/if}

    <form onsubmit={handleSubmit} class="space-y-6">
        <div>
            <Label for="username" class="mb-2">ユーザー名</Label>
            <Input
                id="username"
                name="username"
                type="text"
                required
                bind:value={username}
                placeholder="管理者ユーザー名を入力"
                disabled={isLoading}
                size="lg"
            />
        </div>

        <div>
            <Label for="password" class="mb-2">パスワード</Label>
            <Input
                id="password"
                name="password"
                type="password"
                required
                bind:value={password}
                placeholder="パスワードを入力"
                disabled={isLoading}
                size="lg"
            />
        </div>

        <Button
            type="submit"
            disabled={isLoading}
            color="red"
            size="lg"
            class="w-full mb-10"
        >
            {#if isLoading}
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                ログイン中...
            {:else}
                <Lock class="w-4 h-4 mr-2" />
                ログイン
            {/if}
        </Button>
    </form>
</div>
