<script>
    import { Calendar, Heart, MapPin, User, Bookmark, Plus } from "lucide-svelte";

    let events = [
        {
            title: "イベント1",
            description: "イベント1の説明",
            datetime: "2025-06-09 12:00:00",
            thumbnail: "https://picsum.photos/150",
            location: "東京都",
            organizer: "イベント1の主催者",
        },
        {
            title: "イベント2",
            description: "イベント2の説明",
            datetime: "2025-06-09 12:00:00",
            thumbnail: "https://picsum.photos/100",
            location: "東京都",
            organizer: "イベント2の主催者",
        },
        
        {
            title: "イベント3",
            description: "イベント3の説明",
            datetime: "2025-06-09 12:00:00",
            thumbnail: "https://picsum.photos/200",
            location: "東京都",
            organizer: "イベント3の主催者",
        },
        {
            title: "イベント4",
            description: "イベント4の説明",
            datetime: "2025-06-09 12:00:00",
            thumbnail: "https://picsum.photos/300",
            location: "東京都",
            organizer: "イベント4の主催者",
        },
        {
            title: "イベント5",
            description: "イベント5の説明",
            datetime: "2025-06-09 12:00:00",
            thumbnail: "https://picsum.photos/400",
            location: "東京都",
            organizer: "イベント5の主催者",
        },
    ]
</script>

<div class="flex flex-col gap-2 h-full">
    <div class="flex flex-col gap-2">
        <p class="text-lg font-bold">現在進行中のイベント</p>
        <div class="flex flex-row w-full bg-white rounded-lg p-2 gap-4 border border-gray-300 items-center">
            <img src="https://picsum.photos/150" alt="イベント1" class="w-24 h-24 object-cover rounded-lg" />
            <div class="flex flex-col justify-center">
                <p class="text-lg font-bold">イベント1</p>
                <p class="text-sm text-gray-600 mt-1">イベント1の説明</p>
            </div>
            <div class="flex flex-col gap-2 items-end justify-between">
            </div>
        </div>
    </div>

    <hr class="border-gray-300 my-4">

    <div class="flex flex-col gap-2 h-full">
        {#each events as event}
            <div class="flex flex-row w-full bg-white rounded-lg p-2 gap-4 border border-gray-300">
                <img src={event.thumbnail} alt={event.title} class="w-24 h-24 object-cover rounded-lg" />
                <div class="flex flex-row justify-between w-full">
                    <div class="flex flex-col justify-center">
                        <p class="text-lg font-bold">{event.title}</p>
                        <p class="text-sm text-gray-600 mt-1">{event.description}</p>
                        </div>
                    <div class="flex flex-col gap-2 items-end justify-between">
                        <div class="flex gap-2 items-center">
                            <Bookmark class="w-6 h-6 text-gray-500" />
                        </div>
                        <div class="flex flex-row gap-2 items-center">
                            <MapPin class="w-4 h-4 text-gray-500" />
                            <p class="text-xs text-gray-500">{event.location}</p>
                            <User class="w-4 h-4 text-gray-500" />
                            <p class="text-xs text-gray-500">{event.organizer}</p>
                            <Calendar class="w-4 h-4 text-gray-500" />
                            <p class="text-xs text-gray-500">{event.datetime}</p>
                        </div>
                    </div>
                </div>
            </div>
        {/each}


        <!-- フローティングボタン -->
        <div class="flex justify-end items-end h-full p-2">
            <button 
                class="w-12 h-12 bg-sky-500 text-white rounded-full hover:cursor-pointer flex items-center justify-center z-40"
                onclick={() => console.log('新しいイベントを作成')}
                aria-label="新しいイベントを作成"
            >
                <Plus class="w-6 h-6 text-white" />
            </button>
        </div>
    </div>
</div>