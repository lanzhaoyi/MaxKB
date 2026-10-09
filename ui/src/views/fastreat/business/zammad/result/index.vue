<template>
  <el-scrollbar>
    <div class="business-zammad-result p-16">
      <el-card style="--el-card-padding: 24px">
        <div class="flex-between align-center mb-16">
          <div class="flex align-center">
            <el-button class="mr-16" @click="goBack">
              <el-icon class="mr-4"><Back /></el-icon>
              {{ $t('views.business.zammad.resultBack') }}
            </el-button>
            <h4>{{ $t('views.business.zammad.resultTitle', { id: taskId }) }}</h4>
          </div>
          <el-button :loading="loading" @click="loadResult">
            <AppIcon iconName="app-refresh" class="mr-4" />
            {{ $t('common.refresh') }}
          </el-button>
        </div>

        <div v-loading="loading" class="result-body">
          <el-descriptions v-if="result" :column="2" border class="mb-16">
            <el-descriptions-item :label="$t('views.business.zammad.taskId')">
              {{ result.id ?? '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('views.business.zammad.dataType')">
              {{ dataTypeLabel(result.dataType) }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('views.business.zammad.model')">
              {{ result.modelName || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('views.business.zammad.analysisTime')">
              {{ datetimeFormat(result.analysisTime) }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('views.business.zammad.prompt')" :span="2">
              {{ result.promptText || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('views.business.zammad.filterJson')" :span="2">
              {{ result.filterJson || '-' }}
            </el-descriptions-item>
          </el-descriptions>

          <el-empty
            v-if="!loading && !htmlResult"
            :description="$t('views.business.zammad.resultEmpty')"
          />
          <!-- 分析结果为模型生成的 HTML，渲染前统一做白名单净化，避免 XSS -->
          <div v-else class="html-result" v-html="htmlResult"></div>
        </div>
      </el-card>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Back } from '@element-plus/icons-vue'
import sanitizeHtml from 'sanitize-html'
import { t } from '@/locales'
import { datetimeFormat } from '@/utils/time'
import businessApi from '@/api/business/business'
import zammadApi from '@/api/business/zammad'
import type { ZammadTaskResult } from '@/api/type/business'

defineOptions({ name: 'BusinessZammadResult' })

const REGION_STORAGE_KEY = 'business_zammad_region'

const DATA_TYPE_LABEL_KEY: Record<string, string> = {
  ticket_level: 'views.business.zammad.tabTicket',
  message_level: 'views.business.zammad.tabMessage',
  agent_level: 'views.business.zammad.tabAgent',
  combined_level: 'views.business.zammad.tabCombined',
}

const route = useRoute()
const router = useRouter()

const taskId = route.params.taskId as string
const loading = ref(false)
const region = ref('')
const result = ref<ZammadTaskResult | null>(null)

const dataTypeLabel = (dataType?: string) => {
  const key = dataType ? DATA_TYPE_LABEL_KEY[dataType] : undefined
  return key ? t(key) : dataType || '-'
}

const decodeEscapedHtml = (html?: string) => {
  if (typeof html !== 'string' || !html) return ''
  return html
    .replace(/\\r\\n/g, '\n')
    .replace(/\\n/g, '\n')
    .replace(/\\r/g, '\n')
    .replace(/\\t/g, '\t')
}

const htmlResult = computed(() =>
  sanitizeHtml(decodeEscapedHtml(result.value?.htmlResult), {
    allowedTags: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'blockquote', 'pre', 'code',
      'em', 'strong', 'del', 'ul', 'ol', 'li', 'span', 'div', 'section',
      'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption',
      'a', 'img',
    ],
    allowedAttributes: {
      a: ['href', 'name', 'target', 'title'],
      img: ['src', 'alt', 'title'],
      code: ['class'],
      th: ['align', 'colspan', 'rowspan', 'style'],
      td: ['align', 'colspan', 'rowspan', 'style'],
      table: ['style', 'border', 'cellpadding', 'cellspacing'],
      div: ['style'],
      span: ['style'],
      p: ['style'],
      h1: ['style'], h2: ['style'], h3: ['style'], h4: ['style'], h5: ['style'], h6: ['style'],
    },
    allowedSchemes: ['http', 'https', 'mailto'],
  }),
)

const resolveRegion = () => {
  const queryRegion = route.query.region ? String(route.query.region) : ''
  if (queryRegion) return Promise.resolve(queryRegion)
  const cached = localStorage.getItem(REGION_STORAGE_KEY)
  if (cached) return Promise.resolve(cached)
  return businessApi
    .getRegions()
    .then((res: any) => res?.data?.default_region || res?.data?.regions?.[0] || '')
    .catch(() => '')
}

const loadResult = () => {
  if (!region.value) {
    return Promise.resolve()
  }
  return zammadApi
    .getTaskResult(Number(taskId), { region: region.value }, loading)
    .then((res: any) => {
      result.value = res?.data || null
    })
    .catch(() => {
      result.value = null
    })
}

const goBack = () => {
  router.push({ name: 'businessZammad' })
}

onMounted(() => {
  resolveRegion().then((value) => {
    region.value = value
    return loadResult()
  })
})
</script>
<style lang="scss" scoped>
.business-zammad-result {
  .result-body {
    min-height: 200px;
  }

  .html-result {
    font-size: 14px;
    line-height: 1.8;
    color: var(--el-text-color-primary);
    word-break: break-word;

    :deep(table) {
      width: 100%;
      margin-bottom: 16px;
      border-collapse: collapse;
    }

    :deep(th),
    :deep(td) {
      padding: 8px 12px;
      border: 1px solid var(--el-border-color-lighter);
      text-align: left;
    }

    :deep(th) {
      background: var(--el-fill-color-lighter);
      font-weight: 500;
    }

    :deep(img) {
      max-width: 100%;
    }
  }
}
</style>
