import { apiClient } from '$lib/services/django.js';

/**
 * 指定された年月のNewScheduleを取得する関数
 * @param {number} year - 年（例: 2024）
 * @param {number} month - 月（例: 12）
 * @returns {Promise<Array>} スケジュールの配列
 */
export async function getNewSchedules(year, month) {
    try {
        console.log(`NewSchedule取得開始: year=${year}, month=${month}`);
        
        // APIエンドポイントを構築
        const endpoint = `/calendar/new-schedules/${year}/${month}`;
        
        // APIを呼び出してスケジュールデータを取得
        const schedules = await apiClient.get(endpoint);
        
        console.log('取得したNewScheduleデータ:', schedules);
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
                    is_all_day: schedule.is_all_day,
                    user: schedule.user
                });
            });
        } else {
            console.log('この月にはスケジュールが登録されていません');
        }
        
        return schedules || [];
        
    } catch (error) {
        console.error('NewSchedule取得エラー:', error);
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
 * 複数のカレンダーから指定年月のスケジュールを一括取得する関数（後方互換性のため残す）
 * @param {Array} calendarIds - カレンダーIDの配列
 * @param {number} year - 年
 * @param {number} month - 月
 * @returns {Promise<Array>} 全てのスケジュールをまとめた配列
 */
export async function getSchedulesFromMultipleCalendars(calendarIds, year, month) {
    // NewScheduleのAPIを使用
    return await getNewSchedules(year, month);
}
