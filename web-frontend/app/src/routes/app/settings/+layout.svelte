<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { page } from "$app/stores";
    import {
        Bell,
        Sun,
        Moon,
        Shield,
    } from "lucide-svelte";
    import InPageSideBar from "$lib/components/page-components/inPageSideBar.svelte";
    import { initialize, settingsStore } from "$lib/stores/serverSettingsStore";

    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();

    // 設定項目の定義
    let settingsItems = [
        {
            id: "privacy",
            title: "プライバシー",
            icon: Shield,
            href: "/settings/privacy"
        },
/*        {
            id: "theme", 
            title: "テーマ設定",
            icon: Sun,
            href: "/settings/theme"
        },*/
        {
            id: "notifications",
            title: "通知設定", 
            icon: Bell,
            href: "/settings/notifications"
        },
    ];

    // 初期化
    onMount(() => {
        initialize();
    });

    // 現在のページを取得
    let currentPath = $derived($page.url.pathname);
</script>

<div class="flex flex-row h-full">
    <!-- 左側メニュー（1/4幅） -->
    <div class="w-1/4 flex-shrink-0 border-r border-gray-300">
        <div class="h-full">
            <div class="p-4 border-b border-gray-300">
                <h1 class="text-2xl font-bold text-gray-800">設定</h1>
            </div>

            <nav class="">
                <ul class="">
                    {#each settingsItems as item}
                        <li>
                            <a
                                href={item.href}
                                class="flex items-center w-full p-4 hover:bg-gray-100 hover:cursor-pointer gap-2 transition-colors duration-200"
                                class:bg-blue-50={currentPath === item.href}
                                class:border-r-2={currentPath === item.href}
                                class:border-blue-500={currentPath === item.href}
                            >
                                <svelte:component
                                    this={item.icon}
                                    class="w-5 h-5 {currentPath === item.href ? 'text-blue-600' : ''}"
                                />
                                <span class="font-medium" class:text-blue-600={currentPath === item.href}>{item.title}</span>
                            </a>
                        </li>
                    {/each}
                </ul>
            </nav>
        </div>
    </div>

    <!-- 右側コンテンツ（3/4幅） -->
    <div class="w-3/4 bg-white overflow-y-auto">
        <div class="p-8">
            {@render children()}
        </div>
    </div>
</div>