<template>
  <el-scrollbar>
    <div class="business-zammad p-16">
      <el-card style="--el-card-padding: 24px">
        <div class="flex-between align-center mb-16">
          <h4>{{ $t('views.business.zammad.title') }}</h4>
          <div class="flex align-center">
            <span class="mr-8 color-secondary">{{ $t('views.business.zammad.region') }}</span>
            <el-select
              v-model="region"
              class="mr-8"
              style="width: 120px"
              @change="onRegionChange"
            >
              <el-option
                v-for="item in regionOptions"
                :key="item"
                :label="item.toUpperCase()"
                :value="item"
              />
            </el-select>
            <el-button @click="handleRefresh">
              <AppIcon iconName="app-refresh" class="mr-4" />
              {{ $t('common.refresh') }}
            </el-button>
          </div>
        </div>

        <el-tabs v-model="activeDataType" @tab-change="onDataTypeChange">
          <el-tab-pane
            v-for="item in DATA_TYPE_LIST"
            :key="item.value"
            :label="$t(item.label)"
            :name="item.value"
          />
        </el-tabs>

        <div class="filter-panel mb-16">
          <div class="flex align-center mb-16">
            <span class="mr-8 color-secondary">{{ $t('views.business.zammad.createdAtStart') }}</span>
            <el-date-picker
              v-model="filter.createdAtStart"
              type="datetime"
              class="mr-16"
              value-format="YYYY-MM-DD HH:mm:ss"
              :placeholder="$t('views.business.zammad.createdAtStart')"
            />
            <span class="mr-8 color-secondary">{{ $t('views.business.zammad.createdAtEnd') }}</span>
            <el-date-picker
              v-model="filter.createdAtEnd"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              :placeholder="$t('views.business.zammad.createdAtEnd')"
            />
            <el-button class="ml-16" @click="handleDataSearch">
              {{ $t('views.business.zammad.queryData') }}
            </el-button>
          </div>
          <div class="mb-16">
            <div class="mb-8 color-secondary">{{ $t('views.business.zammad.analysisPrompt') }}</div>
            <el-input
              v-model="prompts[activeDataType]"
              type="textarea"
              :rows="4"
              :placeholder="$t('views.business.zammad.promptPlaceholder')"
            />
          </div>
          <el-button type="primary" :loading="creating" @click="handleCreateTask">
            {{ $t('views.business.zammad.createTask') }}
          </el-button>
        </div>

        <div class="flex-between align-center mb-16">
          <el-radio-group v-model="listView" @change="onListViewChange">
            <el-radio-button value="data">
              {{ $t('views.business.zammad.dataList') }}
            </el-radio-button>
            <el-radio-button value="task">
              {{ $t('views.business.zammad.taskList') }}
            </el-radio-button>
          </el-radio-group>
        </div>

        <!-- 数据列表 -->
        <div v-if="listView === 'data'" v-loading="dataLoading">
          <template v-if="activeDataType !== 'combined_level'">
            <div class="flex-between align-center mb-8">
              <span>{{ $t('views.business.zammad.currentData') }}</span>
              <span class="color-secondary">
                {{ $t('views.business.zammad.totalCount', { total: singleData.total || 0 }) }}
              </span>
            </div>
            <DataTable :data-type="activeDataType" :page="singleData" />
            <div class="flex-end mt-8">
              <el-pagination
                v-model:current-page="singlePageNo"
                :page-size="singlePageSize"
                :total="singleData.total || 0"
                layout="prev, pager, next"
                @current-change="loadData"
              />
            </div>
          </template>

          <template v-else>
            <div class="flex-between align-center mb-8">
              <span>{{ $t('views.business.zammad.currentDataCombined') }}</span>
              <span class="color-secondary">
                Ticket {{ combinedData.ticket?.total || 0 }} / Message
                {{ combinedData.message?.total || 0 }} / Agent {{ combinedData.agent?.total || 0 }}
              </span>
            </div>
            <div v-for="dim in COMBINED_DIMENSION_LIST" :key="dim.dataType" class="dim-block mb-16">
              <h5 class="mb-8">{{ $t(dim.label) }}</h5>
              <DataTable :data-type="dim.dataType" :page="combinedData[dim.key]" />
              <div class="flex-end mt-8">
                <el-pagination
                  v-model:current-page="combinedPage[dim.pageNoKey]"
                  :page-size="combinedPage[dim.pageSizeKey]"
                  :total="combinedData[dim.key]?.total || 0"
                  layout="prev, pager, next"
                  @current-change="loadData"
                />
              </div>
            </div>
          </template>
        </div>

        <!-- 任务记录 -->
        <div v-else>
          <div class="flex-between align-center mb-8">
            <div class="flex align-center">
              <span class="mr-8 color-secondary">{{ $t('views.business.zammad.taskStatus') }}</span>
              <el-select v-model="taskStatus" style="width: 140px" @change="onTaskStatusChange">
                <el-option
                  v-for="item in TASK_STATUS_LIST"
                  :key="item.value"
                  :label="$t(item.label)"
                  :value="item.value"
                />
              </el-select>
            </div>
            <span class="color-secondary">
              {{ $t('views.business.zammad.totalCount', { total: taskTotal }) }}
            </span>
          </div>
          <el-table v-loading="taskLoading" :data="taskRows" :empty-text="$t('common.noData')">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="filterJson" :label="$t('views.business.zammad.filterJson')" min-width="200" />
            <el-table-column :label="$t('views.business.zammad.prompt')" min-width="200">
              <template #default="{ row }">
                <span :title="row.promptText || '-'">{{ previewText(row.promptText) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="modelName" :label="$t('views.business.zammad.model')" width="120" />
            <el-table-column :label="$t('views.business.zammad.dataType')" width="120">
              <template #default="{ row }">{{ dataTypeLabel(row.dataType) }}</template>
            </el-table-column>
            <el-table-column :label="$t('views.business.zammad.analysisTime')" width="170">
              <template #default="{ row }">
                {{ datetimeFormat(row.analysisTime || row.createTime) }}
              </template>
            </el-table-column>
            <el-table-column :label="$t('views.business.zammad.status')" width="100">
              <template #default="{ row }">
                <el-tag :type="taskStatusTagType(row.status)">{{ taskStatusLabel(row) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="failReason" :label="$t('views.business.zammad.failReason')" min-width="160" />
            <el-table-column :label="$t('common.operation')" width="220" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openTaskDetail(row)">
                  {{ $t('views.business.zammad.detail') }}
                </el-button>
                <el-button v-if="row.hasResult" link type="primary" @click="openResult(row)">
                  {{ $t('views.business.zammad.viewResult') }}
                </el-button>
                <el-button v-if="row.status === 3" link type="danger" @click="openRetry(row)">
                  {{ $t('views.business.zammad.retry') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="flex-end mt-8">
            <el-pagination
              v-model:current-page="taskPageNo"
              :page-size="taskPageSize"
              :total="taskTotal"
              layout="prev, pager, next"
              @current-change="loadTasks"
            />
          </div>
        </div>
      </el-card>

      <!-- 数据明细 -->
      <el-dialog
        v-model="detailVisible"
        :title="$t('views.business.zammad.detailTitle', { id: detailTaskId })"
        width="1100px"
        append-to-body
      >
        <div v-loading="detailLoading" class="detail-body">
          <template v-if="detailDataType !== 'combined_level'">
            <DataTable :data-type="detailDataType" :page="detailData" />
            <div class="flex-end mt-8">
              <el-pagination
                v-model:current-page="detailPageNo"
                :page-size="detailPageSize"
                :total="detailData.total || 0"
                layout="prev, pager, next"
                @current-change="loadTaskDetailData"
              />
            </div>
          </template>
          <template v-else>
            <div v-for="dim in COMBINED_DIMENSION_LIST" :key="dim.dataType" class="dim-block mb-16">
              <h5 class="mb-8">{{ $t(dim.label) }}</h5>
              <DataTable :data-type="dim.dataType" :page="detailData[dim.key]" />
            </div>
          </template>
        </div>
      </el-dialog>

      <!-- 失败重试 -->
      <el-dialog
        v-model="retryVisible"
        :title="$t('views.business.zammad.retryTitle')"
        width="760px"
        append-to-body
        destroy-on-close
      >
        <div class="mb-16">
          <div class="mb-8 color-secondary">{{ $t('views.business.zammad.prompt') }}</div>
          <el-input
            v-model="retryForm.promptText"
            type="textarea"
            :rows="12"
            :placeholder="$t('views.business.zammad.retryPromptPlaceholder')"
          />
        </div>
        <div>
          <div class="mb-8 color-secondary">{{ $t('views.business.zammad.sampleSize') }}</div>
          <el-input v-model="retryForm.sampleSize" type="number" :placeholder="'1000'" />
        </div>
        <template #footer>
          <el-button @click="retryVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="retrying" @click="submitRetry">
            {{ $t('views.business.zammad.retryConfirm') }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { t } from '@/locales'
import { MsgError, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import businessApi from '@/api/business/business'
import zammadApi from '@/api/business/zammad'
import DataTable from './component/DataTable.vue'
import type {
  ZammadAgentRow,
  ZammadCombinedData,
  ZammadDataType,
  ZammadMessageRow,
  ZammadPageData,
  ZammadTaskItem,
  ZammadTicketRow,
} from '@/api/type/business'

defineOptions({ name: 'BusinessZammad' })

const REGION_STORAGE_KEY = 'business_zammad_region'

const DATA_TYPE_LIST: { label: string; value: ZammadDataType }[] = [
  { label: 'views.business.zammad.tabTicket', value: 'ticket_level' },
  { label: 'views.business.zammad.tabMessage', value: 'message_level' },
  { label: 'views.business.zammad.tabAgent', value: 'agent_level' },
  { label: 'views.business.zammad.tabCombined', value: 'combined_level' },
]

const COMBINED_DIMENSION_LIST = [
  {
    dataType: 'ticket_level' as ZammadDataType,
    key: 'ticket' as const,
    label: 'views.business.zammad.tabTicket',
    pageNoKey: 'ticketNo' as const,
    pageSizeKey: 'ticketSize' as const,
  },
  {
    dataType: 'message_level' as ZammadDataType,
    key: 'message' as const,
    label: 'views.business.zammad.tabMessage',
    pageNoKey: 'messageNo' as const,
    pageSizeKey: 'messageSize' as const,
  },
  {
    dataType: 'agent_level' as ZammadDataType,
    key: 'agent' as const,
    label: 'views.business.zammad.tabAgent',
    pageNoKey: 'agentNo' as const,
    pageSizeKey: 'agentSize' as const,
  },
]

const TASK_STATUS_LIST = [
  { label: 'views.business.zammad.statusAll', value: -1 },
  { label: 'views.business.zammad.statusPending', value: 0 },
  { label: 'views.business.zammad.statusRunning', value: 1 },
  { label: 'views.business.zammad.statusFinished', value: 2 },
  { label: 'views.business.zammad.statusFailed', value: 3 },
]

const STATUS_TEXT_KEY: Record<number, string> = {
  0: 'views.business.zammad.statusPending',
  1: 'views.business.zammad.statusRunning',
  2: 'views.business.zammad.statusFinished',
  3: 'views.business.zammad.statusFailed',
}

const STATUS_TAG_TYPE: Record<number, 'primary' | 'success' | 'info' | 'warning' | 'danger'> = {
  0: 'info',
  1: 'primary',
  2: 'success',
  3: 'danger',
}

const router = useRouter()

const regionOptions = ref<string[]>([])
const region = ref('')
const activeDataType = ref<ZammadDataType>('ticket_level')
const listView = ref<'data' | 'task'>('data')

const filter = reactive({ createdAtStart: '', createdAtEnd: '' })
const prompts = reactive<Record<string, string>>({
  ticket_level: t('views.business.zammad.defaultPromptTicket'),
  message_level: t('views.business.zammad.defaultPromptMessage'),
  agent_level: t('views.business.zammad.defaultPromptAgent'),
  combined_level: t('views.business.zammad.defaultPromptCombined'),
})

const dataLoading = ref(false)
const creating = ref(false)
const singleData = ref<ZammadPageData<ZammadTicketRow | ZammadMessageRow | ZammadAgentRow>>({})
const singlePageNo = ref(1)
const singlePageSize = ref(10)
const combinedData = reactive<{
  ticket: ZammadPageData<ZammadTicketRow>
  message: ZammadPageData<ZammadMessageRow>
  agent: ZammadPageData<ZammadAgentRow>
}>({ ticket: {}, message: {}, agent: {} })
const combinedPage = reactive({
  ticketNo: 1,
  ticketSize: 10,
  messageNo: 1,
  messageSize: 10,
  agentNo: 1,
  agentSize: 10,
})

const taskLoading = ref(false)
const taskRows = ref<ZammadTaskItem[]>([])
const taskTotal = ref(0)
const taskPageNo = ref(1)
const taskPageSize = ref(10)
const taskStatus = ref(-1)

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailTaskId = ref<number | null>(null)
const detailDataType = ref<ZammadDataType>('ticket_level')
const detailPageNo = ref(1)
const detailPageSize = ref(20)
const detailData = reactive<{
  total?: number
  records?: (ZammadTicketRow | ZammadMessageRow | ZammadAgentRow)[]
  ticket?: ZammadPageData<ZammadTicketRow>
  message?: ZammadPageData<ZammadMessageRow>
  agent?: ZammadPageData<ZammadAgentRow>
}>({})

const retryVisible = ref(false)
const retrying = ref(false)
const retryTaskId = ref<number | null>(null)
const retryForm = reactive({ promptText: '', sampleSize: '1000' })

const previewText = (text?: string, maxLength = 60) => {
  const value = (text || '').trim()
  if (!value) return '-'
  return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value
}

const dataTypeLabel = (dataType?: string) => {
  const item = DATA_TYPE_LIST.find((row) => row.value === dataType)
  return item ? t(item.label) : dataType || '-'
}

const taskStatusLabel = (row: ZammadTaskItem) => {
  const key = row.status === undefined || row.status === null ? undefined : STATUS_TEXT_KEY[row.status]
  if (key) return t(key)
  return row.statusText || ''
}

const taskStatusTagType = (status?: number) => {
  if (status === undefined || status === null) return 'info'
  return STATUS_TAG_TYPE[status] || 'info'
}

const buildQueryPayload = () => {
  if (activeDataType.value === 'combined_level') {
    return {
      data_type: activeDataType.value,
      region: region.value,
      created_at_start: filter.createdAtStart,
      created_at_end: filter.createdAtEnd,
      ticket_page_no: combinedPage.ticketNo,
      ticket_page_size: combinedPage.ticketSize,
      message_page_no: combinedPage.messageNo,
      message_page_size: combinedPage.messageSize,
      agent_page_no: combinedPage.agentNo,
      agent_page_size: combinedPage.agentSize,
    }
  }
  return {
    data_type: activeDataType.value,
    region: region.value,
    created_at_start: filter.createdAtStart,
    created_at_end: filter.createdAtEnd,
    page_no: singlePageNo.value,
    page_size: singlePageSize.value,
  }
}

const fillCombinedData = (data: ZammadCombinedData) => {
  combinedData.ticket = data?.ticketPage || {}
  combinedData.message = data?.messagePage || {}
  combinedData.agent = data?.agentPage || {}
}

const loadData = () => {
  return zammadApi
    .queryData(buildQueryPayload(), dataLoading)
    .then((res: any) => {
      const data = res?.data || {}
      if (activeDataType.value === 'combined_level') {
        fillCombinedData(data)
        return
      }
      singleData.value = data
    })
    .catch(() => {
      singleData.value = {}
      combinedData.ticket = {}
      combinedData.message = {}
      combinedData.agent = {}
    })
}

const loadTasks = () => {
  return zammadApi
    .getTaskList(
      taskPageNo.value,
      taskPageSize.value,
      {
        region: region.value,
        data_type: activeDataType.value,
        status: taskStatus.value === -1 ? undefined : taskStatus.value,
      },
      taskLoading,
    )
    .then((res: any) => {
      taskRows.value = Array.isArray(res?.data?.records) ? res.data.records : []
      taskTotal.value = res?.data?.total || 0
    })
    .catch(() => {
      taskRows.value = []
      taskTotal.value = 0
    })
}

const handleRefresh = () => {
  return listView.value === 'task' ? loadTasks() : loadData()
}

const handleDataSearch = () => {
  singlePageNo.value = 1
  combinedPage.ticketNo = 1
  combinedPage.messageNo = 1
  combinedPage.agentNo = 1
  return loadData()
}

const handleCreateTask = () => {
  const promptText = (prompts[activeDataType.value] || '').trim()
  if (!promptText) {
    MsgError(t('views.business.zammad.promptRequired'))
    return
  }
  creating.value = true
  zammadApi
    .createTask({
      data_type: activeDataType.value,
      region: region.value,
      created_at_start: filter.createdAtStart,
      created_at_end: filter.createdAtEnd,
      prompt_text: promptText,
    })
    .then(() => {
      MsgSuccess(t('views.business.zammad.createSuccess'))
      listView.value = 'task'
      taskPageNo.value = 1
      return loadTasks()
    })
    .finally(() => {
      creating.value = false
    })
}

const openTaskDetail = (row: ZammadTaskItem) => {
  detailTaskId.value = row.id
  detailDataType.value = (row.dataType as ZammadDataType) || activeDataType.value
  detailPageNo.value = 1
  detailVisible.value = true
  loadTaskDetailData()
}

const fillDetailData = (data: any) => {
  Object.keys(detailData).forEach((key) => {
    delete (detailData as any)[key]
  })
  if (detailDataType.value === 'combined_level') {
    detailData.ticket = data?.ticketPage || {}
    detailData.message = data?.messagePage || {}
    detailData.agent = data?.agentPage || {}
    return
  }
  Object.assign(detailData, data || {})
}

const loadTaskDetailData = () => {
  if (detailTaskId.value === null) return
  return zammadApi
    .getTaskData(
      detailTaskId.value,
      detailPageNo.value,
      detailPageSize.value,
      { region: region.value },
      detailLoading,
    )
    .then((res: any) => {
      fillDetailData(res?.data)
    })
    .catch(() => {
      fillDetailData({})
    })
}

const openResult = (row: ZammadTaskItem) => {
  router.push({
    name: 'businessZammadResult',
    params: { taskId: row.id },
    query: { region: region.value },
  })
}

const openRetry = (row: ZammadTaskItem) => {
  retryTaskId.value = row.id
  retryForm.promptText = row.promptText || prompts[activeDataType.value] || ''
  retryForm.sampleSize = '1000'
  retryVisible.value = true
}

const submitRetry = () => {
  const promptText = (retryForm.promptText || '').trim()
  if (!promptText) {
    MsgError(t('views.business.zammad.promptRequired'))
    return
  }
  const sampleSizeText = (retryForm.sampleSize || '').toString().trim()
  let sampleSize: number | undefined
  if (sampleSizeText) {
    const parsed = Number(sampleSizeText)
    if (!Number.isInteger(parsed) || parsed < 1 || parsed > 1000) {
      MsgError(t('views.business.zammad.sampleSizeInvalid'))
      return
    }
    sampleSize = parsed
  }
  if (retryTaskId.value === null) return
  retrying.value = true
  zammadApi
    .retryTask(retryTaskId.value, {
      region: region.value,
      prompt_text: promptText,
      sample_size: sampleSize,
    })
    .then(() => {
      MsgSuccess(t('views.business.zammad.retrySuccess'))
      retryVisible.value = false
      return loadTasks()
    })
    .finally(() => {
      retrying.value = false
    })
}

const onRegionChange = (value: string) => {
  localStorage.setItem(REGION_STORAGE_KEY, value)
  singlePageNo.value = 1
  taskPageNo.value = 1
  combinedPage.ticketNo = 1
  combinedPage.messageNo = 1
  combinedPage.agentNo = 1
  return handleRefresh()
}

const onDataTypeChange = () => {
  taskPageNo.value = 1
  singlePageNo.value = 1
  return handleRefresh()
}

const onListViewChange = () => {
  return handleRefresh()
}

const onTaskStatusChange = () => {
  taskPageNo.value = 1
  return loadTasks()
}

onMounted(() => {
  businessApi
    .getRegions()
    .then((res: any) => {
      const regions: string[] = Array.isArray(res?.data?.regions) ? res.data.regions : []
      regionOptions.value = regions
      const cached = localStorage.getItem(REGION_STORAGE_KEY)
      region.value =
        cached && regions.includes(cached) ? cached : res?.data?.default_region || regions[0] || ''
    })
    .catch(() => {
      regionOptions.value = []
    })
    .finally(() => {
      loadData()
    })
})
</script>
<style lang="scss" scoped>
.business-zammad {
  .filter-panel {
    padding: 16px;
    background: var(--el-fill-color-lighter);
    border-radius: 6px;
  }

  .dim-block h5 {
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .detail-body {
    min-height: 160px;
  }
}
</style>
