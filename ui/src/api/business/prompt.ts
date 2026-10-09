import { Result } from '@/request/Result'
import { get, post, del } from '@/request/index'
import { type Ref } from 'vue'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/business/prompt'
  },
})

/**
 * 助手类型列表
 * @param params {region}
 */
const getAssistantTypes: (params: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  params,
  loading,
) => {
  return get(`${prefix.value}/assistant-types`, params, loading)
}

/**
 * 节点配置列表
 * @param params {assistant_type, region}
 */
const getNodes: (params: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  params,
  loading,
) => {
  return get(`${prefix.value}/nodes`, params, loading)
}

/**
 * 提示词历史记录
 * @param params {assistant_type, node_name, prompt_type, region}
 */
const getHistory: (params: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  params,
  loading,
) => {
  return get(`${prefix.value}/history`, params, loading)
}

/**
 * 新增提示词
 * @param data {assistant_type, node_name, prompt_type, region, identity_id, version, content, summary}
 */
const createPrompt: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix.value}`, data, undefined, loading)
}

/**
 * 删除提示词
 * @param prompt_id 提示词id
 * @param params {region}
 */
const deletePrompt: (
  prompt_id: number,
  params: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (prompt_id, params, loading) => {
  return del(`${prefix.value}/${prompt_id}`, params, undefined, loading)
}

export default {
  getAssistantTypes,
  getNodes,
  getHistory,
  createPrompt,
  deletePrompt,
}
