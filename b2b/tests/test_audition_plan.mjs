import test from 'node:test';
import assert from 'node:assert/strict';
import {planAudition} from '../web/audition-plan.js';

const edge={from:'b',to:'c',bars:8,entry:32,exit:300,duration:15.48,astraReason:'Let the record breathe.'};
const plan={tempo:124,mode:'Astra',reason:'A gradual lift.',order:['a','b','c'],transitions:[{from:'a',to:'b'},edge]};
const checked={order:['b','c'],transitions:[{...edge}],tempo:124,mode:'Manual'};

test('audition preserves the exact Astra edge and whole set even for a later pair or different overlap setting',async()=>{
 let sent;
 const result=await planAudition(plan,['b','c'],124,16,async body=>{sent=body;return checked;});
 assert.deepEqual(sent,{ids:['b','c'],tempo:124,bars:8,fixed:true,previous:[edge]});
 assert.equal(result.plan,plan);
 assert.equal(result.edge,edge);
 assert.equal(result.edge.astraReason,'Let the record breathe.');
});
test('unmatched, reversed, manual and different-tempo pairs use a fixed plan without inherited Astra claims',async()=>{
 for(const [current,ids,tempo] of [[plan,['a','c'],124],[plan,['c','b'],124],[plan,['b','c'],125],[{...plan,transitions:[{...edge,astraReason:undefined}]},['b','c'],124],[null,['b','c'],124]]){
  const fallback={order:ids,transitions:[{from:ids[0],to:ids[1],bars:16}],tempo,mode:'Manual'};
  const result=await planAudition(current,ids,tempo,16,async body=>{
   assert.equal(body.previous,undefined);assert.equal(body.bars,16);return fallback;
  });
  assert.equal(result.plan,fallback);assert.equal(result.edge.astraReason,undefined);
 }
});
test('changed or invalid validated cues fail instead of silently substituting a different transition',async()=>{
 await assert.rejects(planAudition(plan,['b','c'],124,16,async()=>({...checked,transitions:[{...edge,entry:0}]})),/selected handoff changed/);
 await assert.rejects(planAudition(plan,['b','c'],124,16,async()=>({...checked,order:['b']})),/grid \/ cue review/);
 await assert.rejects(planAudition(plan,['b','c'],124,16,async()=>{throw Error('Song map changed');}),/Song map changed/);
});
