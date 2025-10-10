<script>
    import { Toggle, Button } from "flowbite-svelte";
    import { settingsStore } from "$lib/stores/serverSettingsStore";

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    // チェックボックスの値を取得
    let profile = $state(false);
    let birthday = $state(false);
    let location = $state(false);
    let activity = $state(false);

    $effect(() => {
        if ($settingsStore) {
            profile = $settingsStore.is_profile_public || false;
            birthday = $settingsStore.is_birthday_public || false;
            location = $settingsStore.is_location_public || false;
            activity = $settingsStore.is_activity_public || false;
        }
    });

    function HandlePrivacySave() {
        console.log(
            "プロフィール公開:",
            profile,
            "誕生日公開:",
            birthday,
            "出身地公開:",
            location,
            "アクティビティ公開:",
            activity,
        );
        // 保存処理をここに実装
    }
</script>

<form>
    <div class="setting-content fade-in">
        <div class="mb-6">
            <h2 class="text-3xl font-bold text-gray-800 mb-2">
                プライバシー設定
            </h2>
            <p class="text-gray-600">
                アカウントのプライバシーを管理します
            </p>
        </div>

        <div class="space-y-6">
            <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3
                    class="text-lg font-semibold text-gray-800 mb-4"
                >
                    アカウントの公開設定
                </h3>
                <div class="space-y-4">
                    <!-- プロフィールを公開 -->
                    <div
                        class="flex items-center justify-between"
                    >
                        <div>
                            <label
                                class="text-sm font-medium text-gray-700"
                            >
                                プロフィールを公開
                            </label>
                            <p class="text-sm text-gray-500">
                                誰でもあなたのプロフィールを見ることができます
                            </p>
                        </div>
                        <Toggle bind:checked={profile} class="hover:cursor-pointer" />
                    </div>
                    <!-- 誕生日を公開 -->
                    <div
                        class="flex items-center justify-between"
                    >
                        <div>
                            <label
                                class="text-sm font-medium text-gray-700"
                            >
                                誕生日を公開
                            </label>
                            <p class="text-sm text-gray-500">
                                誕生日を他のユーザーに表示します
                            </p>
                        </div>
                        <Toggle bind:checked={birthday} class="hover:cursor-pointer" />
                    </div>
                    <!-- 出身地を公開 -->
                    <div
                        class="flex items-center justify-between"
                    >
                        <div>
                            <label
                                class="text-sm font-medium text-gray-700"
                            >
                                出身地を公開
                            </label>
                            <p class="text-sm text-gray-500">
                                出身地を他のユーザーに表示します
                            </p>
                        </div>
                        <Toggle bind:checked={location} class="hover:cursor-pointer" />
                    </div>
                    <!-- アクティビティを公開 -->
                    <div
                        class="flex items-center justify-between"
                    >
                        <div>
                            <label
                                class="text-sm font-medium text-gray-700"
                            >
                                アクティビティを公開
                            </label>
                            <p class="text-sm text-gray-500">
                                誰でもあなたのアクティビティを見ることができます
                            </p>
                        </div>
                        <Toggle bind:checked={activity} class="hover:cursor-pointer" />
                    </div>
                </div>
            </div>
        </div>
    </div>
    <div class="flex justify-end mt-8">
        <Button
            type="submit"
            class="px-6 py-3 hover:cursor-pointer"
            color="green"
            size="lg"
            onclick={() => HandlePrivacySave?.()}
        >
            保存
        </Button>
    </div>
</form>