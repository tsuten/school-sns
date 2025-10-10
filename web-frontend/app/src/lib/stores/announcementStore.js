import { derived, writable } from "svelte/store";
import { JoinGroup, LeaveGroup, messages } from "$lib/stores/unifiedBaseWSStore.js";
import { apiClient } from "$lib/services/django";

export const announcements = writable([]);

// メッセージが更新されてtypeがannouncementだったらannouncements変数に代入
messages.subscribe($messages => {
    $messages.forEach(message => {
        if (message.type === "announcement") {
            announcements.update(state => [...state, message.data]);
        }
    });
});

const JoinAnnouncementsGroup = async (announcements_id) => {
    try {
        await JoinGroup("announcements_" + announcements_id);
        console.log("Joined announcements group");
    } catch (error) {
        console.error(error);
    }
}

const LeaveAnnouncementsGroup = async (announcements_id) => {
    await LeaveGroup("announcements_" + announcements_id);
}

const fetchAnnouncements = async (id) => {
    const response = await apiClient.get("/announcement/announcements/" + id);
    return response;
}

export const InitializeAnnouncements = async (id) => {
    announcements.set([]);
    const fetched_announcements = await fetchAnnouncements(id);
    announcements.set(fetched_announcements);
    JoinAnnouncementsGroup(id);
}