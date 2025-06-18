import { apiClient } from '$lib/services/django.js';

/**
 * 指定されたカレンダーの指定年月のスケジュールを取得する関数
 * @param {string} calendarId - カレンダーのID
 * @param {number} year - 年（例: 2024）
 * @param {number} month - 月（例: 12）
 * @returns {Promise<Array>} スケジュールの配列
 */
export async function getSchedules(calendarId, year, month) {
    try {
        console.log(`スケジュール取得開始: calendarId=${calendarId}, year=${year}, month=${month}`);
        
        // APIエンドポイントを構築
        const endpoint = `/calendar/schedules/${calendarId}/${year}/${month}`;
        
        // APIを呼び出してスケジュールデータを取得
        const schedules = await apiClient.get(endpoint);
        
        console.log('取得したスケジュールデータ:', schedules);
        console.log(`スケジュール数: ${schedules ? schedules.length : 0}件`);
        
        // 各スケジュールの詳細をログ出力
        if (schedules && schedules.length > 0) {
            schedules.forEach((schedule, index) => {
                console.log(`スケジュール ${index + 1}:`, {
                    id: schedule.id,
                    title: schedule.title,
                    description: schedule.description,
                    start_time: schedule.start_time,
                    end_time: schedule.end_time,
                    location: schedule.location,
                    is_all_day: schedule.is_all_day
                });
            });
        } else {
            console.log('この月にはスケジュールが登録されていません');
        }
        
        return schedules || [];
        
    } catch (error) {
        console.error('スケジュール取得エラー:', error);
        console.error('エラー詳細:', {
            status: error.status,
            message: error.message,
            data: error.data
        });
        
        // エラーが発生した場合は空の配列を返す
        return [];
    }
}

/**
 * 複数のカレンダーから指定年月のスケジュールを一括取得する関数
 * @param {Array} calendarIds - カレンダーIDの配列
 * @param {number} year - 年
 * @param {number} month - 月
 * @returns {Promise<Array>} 全てのスケジュールをまとめた配列
 */
export async function getSchedulesFromMultipleCalendars(calendarIds, year, month) {
    try {
        console.log(`複数カレンダーからスケジュール取得開始:`, {
            calendarIds,
            year,
            month,
            calendarCount: calendarIds.length
        });
        
        // 各カレンダーから並行してスケジュールを取得
        const promises = calendarIds.map(calendarId => 
            getSchedules(calendarId, year, month)
        );
        
        const results = await Promise.all(promises);
        
        // 全てのスケジュールを1つの配列にまとめる
        const allSchedules = results.flat();
        
        console.log('複数カレンダーから取得した全スケジュール:', allSchedules);
        console.log(`合計スケジュール数: ${allSchedules.length}件`);
        
        return allSchedules;
        
    } catch (error) {
        console.error('複数カレンダーからのスケジュール取得エラー:', error);
        return [];
    }
}
