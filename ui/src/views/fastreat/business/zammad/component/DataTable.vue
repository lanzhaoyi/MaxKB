<template>
  <el-table :data="records" :empty-text="$t('common.noData')" style="width: 100%">
    <template v-if="dataType === 'ticket_level'">
      <el-table-column prop="ticketId" label="ticket_id" width="100" />
      <el-table-column prop="channel" :label="$t('views.business.zammad.channel')" width="110" />
      <el-table-column prop="userId" label="user_id" width="100" />
      <el-table-column :label="$t('views.business.zammad.createdAt')" width="170">
        <template #default="{ row }">{{ datetimeFormat(row.createdAt) }}</template>
      </el-table-column>
      <el-table-column :label="$t('views.business.zammad.firstResponseAt')" width="170">
        <template #default="{ row }">{{ datetimeFormat(row.firstResponseAt) }}</template>
      </el-table-column>
      <el-table-column :label="$t('views.business.zammad.closedAt')" width="170">
        <template #default="{ row }">{{ datetimeFormat(row.closedAt) }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="$t('views.business.zammad.status')" width="100" />
      <el-table-column prop="groupName" :label="$t('views.business.zammad.group')" min-width="120" />
      <el-table-column prop="priority" :label="$t('views.business.zammad.priority')" width="100" />
      <el-table-column prop="tags" :label="$t('views.business.zammad.tags')" min-width="140" />
    </template>
    <template v-else-if="dataType === 'message_level'">
      <el-table-column prop="messageId" label="message_id" width="110" />
      <el-table-column prop="ticketId" label="ticket_id" width="100" />
      <el-table-column prop="senderType" :label="$t('views.business.zammad.senderType')" width="120" />
      <el-table-column prop="agentId" label="agent_id" width="100" />
      <el-table-column :label="$t('views.business.zammad.createdAt')" width="170">
        <template #default="{ row }">{{ datetimeFormat(row.createdAt) }}</template>
      </el-table-column>
      <el-table-column prop="content" :label="$t('views.business.zammad.content')" min-width="240" />
      <el-table-column :label="$t('views.business.zammad.responseTime')" width="130">
        <template #default="{ row }">{{ formatMinutes(row.responseTime) }}</template>
      </el-table-column>
    </template>
    <template v-else>
      <el-table-column prop="agentId" label="agent_id" width="100" />
      <el-table-column prop="agentName" label="agent_name" min-width="140" />
      <el-table-column prop="team" :label="$t('views.business.zammad.team')" min-width="120" />
      <el-table-column :label="$t('views.business.zammad.activeTime')" width="170">
        <template #default="{ row }">{{ datetimeFormat(row.activeTime) }}</template>
      </el-table-column>
      <el-table-column :label="$t('views.business.zammad.inactiveTime')" width="140">
        <template #default="{ row }">{{ formatHours(row.inactiveTime) }}</template>
      </el-table-column>
      <el-table-column prop="ticketsHandled" :label="$t('views.business.zammad.ticketsHandled')" width="130" />
      <el-table-column prop="status" :label="$t('views.business.zammad.status')" width="100" />
    </template>
  </el-table>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { t } from '@/locales'
import { datetimeFormat } from '@/utils/time'
import type {
  ZammadAgentRow,
  ZammadDataType,
  ZammadMessageRow,
  ZammadPageData,
  ZammadTicketRow,
} from '@/api/type/business'

defineOptions({ name: 'ZammadDataTable' })

const props = defineProps<{
  dataType: ZammadDataType
  page?: ZammadPageData<ZammadTicketRow | ZammadMessageRow | ZammadAgentRow> | null
}>()

const records = computed(() => props.page?.records || [])

const formatMinutes = (val?: number | null) => {
  if (val === null || val === undefined) return '-'
  const num = Number(val)
  return Number.isNaN(num) ? '-' : `${num.toFixed(2)} ${t('views.business.zammad.minuteUnit')}`
}

const formatHours = (val?: number | null) => {
  if (val === null || val === undefined) return '-'
  const num = Number(val)
  return Number.isNaN(num) ? '-' : `${num.toFixed(2)} ${t('views.business.zammad.hourUnit')}`
}
</script>
<style lang="scss" scoped></style>
