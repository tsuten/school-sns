 <script>
    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();
    import { MessageSquareMore, Users, FileText, Megaphone, UsersRound, Info, Settings } from "lucide-svelte";
    import Tab from "$lib/components/page-components/tab.svelte";
    import { page } from "$app/stores";
    import { apiClient } from "$lib/services/django.js";
    import { onMount } from "svelte";
    
    let tabs = $state([
        {
            label: "お知らせ",
            href: `/class/${$page.params.class}/announcement`,
            icon: Megaphone
        },
        {
            label: "チャット",
            href: `/class/${$page.params.class}/chat`,
            icon: MessageSquareMore
        },
        {
            label: "メンバー",
            href: `/class/${$page.params.class}/members`,
            icon: UsersRound
        },
        {
            label: "ファイル",
            href: `/class/${$page.params.class}/files`,
            icon: FileText
        },
        {
            label: "情報",
            href: `/class/${$page.params.class}/info`,
            icon: Info
        }
    ]);

    async function fetchIsManager() {
        const response = await apiClient.get("/organizations/is_manager/" + $page.params.class);
        console.log(response);
        return response;
    }

    async function addTabIfManager() {
        const isManager = await fetchIsManager();
        if (isManager) {
            tabs.push({
                label: "管理・設定",
                href: `/class/${$page.params.class}/manage`,
                icon: Settings
            });
        }
    }

    onMount(async () => {
        await addTabIfManager();
    });
</script>

<div class="flex flex-col">
    <div class="">
        <Tab tabsData={tabs} />
    </div>
    {@render children()}
</div>