<template>
  <el-scrollbar>
    <div class="business-zoom p-16">
      <el-card style="--el-card-padding: 24px">
        <div class="flex-between align-center mb-16">
          <h4>{{ $t('views.business.zoom.title') }}</h4>
          <el-button :loading="loading" @click="loadReportList">
            <AppIcon iconName="app-refresh" class="mr-4" />
            {{ $t('common.refresh') }}
          </el-button>
        </div>
        <el-table
          :data="reportList"
          v-loading="loading"
          :empty-text="$t('common.noData')"
          style="width: 100%"
        >
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column
            v-for="index in PROMPT_INDEX_LIST"
            :key="index"
            :label="$t('views.business.zoom.promptStatus', { index: index })"
            min-width="120"
          >
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(getPromptStatus(row, index))">
                {{ getStatusText(getPromptStatus(row, index)) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            :label="$t('views.business.zoom.downloadStatus')"
            min-width="150"
          >
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.apptDataStatus)">
                {{ getStatusText(row.apptDataStatus) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="$t('common.createTime')" width="180">
            <template #default="{ row }">{{ datetimeFormat(row.createTime) }}</template>
          </el-table-column>
          <el-table-column :label="$t('common.operation')" width="170" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDetail(row)">
                {{ $t('views.business.zoom.detail') }}
              </el-button>
              <el-button
                link
                type="danger"
                :loading="resettingId === row.id"
                @click="resetReport(row)"
              >
                {{ $t('views.business.zoom.reset') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-dialog
        v-model="detailVisible"
        :title="t('views.business.zoom.detailTitle', { id: detailReport?.id })"
        width="900px"
        append-to-body
      >
        <div v-for="index in PROMPT_INDEX_LIST" :key="index" class="detail-item">
          <div class="detail-label mb-8">
            {{ $t('views.business.zoom.promptOutput', { index: index }) }}
          </div>
          <pre class="detail-value">{{ getPromptOutput(detailReport, index) || '-' }}</pre>
        </div>
      </el-dialog>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { t } from '@/locales'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import zoomApi from '@/api/business/zoom'
import type { ZoomReportData } from '@/api/type/business'

defineOptions({ name: 'BusinessZoom' })

const PROMPT_INDEX_LIST = [1, 2, 3, 4, 5]

// 业务服务状态码: 0 初始 1 生成中 2 生成成功 3 生成失败
const STATUS_TEXT_KEY: Record<number, string> = {
  0: 'views.business.zoom.status.initial',
  1: 'views.business.zoom.status.generating',
  2: 'views.business.zoom.status.success',
  3: 'views.business.zoom.status.failed',
}

const STATUS_TAG_TYPE: Record<number, 'primary' | 'success' | 'info' | 'danger'> = {
  0: 'info',
  1: 'primary',
  2: 'success',
  3: 'danger',
}

const loading = ref(false)
const resettingId = ref<number | null>(null)
const reportList = ref<ZoomReportData[]>([])
const detailVisible = ref(false)
const detailReport = ref<ZoomReportData | null>(null)

const getStatusText = (status: number | undefined | null) => {
  const key = status === undefined || status === null ? undefined : STATUS_TEXT_KEY[status]
  return key ? t(key) : t('views.business.zoom.status.unknown', { status: status ?? '-' })
}

const getStatusTagType = (status: number | undefined | null) => {
  if (status === undefined || status === null) return 'info'
  return STATUS_TAG_TYPE[status] || 'info'
}

// 提示词1~5的状态与输出在接口中以 promptNOutputStatus / promptNOutput 命名，这里统一转换取值
const getPromptStatus = (row: ZoomReportData, index: number) => {
  return (row as unknown as Record<string, number | undefined>)[`prompt${index}OutputStatus`]
}

const getPromptOutput = (row: ZoomReportData | null, index: number) => {
  if (!row) return ''
  return (row as unknown as Record<string, string | null | undefined>)[`prompt${index}Output`]
}

const loadReportList = () => {
  return zoomApi
    .getZoomReportList(loading)
    .then((res: any) => {
      const list: ZoomReportData[] = Array.isArray(res?.data) ? res.data : []
      // 业务服务未提供排序，按创建时间倒序展示，最新的报告在最前面
      reportList.value = list.sort((a, b) => {
        const timeA = a?.createTime ? new Date(a.createTime).getTime() : 0
        const timeB = b?.createTime ? new Date(b.createTime).getTime() : 0
        return (Number.isNaN(timeB) ? 0 : timeB) - (Number.isNaN(timeA) ? 0 : timeA)
      })
    })
    .catch(() => {
      // 请求异常已由拦截器统一提示，这里只保证不展示过期数据
      reportList.value = []
    })
}

const openDetail = (row: ZoomReportData) => {
  detailReport.value = row
  detailVisible.value = true
}

const resetReport = (row: ZoomReportData) => {
  MsgConfirm(
    t('views.business.zoom.resetConfirmTitle'),
    t('views.business.zoom.resetConfirmMessage', { id: row.id }),
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      resettingId.value = row.id
      return zoomApi
        .resetZoomReport(row.id)
        .then(() => {
          MsgSuccess(t('views.business.zoom.resetSuccess'))
          return loadReportList()
        })
        .finally(() => {
          resettingId.value = null
        })
    })
    .catch(() => {})
}

onMounted(() => {
  loadReportList()
})
</script>
<style lang="scss" scoped>
.business-zoom {
  .detail-item {
    margin-bottom: 16px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .detail-label {
    font-size: 13px;
    color: var(--el-text-color-regular);
  }

  .detail-value {
    margin: 0;
    padding: 10px 12px;
    max-height: 320px;
    overflow: auto;
    font-size: 13px;
    line-height: 1.6;
    color: var(--el-text-color-primary);
    background: var(--el-fill-color-lighter);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 6px;
    white-space: pre-wrap;
    word-break: break-word;
  }
}
</style>
