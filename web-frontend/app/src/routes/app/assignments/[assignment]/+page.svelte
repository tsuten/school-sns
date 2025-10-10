<script>
    import { onMount } from 'svelte';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { apiClient } from '$lib/services/django';
    import { theme } from '$lib/theme.js';
    import { Button, Card, Badge, Modal, Input, Textarea, Spinner } from 'flowbite-svelte';
    import { Edit, Trash2, Calendar, User, ArrowLeft, CheckCircle, Clock, AlertCircle } from 'lucide-svelte';
    import { toast } from '$lib/utils/toast.js';
    import { dateNormalize, timeNormalize } from '$lib/utils/datetimeNormalize.js';

    let assignment = $state(null);
    let loading = $state(true);
    let editing = $state(false);
    let showDeleteModal = $state(false);
    let assignmentId = $state('');

    // 編集用のフォームデータ
    let editForm = $state({
        title: '',
        description: '',
        due_date: '',
        assigned_to_ids: []
    });

    // ユーザーリスト（割り当て先選択用）
    let users = $state([]);
    let loadingUsers = $state(false);

    onMount(async () => {
        assignmentId = $page.params.assignment;
        await loadAssignment();
    });

    async function loadAssignment() {
        try {
            loading = true;
            const response = await apiClient.get(`/assignments/${assignmentId}`);
            assignment = response;
            
            // 編集フォームに現在の値を設定
            editForm = {
                title: assignment.title || '',
                description: assignment.description || '',
                due_date: assignment.due_date ? assignment.due_date.split('T')[0] : '',
                assigned_to_ids: assignment.assigned_to_ids || []
            };
        } catch (error) {
            console.error('課題の読み込みに失敗しました:', error);
            toast.error('課題の読み込みに失敗しました');
        } finally {
            loading = false;
        }
    }

    async function loadUsers() {
        try {
            loadingUsers = true;
            const response = await apiClient.get('/users/list');
            users = response || [];
        } catch (error) {
            console.error('ユーザーリストの読み込みに失敗しました:', error);
        } finally {
            loadingUsers = false;
        }
    }

    async function handleEdit() {
        try {
            const response = await apiClient.put(`/assignments/${assignmentId}`, editForm);
            assignment = response;
            editing = false;
            toast.success('課題が更新されました');
        } catch (error) {
            console.error('課題の更新に失敗しました:', error);
            toast.error('課題の更新に失敗しました');
        }
    }

    async function handleDelete() {
        try {
            await apiClient.delete(`/assignments/${assignmentId}`);
            toast.success('課題が削除されました');
            goto('/app/assignments');
        } catch (error) {
            console.error('課題の削除に失敗しました:', error);
            toast.error('課題の削除に失敗しました');
        }
    }

    function cancelEdit() {
        editing = false;
        // 編集フォームを元の値に戻す
        editForm = {
            title: assignment.title || '',
            description: assignment.description || '',
            due_date: assignment.due_date ? assignment.due_date.split('T')[0] : '',
            assigned_to_ids: assignment.assigned_to_ids || []
        };
    }

    function getStatusBadge() {
        if (!assignment?.due_date) return null;
        
        const now = new Date();
        const dueDate = new Date(assignment.due_date);
        const diff = dueDate - now;
        
        if (diff < 0) {
            return { color: 'red', text: '期限切れ', icon: AlertCircle };
        } else if (diff < 24 * 60 * 60 * 1000) {
            return { color: 'yellow', text: '期限間近', icon: Clock };
        } else {
            return { color: 'green', text: '進行中', icon: CheckCircle };
        }
    }

    function getAssignedUsers() {
        if (!assignment?.assigned_to_ids || !users.length) return [];
        return users.filter(user => assignment.assigned_to_ids.includes(user.id));
    }
</script>

