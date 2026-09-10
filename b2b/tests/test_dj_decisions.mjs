import test from 'node:test';
import assert from 'node:assert/strict';
import {nextDecision,requestActions} from '../web/dj-decisions.js';

test('identified requests never ask the DJ to select the same recording again',()=>{
 for(const status of ['review','rejected','error','dismissed','accepted','added']) {
  assert.equal(requestActions({status,provider:'youtube'},true).match,false);
 }
 assert.equal(requestActions({status:'review'},true).recheck,true);
 assert.equal(requestActions({status:'rejected'},true).inspect,true);
});
test('unresolved recordings can be matched, while processing and queued requests need no intervention',()=>{
 assert.equal(requestActions({status:'needs_audio',provider:'spotify'},false).match,true);
 for(const status of ['pending','identifying','downloading','analyzing','accepted','added']) {
  assert.deepEqual(requestActions({status},false),{match:false,inspect:false,recheck:false,retry:false});
 }
});
test('the explanation follows the armed handoff rather than repeating the first transition',()=>{
 const first={to:'b',bars:8,astraReason:'First choice.'};
 const armed={to:'c',bars:16,astraReason:'A warmer groove to build on the outgoing record.'};
 const result=nextDecision({transitions:[first,armed]},armed,{active:true});
 assert.equal(result.trackId,'c');
 assert.equal(result.reason,armed.astraReason);
 assert.equal(result.title,'Up next');
 assert.equal(result.bars,16);
});
test('manual plans and finished sets do not misrepresent Astra or announce a stale next track',()=>{
 const plan={transitions:[{to:'b',reason:'Compatible tempo.',bars:8}]};
 assert.equal(nextDecision(plan).heading,'Next move · your order');
 assert.equal(nextDecision(plan,null,{finished:true}).trackId,null);
 assert.equal(nextDecision(plan,null,{planning:true}).trackId,null);
});
