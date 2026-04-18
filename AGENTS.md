# Frontend Architecture & Shadcn UI Guidelines

This file serves as a strict architectural guideline for any Agent working on the frontend of this project.

## 核心哲學：原子化設計 (Atomic Design)
本專案的 `components/ui` 並不是用來放置「自定義的黑盒大組件」，而是**「專案源碼的一部分」**。
在設計與構建任何 UI（如側邊欄、指令面板、對話框、表單）時，**絕對禁止**創建將所有邏輯（Header, Footer, Menu, Triggers等）包在一個巨大檔案中（Monolith）的做法。

### 1. 基礎 UI 必須從 CLI 產生
*   **不要手工編寫基礎元件。**
*   當需要類似 Sidebar, Dialog, Command, Tabs, Table 等佈局或功能時，請一律使用 `shadcn-vue` 的 CLI 下載原子組件。
    ```bash
    # (範例)
    pnpm dlx shadcn-vue@latest add sidebar
    pnpm dlx shadcn-vue@latest add command
    ```

### 2. 極致的組合靈活性 (Composability)
透過 CLI 加入的元件將會以**子資料夾及 `index.ts`** 模式呈現。你必須透過這些「積木」來組裝你的視圖，而不是把它們封裝死：
*   **錯誤作法（Monolith）：** 寫一個 300 行的 `AppSidebar.vue`，把 `div` 手刻樣式包辦到底。
*   **正確作法（Atomic 組裝）：** 導入 `<Sidebar>`, `<SidebarHeader>`, `<SidebarContent>`, `<SidebarGroup>` 等組件，在你的外層容器（如 `AppLayout.vue` 或精簡後的 `AppSidebar.vue`）中將它們組裝。

### 3. 單一職責原則與 Props 透傳 ($attrs)
*   所有封裝的自定義子組件（如果非得自建），最外層渲染必須接收外部傳遞的屬性與深色模式：`v-bind="$attrs"`。
*   樣式合併必須統一透過 `src/lib/utils.ts` 的 `cn()` utility，不可以使用單純字串插值，避免 Tailwind className 衝突。

### 4. 工具鏈與生態
*   **無樣式底層**：認可並善用 `radix-vue` (或是 `reka-ui`) 來作為複雜組件的基底。不要自己造輪子寫具備 Accessibility (A11y) 的 Dropdown、Dialog 或 Focus 狀態管理。
*   **Icon 規則**：禁止使用 Emoji 作為 Icon，全站統一規範使用 `lucide-vue-next`。
*   **Toast 管理**：依賴 `vue-sonner` (取代原生的 `alert()` 或粗糙的自行封裝)。

---
**Agent 指導原則 Checklist：**
1. 準備建構複雜的區塊（如：側邊欄、搜尋面板、表格控制）時，先檢查是否有對應的 shadcn CLI 組件可以 `add`。
2. 開發表單時，考慮使用 `<Form>`, `<FormField>`, `<FormItem>` 的組合，而非單純的 `<div class="grid">` + `<input>`。
3. 把所有的基底依賴放入 `@/components/ui`（並且保持小寫資料夾名稱 `ui/button/index.ts`），將你的業務視圖和「組裝工廠」放在對應頁面或 `@/components/layout`。

### 5. Inline Class 規範（重要！）

**核心原則：永遠優先修改 `components/ui` 的基底，而不是在外面堆 class。**

**❌ 錯誤做法（每次使用都重複加 class）：**
```vue
<!-- 每個地方都要手動加尺寸、顏色、hover — 這是維護地獄 -->
<SidebarTrigger class="h-9 w-9 text-muted-foreground hover:bg-accent hover:text-foreground transition-all" />
<Button class="h-9 w-9 text-muted-foreground hover:text-foreground" />
```

**✅ 正確做法（修改基底一次，所有地方自動套用）：**
```ts
// components/ui/button/index.ts — 新增一個語意明確的 variant/size
size: {
  'icon-sm': 'h-9 w-9',  // Header toolbar standard
}
```
```vue
<!-- 使用端只需要傳入 prop，HTML 乾淨易讀 -->
<Button variant="ghost" size="icon-sm" />
<SidebarTrigger />  <!-- 基底已設定好，不需要任何 class -->
```

**決策樹（每次新增樣式前先問自己）：**
- 這個樣式會在 **2 個以上地方** 重複使用嗎？→ **修改基底組件**
- 這是某個頁面的**一次性**視覺需求嗎？→ 才可以加 inline class
- 是「全域通用」的行為（如 cursor-pointer）？→ 寫進 `style.css` 的 `@layer base`

---

## 6. 字體規範 (Typography)

- **英文字體**：`Inter` — 經典的高品質數位 UI 字體，極致的可讀性
- **中文字體**：`Noto Sans TC` — 繁體中文最佳選擇，fallback 於英文字體之後
- **CSS 寫法固定**：`font-family: 'Inter Variable', 'Noto Sans TC', sans-serif;`
- **載入方式**：使用 `@fontsource` 本地化部署，確保在公司內網 (Intranet) 離線環境下字體仍能正常載入。在 `main.ts` 引入對應 CSS。
- ❌ 禁止在 `index.html` 使用連結外部 CDN (如 Google Fonts)，確保 100% 離線可用。

---

## 7. 國際化 (i18n) 規範

- **套件**：`vue-i18n@11`（Composition API 模式）
- **配置位置**：`src/i18n/index.ts`，在 `main.ts` 以 `app.use(i18n)` 掛載（必須在 router **之前**）
- **Locale 檔案**：`src/i18n/locales/en.ts`（型別基準）、`src/i18n/locales/zh-TW.ts`（實作 `MessageSchema`）
- **語言切換**：透過 `src/composables/useLocale.ts` 的 `setLocale()`，儲存至 localStorage，並同步 `document.documentElement.lang`
- **Navigation config** (`src/config/navigation.ts`): `label`、`name`、`description` 欄位存 **i18n key**（如 `'nav.items.home'`），不存顯示文字，所有使用端需呼叫 `t()` 或 `$t()`
- **Router breadcrumb**: `meta.breadcrumb` 存 i18n key，`useBreadcrumbs.ts` 內部呼叫 `t()` 翻譯
- **globalInjection: true** — 讓 `$t()` 在所有 template 中直接可用，不需每個組件都 `useI18n()`
- ❌ 禁止在 config/navigation.ts 直接放中文或英文顯示文字

---

## 8. Toast 規範 (vue-sonner)

- **套件**：`vue-sonner`（已安裝，勿更換）
- **掛載位置**：`src/App.vue` 的 `<Toaster>` 組件，已完整配置（含 dark mode 同步、rich-colors、close-button）
- **使用方式**：在任何 component 中直接 `import { toast } from 'vue-sonner'` 呼叫
- **CSS 整合**：已在 `src/style.css` 尾部加入設計系統 token 覆寫（字體、圓角、背景色）
  - `rich-colors` 的顏色為 Sonner 官方設計，**不要覆寫**
  - 預設（非 rich）toast 使用 `--popover` 系列 token，與 Card/Dropdown 一致
- ❌ 禁止使用 `alert()`、自行封裝 toast div 或引入其他 notification 套件
- ❌ 不要在 Sonner toast 的 CSS 覆寫中動到 `--success-bg`、`--error-bg` 等 rich color 變數
