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
    import EventInput from "$lib/components/input/eventInput.svelte";
    import Tab from "$lib/components/page-components/tab.svelte";
    import { apiClient } from "$lib/services/django";
    import { fly } from 'svelte/transition';
    import { onMount } from 'svelte';

    // APIから取得したイベントデータ
    let nextEvents = [];
    let heldEvents = [];

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

    async function fetchData() {
        try {
            // 並行してAPIからデータを取得
            const [heldRes, nextRes] = await Promise.all([
                apiClient.get("/events/held_events"),
                apiClient.get("/events/next_events")
            ]);
            
            // 取得したデータで nextEvents, heldEvents を更新
            heldEvents = heldRes || [];
            nextEvents = nextRes || [];
        } catch (error) {
            console.error('イベントデータの取得に失敗しました:', error);
            // エラーが発生した場合は空の配列を設定
            heldEvents = [];
            nextEvents = [];
        }
    }

    // ページロード時にデータを取得
    onMount(() => {
        fetchData();
    });

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
    <!-- イベント作成フォーム -->
    <EventInput on:eventSent={handleDataAdded} />

    <hr class="border-gray-300 my-4" />

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
    </div>
</div>
