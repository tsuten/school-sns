<script>
    import { onMount } from "svelte";
    import {
        House,
        Bell,
        User,
        Settings,
        MessageCircle,
        Calendar,
        LogOut,
        Crown,
        TrendingUp,
        Tickets,
        ChartGantt,
        Bookmark,
        Vote,
        Heart,
        Key,
        NotebookPen,
        School,
        University,
        Presentation,
        HeartHandshake,
        Shield,
        Sun,
        Moon,
        Monitor,
    } from "lucide-svelte";
    import { Toggle, Button } from "flowbite-svelte";

    // 設定項目の定義
    let settingsItems = [
        {
            id: "privacy",
            title: "プライバシー",
            icon: Shield,
        },
        {
            id: "theme",
            title: "テーマ設定",
            icon: Sun,
        },
        {
            id: "notifications",
            title: "通知設定",
            icon: Bell,
        },
    ];

    // 現在選択されている設定項目
    let currentSetting = "privacy";

    // 設定項目を切り替える関数
    function showSetting(settingId) {
        currentSetting = settingId;
    }

    // 初期化時にプロフィールを選択
    onMount(() => {
        currentSetting = "privacy";
    });

    // チェックボックスの値を取得
    let profile = true;
    let birthday = true;
    let location = true;
    let activity = true;

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

    // 外観モードの選択状態
    let themeMode = "light";

    function HandleThemeSave() {
        console.log("選択されたテーマモード:", themeMode);
        // 保存処理をここに実装
    }
    
    // 通知設定の状態
    let notification = true;

    function HandleNotificationSave() {
        console.log("通知設定:", notification);
        // 保存処理をここに実装
    }
</script>

<div class="flex h-full">
    <!-- 左側メニュー -->
    <div class="w-50 bg-white border-r border-gray-200 shadow-sm">
        <div class="p-6 border-b border-gray-100">
            <h1 class="text-2xl font-bold text-gray-800">設定</h1>
            <p class="text-gray-600 text-sm mt-1">アカウント設定を管理</p>
        </div>

        <nav class="p-4">
            <ul class="space-y-2">
                {#each settingsItems as item}
                    <li>
                        <button
                            onclick={() => showSetting(item.id)}
                            class="setting-item w-full text-left px-4 py-3 rounded-lg hover:bg-mint-50 hover:text-mint-700 transition-colors duration-200 flex items-center space-x-3"
                            class:bg-mint-100={currentSetting === item.id}
                            class:text-mint-700={currentSetting === item.id}
                            class:active-menu={currentSetting === item.id}
                        >
                            <svelte:component
                                this={item.icon}
                                class="w-5 h-5"
                            />
                            <span class="font-medium">{item.title}</span>
                        </button>
                    </li>
                {/each}
            </ul>
        </nav>
    </div>

    <!-- 右側コンテンツ -->
    <div class="flex-1 bg-white overflow-y-auto">
        <div class="p-8">
            <!-- プライバシー設定 -->
            {#if currentSetting === "privacy"}
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
                            save
                        </Button>
                    </div>
                </form>
            {/if}

            <!-- テーマ設定 -->
            {#if currentSetting === "theme"}
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
                                    for="right"
                                    class="border-2 rounded-lg p-4 cursor-pointer transition-shadow flex flex-col items-center justify-center space-y-2 w-full bg-white border-mint-500 shadow-md"
                                    class:bg-mint-50={themeMode === "light"}
                                    class:border-mint-500={themeMode ===
                                        "light"}
                                    class:border-gray-200={themeMode !==
                                        "light"}
                                >
                                    <input
                                        id="right"
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
                                save
                            </Button>
                        </div>
                    </form>
                </div>
            {/if}

            <!-- 通知設定 -->
            {#if currentSetting === "notifications"}
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
                                                通知を全部切れます　切れるナイフだw
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
                            save
                        </Button>
                    </div>
                    </form>
                </div>
            {/if}
        </div>
    </div>
</div>

<style>
    .setting-item {
        transition: all 0.2s ease;
    }
    .setting-item:hover {
        transform: translateX(4px);
    }
    .fade-in {
        animation: fadeIn 0.3s ease-in-out;
    }
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>