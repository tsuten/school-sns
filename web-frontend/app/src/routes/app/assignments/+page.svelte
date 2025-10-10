<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { isAuthenticated, currentUser } from '$lib/stores/auth.js';
  import { apiClient } from '$lib/services/django.js';
  import { toast } from '$lib/utils/toast.js';
  import { datetimeNormalize } from '$lib/utils/datetimeNormalize.js';
  import { theme } from '$lib/theme.js';
  import { goto } from '$app/navigation';
  import DatetimeBadge from '$lib/components/badge/datetimeBadge.svelte';
  import UserChip from "$lib/components/card/chips/userChip.svelte";
  let assignments = $state([]);
  let loading = $state(true);
  let error = $state(null);
  let username = $state(null);

  $effect(() => {
    assignments.forEach(assignment => {
      if (!assignment.created_by_id) {
        return;
      }
      getUsername(assignment.created_by_id);
    });
  });
  
  onMount(async () => {
    await loadAssignments();
  });

  async function getUsername(id) {
    const response = await apiClient.get(`/users/profile/${id}`);
    username = response.user_username;
    return username;
  }
  
  async function loadAssignments() {
    try {
      loading = true;
      const response = await apiClient.get('/assignments/my-assignments');
      assignments = response || [];
    } catch (err) {
      error = '課題の読み込みに失敗しました';
      toast.error('課題の読み込みに失敗しました');
      console.error('Error loading assignments:', err);
    } finally {
      loading = false;
    }
  }
  
  function isOverdue(dueDate) {
    return new Date(dueDate) < new Date();
  }
  
  function getRemainingTime(dueDate) {
    const now = new Date();
    const due = new Date(dueDate);
    const diff = due - now;
    
    if (diff <= 0) return '期限切れ';
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `残り${days}日`;
    if (hours > 0) return `残り${hours}時間`;
    return '残り1時間未満';
  }
</script>

<svelte:head>
  <title>課題一覧 | SNS</title>
</svelte:head>

<div class="container mx-auto px-4 py-6">
  <div class="mb-6">
    <h1 class="text-3xl font-bold {$theme.text.primary} mb-2">課題</h1>
  </div>
  

  
  <!-- 課題一覧 -->
    {#if loading}
      <div class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 {$theme.text.tertiary}">読み込み中...</p>
      </div>
    {:else if error}
      <div class="text-center py-8">
        <p class="{$theme.text.secondary}">{error}</p>
        <button 
          onclick={loadAssignments}
          class="mt-2 px-4 py-2 {$theme.button.secondary} rounded-md"
        >
          再試行
        </button>
      </div>
    {:else if assignments.length === 0}
      <div class="text-center py-8">
        <p class="{$theme.text.tertiary}">課題がありません</p>
      </div>
    {:else}
      <div class="space-y-3">
        {#each assignments as assignment}
          <div 
            class="p-4 border {$theme.border.secondary} rounded-lg {$theme.background.primary} hover:{$theme.background.secondary} transition-colors cursor-pointer"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="flex flex-row gap-2 items-center mb-2">
                <h3 class="text-lg font-bold {$theme.text.primary}">
                  {assignment.title}
                </h3>
                <div class="flex flex-row gap-2 items-center"> 
                    <span class="{$theme.text.primary} font-medium">
                      <DatetimeBadge date={assignment.due_date} />
                    </span>
                    <span class="text-xs {isOverdue(assignment.due_date) ? 'text-red-500' : $theme.text.tertiary}">
                      ({getRemainingTime(assignment.due_date)})
                    </span>
                  </div>
                </div>
                {#if assignment.description}
                  <p class="{$theme.text.secondary} text-sm mb-3 line-clamp-2">
                    {assignment.description}
                  </p>
                {/if}
                
                {#if assignment.created_by_id}
                  <div class="flex flex-wrap gap-4 text-sm">
                    <UserChip user={username} />
                  </div>
                {/if}
              </div>
              
              <div class="flex-shrink-0 ml-4">
                <div class="w-2 h-2 rounded-full {isOverdue(assignment.due_date) ? 'bg-red-400' : 'bg-green-400'}"></div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}

  
  <!-- 新規作成ボタン -->
  <!-- <div class="mt-6 text-center">
    <button 
      class="px-6 py-3 {$theme.button.primary} rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      onclick={() => goto('/app/assignments/create')}
    >
      新しい課題を作成
    </button>
  </div> -->
</div>
