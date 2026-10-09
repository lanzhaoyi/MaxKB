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

