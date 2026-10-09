<template>
  <el-scrollbar>
    <div class="business-prompt p-16">
      <el-card style="--el-card-padding: 24px">
        <div class="flex-between align-center mb-16">
          <h4>{{ $t('views.business.prompt.title') }}</h4>
          <div class="flex align-center">
            <span class="mr-8 color-secondary">{{ $t('views.business.prompt.region') }}</span>
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
            <el-button :loading="loading" @click="loadAssistantTypes">
              <AppIcon iconName="app-refresh" class="mr-4" />
              {{ $t('common.refresh') }}
            </el-button>
          </div>
        </div>

        <div class="prompt-layout flex">
          <div class="prompt-list-section">
            <el-empty
              v-if="!loading && assistantTypes.length === 0"
              :description="$t('common.noData')"
            />
            <el-collapse v-else v-model="expandedType" accordion @change="onTypeChange">
              <el-collapse-item
                v-for="assistantType in assistantTypes"
                :key="assistantType.code"
                :name="assistantType.code"
              >
                <template #title>
                  <span class="accordion-title">
                    {{ assistantType.description || assistantType.code }}
                  </span>
                </template>
                <div v-loading="nodesLoading">
                  <el-empty
                    v-if="!nodesLoading && nodes.length === 0"
                    :description="$t('views.business.prompt.noNode')"
                    :image-size="60"
                  />
                  <div
                    v-for="node in nodes"
                    :key="node.code"
                    class="node-item flex-between align-center"
                  >
                    <div class="node-content">
                      <div class="node-name">{{ node.description || node.code }}</div>
                      <div v-if="node.validRoles && node.validRoles.length" class="node-roles mt-4">
                        <el-tag
                          v-for="role in node.validRoles"
                          :key="role.code"
                          class="mr-8 role-tag"
                          @click="openPreview(assistantType.code, node, role.code)"
                        >
                          {{ roleLabel(role) }}
                        </el-tag>
                      </div>
                    </div>
                    <el-button link type="primary" @click="openPreview(assistantType.code, node, null)">
                      {{ $t('views.business.prompt.preview') }}
                    </el-button>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <div v-if="previewVisible" class="prompt-preview-section">
            <div class="flex-between align-center mb-16">
              <span class="preview-title ellipsis" :title="previewTitle">{{ previewTitle }}</span>
              <el-button link @click="closePreview">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <el-tabs v-model="activeRole" @tab-change="loadHistory">
              <el-tab-pane
                v-for="role in currentRoles"
                :key="role.code"
                :label="roleLabel(role)"
                :name="role.code"
              />
            </el-tabs>
            <el-button class="w-full mb-16" @click="openCreate">
              <AppIcon iconName="app-add-outlined" class="mr-4" />
              {{ $t('views.business.prompt.addPrompt') }}
            </el-button>
            <div v-loading="historyLoading" class="history-list">
              <el-empty
                v-if="!historyLoading && historyList.length === 0"
                :description="$t('common.noData')"
                :image-size="60"
              />
              <div
                v-for="item in historyList"
                :key="item.id"
                class="history-item"
                @click="openDetail(item)"
              >
                <div class="flex-between align-center">
                  <span class="history-version">v{{ item.version || '1.0.0' }}</span>
                  <el-tag size="small" :type="statusTagType(item.status)">
                    {{ statusLabel(item) }}
                  </el-tag>
                </div>
                <div class="flex-between align-center mt-4">
                  <span class="history-meta ellipsis">
                    <span v-if="item.region">{{ item.region }}</span>
                    <span v-if="item.region && item.summary"> · </span>
                    <span v-if="item.summary">{{ item.summary }}</span>
                  </span>
                  <el-button link type="danger" @click.stop="deletePrompt(item)">
                    {{ $t('common.delete') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <el-dialog
        v-model="createVisible"
        :title="$t('views.business.prompt.addPrompt')"
        width="640px"
        append-to-body
        destroy-on-close
      >
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item v-if="currentEnvVars.length" :label="$t('views.business.prompt.envVars')">
            <div class="env-vars">{{ currentEnvVars.join(', ') }}</div>
          </el-form-item>
          <el-form-item :label="$t('views.business.prompt.version')" prop="version">
            <el-input
              v-model="form.version"
              :placeholder="$t('views.business.prompt.versionPlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="$t('views.business.prompt.content')" prop="content">
            <el-input
              v-model="form.content"
              type="textarea"
              :rows="10"
              :placeholder="$t('views.business.prompt.contentPlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="$t('views.business.prompt.summary')" prop="summary">
            <el-input
              v-model="form.summary"
              maxlength="50"
              show-word-limit
              :placeholder="$t('views.business.prompt.summaryPlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="$t('views.business.prompt.identityId')" prop="identity_id">
            <el-input
              v-model="form.identity_id"
              :placeholder="$t('views.business.prompt.identityIdPlaceholder')"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="createVisible = false">{{ $t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="creating" @click="createPrompt">
            {{ $t('common.save') }}
          </el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="detailVisible" :title="detailTitle" width="760px" append-to-body>
        <div class="flex align-center mb-16">
          <el-tag v-if="detailData?.summary" class="mr-8">{{ detailData.summary }}</el-tag>
          <el-tag v-if="detailData?.region" class="mr-8" type="info">{{ detailData.region }}</el-tag>
          <el-tag v-if="detailData?.identityId" class="mr-8" type="info">
            {{ detailData.identityId }}
          </el-tag>
          <el-tag type="info">{{ statusLabel(detailData) }}</el-tag>
        </div>
        <pre class="detail-value">{{ detailData?.content }}</pre>
        <template #footer>
          <el-button @click="copyToCreate">
            {{ $t('views.business.prompt.copyAndCreate') }}
          </el-button>
        </template>
      </el-dialog>
    </div>
  </el-scrollbar>
</template>
<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import { t } from '@/locales'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import promptApi from '@/api/business/prompt'
import type {
  PromptAssistantType,
  PromptHistoryItem,
  PromptNode,
  PromptRole,
} from '@/api/type/business'

defineOptions({ name: 'BusinessPrompt' })

const REGION_STORAGE_KEY = 'business_prompt_region'

// 提示词状态: 0 系统默认 1 最新版本 2 过期版本 3 特定版本
const STATUS_TEXT_KEY: Record<number, string> = {
  0: 'systemDefault',
  1: 'latest',
  2: 'expired',
  3: 'specific',
}

const STATUS_TAG_TYPE: Record<number, 'primary' | 'success' | 'info' | 'warning'> = {
  0: 'info',
  1: 'success',
  2: 'warning',
  3: 'primary',
}

const loading = ref(false)
const nodesLoading = ref(false)
const historyLoading = ref(false)
const creating = ref(false)
const regionOptions = ref<string[]>([])
const region = ref('')
const assistantTypes = ref<PromptAssistantType[]>([])
const expandedType = ref<string>('')
const nodes = ref<PromptNode[]>([])
const previewTypeCode = ref('')
const previewNode = ref<PromptNode | null>(null)
const previewVisible = ref(false)
const currentRoles = ref<PromptRole[]>([])
const currentEnvVars = ref<string[]>([])
const activeRole = ref<number>(1)
const historyList = ref<PromptHistoryItem[]>([])
const createVisible = ref(false)
const detailVisible = ref(false)
const detailData = ref<PromptHistoryItem | null>(null)
const formRef = ref<FormInstance>()

const form = ref({
  version: '',
  content: '',
  summary: '',
  identity_id: '',
})

const rules = {
  version: [
    { required: true, message: t('views.business.prompt.versionRequired'), trigger: 'blur' },
    {
      pattern: /^\d+\.\d+\.\d+$/,
      message: t('views.business.prompt.versionInvalid'),
      trigger: 'blur',
    },
  ],
  content: [
    { required: true, message: t('views.business.prompt.contentRequired'), trigger: 'blur' },
  ],
  summary: [
    { required: true, message: t('views.business.prompt.summaryRequired'), trigger: 'blur' },
  ],
}

const previewTitle = computed(() => {
  const role = activeRole.value
  return `${previewTypeCode.value} / ${previewNode.value?.code || ''} / ${roleLabel({
    code: role,
  })}`
})

const detailTitle = computed(
  () =>
    `${roleLabel({ code: activeRole.value })} - v${detailData.value?.version || ''}`,
)

const roleLabel = (role: PromptRole) => {
  if (role?.code === 0) return t('views.business.prompt.systemPrompt')
  if (role?.code === 1) return t('views.business.prompt.userPrompt')
  return role?.description || String(role?.code ?? '')
}

const statusLabel = (item: PromptHistoryItem | null) => {
  const key = item?.status === undefined || item?.status === null ? undefined : STATUS_TEXT_KEY[item.status]
  if (key) return t(`views.business.prompt.status.${key}`)
  return item?.statusDesc || ''
}

const statusTagType = (status?: number) => {
  if (status === undefined || status === null) return 'info'
  return STATUS_TAG_TYPE[status] || 'info'
}

const loadAssistantTypes = () => {
  return promptApi
    .getAssistantTypes({ region: region.value }, loading)
    .then((res: any) => {
      assistantTypes.value = Array.isArray(res?.data) ? res.data : []
    })
    .catch(() => {
      assistantTypes.value = []
    })
}

const loadNodes = (assistantType: string) => {
  return promptApi
    .getNodes({ assistant_type: assistantType, region: region.value }, nodesLoading)
    .then((res: any) => {
      nodes.value = Array.isArray(res?.data) ? res.data : []
    })
    .catch(() => {
      nodes.value = []
    })
}

const onRegionChange = (value: string) => {
  localStorage.setItem(REGION_STORAGE_KEY, value)
  expandedType.value = ''
  nodes.value = []
  closePreview()
  loadAssistantTypes()
}

const onTypeChange = (name: any) => {
  nodes.value = []
  closePreview()
  if (!name) return
  loadNodes(String(name))
}

const openPreview = (assistantType: string, node: PromptNode, roleCode: number | null) => {
  previewTypeCode.value = assistantType
  previewNode.value = node
  previewVisible.value = true
  const roles = node.validRoles && node.validRoles.length > 0
    ? node.validRoles
    : [{ code: 1, description: 'user' }]
  currentRoles.value = roles
  activeRole.value = roleCode === null || roleCode === undefined ? roles[0].code : roleCode
  syncEnvVars()
  loadHistory()
}

const closePreview = () => {
  previewVisible.value = false
  previewNode.value = null
  historyList.value = []
}

const syncEnvVars = () => {
  const variables = previewNode.value?.environmentVariables || {}
  currentEnvVars.value = variables[String(activeRole.value)] || []
}

const loadHistory = () => {
  if (!previewNode.value) return
  syncEnvVars()
  return promptApi
    .getHistory(
      {
        assistant_type: previewTypeCode.value,
        node_name: previewNode.value.code,
        prompt_type: activeRole.value,
        region: region.value,
      },
      historyLoading,
    )
    .then((res: any) => {
      historyList.value = Array.isArray(res?.data) ? res.data : []
    })
    .catch(() => {
      historyList.value = []
    })
}

const openCreate = () => {
  form.value = { version: '', content: '', summary: '', identity_id: '' }
  createVisible.value = true
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const copyToCreate = () => {
  form.value = {
    version: '',
    content: detailData.value?.content || '',
    summary: detailData.value?.summary || '',
    identity_id: detailData.value?.identityId || '',
  }
  detailVisible.value = false
  createVisible.value = true
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const createPrompt = () => {
  formRef.value?.validate((valid: boolean) => {
    if (!valid || !previewNode.value) return
    creating.value = true
    promptApi
      .createPrompt({
        assistant_type: previewTypeCode.value,
        node_name: previewNode.value.code,
        prompt_type: activeRole.value,
        region: region.value,
        identity_id: form.value.identity_id || null,
        version: form.value.version,
        content: form.value.content,
        summary: form.value.summary,
      })
      .then(() => {
        MsgSuccess(t('views.business.prompt.addSuccess'))
        createVisible.value = false
        return loadHistory()
      })
      .finally(() => {
        creating.value = false
      })
  })
}

const openDetail = (item: PromptHistoryItem) => {
  detailData.value = item
  detailVisible.value = true
}

const deletePrompt = (item: PromptHistoryItem) => {
  MsgConfirm(
    t('views.business.prompt.deleteConfirm'),
    `${previewNode.value?.code || ''} - v${item.version || '1.0.0'}`,
    {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      confirmButtonClass: 'danger',
    },
  )
    .then(() => {
      return promptApi
        .deletePrompt(item.id, { region: region.value })
        .then(() => {
          MsgSuccess(t('common.deleteSuccess'))
          return loadHistory()
        })
    })
    .catch(() => {})
}

onMounted(() => {
  promptApi
    .getRegions()
    .then((res: any) => {
      const regions: string[] = Array.isArray(res?.data?.regions) ? res.data.regions : []
      regionOptions.value = regions
      const cached = localStorage.getItem(REGION_STORAGE_KEY)
      region.value =
        cached && regions.includes(cached) ? cached : res?.data?.default_region || regions[0] || ''
      return loadAssistantTypes()
    })
    .catch(() => {
      regionOptions.value = []
    })
})
</script>
<style lang="scss" scoped>
.business-prompt {
  .prompt-layout {
    gap: 16px;
    min-height: 400px;
  }

  .prompt-list-section {
    flex: 1;
    min-width: 0;
  }

  .prompt-preview-section {
    width: 400px;
    flex-shrink: 0;
    padding-left: 16px;
    border-left: 1px solid var(--el-border-color-lighter);
  }

  .accordion-title {
    font-size: 14px;
    font-weight: 500;
  }

  .node-item {
    padding: 8px 0;

    & + .node-item {
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }

  .node-content {
    flex: 1;
    min-width: 0;
  }

  .node-name {
    font-size: 14px;
    color: var(--el-text-color-primary);
  }

  .node-roles {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 0;
  }

  .role-tag {
    cursor: pointer;
  }

  .preview-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
  }

  .history-list {
    min-height: 120px;
  }

  .history-item {
    padding: 10px 12px;
    margin-bottom: 8px;
    background: var(--el-fill-color-lighter);
    border-radius: 6px;
    cursor: pointer;

    &:hover {
      background: var(--el-fill-color-light);
    }
  }

  .history-version {
    font-size: 13px;
    color: var(--el-color-primary);
  }

  .history-meta {
    flex: 1;
    min-width: 0;
    margin-right: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .env-vars {
    width: 100%;
    padding: 6px 10px;
    font-size: 12px;
    line-height: 1.6;
    color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
    border: 1px solid var(--el-color-primary-light-7);
    border-radius: 4px;
    word-break: break-word;
  }

  .detail-value {
    margin: 0;
    padding: 12px;
    max-height: 400px;
    overflow: auto;
    font-size: 13px;
    line-height: 1.8;
    color: var(--el-text-color-primary);
    background: var(--el-fill-color-lighter);
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 6px;
    white-space: pre-wrap;
    word-break: break-word;
  }
}
</style>
