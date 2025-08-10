<script>
    import Page from "$lib/components/utils/page.svelte";
    import { Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell, PaginationNav } from 'flowbite-svelte';
    import { datetimeNormalize } from "$lib/utils/datetimeNormalize";

    let allUsers = [
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        {
            name: "佐藤花子",
            email: "sato@example.com", 
            role: "メンバー",
            joined_at: new Date().toISOString()
        },
        {
            name: "田中一郎",
            email: "tanaka@example.com",
            role: "メンバー",
            joined_at: new Date().toISOString()
        },
        {
            name: "鈴木次郎",
            email: "suzuki@example.com",
            role: "メンバー",
            joined_at: new Date().toISOString()
        },
        {
            name: "高橋三郎",
            email: "takahashi@example.com",
            role: "メンバー",
            joined_at: new Date().toISOString()
        },
        {
            name: "伊藤四郎",
            email: "ito@example.com",
            role: "メンバー",
            joined_at: new Date().toISOString()
        },
        {
            name: "渡辺五郎",
            email: "watanabe@example.com",
            role: "メンバー",
            joined_at: new Date().toISOString()
        },
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        {
            name: "山田太郎",
            email: "yamada@example.com",
            role: "管理者",
            joined_at: new Date().toISOString()
        },
        
    ];

    let currentPage = $state(1);
    const itemsPerPage = 10;
    const totalPages = Math.ceil(allUsers.length / itemsPerPage);

    // 現在のページのユーザーを計算
    let displayedUsers = $derived(allUsers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage));

    function handlePageChange(page) {
        currentPage = page;
    }
</script>

<Page>
    <h1>ユーザー管理</h1>
    <Table hoverable={true} class="border border-gray-300 rounded-sm table-fixed">
        <TableHead>
            <TableHeadCell>名前</TableHeadCell>
            <TableHeadCell>役割</TableHeadCell>
            <TableHeadCell>参加日時</TableHeadCell>
        </TableHead>
        <TableBody>
            {#each displayedUsers as user}
                <TableBodyRow>
                    <TableBodyCell>{user.name}</TableBodyCell>
                    <TableBodyCell>{user.role}</TableBodyCell>
                    <TableBodyCell>{datetimeNormalize(user.joined_at)}</TableBodyCell>
                </TableBodyRow>
            {/each}
        </TableBody>
    </Table>
    
    <div class="mt-4 flex items-center justify-between">
        <div class="text-sm text-gray-700 dark:text-gray-400">
            表示中: <span class="font-semibold">{(currentPage - 1) * itemsPerPage + 1}</span> - 
            <span class="font-semibold">{Math.min(currentPage * itemsPerPage, allUsers.length)}</span> / 
            全<span class="font-semibold">{allUsers.length}</span>件
        </div>
        <PaginationNav {currentPage} {totalPages} onPageChange={handlePageChange} visiblePages={5} />
    </div>
</Page>