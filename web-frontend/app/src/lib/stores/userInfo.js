import { writable } from 'svelte/store';
import { apiClient } from '../services/django.js';

// 初期値
const initialUserInfo = {
    username: "",
    display_name: "",
    email: "",
    pfp: "",
    bio: "",
    location: "",
    birth_place: "",
    birthday: "",
    created_at: "",
    authenticated: false
};

export const userInfo = writable(initialUserInfo);

// ユーザー情報を設定する関数
export function setUserInfo(userData) {
    if (!userData) {
        userInfo.set(initialUserInfo);
        return;
    }
    
    userInfo.set({
        username: userData.user_username || "",
        display_name: userData.display_name || "",
        email: userData.user_email || "",
        pfp: apiClient.getMediaURL(userData.pfp) || "",
        bio: userData.bio || "",
        location: userData.location || "",
        birth_place: userData.birth_place || "",
        birthday: userData.birthday || "",
        created_at: userData.created_at || "",
        authenticated: true
    });
}

// ユーザー情報をクリアする関数
export function clearUserInfo() {
    userInfo.set(initialUserInfo);
}