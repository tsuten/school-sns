<script>
    import { Sun, Moon } from "lucide-svelte";
    import { Button } from "flowbite-svelte";
    import { settingsStore } from "$lib/stores/serverSettingsStore";

    // 外観モードの選択状態
    let themeMode = $state("light");

    $effect(() => {
        if ($settingsStore) {
            themeMode = $settingsStore.is_dark_mode_enabled ? "dark" : "light";
        }
    });

    function HandleThemeSave() {
        console.log("選択されたテーマモード:", themeMode);
        // 保存処理をここに実装
    }
</script>

<div class="setting-content fade-in">
    <form>
        <div class="mb-6">
            <h2 class="text-3xl font-bold text-gray-800 mb-2">
                テーマ設定
            </h2>
            <p class="text-gray-600">
                アプリの外観をカスタマイズします
            </p>
        </div>

        <div class="bg-gray-50 rounded-xl p-6">
            <h3
                class="text-lg font-semibold text-gray-800 mb-4"
            >
                外観モード
            </h3>
            <!-- 外観モードの選択UIをラジオボタンで実装、システムは削除 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- ライトモード -->
                <label
                    for="light"
                    class="border-2 rounded-lg p-4 cursor-pointer transition-shadow flex flex-col items-center justify-center space-y-2 w-full bg-white border-mint-500 shadow-md"
                    class:bg-mint-50={themeMode === "light"}
                    class:border-mint-500={themeMode === "light"}
                    class:border-gray-200={themeMode !== "light"}
                >
                    <input
                        id="light"
                        type="radio"
                        name="themeMode"
                        value="light"
                        class="sr-only peer"
                        bind:group={themeMode}
                    />
                    <Sun class="w-6 h-6 text-gray-600 mb-2" />
                    <span
                        class="text-sm font-medium text-gray-700"
                        >ライトモード</span
                    >
                    {#if themeMode === "light"}
                        <div
                            class="w-4 h-4 bg-mint-500 rounded-full mt-2"
                        />
                    {/if}
                </label>
                <!-- ダークモード -->
                <label
                    for="dark"
                    class="border-2 rounded-lg p-4 cursor-pointer transition-shadow flex flex-col items-center justify-center space-y-2 w-full bg-white border-gray-200"
                    class:bg-mint-50={themeMode === "dark"}
                    class:border-mint-500={themeMode === "dark"}
                    class:border-gray-200={themeMode !== "dark"}
                >
                    <input
                        id="dark"
                        type="radio"
                        name="themeMode"
                        value="dark"
                        class="sr-only peer"
                        bind:group={themeMode}
                    />
                    <Moon class="w-6 h-6 text-gray-300 mb-2" />
                    <span
                        class="text-sm font-medium text-gray-700"
                        >ダークモード</span
                    >
                    {#if themeMode === "dark"}
                        <div
                            class="w-4 h-4 bg-mint-500 rounded-full mt-2"
                        />
                    {/if}
                </label>
            </div>
        </div>
        <div class="flex justify-end mt-8">
            <Button
                type="submit"
                class="px-6 py-3 hover:cursor-pointer"
                color="green"
                size="lg"
                onclick={() => HandleThemeSave?.()}
            >
                保存
            </Button>
        </div>
    </form>
</div> 