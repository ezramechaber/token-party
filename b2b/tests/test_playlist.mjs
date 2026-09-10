import test from 'node:test';
import assert from 'node:assert/strict';
import {moveTrack,setCandidates} from '../web/playlist.js';

test('rejected and review imports stay in the library, never the candidate set',()=>{
 const tracks=['house','rejected','review','queued','added','bad-grid','wrong-tempo'].map(id=>({id,ready:id!=='bad-grid',bpm:id==='wrong-tempo'?100:124}));
 const requests=['rejected','review','queued','added'].map(id=>({trackId:id,status:id==='queued'?'accepted':id,updatedAt:1}));
 assert.deepEqual(setCandidates(tracks.map(t=>t.id),tracks,requests,124),['house','added']);
});
test('drag move preserves exactly one occurrence of every track in either direction',()=>{
 assert.deepEqual(moveTrack(['a','b','c','d'],'b','d'),['a','c','d','b']);
 assert.deepEqual(moveTrack(['a','b','c','d'],'d','b'),['a','d','b','c']);
});
test('live reorder locks played tracks and the already prepared handoff',()=>{
 assert.throws(()=>moveTrack(['a','b','c','d'],'c','b',2),/prepared handoff/);
 assert.throws(()=>moveTrack(['a','b','c','d'],'a','d',2),/prepared handoff/);
 assert.deepEqual(moveTrack(['a','b','c','d'],'d','c',2),['a','b','d','c']);
});
