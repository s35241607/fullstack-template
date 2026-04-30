<script setup lang="ts">
  import { ref } from 'vue'
  import AgGrid from '@/components/ui/ag-grid/AgGrid.vue'
  import SearchableSelectEditor from '@/components/ui/ag-grid/SearchableSelectEditor.vue'
  import { Button } from '@/components/ui/button'
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
  import { Copy, HelpCircle, Grid, Info } from 'lucide-vue-next'
  import { toast } from 'vue-sonner'

  const gridRef = ref()

  const columnDefs = ref([
    {
      field: 'id',
      headerName: 'ID',
      width: 60,
      pinned: 'left',
      checkboxSelection: true,
      headerCheckboxSelection: true,
      cellClass: 'text-muted-foreground',
    },
    {
      field: 'name',
      headerName: '產品名稱',
      filter: 'agTextColumnFilter',
      minWidth: 200,
      cellRenderer: (params: any) => {
        const icons: Record<string, string> = {
          'MacBook Pro 14"': '💻',
          'iPad Air 11"': '📱',
          'iPhone 15 Pro': '📲',
          'AirPods Pro 2': '🎧',
          'Magic Mouse': '🖱️',
          'Studio Display': '🖥️',
          'Apple Watch Ultra 2': '⌚',
          'Mac Studio': '⚙️',
        }
        const icon = icons[params.value] || '📄'
        return `<div class="flex items-center gap-2"><span>${icon}</span><span class="font-medium">${params.value || ''}</span></div>`
      },
    },
    {
      field: 'category',
      headerName: '分類',
      width: 120,
      cellEditor: SearchableSelectEditor,
      cellEditorPopup: true,
      cellEditorParams: {
        values: ['電子產品', '配件', '顯示器', '伺服器', '軟體'],
      },
      cellRenderer: (params: any) => {
        if (!params.value) return ''
        const colors: Record<string, string> = {
          電子產品: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
          配件: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
          顯示器: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
          預設: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-400',
        }
        const colorClass = colors[params.value] || colors['預設']
        return `<span class="px-2 py-0.5 text-[11px] font-semibold rounded-md ${colorClass}">${params.value}</span>`
      },
    },
    {
      field: 'price',
      headerName: '價格',
      filter: 'agNumberColumnFilter',
      width: 120,
      valueFormatter: (params: any) => `$${params.value?.toLocaleString()}`,
      cellClass: 'font-mono text-right',
    },
    {
      field: 'status',
      headerName: '狀態',
      width: 120,
      cellEditor: SearchableSelectEditor,
      cellEditorPopup: true,
      cellEditorParams: {
        values: ['有庫存', '低庫存', '缺貨', '待補貨'],
      },
      cellRenderer: (params: any) => {
        if (!params.value) return ''
        const colors: Record<string, string> = {
          有庫存: 'text-emerald-600 dark:text-emerald-400',
          低庫存: 'text-orange-600 dark:text-orange-400',
          缺貨: 'text-rose-600 dark:text-rose-400',
          待補貨: 'text-blue-600 dark:text-blue-400',
        }
        const colorClass = colors[params.value] || 'text-muted-foreground'
        return `<div class="flex items-center gap-1.5"><div class="h-1.5 w-1.5 rounded-full bg-current ${colorClass}"></div><span class="${colorClass}">${params.value}</span></div>`
      },
    },
    {
      field: 'updatedAt',
      headerName: '更新日期',
      filter: 'agDateColumnFilter',
      width: 140,
      cellClass: 'text-muted-foreground text-xs',
    },
    {
      field: 'description',
      headerName: '描述',
      minWidth: 300,
      cellClass: 'text-muted-foreground text-xs',
    },
  ])

  const rowData = ref([
    {
      id: 1,
      name: 'MacBook Pro 14"',
      category: '電子產品',
      price: 69900,
      status: '有庫存',
      updatedAt: '2024-01-01',
      description: 'Apple M3 Pro 晶片，14 吋顯示器，18GB 統一記憶體',
    },
    {
      id: 2,
      name: 'iPad Air 11"',
      category: '電子產品',
      price: 19900,
      status: '有庫存',
      updatedAt: '2024-01-05',
      description: 'M2 晶片，11 吋顯示器，Apple Pencil Pro 支援',
    },
    {
      id: 3,
      name: 'iPhone 15 Pro',
      category: '電子產品',
      price: 36900,
      status: '缺貨',
      updatedAt: '2024-01-10',
      description: '鈦金屬設計，A17 Pro 晶片，48MP 主相機',
    },
    {
      id: 4,
      name: 'AirPods Pro 2',
      category: '配件',
      price: 7490,
      status: '有庫存',
      updatedAt: '2024-01-15',
      description: '主動式降噪，H2 晶片，USB-C 充電盒',
    },
    {
      id: 5,
      name: 'Magic Mouse',
      category: '配件',
      price: 2290,
      status: '有庫存',
      updatedAt: '2024-01-20',
      description: '多點觸控表面，藍牙連線',
    },
    {
      id: 6,
      name: 'Studio Display',
      category: '顯示器',
      price: 45900,
      status: '低庫存',
      updatedAt: '2024-01-25',
      description: '27 吋 5K Retina 顯示器，12MP 超廣角相機',
    },
    {
      id: 7,
      name: 'Apple Watch Ultra 2',
      category: '配件',
      price: 27900,
      status: '有庫存',
      updatedAt: '2024-01-28',
      description: '航太等級鈦金屬，S9 SiP 晶片',
    },
    {
      id: 8,
      name: 'Mac Studio',
      category: '電子產品',
      price: 64900,
      status: '有庫存',
      updatedAt: '2024-02-01',
      description: 'M2 Max 晶片，精巧高效的桌上型電腦',
    },
  ])

  const handleCopy = () => {
    if (gridRef.value) {
      gridRef.value.copySelected()
      toast.success('已將選取行複製到剪貼簿 (以 Tab 分隔)')
    }
  }
