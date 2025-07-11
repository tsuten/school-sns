<script>
    import BaseCard from "$lib/components/utils/baseCard.svelte";
    import { Button } from "flowbite-svelte";
    import { Check, Star, User, Clock } from "lucide-svelte";
    import { datetimeNormalize } from "$lib/utils/datetimeNormalize";
    let { announcement } = $props();
</script>

<BaseCard>
    <div class="flex flex-col gap-2">
        <div class="flex flex-col gap-2">
            <h1>{announcement.title}</h1>
            <p>{announcement.content}</p>
            <div class="flex flex-row gap-2">
                <Star />
                <p>{announcement.priority}</p>
            </div>
            <div class="flex flex-row gap-2">
                <Clock />
                <p>{datetimeNormalize(announcement.created_at)}</p>
            </div>
            <div class="flex flex-row gap-2">
                <User />
                <p>{announcement.posted_by}</p>
            </div>
        </div>
        <Button color="green" class="gap-2 w-auto self-end hover:cursor-pointer">
            <Check />
            <span>既読</span>
        </Button>
    </div>
</BaseCard>