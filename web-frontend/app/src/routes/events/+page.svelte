<script>
    import { Calendar, Heart, MapPin, User, Bookmark, Plus } from "lucide-svelte";
    import EventCard from "$lib/components/page-components/eventCard.svelte";
    import EventForm from '$lib/components/page-components/eventForm.svelte';


    // サーバーから取得したデータを受け取る
    export let data;
    
    // APIから取得したイベントデータ
    $: nextEvents = data.nextEvents || [];
    $: heldEvents = data.heldEvents || [];
    
    // 日時をフォーマットする関数
    function formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        return date.toLocaleString('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    let showForm = false;

  function openForm() {
    showForm = true;
  }

  function closeForm() {
    showForm = false;
  }

    
    // 今後のイベントを取得（APIから直接取得するので不要だが、念のため保持）
    function getUpcomingEvents() {
        // nextEventsを開始日時でソート
        return nextEvents.filter(event => !event.is_cancelled)
                        .sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime));
    }
    
    $: upcomingEvents = getUpcomingEvents();
</script>

<div class="flex flex-col gap-2 h-full p-2">
    <!-- 現在進行中のイベント -->
    {#if heldEvents.length > 0}
        <div class="flex flex-col gap-2">
            <p class="text-lg font-bold">現在進行中のイベント</p>
            {#each heldEvents as event}
                <EventCard {event} />
            {/each}
        </div>
        
        <hr class="border-gray-300 my-4">
    {:else}
        <div class="flex flex-col gap-2">
            <p class="text-lg font-bold">現在進行中のイベント</p>
            <div class="flex flex-col items-center justify-center py-8 text-gray-500">
                <Calendar class="w-16 h-16 text-gray-300 mb-4" />
                <p class="text-lg">現在進行中のイベントはありません</p>
            </div>
        </div>
        
        <hr class="border-gray-300 my-4">
    {/if}

    <!-- 今後のイベント -->
    <div class="flex flex-col gap-2 h-full">
        <p class="text-lg font-bold">今後のイベント</p>
        
        {#if upcomingEvents.length === 0}
            <div class="flex flex-col items-center justify-center py-8 text-gray-500">
                <Calendar class="w-16 h-16 text-gray-300 mb-4" />
                <p class="text-lg">今後のイベントはありません</p>
            </div>
        {:else}
            {#each upcomingEvents as event}
                <EventCard {event} />
            {/each}
        {/if}

        <!-- フローティングボタン -->
        <div class="flex justify-end items-end h-full p-2">
  <button 
    class="w-12 h-12 bg-sky-500 text-white rounded-full hover:cursor-pointer flex items-center justify-center z-40"
    onclick={openForm}
    aria-label="新しいイベントを作成"
  >
    <Plus class="w-6 h-6 text-white" />
  </button>

  {#if showForm}
    <EventForm onClose={closeForm} />
  {/if}
</div>

    </div>
</div>