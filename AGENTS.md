# Frontend Architecture & Shadcn UI Guidelines

> **所有在此專案前端工作的 Agent 必須嚴格遵守本文件。本文件是高優先級約束，違反任何規定均不可接受。**

---

## 目錄結構職責

| 目錄 | 職責 |
|---|---|
| `src/components/ui/` | shadcn-vue CLI 產生的**原子基底元件**，可修改 CVA 定義，禁止加業務邏輯 |
| `src/components/layout/` | 業務層級的**組裝元件**（AppHeader、CommandPalette 等），透過 `ui/` 積木組合 |
| `src/i18n/locales/` | 所有使用者可見文字的唯一來源 |
| `src/config/navigation.ts` | 只存 i18n key，不存顯示文字 |

---

## 1. shadcn-vue 元件規範（最高優先級）

### 1.1 新增元件：一律使用 CLI
```bash
pnpm dlx shadcn-vue@latest add sidebar
pnpm dlx shadcn-vue@latest add command dialog
```
❌ **禁止手工在 `components/ui/` 建立任何基底元件**

### 1.2 修改元件：只能修改 CVA 定義
當需要新增一個重複使用的樣式，**修改基底一次，而不是每次使用時加 inline class**：

```ts
// ✅ 正確：在 components/ui/button/index.ts 新增 variant/size
size: {
  'icon-sm': 'h-9 w-9', // 所有地方自動套用
}
```

```vue
<!-- ✅ 正確：使用端語意清晰 -->
<Button variant="ghost" size="icon-sm" />

<!-- ❌ 錯誤：每個地方重複堆 class，製造維護地獄 -->
<Button class="h-9 w-9 text-muted-foreground hover:bg-accent transition-all" />
```

### 1.3 樣式決策樹（每次新增樣式前必須過此決策樹）

```
這個樣式會被使用 2 次以上？
├─ YES → 修改 components/ui/ 基底的 CVA (variant/size)
├─ NO  → 這是一次性業務視覺需求？
│         ├─ YES → 可在 layout/ 組件中使用 inline class
│         └─ NO  → 全域行為？→ 寫入 style.css 的 @layer base
```

### 1.4 原子化組合（禁止 Monolith）

```vue
<!-- ❌ 錯誤：一個 300 行的黑盒組件包辦所有 -->
<AppSidebar />  <!-- 內部自己 div 手刻 -->

<!-- ✅ 正確：透過 shadcn 積木組裝，每個子元件單一職責 -->
<Sidebar>
  <SidebarHeader />
  <SidebarContent>
    <SidebarGroup />
  </SidebarContent>
</Sidebar>
```

---

## 2. 工具鏈規範（不可更換）

| 功能 | 套件 | 禁止替代 |
|---|---|---|
| UI 無障礙底層 | `reka-ui` / `radix-vue` | 禁止自行實作 Dropdown/Dialog/Focus |
| Icon | `lucide-vue-next` | ❌ 禁止使用 Emoji 作為 Icon |
| Toast | `vue-sonner` | ❌ 禁止使用 `alert()` 或自封裝 |
| 樣式合併 | `cn()` from `src/lib/utils.ts` | ❌ 禁止字串插值合併 className |

**Props 透傳：** 所有自建的包裝組件最外層必須加 `v-bind="$attrs"`。

---

## 3. 字體規範

- **字體組合（固定）**：`font-family: 'Inter Variable', 'Noto Sans TC', sans-serif;`
- **載入方式**：使用 `@fontsource` 在 `main.ts` 引入，確保離線可用
- ❌ 禁止在 `index.html` 使用 Google Fonts 等外部 CDN

---

## 4. 國際化 (i18n) 規範

**核心原則：所有使用者可見的文字，100% 必須透過 i18n。**

### 4.1 基礎設定
- **套件**：`vue-i18n@11`（Composition API 模式）
- **掛載**：`src/i18n/index.ts`，在 `main.ts` 中必須在 router **之前** `app.use(i18n)`
- **globalInjection: true** — `$t()` 在所有 template 中全域可用，不需每個組件 `useI18n()`

### 4.2 新增文字的標準流程（必須照順序）
1. 在 `src/i18n/locales/en.ts` 新增 key（`en.ts` 是型別基準）
2. 在 `src/i18n/locales/zh-TW.ts` 補上對應翻譯
3. Template 中使用 `$t('your.key')` 或 Script 中使用 `t('your.key')`

### 4.3 禁止項目
❌ 禁止在任何 `.vue` Template 中直接寫任何中文或英文顯示文字（Hardcoded strings）  
❌ 禁止在 `src/config/navigation.ts` 的 `label`/`name`/`description` 欄位存顯示文字（只存 i18n key）  
❌ 禁止只更新 `en.ts` 而不同步更新 `zh-TW.ts`（TypeScript 型別會報錯）

### 4.4 語言切換
透過 `src/composables/useLocale.ts` 的 `setLocale()` 切換，自動儲存至 localStorage 並同步 `document.documentElement.lang`。

---

## 5. Toast 規範

- 使用方式：`import { toast } from 'vue-sonner'`，直接呼叫
- `<Toaster>` 已在 `src/App.vue` 全域掛載，含 dark mode 同步
- ❌ 禁止覆寫 `--success-bg`、`--error-bg` 等 rich color CSS 變數

---

## 6. 開發前必做 Checklist

在開始任何 UI 開發任務前，逐項確認：

- [ ] **新功能**：是否有對應的 shadcn-vue CLI 元件可用？先 `add` 再組裝
- [ ] **新樣式**：通過 §1.3 決策樹，確認放在正確位置（CVA / inline / style.css）
- [ ] **新文字**：是否已在 `en.ts` + `zh-TW.ts` 同時定義 key？
- [ ] **表單**：是否使用 `<Form>`, `<FormField>`, `<FormItem>` 而非 `div` + `input`？
- [ ] **Props**：自建包裝組件是否有 `v-bind="$attrs"`？