<div class="min-h-screen {$theme.background.primary} p-6">
    <div class="max-w-4xl mx-auto">
        <!-- ヘッダー -->
        <div class="flex items-center gap-4 mb-6">
            <Button 
                color="light" 
                size="sm"
                onclick={() => goto('/app/assignments')}
                class="{$theme.text.primary} hover:{$theme.text.secondary}"
            >
                <ArrowLeft class="w-4 h-4 mr-2" />
                戻る
            </Button>
            <h1 class="text-3xl font-bold {$theme.text.primary}">課題の詳細</h1>
        </div>

        {#if loading}
            <div class="flex justify-center items-center h-64">
                <div class="text-center">
                    <Spinner size="12" class="mx-auto mb-4" />
                    <p class="{$theme.text.secondary}">読み込み中...</p>
                </div>
            </div>
        {:else if assignment}
            <div class="space-y-6">
                <!-- 課題カード -->
                <div class="border {$theme.border.primary} rounded-lg {$theme.background.primary} p-6">
                    <div class="flex justify-between items-start mb-6">
                        <div class="flex-1">
                            <div class="flex items-center gap-3 mb-3">
                                <h2 class="text-2xl font-bold {$theme.text.primary}">
                                    {editing ? '課題を編集' : assignment.title}
                                </h2>
                                {#if !editing}
                                    {@const status = getStatusBadge()}
                                    {#if status}
                                        <Badge color={status.color} class="flex items-center gap-1">
                                            <svelte:component this={status.icon} class="w-3 h-3" />
                                            {status.text}
                                        </Badge>
                                    {/if}
                                {/if}
                            </div>
                            
                            {#if !editing}
                                <p class="{$theme.text.secondary} text-lg leading-relaxed">{assignment.description}</p>
                            {/if}
                        </div>
                        
                        {#if !editing}
                            <div class="flex gap-2">
                                <Button 
                                    color="light" 
                                    size="sm"
                                    onclick={() => editing = true}
                                    class="{$theme.text.primary} hover:{$theme.text.secondary}"
                                >
                                    <Edit class="w-4 h-4 mr-2" />
                                    編集
                                </Button>
                                <Button 
                                    color="failure" 
                                    size="sm"
                                    onclick={() => showDeleteModal = true}
                                >
                                    <Trash2 class="w-4 h-4 mr-2" />
                                    削除
                                </Button>
                            </div>
                        {/if}
                    </div>

                    {#if editing}
                        <div class="space-y-4">
                            <div>
                                <label class="block text-sm font-medium {$theme.text.primary} mb-2">タイトル</label>
                                <Input 
                                    bind:value={editForm.title}
                                    placeholder="課題のタイトル"
                                    class="w-full"
                                />
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium {$theme.text.primary} mb-2">説明</label>
                                <Textarea 
                                    bind:value={editForm.description}
                                    placeholder="課題の詳細説明"
                                    rows="4"
                                    class="w-full"
                                />
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium {$theme.text.primary} mb-2">提出期限</label>
                                <Input 
                                    type="date"
                                    bind:value={editForm.due_date}
                                    class="w-full"
                                />
                            </div>
                            
                            <div>
                                <label class="block text-sm font-medium {$theme.text.primary} mb-2">割り当て先</label>
                                <div class="space-y-2 max-h-32 overflow-y-auto p-3 border {$theme.border.secondary} rounded">
                                    {#each users as user}
                                        <label class="flex items-center gap-2">
                                            <input 
                                                type="checkbox" 
                                                value={user.id}
                                                checked={editForm.assigned_to_ids.includes(user.id)}
                                                onchange={(e) => {
                                                    if (e.target.checked) {
                                                        editForm.assigned_to_ids = [...editForm.assigned_to_ids, user.id];
                                                    } else {
                                                        editForm.assigned_to_ids = editForm.assigned_to_ids.filter(id => id !== user.id);
                                                    }
                                                }}
                                                class="rounded"
                                            />
                                            <span class="{$theme.text.secondary} text-sm">
                                                {user.display_name || user.user_username}
                                            </span>
                                        </label>
                                    {/each}
                                </div>
                            </div>
                            
                            <div class="flex gap-2 pt-4">
                                <Button 
                                    color="success"
                                    onclick={handleEdit}
                                    class="flex-1"
                                >
                                    保存
                                </Button>
                                <Button 
                                    color="light"
                                    onclick={cancelEdit}
                                    class="flex-1"
                                >
                                    キャンセル
                                </Button>
                            </div>
                        </div>
                    {:else}
                        <!-- 課題の詳細情報 -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
                            <div class="space-y-4">
                                <div class="flex items-center gap-3 p-3 border {$theme.border.secondary} rounded-lg">
                                    <Calendar class="w-5 h-5 {$theme.text.tertiary}" />
                                    <div>
                                        <p class="text-sm {$theme.text.tertiary}">提出期限</p>
                                        <p class="{$theme.text.primary} font-medium">
                                            {assignment.due_date ? dateNormalize(assignment.due_date) : '未設定'}
                                        </p>
                                    </div>
                                </div>
                                
                                <div class="flex items-center gap-3 p-3 border {$theme.border.secondary} rounded-lg">
                                    <User class="w-5 h-5 {$theme.text.tertiary}" />
                                    <div>
                                        <p class="text-sm {$theme.text.tertiary}">作成者</p>
                                        <p class="{$theme.text.primary} font-medium">
                                            {assignment.created_by?.display_name || assignment.created_by?.user_username || '不明'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="space-y-4">
                                <div>
                                    <p class="text-sm {$theme.text.tertiary} mb-3">割り当て先</p>
                                    <div class="space-y-2">
                                        {#if assignment.assigned_to_ids?.length > 0}
                                            {#each getAssignedUsers() as user}
                                                <div class="flex items-center gap-3 p-3 border {$theme.border.secondary} rounded-lg">
                                                    <div class="w-8 h-8 {$theme.background.quaternary} rounded-lg flex items-center justify-center">
                                                        <span class="text-sm {$theme.text.primary} font-medium">
                                                            {user.display_name?.charAt(0) || user.user_username?.charAt(0) || 'U'}
                                                        </span>
                                                    </div>
                                                    <span class="{$theme.text.primary} font-medium">
                                                        {user.display_name || user.user_username}
                                                    </span>
                                                </div>
                                            {/each}
                                        {:else}
                                            <div class="p-3 border {$theme.border.secondary} rounded-lg">
                                                <p class="{$theme.text.tertiary} text-sm">割り当て先なし</p>
                                            </div>
                                        {/if}
                                    </div>
                                </div>
                            </div>
                        </div>
                    {/if}
                </div>
            </div>
        {:else}
            <div class="text-center py-12">
                <p class="{$theme.text.secondary} text-lg">課題が見つかりませんでした</p>
                <Button 
                    color="light" 
                    onclick={() => goto('/app/assignments')}
                    class="mt-4"
                >
                    課題一覧に戻る
                </Button>
            </div>
        {/if}
    </div>
</div>

<!-- 削除確認モーダル -->
{#if showDeleteModal}
    <Modal bind:open={showDeleteModal} size="md">
        <div class="text-center">
            <h3 class="mb-4 text-lg font-normal {$theme.text.primary}">
                この課題を削除しますか？
            </h3>
            <p class="{$theme.text.secondary} mb-6">
                「{assignment?.title}」を削除すると、元に戻すことはできません。
            </p>
            <div class="flex justify-center gap-4">
                <Button color="failure" onclick={handleDelete}>
                    削除する
                </Button>
                <Button color="light" onclick={() => showDeleteModal = false}>
                    キャンセル
                </Button>
            </div>
        </div>
    </Modal>
{/if}
