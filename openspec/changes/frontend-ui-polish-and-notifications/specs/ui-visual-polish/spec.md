## ADDED Requirements

### Requirement: 卡片元件視覺提升
Card 元件 SHALL 具備精緻的邊框、陰影與 hover 效果，在深色與淺色模式下都有良好的視覺層次。

#### Scenario: 深色模式下卡片樣式
- **WHEN** 使用者在深色模式下查看含有 Card 元件的頁面
- **THEN** 卡片 SHALL 具有微妙的邊框、適當的背景色，與頁面背景形成清晰層次

#### Scenario: 卡片 hover 效果
- **WHEN** 使用者滑鼠移入卡片區域
- **THEN** 卡片 SHALL 展示微妙的視覺回饋（如陰影加深或邊框高亮）

### Requirement: 表格排版一致化
表格元素 SHALL 具備統一的 header 樣式、行高、padding 與 hover 效果，確保資料可讀性。

#### Scenario: 表格 header 與內容的視覺區分
- **WHEN** 頁面渲染資料表格
- **THEN** 表格 header SHALL 以明顯的背景色或字重與 body 區分，且各欄寬度合理

#### Scenario: 表格行 hover 效果
- **WHEN** 使用者滑鼠移入某一表格行
- **THEN** 該行 SHALL 展示微妙的背景色變化作為視覺回饋

### Requirement: 頁面間距與佈局一致性
所有頁面 SHALL 使用統一的 padding、margin 與 gap spacing，形成一致的視覺節奏。

#### Scenario: 頁面內容區域 padding 統一
- **WHEN** 使用者瀏覽不同功能頁面
- **THEN** 各頁面主內容區域 SHALL 具有相同的 padding 與最大寬度限制

#### Scenario: 元件間距一致
- **WHEN** 頁面包含多個區塊（標題、表單、表格）
- **THEN** 各區塊之間 SHALL 使用統一的垂直間距

### Requirement: 表單元件樣式優化
表單 input、select、button 等元素 SHALL 具備一致的高度、圓角、邊框與聚焦樣式。

#### Scenario: Input 聚焦狀態
- **WHEN** 使用者點擊一個 text input
- **THEN** input SHALL 展示清晰的聚焦環（focus ring），顏色與主題色一致

#### Scenario: Button 樣式統一
- **WHEN** 頁面包含多個 primary button
- **THEN** 所有 primary button SHALL 具有相同的高度、圓角、字型大小與 hover 效果
