<script>
    import { apiClient } from "$lib/services/django";
    import Page from "$lib/components/utils/page.svelte";

    let password = $state();
    let username = $state();

    let valuesError_1 = $state();
    valuesError_1 = false;
    let valuesError_2 = $state();
    valuesError_2 = false;

    function HandleLogin() {
        valuesError_1 = false;
        valuesError_2 = false;
        if (username == null || password == null) {
            valuesError_1 = true;      
            return;
        }
        const response = apiClient.post("/token/pair", {
            password: password,
            username: username,
        });
        response
            .then((result) => {
                console.log("成功:", result);
                const access_token =result.access;
                document.cookie = `access_token=${access_token}; path=/`;
            })
            .catch((error) => {
                console.error("失敗:", error);
                valuesError_2 = true;
                return;
            })
            .finally(() => {
                console.log("完了");
            });
    }
</script>

<Page>
    <div class="flex flex-col items-center justify-center min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-md w-full space-y-8">
            <!-- ヘッダー -->
            <div class="text-center">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">ログイン</h1>
                <p class="text-gray-600">アカウントにサインインしてください</p>
            </div>

            <!-- エラーメッセージ -->
            {#if valuesError_1 === true}
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-red-800">ユーザー名またはパスワードを入力してください</p>
                        </div>
                    </div>
                </div>
            {/if}
            {#if valuesError_2 === true}
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-red-800">ログインに失敗しました。ユーザー名とパスワードを再確認してください</p>
                        </div>
                    </div>
                </div>
            {/if}

            <!-- ログインフォーム -->
            <form class="mt-8 space-y-6">
                <div class="space-y-4">
                    <div>
                        <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
                            ユーザーネーム
                        </label>
                        <input
                            type="text"
                            id="username"
                            bind:value={username}
                            placeholder="ユーザーネームを入力してください"
                            class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm transition-colors duration-200"
                            required
                        />
                    </div>
                    
                    <div>
                        <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                            パスワード
                        </label>
                        <input
                            type="password"
                            id="password"
                            bind:value={password}
                            placeholder="パスワードを入力してください"
                            class="appearance-none relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm transition-colors duration-200"
                            required
                        />
                    </div>
                </div>

                <div>
                    <button 
                        type="submit" 
                        id="submitBtn" 
                        on:click={() => HandleLogin?.()}
                        class="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <span class="absolute left-0 inset-y-0 flex items-center pl-3">
                            <svg class="h-5 w-5 text-blue-500 group-hover:text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
                            </svg>
                        </span>
                        ログイン
                    </button>
                </div>

                <!-- 追加リンク -->
                <div class="text-center">
                    <a href="#" class="font-medium text-blue-600 hover:text-blue-500 text-sm">
                        パスワードを忘れた場合
                    </a>
                </div>
            </form>
        </div>
    </div>
</Page>
