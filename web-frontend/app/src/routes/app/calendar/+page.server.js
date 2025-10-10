/** @type {import('./$types').PageServerLoad} */
export async function load({ cookies }) {
    // クライアントサイドでデータ取得を行うため、サーバーサイドでは空のデータを返す
    return {
        calendars: []
    };
};