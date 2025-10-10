import { writable } from "svelte/store";
import { messages } from "./unifiedBaseWSStore.js";

export const classMessages = writable([]);

// messagesからclass_messageタイプのメッセージをclassMessagesにset
messages.subscribe($messages => {
    const filteredMessages = $messages
        .filter(message => message.type === "class_message")
        .map(message => message.data);
    
    classMessages.set(filteredMessages);
});

const initializeClassMessages = () => {
    classMessages.set([]);
};

initializeClassMessages();