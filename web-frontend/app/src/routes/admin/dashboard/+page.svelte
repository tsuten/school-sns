<script>
    import '../../../app.css';
    import { onMount } from "svelte";
    import { Badge, Table, TableBody, TableBodyCell, TableBodyRow, TableHead, TableHeadCell } from 'flowbite-svelte';
    import { 
        Users, 
        MessageSquare, 
        FileText, 
        Settings,
        TrendingUp, 
        AlertTriangle, 
        CheckCircle, 
        Clock,
        BarChart3,
        Activity
    } from 'lucide-svelte';
    import { apiClient } from '$lib/services/django.js';

    // ダッシュボードデータ
    let stats = $state({
        totalUsers: 0,
        activeUsers: 0,
        totalPosts: 0,
        totalCircles: 0,
        systemHealth: 0,
        activeSessions: 0,
        newUsersThisMonth: 0,
        postsThisMonth: 0,
        activeCircles: 0
    });

    let isLoading = $state(true);
    let error = $state(null);

    // APIから統計データを取得
    async function fetchStats() {
        try {
            isLoading = true;
            error = null;
            
            console.log('統計データの取得を開始...');
            
            // まずテストエンドポイントを試してみる
            try {
                const testResponse = await apiClient.get("/admin/test");
                console.log('テストエンドポイントの結果:', testResponse);
            } catch (testErr) {
                console.log('テストエンドポイントエラー:', testErr);
            }
            
            // 統計データを取得
            const data = await apiClient.get("/admin/stats");
            console.log('取得したデータ:', data);
            
            if (data && !data.error) {
                stats = {
                    totalUsers: data.total_users || 0,
                    activeUsers: data.active_users || 0,
                    totalPosts: data.total_posts || 0,
                    totalCircles: data.total_circles || 0,
                    systemHealth: data.system_health || 0,
                    activeSessions: data.active_sessions || 0,
                    newUsersThisMonth: data.new_users_this_month || 0,
                    postsThisMonth: data.posts_this_month || 0,
                    activeCircles: data.active_circles || 0
                };
            } else {
                throw new Error(data?.error || 'データの取得に失敗しました');
            }
        } catch (err) {
            console.error('統計データの取得に失敗:', err);
            console.error('エラーの詳細:', {
                message: err.message,
                name: err.name,
                stack: err.stack
            });
            error = err.message;
            // エラー時はデフォルト値を設定
            stats = {
                totalUsers: 0,
                activeUsers: 0,
                totalPosts: 0,
                totalCircles: 0,
                systemHealth: 0,
                activeSessions: 0,
                newUsersThisMonth: 0,
                postsThisMonth: 0,
                activeCircles: 0
            };
        } finally {
            isLoading = false;
        }
    }

    // コンポーネントマウント時にデータを取得
    onMount(() => {
        fetchStats();
    });

    let recentActivities = $state([
        { id: 1, action: "新規ユーザー登録", user: "田中太郎", time: "2分前", status: "success" },
        { id: 2, action: "投稿削除", user: "佐藤花子", time: "15分前", status: "warning" },
        { id: 3, action: "サークル作成", user: "山田次郎", time: "1時間前", status: "success" },
        { id: 4, action: "ユーザー停止", user: "鈴木三郎", time: "2時間前", status: "error" },
        { id: 5, action: "システム更新", user: "システム", time: "3時間前", status: "success" }
    ]);

    // 動的なアクティビティデータを生成
    $effect(() => {
        if (!isLoading && stats.totalUsers > 0) {
            // APIデータを基にした動的なアクティビティを生成
            const activities = [];
            
            // 新規ユーザー登録のアクティビティ
            if (stats.newUsersThisMonth > 0) {
                activities.push({
                    id: 1,
                    action: "新規ユーザー登録",
                    user: `${stats.newUsersThisMonth}人`,
                    time: "今月",
                    status: "success"
                });
            }
            
            // 投稿関連のアクティビティ
            if (stats.postsThisMonth > 0) {
                activities.push({
                    id: 2,
                    action: "新規投稿",
                    user: `${stats.postsThisMonth}件`,
                    time: "今月",
                    status: "success"
                });
            }
            
            // サークル関連のアクティビティ
            if (stats.activeCircles > 0) {
                activities.push({
                    id: 3,
                    action: "アクティブサークル",
                    user: `${stats.activeCircles}個`,
                    time: "現在",
                    status: "success"
                });
            }
            
            // システムヘルスのアクティビティ
            if (stats.systemHealth >= 90) {
                activities.push({
                    id: 4,
                    action: "システム状態",
                    user: "良好",
                    time: `${stats.systemHealth}%`,
                    status: "success"
                });
            } else if (stats.systemHealth >= 70) {
                activities.push({
                    id: 4,
                    action: "システム状態",
                    user: "注意",
                    time: `${stats.systemHealth}%`,
                    status: "warning"
                });
            } else {
                activities.push({
                    id: 4,
                    action: "システム状態",
                    user: "要確認",
                    time: `${stats.systemHealth}%`,
                    status: "error"
                });
            }
            
            // アクティブユーザーのアクティビティ
            if (stats.activeUsers > 0) {
                const activeRate = Math.round((stats.activeUsers / stats.totalUsers) * 100);
                activities.push({
                    id: 5,
                    action: "ユーザーアクティビティ",
                    user: `${activeRate}%`,
                    time: `${stats.activeUsers}人`,
                    status: activeRate >= 70 ? "success" : activeRate >= 50 ? "warning" : "error"
                });
            }
            
            // デフォルトのアクティビティを追加（データが少ない場合）
            if (activities.length < 3) {
                activities.push({
                    id: 6,
                    action: "データ更新",
                    user: "システム",
                    time: "最新",
                    status: "success"
                });
            }
            
            recentActivities = activities.slice(0, 5); // 最大5件まで表示
        }
    });

    let quickActions = [
        { 
            title: "ユーザー管理", 
            description: "ユーザーアカウントの管理", 
            icon: Users, 
            color: "blue",
            href: "/admin/users"
        },
        { 
            title: "投稿管理", 
            description: "投稿内容の監視・管理", 
            color: "green",
            icon: FileText, 
            href: "/admin/posts"
        },
        { 
            title: "サークル管理", 
            description: "サークルの承認・管理", 
            color: "purple",
            icon: MessageSquare, 
            href: "/admin/circles"
        },
        { 
            title: "システム設定", 
            description: "システム設定の変更", 
            color: "gray",
            icon: Settings, 
            href: "/admin/settings"
        }
    ];

    function getStatusColor(status) {
        switch (status) {
            case 'success': return 'green';
            case 'warning': return 'yellow';
            case 'error': return 'red';
            default: return 'gray';
        }
    }

    function getStatusIcon(status) {
        switch (status) {
            case 'success': return CheckCircle;
            case 'warning': return AlertTriangle;
            case 'error': return AlertTriangle;
            default: return Clock;
        }
    }

    function navigateTo(action) {
        // 実際のナビゲーション処理
        console.log(`Navigating to: ${action.href}`);
        // goto(action.href);
    }
