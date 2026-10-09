import { Result } from '@/request/Result'
import { get } from '@/request/index'
import { type Ref } from 'vue'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/business'
  },
})

/**
 * 业务服务可用区域
 */
const getRegions: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/regions`, undefined, loading)
}

export default {
  getRegions,
}
