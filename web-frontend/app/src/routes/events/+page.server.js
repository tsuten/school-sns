/** @type {import('./$types').PageServerLoad} */
export async function load() {
    try {
        // 並行してAPIからデータを取得
        const [nextEventsResponse, heldEventsResponse] = await Promise.all([
            fetch('http://localhost:8000/api/events/next_events', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            }),
            fetch('http://localhost:8000/api/events/held_events', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
        ]);

        // レスポンスのチェック
        if (!nextEventsResponse.ok) {
            throw new Error(`今後のイベント取得エラー! status: ${nextEventsResponse.status}`);
        }
        
        if (!heldEventsResponse.ok) {
            throw new Error(`現在進行中のイベント取得エラー! status: ${heldEventsResponse.status}`);
        }

        // JSONデータの取得
        const [nextEvents, heldEvents] = await Promise.all([
            nextEventsResponse.json(),
            heldEventsResponse.json()
        ]);
        
        return {
            nextEvents: nextEvents || [],
            heldEvents: heldEvents || []
        };
    } catch (error) {
        console.error('イベントデータの取得に失敗しました:', error);
        
        // エラーが発生した場合は空の配列を返す
        return {
            nextEvents: [],
            heldEvents: []
        };
    }
};