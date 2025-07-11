 <script>
    /** @type {{ data: import('./$types').LayoutData, children: import('svelte').Snippet }} */
    let { data, children } = $props();
    import { MessageSquareMore, Users, FileText, Megaphone, UsersRound, Info } from "lucide-svelte";
    import Tab from "$lib/components/page-components/tab.svelte";
    import { page } from "$app/stores";

    let tabs = [
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
    ]
</script>

<div class="flex flex-col gap-4">
    <div class="">
        <Tab tabsData={tabs} />
    </div>
    {@render children()}
</div>