<script>
    import {
        Calendar,
        Heart,
        MapPin,
        User,
        Bookmark,
        Plus,
        Bird,
        TicketPlus,
        TicketCheck,
    } from "lucide-svelte";
    import EventCard from "$lib/components/page-components/eventCard.svelte";
    import EventForm from "$lib/components/page-components/eventForm.svelte";
    import Tab from "$lib/components/page-components/tab.svelte";
    import { apiClient } from "$lib/services/django";
    import { fly } from 'svelte/transition';

    // サーバーから取得したデータを受け取る
    export let data;

    // APIから取得したイベントデータ
    $: nextEvents = data.nextEvents || [];
    $: heldEvents = data.heldEvents || [];

    let tabdata = [
        {
            label: "現在・未来のイベント",
            href: "/test",
            icon: TicketPlus,
        },
        {
            label: "過去のイベント",
            href: "/test2",
            icon: TicketCheck,
        },
    ];

    // 日時をフォーマットする関数
    function formatDateTime(dateTimeString) {
        const date = new Date(dateTimeString);
        return date.toLocaleString("ja-JP", {
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    let showForm = false;

    function openForm() {
        showForm = true;
    }

    function closeForm() {
        showForm = false;
    }

    async function fetchData() {
        // APIから最新データを取得
        const heldRes = await apiClient.get("/events/held_events");
        const nextRes = await apiClient.get("/events/next_events");
        // 取得したデータで nextEvents, heldEvents を更新
        heldEvents = heldRes || [];
        nextEvents = nextRes || [];
    }

    function handleDataAdded() {
        fetchData(); // 子から通知が来たら再フェッチ！
    }

    // 今後のイベントを取得（APIから直接取得するので不要だが、念のため保持）
    function getUpcomingEvents() {
        // nextEventsを開始日時でソート
        return nextEvents
            .filter((event) => !event.is_cancelled)
            .sort(
                (a, b) =>
                    new Date(a.start_datetime) - new Date(b.start_datetime),
            );
    }

    $: upcomingEvents = getUpcomingEvents();
</script>

<Tab tabsData={tabdata} />

<div class="flex flex-col gap-2 h-full p-2">
    <!-- 現在進行中のイベント -->
    {#if heldEvents.length > 0}
        <div class="flex flex-col gap-2">
            <p class="text-lg font-bold">現在進行中のイベント</p>
            {#each heldEvents as event}
                <EventCard {event} />
            {/each}
        </div>

        <hr class="border-gray-300 my-4" />
    {:else}
        <div class="flex flex-col gap-2">
            <p class="text-lg font-bold">現在進行中のイベント</p>
            <div
                class="flex flex-col items-center justify-center py-8 text-gray-500"
            >
                <Calendar class="w-16 h-16 text-gray-300 mb-4" />
                <p class="text-lg">現在進行中のイベントはありません</p>
            </div>
        </div>

        <hr class="border-gray-300 my-4" />
    {/if}

    <!-- EventForm を最上位レイヤーに配置 -->
    {#if showForm}
        <div class="fixed inset-0 flex items-end justify-center z-[100] p-4">
            <div
                class="bg-white rounded-lg w-full max-w-[68vw] max-h-[70vh] overflow-y-auto shadow-2xl"
                in:fly={{ y: 200, duration: 400 }}
                out:fly={{ y: 200, duration: 400 }}
            >
                <EventForm on:added={handleDataAdded} onClose={closeForm} />
            </div>
        </div>
    {/if}

    <!-- 今後のイベント -->
    <div class="flex flex-col gap-2 h-full">
        <p class="text-lg font-bold">今後のイベント</p>

        {#if upcomingEvents.length === 0}
            <div
                class="flex flex-col items-center justify-center py-8 text-gray-500"
            >
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
                class="fixed bottom-4 right-70 w-12 h-12 bg-sky-500 text-white rounded-full hover:bg-sky-600 hover:cursor-pointer flex items-center justify-center z-50 shadow-lg transition-colors duration-200"
                onclick={openForm}
                aria-label="新しいイベントを作成"
            >
                <Plus class="w-6 h-6 text-white" />
            </button>
        </div>
    </div>
</div>
