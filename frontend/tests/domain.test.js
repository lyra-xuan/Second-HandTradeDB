import {test} from 'node:test'
import assert from 'node:assert/strict'
import {orderActions,safeImage,errorText} from '../src/domain.js'
test('only seller can confirm; both parties can complete or cancel eligible orders',()=>{
 const order={buyer_id:1,seller_id:2,status:1}
 assert.deepEqual(orderActions(order,1),['cancel'])
 assert.deepEqual(orderActions(order,2),['confirm','cancel'])
 assert.deepEqual(orderActions({...order,status:2},1),['complete','cancel'])
 assert.deepEqual(orderActions({...order,status:3},2),[])
 assert.deepEqual(orderActions(order,3),[])
})
test('image sources reject executable and protocol-relative URLs',()=>{
 assert.equal(safeImage('javascript:alert(1)'),'')
 assert.equal(safeImage('//unknown.test/x'),'')
 assert.equal(safeImage('/static/a.jpg'),'/static/a.jpg')
 assert.equal(safeImage('https://example.com/a.jpg'),'https://example.com/a.jpg')
})
test('FastAPI validation errors remain readable',()=>{
 assert.equal(errorText({detail:[{loc:['body','email'],msg:'invalid email'}]}),'email: invalid email')
 assert.equal(errorText({detail:'密码错误'}),'密码错误')
})
