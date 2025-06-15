import { writable } from 'svelte/store';

export const userInfo = writable({
    name: "",
    email: "",
    pfp: "",
});