interface ZoomReportData {
  id: number
  serverId?: number
  bizId?: string
  bizDt?: string
  modelName?: string
  totalSessionCount?: number
  prompt1Output?: string | null
  prompt1OutputStatus?: number
  prompt2Output?: string | null
  prompt2OutputStatus?: number
  prompt3Output?: string | null
  prompt3OutputStatus?: number
  prompt4Output?: string | null
  prompt4OutputStatus?: number
  prompt5Output?: string | null
  prompt5OutputStatus?: number
  apptDataStatus?: number
  apptSourceData?: string | null
  apptTargetData?: string | null
  createTime?: string
  updateTime?: string
}

interface PromptRegions {
  regions: string[]
  default_region: string
}

interface PromptAssistantType {
  code: string
  description?: string
}

interface PromptRole {
  code: number
  description?: string
}

interface PromptNode {
  code: string
  description?: string
  tag?: string
  validRoles?: PromptRole[]
  environmentVariables?: Record<string, string[]>
}

interface PromptHistoryItem {
  id: number
  assistantType?: string
  nodeName?: string
  promptType?: number
  region?: string
  identityId?: string
  version?: string
  content?: string
  summary?: string
  isActive?: number
  status?: number
  statusDesc?: string
  createTime?: string
  updateTime?: string
}

interface PromptCreateData {
  assistant_type: string
  node_name: string
  prompt_type: number
  region: string
  identity_id?: string
  version: string
  content: string
  summary: string
}

export type {
  ZoomReportData,
  PromptRegions,
  PromptAssistantType,
  PromptRole,
  PromptNode,
  PromptHistoryItem,
  PromptCreateData,
}


type ZammadDataType = 'ticket_level' | 'message_level' | 'agent_level' | 'combined_level'

interface ZammadTicketRow {
  ticketId?: number
  channel?: string
  userId?: number
  createdAt?: string
  firstResponseAt?: string
  closedAt?: string
  hasFirstResponse?: boolean
  hasClosedAt?: boolean
  firstResponseTimeMinutes?: number
  resolutionTimeMinutes?: number
  status?: string
  groupName?: string
  priority?: string
  tags?: string
}

interface ZammadMessageRow {
  messageId?: number
  ticketId?: number
  senderType?: string
  agentId?: number
  createdAt?: string
  content?: string
  responseTime?: number
  hasResponseTime?: boolean
  followUpSignal?: boolean
  lastUserMessageAt?: string
}

interface ZammadAgentRow {
  agentId?: number
  agentName?: string
  team?: string
  firstActivityTime?: string
  activeTime?: string
  inactiveTime?: number
  ticketsHandled?: number
  agentMessageCount?: number
  avgResponseTime?: number
  workingSpanHours?: number
  lastLogin?: string
  status?: string
}

interface ZammadPageData<T> {
  records?: T[]
  total?: number
  page?: number
  size?: number
}

interface ZammadCombinedData {
  ticketPage?: ZammadPageData<ZammadTicketRow>
  messagePage?: ZammadPageData<ZammadMessageRow>
  agentPage?: ZammadPageData<ZammadAgentRow>
}

interface ZammadTaskItem {
  id: number
  dataType?: string
  filterJson?: string
  promptText?: string
  modelName?: string
  analysisTime?: string
  status?: number
  statusText?: string
  failReason?: string
  hasResult?: boolean
  createTime?: string
}

interface ZammadTaskResult {
  id?: number
  dataType?: string
  filterJson?: string
  promptText?: string
  modelName?: string
  analysisTime?: string
  htmlResult?: string
}

export type {
  ZammadDataType,
  ZammadTicketRow,
  ZammadMessageRow,
  ZammadAgentRow,
  ZammadPageData,
  ZammadCombinedData,
  ZammadTaskItem,
  ZammadTaskResult,
}
