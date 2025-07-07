/**
 * 日時の入力を正規化して「YYYY/MM/DD HH:MM」形式で返す関数
 * @param {Date|string|number} input - 日時データ（Date オブジェクト、ISO文字列、タイムスタンプなど）
 * @returns {string} 正規化された日時文字列（例: "2025/07/02 15:10"）
 */
export function datetimeNormalize(input) {
    let date;
    
    // null または undefined の場合は空文字を返す
    if (input === null || input === undefined) {
        return '';
    }
    
    // 入力タイプに応じてDateオブジェクトに変換
    if (input instanceof Date) {
        date = input;
    } else if (typeof input === 'string') {
        date = new Date(input);
    } else if (typeof input === 'number') {
        date = new Date(input);
    } else {
        return '';
    }
    
    // 無効な日時の場合は空文字を返す
    if (isNaN(date.getTime())) {
        return '';
    }
    
    // 年月日時分を取得
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}/${month}/${day} ${hours}:${minutes}`;
}

/**
 * 日時の入力を正規化して日付のみ「YYYY/MM/DD」形式で返す関数
 * @param {Date|string|number} input - 日時データ（Date オブジェクト、ISO文字列、タイムスタンプなど）
 * @returns {string} 正規化された日付文字列（例: "2025/07/02"）
 */
export function dateNormalize(input) {
    let date;
    
    // null または undefined の場合は空文字を返す
    if (input === null || input === undefined) {
        return '';
    }
    
    // 入力タイプに応じてDateオブジェクトに変換
    if (input instanceof Date) {
        date = input;
    } else if (typeof input === 'string') {
        date = new Date(input);
    } else if (typeof input === 'number') {
        date = new Date(input);
    } else {
        return '';
    }
    
    // 無効な日時の場合は空文字を返す
    if (isNaN(date.getTime())) {
        return '';
    }
    
    // 年月日を取得
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}/${month}/${day}`;
}

/**
 * 日時の入力を正規化して時間のみ「HH:MM」形式で返す関数
 * @param {Date|string|number} input - 日時データ（Date オブジェクト、ISO文字列、タイムスタンプなど）
 * @returns {string} 正規化された時間文字列（例: "15:10"）
 */
export function timeNormalize(input) {
    let date;
    
    // null または undefined の場合は空文字を返す
    if (input === null || input === undefined) {
        return '';
    }
    
    // 入力タイプに応じてDateオブジェクトに変換
    if (input instanceof Date) {
        date = input;
    } else if (typeof input === 'string') {
        date = new Date(input);
    } else if (typeof input === 'number') {
        date = new Date(input);
    } else {
        return '';
    }
    
    // 無効な日時の場合は空文字を返す
    if (isNaN(date.getTime())) {
        return '';
    }
    
    // 時分を取得
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${hours}:${minutes}`;
}

/**
 * 現在の日時を正規化して返す関数
 * @returns {string} 正規化された現在日時文字列
 */
export function getCurrentDatetimeNormalized() {
    return datetimeNormalize(new Date());
}

/**
 * 現在の日付のみを正規化して返す関数
 * @returns {string} 正規化された現在日付文字列
 */
export function getCurrentDateNormalized() {
    return dateNormalize(new Date());
}

/**
 * 現在の時間のみを正規化して返す関数
 * @returns {string} 正規化された現在時間文字列
 */
export function getCurrentTimeNormalized() {
    return timeNormalize(new Date());
}

/**
 * ISO文字列を正規化して返す関数
 * @param {string} isoString - ISO形式の日時文字列
 * @returns {string} 正規化された日時文字列
 */
export function normalizeISOString(isoString) {
    return datetimeNormalize(isoString);
}
