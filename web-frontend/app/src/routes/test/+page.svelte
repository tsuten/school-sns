<script>
    import ChatSystem from '$lib/components/utils/chat/chatSystem.svelte';
    import Input from '$lib/components/utils/chat/input.svelte';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    let messageInput = $state("");
    let handleKeyPress = $state((event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            dispatch("sendMessage", { content: messageInput });
        }
    });

    // ダミーメッセージデータ
    let messages = $state([
        {
            id: "msg1",
            user_id: "user1",
            display_name: "田中太郎",
            content: "こんにちは！みなさんお疲れ様です。",
            sent_at: "2024-01-15T09:00:00Z"
        },
        {
            id: "msg2", 
            user_id: "user2",
            display_name: "佐藤花子",
            content: "お疲れ様です！今日の勉強会の準備はいかがですか？",
            sent_at: "2024-01-15T09:15:00Z"
        },
        {
            id: "msg3",
            user_id: "current-user",
            display_name: "自分",
            content: "準備順調です！資料の共有ありがとうございました。\n皆さんで頑張りましょう！",
            sent_at: "2024-01-15T09:30:00Z"
        },
        {
            id: "msg4",
            user_id: "founder",
            display_name: "山田一郎",
            content: "みなさん、お疲れ様です！\n今日はよろしくお願いします🙏",
            sent_at: "2024-01-15T10:00:00Z"
        }
    ]);

    // 現在のユーザーID
    const currentUserId = "current-user";
    
    // 創始者ID（王冠マーク付与用）
    const founderIds = ["founder"];

    // チャット設定
    let chatSettings = $state({
        showAvatar: true,
        showTimestamp: true,
        enableInput: true,
        disabled: false
    });

    // メッセージ送信ハンドラー
    function handleSendMessage(event) {
        const content = event.detail.content;
        const newMessage = {
            id: `msg${messages.length + 1}`,
            user_id: currentUserId,
            display_name: "自分",
            content: content,
            sent_at: new Date().toISOString()
        };
        
        messages = [...messages, newMessage];
        console.log("メッセージ送信:", newMessage);
    }

    // ファイル添付ハンドラー
    function handleAttachFile() {
        console.log("ファイル添付がクリックされました");
        alert("ファイル添付機能（未実装）");
    }

    // 絵文字ハンドラー
    function handleOpenEmoji() {
        console.log("絵文字ボタンがクリックされました");
        alert("絵文字機能（未実装）");
    }

    // 設定変更ハンドラー
    function toggleSetting(setting) {
        chatSettings[setting] = !chatSettings[setting];
    }
</script>

<div class="container mx-auto p-4 max-w-4xl overflow-y-auto h-full">
    <h1 class="text-2xl font-bold text-gray-800 mb-6">チャットシステム テストページ</h1>
    
    <!-- 設定パネル -->
    <div class="bg-white rounded-sm border border-gray-300 p-4 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">チャット設定</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
                <input 
                    type="checkbox" 
                    bind:checked={chatSettings.showAvatar}
                    class="rounded"
                >
                <span class="text-sm">アバター表示</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
                <input 
                    type="checkbox" 
                    bind:checked={chatSettings.showTimestamp}
                    class="rounded"
                >
                <span class="text-sm">タイムスタンプ表示</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
                <input 
                    type="checkbox" 
                    bind:checked={chatSettings.enableInput}
                    class="rounded"
                >
                <span class="text-sm">入力エリア表示</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
                <input 
                    type="checkbox" 
                    bind:checked={chatSettings.disabled}
                    class="rounded"
                >
                <span class="text-sm">無効化</span>
            </label>
        </div>
    </div>

    <!-- チャット情報 -->
    <div class="bg-blue-50 rounded-sm border border-blue-200 p-4 mb-6">
        <h3 class="font-semibold text-blue-800 mb-2">チャット情報</h3>
        <div class="text-sm text-blue-700 space-y-1">
            <p><strong>総メッセージ数:</strong> {messages.length}</p>
            <p><strong>現在のユーザーID:</strong> {currentUserId}</p>
            <p><strong>創始者ID:</strong> {founderIds.join(', ')}</p>
        </div>
    </div>

    <!-- チャットシステム -->
    <div class="bg-white rounded-sm border border-gray-300 h-96">
        <ChatSystem 
            {messages}
            {currentUserId}
            {founderIds}
            placeholder="テストメッセージを入力してください..."
            showAvatar={chatSettings.showAvatar}
            showTimestamp={chatSettings.showTimestamp}
            enableInput={chatSettings.enableInput}
            disabled={chatSettings.disabled}
            on:sendMessage={handleSendMessage}
            on:attachFile={handleAttachFile}
            on:openEmoji={handleOpenEmoji}
        />
    </div>

    <!-- 使用例 -->
    <div class="mt-8 bg-gray-50 rounded-sm border border-gray-300 p-4">
        <h3 class="font-semibold text-gray-800 mb-3">使用例</h3>
        <div class="space-y-2 text-sm text-gray-600">
            <p>• メッセージを入力してEnterキーで送信</p>
            <p>• Shift+Enterで改行</p>
            <p>• 創始者には王冠マークが表示されます</p>
            <p>• 自分のメッセージは右側、他人のメッセージは左側に表示</p>
            <p>• 設定を変更してUIの動作を確認できます</p>
        </div>
    </div>

    <hr class="my-4 border-gray-300">
<Input 
    messageInput={messageInput}
    handleKeyPress={handleKeyPress}
    disabled={chatSettings.disabled}
    placeholder="〇〇に送信…"
/>
</div>