</script>

<div class="p-8">
    <div class="max-w-4xl mx-auto space-y-8">
        <!-- エラー表示 -->
        {#if error}
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-center">
                    <AlertTriangle class="h-5 w-5 text-red-400 mr-2" />
                    <span class="text-red-800">統計データの取得に失敗しました: {error}</span>
                </div>
                <button 
                    class="mt-2 text-sm text-red-600 hover:text-red-800 underline"
                    onclick={fetchStats}
                >
                    再試行
                </button>
            </div>
        {/if}

        <!-- 統計カード -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            <!-- ユーザー統計カード -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
                <div class="flex items-center mb-6">
                    <div class="p-3 bg-blue-50 rounded-xl">
                        <Users class="h-8 w-8 text-blue-600" />
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">総ユーザー数</p>
                        {#if isLoading}
                            <div class="h-9 bg-gray-200 rounded animate-pulse"></div>
                        {:else}
                            <p class="text-3xl font-bold text-gray-900">{stats.totalUsers.toLocaleString()}</p>
                        {/if}
                    </div>
                </div>
                <div class="space-y-3">
                    <div class="w-full bg-gray-100 rounded-full h-3">
                        <div class="bg-blue-500 h-3 rounded-full transition-all duration-500" style="width: {stats.totalUsers > 0 ? (stats.activeUsers / stats.totalUsers * 100) : 0}%"></div>
                    </div>
                    <div class="flex justify-between text-sm">
                        <span class="text-gray-600">アクティブ: <span class="font-semibold text-blue-600">{stats.activeUsers.toLocaleString()}</span></span>
                        <span class="text-gray-600">今月: <span class="font-semibold text-green-600">+{stats.newUsersThisMonth}</span></span>
                    </div>
                </div>
            </div>

            <!-- 投稿統計カード -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
                <div class="flex items-center mb-6">
                    <div class="p-3 bg-green-50 rounded-xl">
                        <FileText class="h-8 w-8 text-green-600" />
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">総投稿数</p>
                        {#if isLoading}
                            <div class="h-9 bg-gray-200 rounded animate-pulse"></div>
                        {:else}
                            <p class="text-3xl font-bold text-gray-900">{stats.totalPosts.toLocaleString()}</p>
                        {/if}
                    </div>
                </div>
                <div class="flex items-center text-sm text-gray-600">
                    <TrendingUp class="h-5 w-5 mr-2 text-green-500" />
                    <span>今月 <span class="font-semibold text-green-600">+{stats.postsThisMonth}</span></span>
                </div>
            </div>

            <!-- サークル統計カード -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
                <div class="flex items-center mb-6">
                    <div class="p-3 bg-purple-50 rounded-xl">
                        <MessageSquare class="h-8 w-8 text-purple-600" />
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">サークル数</p>
                        {#if isLoading}
                            <div class="h-9 bg-gray-200 rounded animate-pulse"></div>
                        {:else}
                            <p class="text-3xl font-bold text-gray-900">{stats.totalCircles}</p>
                        {/if}
                    </div>
                </div>
                <div class="flex items-center text-sm text-gray-600">
                    <Activity class="h-5 w-5 mr-2 text-purple-500" />
                    <span>アクティブ: <span class="font-semibold text-purple-600">{stats.activeCircles}</span></span>
                </div>
            </div>

            <!-- システムヘルスカード -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow duration-200">
                <div class="flex items-center mb-6">
                    <div class="p-3 bg-green-50 rounded-xl">
                        <BarChart3 class="h-8 w-8 text-green-600" />
                    </div>
                    <div class="ml-4">
                        <p class="text-sm font-medium text-gray-600">システムヘルス</p>
                        {#if isLoading}
                            <div class="h-9 bg-gray-200 rounded animate-pulse"></div>
                        {:else}
                            <p class="text-3xl font-bold text-green-600">{stats.systemHealth}%</p>
                        {/if}
                    </div>
                </div>
                <div class="w-full bg-gray-100 rounded-full h-3">
                    <div class="bg-green-500 h-3 rounded-full transition-all duration-500" style="width: {stats.systemHealth}%"></div>
                </div>
            </div>
        </div>

        <!-- システム詳細とクイックアクション -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- システム詳細カード -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center">
                    <BarChart3 class="h-6 w-6 mr-3 text-blue-600" />
                    システム詳細
                </h3>
                <div class="space-y-6">
                    <div>
                        <div class="flex justify-between text-sm mb-2">
                            <span class="text-gray-600">アクティブセッション</span>
                            <span class="font-semibold text-blue-600">{stats.activeSessions}</span>
                        </div>
                        <div class="w-full bg-gray-100 rounded-full h-3">
                            <div class="bg-blue-500 h-3 rounded-full transition-all duration-500" style="width: {(stats.activeSessions / 500) * 100}%"></div>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-4 text-center">
                        <div class="p-4 bg-gray-50 rounded-lg">
                            <p class="text-2xl font-bold text-gray-900">{stats.totalUsers}</p>
                            <p class="text-sm text-gray-600">総ユーザー</p>
                        </div>
                        <div class="p-4 bg-gray-50 rounded-lg">
                            <p class="text-2xl font-bold text-gray-900">{stats.totalPosts}</p>
                            <p class="text-sm text-gray-600">総投稿</p>
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-4 text-center">
                        <div class="p-4 bg-gray-50 rounded-lg">
                            <p class="text-2xl font-bold text-gray-900">{stats.totalCircles}</p>
                            <p class="text-sm text-gray-600">総サークル</p>
                        </div>
                        <div class="p-4 bg-gray-50 rounded-lg">
                            <p class="text-2xl font-bold text-gray-900">{stats.activeCircles}</p>
                            <p class="text-sm text-gray-600">アクティブ</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- クイックアクションカード -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
                <h3 class="text-xl font-semibold text-gray-900 mb-6">クイックアクション</h3>
                <div class="grid grid-cols-2 gap-4">
                    {#each quickActions as action}
                        <button 
                            class="p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all duration-200 text-left group"
                            onclick={() => navigateTo(action)}
                        >
                            <div class="flex flex-col items-center text-center">
                                <div class="p-2 rounded-lg bg-gray-50 group-hover:bg-gray-100 transition-colors duration-200 mb-3">
                                    <svelte:component this={action.icon} class="h-6 w-6 text-gray-600" />
                                </div>
                                <span class="text-sm font-medium text-gray-900">{action.title}</span>
                                <span class="text-xs text-gray-500 mt-1">{action.description}</span>
                            </div>
                        </button>
                    {/each}
                </div>
            </div>
        </div>

        <!-- 最近のアクティビティカード -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">最近のアクティビティ</h3>
            <div class="overflow-hidden rounded-lg border border-gray-200">
                <Table>
                    <TableHead>
                        <TableHeadCell class="bg-gray-50">アクション</TableHeadCell>
                        <TableHeadCell class="bg-gray-50">ユーザー</TableHeadCell>
                        <TableHeadCell class="bg-gray-50">時間</TableHeadCell>
                        <TableHeadCell class="bg-gray-50">ステータス</TableHeadCell>
                    </TableHead>
                    <TableBody>
                        {#each recentActivities as activity}
                            <TableBodyRow class="hover:bg-gray-50">
                                <TableBodyCell class="font-medium py-4">{activity.action}</TableBodyCell>
                                <TableBodyCell class="py-4">{activity.user}</TableBodyCell>
                                <TableBodyCell class="text-gray-500 py-4">{activity.time}</TableBodyCell>
                                <TableBodyCell class="py-4">
                                    <Badge color={getStatusColor(activity.status)}>
                                        <svelte:component this={getStatusIcon(activity.status)} class="h-3 w-3 mr-1" />
                                        {activity.status}
                                    </Badge>
                                </TableBodyCell>
                            </TableBodyRow>
                        {/each}
                    </TableBody>
                </Table>
            </div>
        </div>
    </div>
</div>