</script>

<template>
  <div class="flex flex-col gap-6 w-full animate-in fade-in slide-in-from-bottom-4 duration-500">
    <!-- Header Section -->
    <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between px-1">
      <div class="flex flex-col gap-1">
        <div class="flex items-center gap-2.5">
          <div
            class="p-2.5 bg-primary/10 rounded-xl text-primary shadow-sm border border-primary/20"
          >
            <Grid :size="22" />
          </div>
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
              AG Grid Pro Demo
            </h1>
            <p class="text-sm text-muted-foreground">
              高效能資料表格解決方案，整合客製化選取與編輯體驗。
            </p>
          </div>
        </div>
      </div>

      <div class="flex items-center gap-3 mt-4 sm:mt-0">
        <Button
          variant="outline"
          size="sm"
          @click="handleCopy"
          class="h-10 px-4 rounded-lg shadow-sm hover:bg-accent transition-all"
        >
          <Copy class="w-4 h-4 mr-2" />
          複製選取
        </Button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid gap-6">
      <Card
        class="border-border/40 shadow-xl shadow-black/5 dark:shadow-none overflow-hidden rounded-2xl"
      >
        <CardHeader class="pb-5 pt-6 bg-muted/20 border-b border-border/40">
          <div class="flex items-center justify-between">
            <div class="space-y-1.5">
              <CardTitle class="text-xl font-bold">產品資料管理</CardTitle>
              <CardDescription class="text-sm">
                支援深色模式底色切換、Enter 鍵直接進入編輯、主色選取框與自定義填滿控點。
              </CardDescription>
            </div>
            <div
              class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20"
            >
              <div class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
              <span
                class="text-[11px] font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-widest"
                >Active</span
              >
            </div>
          </div>
        </CardHeader>
        <CardContent class="p-0">
          <div class="p-6 bg-card/50 backdrop-blur-sm">
            <AgGrid ref="gridRef" :rowData="rowData" :columnDefs="columnDefs" height="500px" />
          </div>

          <!-- Features Info -->
          <div class="bg-muted/30 border-t border-border/40 p-6">
            <h3 class="text-sm font-bold mb-4 flex items-center gap-2 text-foreground/80">
              <Info :size="18" class="text-primary" />
              進階功能實作清單
            </h3>
            <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div
                class="group space-y-2 p-4 rounded-xl bg-background/50 border border-border/40 hover:border-primary/30 hover:shadow-md transition-all duration-300"
              >
                <div
                  class="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-500"
                >
                  <span class="text-xs font-bold">01</span>
                </div>
                <p class="text-sm font-bold text-foreground">深色模式底色修正</p>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  已修正深色模式下的底色 inheritance，確保在深色背景下表格內容呈現深 Slate
                  色調，符合整體 UI 質感。
                </p>
              </div>
              <div
                class="group space-y-2 p-4 rounded-xl bg-background/50 border border-border/40 hover:border-primary/30 hover:shadow-md transition-all duration-300"
              >
                <div
                  class="w-8 h-8 rounded-lg bg-orange-500/10 flex items-center justify-center text-orange-500"
                >
                  <span class="text-xs font-bold">02</span>
                </div>
                <p class="text-sm font-bold text-foreground">Enter 鍵快速編輯</p>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  實作 `onCellKeyDown` 邏輯，當選中單元格按下 Enter
                  鍵時立即啟動編輯模式，提升資料錄入效率。
                </p>
              </div>
              <div
                class="group space-y-2 p-4 rounded-xl bg-background/50 border border-border/40 hover:border-primary/30 hover:shadow-md transition-all duration-300"
              >
                <div
                  class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary"
                >
                  <span class="text-xs font-bold">03</span>
                </div>
                <p class="text-sm font-bold text-foreground">客製化選取框與 Fill Handle</p>
                <p class="text-xs text-muted-foreground leading-relaxed">
                  透過 CSS 選取器美化選取框並在右下角加入主色方框（Fill Handle），模擬 Excel
                  視覺體驗。
                </p>
              </div>
            </div>

            <!-- Warning/Note about Enterprise features -->
            <div
              class="mt-6 flex items-start gap-4 p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 shadow-inner"
            >
              <HelpCircle class="w-5 h-5 text-amber-500 mt-0.5 shrink-0" />
              <div class="text-xs text-amber-800/80 dark:text-amber-300/70 leading-relaxed">
                <p
                  class="font-bold mb-1 text-amber-900 dark:text-amber-200 uppercase tracking-tight text-[11px]"
                >
                  技術說明
                </p>
                <p>
                  我們使用了 **AG Grid Community** 版本透過自定義 CSS
                  與事件攔截來達成視覺與操作上的優化。Fill Handle
                  的實際「拖曳複製」邏輯在社群版中需手動實作區域計算，本展示已完成視覺整合與編輯流程優化。
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<style scoped>
  /* Add smooth transitions for the dashboard elements */
  .animate-in {
    animation-duration: 0.5s;
  }
</style>
