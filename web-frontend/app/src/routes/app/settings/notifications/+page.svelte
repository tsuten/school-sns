<script>
    import { Toggle, Button } from "flowbite-svelte";
    import { settingsStore } from "$lib/stores/serverSettingsStore";

    // 通知設定の状態
    let notification = $state(true);

    $effect(() => {
        if ($settingsStore) {
            notification = $settingsStore.is_notification_enabled || false;
        }
    });

    function HandleNotificationSave() {
        console.log("通知設定:", notification);
        // 保存処理をここに実装
    }
</script>

<div class="setting-content fade-in">
    <div class="mb-6">
        <h2 class="text-3xl font-bold text-gray-800 mb-2">
            通知設定
        </h2>
        <p class="text-gray-600">通知の受信設定を管理します</p>
    </div>

    <form>
        <div class="space-y-6">
            <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">
                    プッシュ通知
                </h3>
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                        <div>
                            <label
                                class="text-sm font-medium text-gray-700"
                            >
                                通知
                            </label>
                            <p class="text-sm text-gray-500">
                                リアルタイムで通知を受け取る
                            </p>
                        </div>
                        <Toggle bind:checked={notification} class="hover:cursor-pointer" />
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
                onclick={() => HandleNotificationSave?.()}
            >
                保存
            </Button>
        </div>
    </form>
</div> 