import test from 'node:test';
import assert from 'node:assert/strict';
import {cueIncoming,handoffTime} from '../web/handoff.js';
function deck(offset=6){
 const parameter=()=>({value:1,events:[],cancelScheduledValues(t){this.events.push(['cancel',t]);},setValueAtTime(v,t){this.value=v;this.events.push(['set',v,t]);}});
 return {buffer:{duration:400},offset,running:false,start:0,fade:{gain:parameter()},low:{gain:parameter()},stop(){this.running=false;},status(value){this.label=value;}};
}
test('paused incoming deck resets to zero when zero is the selected cue',()=>{
 const b=deck();cueIncoming(b,0,10);assert.equal(b.offset,0);assert.equal(b.running,false);assert.equal(b.fade.gain.value,0);assert.equal(b.low.gain.value,-24);assert.equal(b.label,'CUED FOR MIX');
});
test('nonzero phrase cue replaces paused playhead and clears prior automation',()=>{
 const b=deck(9);cueIncoming(b,32.1,10);assert.equal(b.offset,32.1);assert.deepEqual(b.fade.gain.events[0],['cancel',10]);assert.deepEqual(b.low.gain.events[0],['cancel',10]);
});
test('missed exit leaves B cued and does not start either paused deck',()=>{
 const a=deck(300),b=deck(9);cueIncoming(b,32.1,10);assert.throws(()=>handoffTime(a,290,10),/passed its planned exit/);assert.equal(a.running,false);assert.equal(b.running,false);assert.equal(b.offset,32.1);
});
test('future handoff respects outgoing playback clock',()=>{
 const a=deck(100);a.running=true;a.start=5;assert.equal(handoffTime(a,120,10),25);
 const paused=deck(100);assert.ok(Math.abs(handoffTime(paused,120,10)-30.1)<1e-9);
});
