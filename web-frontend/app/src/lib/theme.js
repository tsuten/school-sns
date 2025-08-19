import { writable, derived } from 'svelte/store';

// テーマの定義
const themeConfig = {
    light: {
        // 背景色
        primary: "white",
        secondary: "gray-100",
        tertiary: "gray-200",
        quaternary: "gray-300",
        quinary: "gray-400",
        
        // テキスト色
        text: {
            primary: "text-gray-900",
            secondary: "text-gray-700",
            tertiary: "text-gray-500",
            inverse: "text-white"
        },
        
        // ボーダー色
        border: {
            primary: "border-gray-300 border-1",
            secondary: "border-gray-300",
            accent: "border-blue-500"
        },
        
        // ボタン色
        button: {
            primary: "bg-blue-600 hover:bg-blue-700 text-white hover:cursor-pointer",
            secondary: "bg-gray-200 hover:bg-gray-300 text-gray-800 hover:cursor-pointer",
            danger: "bg-red-600 hover:bg-red-700 text-white hover:cursor-pointer"
        },
        
        // カード・コンテナ色
        card: {
            background: "bg-white",
            shadow: "shadow-none"
        },
        
        // 入力フィールド色
        input: {
            background: "bg-white",
            border: "border-gray-300 focus:border-blue-500",
            text: "text-gray-900"
        }
    },
    dark: {
        // 背景色
        primary: "black",
        secondary: "gray-900",
        tertiary: "gray-800",
        quaternary: "gray-700",
        quinary: "gray-600",
        
        // テキスト色
        text: {
            primary: "text-white",
            secondary: "text-gray-300",
            tertiary: "text-gray-400",
            inverse: "text-gray-900"
        },
        
        // ボーダー色
        border: {
            primary: "border-gray-700 border-1",
            secondary: "border-gray-600",
            accent: "border-blue-400"
        },
        
        // ボタン色
        button: {
            primary: "bg-blue-500 hover:bg-blue-600 text-white hover:cursor-pointer",
            secondary: "bg-gray-700 hover:bg-gray-600 text-gray-200 hover:cursor-pointer",
            danger: "bg-red-500 hover:bg-red-600 text-white hover:cursor-pointer"
        },
        
        // カード・コンテナ色
        card: {
            background: "bg-gray-800",
            shadow: "shadow-none"
        },
        
        // 入力フィールド色
        input: {
            background: "bg-gray-700",
            border: "border-gray-600 focus:border-blue-400",
            text: "text-white"
        }
    }
};

// 現在のテーマ名を管理するstore
export const currentTheme = writable('light');

// テーマオブジェクトを管理するstore
export const theme = derived(currentTheme, ($currentTheme) => {
    return themeConfig[$currentTheme];
});

// 初期化関数
export function initializeTheme() {
    if (typeof window !== 'undefined') {
        const savedTheme = localStorage.getItem('theme') || 'light';
        currentTheme.set(savedTheme);
        document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }
}

// テーマを設定する関数
export function setTheme(themeName) {
    if (typeof window !== 'undefined') {
        localStorage.setItem('theme', themeName);
        currentTheme.set(themeName);
        document.documentElement.classList.toggle('dark', themeName === 'dark');
    }
}

// テーマを切り替える関数
export function toggleTheme() {
    currentTheme.update(theme => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        if (typeof window !== 'undefined') {
            localStorage.setItem('theme', newTheme);
            document.documentElement.classList.toggle('dark', newTheme === 'dark');
        }
        return newTheme;
    });
}

// デフォルトエクスポート
export default themeConfig;