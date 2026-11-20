// Temporary dictionaries exactly matching database/seed_data.sql. Replace with dictionary APIs when available.
export const categories = ['教材书籍','电子产品','生活用品','运动健身','服饰鞋包','文具用品','美妆个护','乐器']
export const conditions = ['全新未拆封','九成新','八成新','七成新','明显使用痕迹']
export const places = ['东区宿舍楼下','西区宿舍楼下','第一食堂门口','图书馆北门','教学楼A栋大厅','校门口快递站']
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
