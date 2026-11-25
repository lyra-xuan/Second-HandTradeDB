export const productStates = {1:'在售',2:'已预订',3:'已售出',4:'已下架'}
export const orderStates = {1:'待确认',2:'已确认',3:'已完成',4:'已取消'}
export const money = value => Number(value || 0).toLocaleString('zh-CN', {minimumFractionDigits:2, maximumFractionDigits:2})
export const date = value => value ? new Date(value).toLocaleString('zh-CN', {hour12:false}) : '—'
export function safeImage(value) { return typeof value === 'string' && (/^https?:\/\//i.test(value) || /^\/(?!\/)/.test(value)) ? value : '' }
export function errorText(data) {
  if (Array.isArray(data?.detail)) return data.detail.map(e => `${(e.loc || []).filter(x=>x!=='body').join('.')}: ${e.msg}`).join('；')
  return typeof data?.detail === 'string' ? data.detail : '请求未成功，请稍后重试'
}
export function orderActions(order, userId) {
  if (![order.buyer_id, order.seller_id].includes(userId)) return []
  return [...(order.status===1 && order.seller_id===userId ? ['confirm'] : []), ...(order.status===2 ? ['complete'] : []), ...([1,2].includes(order.status) ? ['cancel'] : [])]
}
