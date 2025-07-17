<script>
  import { onMount } from "svelte";

  // 親コンポーネントから受け取り、変更を伝える変数
  export let postalCode = "";
  export let prefecture = "";
  export let city = "";
  export let street = "";

  // 内部状態を管理する用の変数
  let suggestions = [];
  let selectedIndex = -1;
  let isDataLoaded = false;
  let csvData = [];

  // マウントされた時に実行
  onMount(() => {
    loadCSV();
  });

  async function loadCSV() {
    try {
      // 郵便番号データcsvファイル（日本郵便の郵便番号データ）を取得
      const res = await fetch("/x-ken-all.csv");
      const buffer = await res.arrayBuffer();
      // エンコードしないと困るのでちゃんとエンコードする
      const text = new TextDecoder("shift_jis").decode(buffer);
      // 改行文字で分割して行ごとに処理
      const lines = text.split("\n");

      // 各行をパースしてデータを抽出
      for (const line of lines) {
        const cols = parseCSVLine(line);
        // 列数をチェック
        if (cols.length >= 9) {
          csvData.push({
            zipcode: cols[2],
            prefecture: cols[6],
            city: cols[7],
            town: cols[8],
          });
        }
      }
      isDataLoaded = true;
    } catch (err) {
      console.error("CSV読み込み失敗:", err);
    }
  }

  // CSVの1行を正しく調整する関数
  function parseCSVLine(line) {
    const result = [];
    let current = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        if (inQuotes && line[i + 1] === '"') {
          current += '"';
          i++;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === "," && !inQuotes) {
        result.push(current);
        current = "";
      } else {
        current += char;
      }
    }
    result.push(current);
    return result;
  }

  $: formattedPostal = formatPostal(postalCode);

  // 郵便番号をハイフン付きの形式にフォーマット
  function formatPostal(code) {
    const digits = code.replace(/\D/g, "");
    if (digits.length <= 3) return digits;
    return digits.slice(0, 3) + "-" + digits.slice(3, 7);
  }

  // 入力された郵便番号が3文字以上の時に検索を実行
  $: if (formattedPostal.replace("-", "").length >= 3) {
    searchSuggestions(formattedPostal);
  } else {
    // 3文字未満の場合は候補をクリア
    suggestions = [];
  }

  // 入力された郵便番号に基づいて候補を検索
  function searchSuggestions(inputCode) {
    if (!isDataLoaded) return;
    const prefix = inputCode.replace("-", "");
    suggestions = csvData
    // 郵便番号が入力値で始まるものをフィルタリング
      .filter((r) => r.zipcode.startsWith(prefix))
      .reduce((acc, cur) => {
        if (!acc.some((e) => e.zipcode === cur.zipcode)) acc.push(cur);
        return acc;
      }, [])
      .slice(0, 8);
  }

  function selectSuggestion(s) {
    postalCode = formatPostal(s.zipcode);
    prefecture = s.prefecture;
    city = s.city;
    if (!street) street = s.town;
    suggestions = [];
  }
</script>

<div class="flex flex-col gap-2 w-full max-w-md mx-auto">
  <div class="flex items-center gap-2 mb-2 relative">
    <label class="block text-sm font-semibold min-w-[5.5rem]">郵便番号</label>
    <input
      class="px-3 py-0.5 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-400 bg-gray-50 placeholder-gray-400 text-sm w-[8.5rem] min-w-0"
      value={formattedPostal}
      oninput={(e) => (postalCode = e.target.value)}
      placeholder="例: 123-4567"
      maxlength="8"
    />
    {#if suggestions.length > 0}
      <div class="absolute left-0 top-full mt-1 w-[18rem] bg-white border border-gray-300 rounded shadow z-50">
        {#each suggestions as s}
          <div
            class="px-3 py-1 hover:bg-blue-50 cursor-pointer text-sm"
            onclick={() => selectSuggestion(s)}
          >
            〒{s.zipcode} {s.prefecture}{s.city}{s.town}
          </div>
        {/each}
      </div>
    {/if}
  </div>
  <div class="flex gap-2 mb-2 ml-[5.5rem] w-[calc(100%-5.5rem-1.5rem)] min-w-0 pr-6">
    <div class="flex-1">
      <label class="block text-xs font-semibold mb-0.5">都道府県</label>
      <input class="px-2 py-0.5 border border-gray-300 rounded bg-gray-50 text-xs w-full min-w-0" value={prefecture} readonly />
    </div>
    <div class="flex-1">
      <label class="block text-xs font-semibold mb-0.5">市区町村</label>
      <input class="px-2 py-0.5 border border-gray-300 rounded bg-gray-50 text-xs w-full min-w-0" value={city} readonly />
    </div>
    <div class="flex-1">
      <label class="block text-xs font-semibold mb-0.5">町名</label>
      <input class="px-2 py-0.5 border border-gray-300 rounded bg-gray-50 text-xs w-full min-w-0" bind:value={street} placeholder="例: 神南" />
    </div>
  </div>
</div>