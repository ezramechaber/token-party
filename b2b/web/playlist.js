export function heldRequestIds(requests=[]) {
 const latest=new Map();
 for(const r of requests)if(r.trackId&&(!latest.has(r.trackId)||(r.updatedAt||0)>=(latest.get(r.trackId).updatedAt||0)))latest.set(r.trackId,r);
 return new Set([...latest.values()].filter(r=>r.status!=='added').map(r=>r.trackId));
}
export function setCandidates(order,tracks,requests,tempo,consumed=new Set()) {
 const byId=new Map(tracks.map(t=>[t.id,t])),held=heldRequestIds(requests);
 return order.filter(id=>{const t=byId.get(id);return t?.ready&&Number.isFinite(t.bpm)&&t.bpm>0&&Math.abs(tempo/t.bpm-1)<=.04&&(!held.has(id)||consumed.has(id));});
}
export function moveTrack(ids,source,target,locked=0) {
 const from=ids.indexOf(source),to=ids.indexOf(target);
 if(from<0||to<0)throw Error('Choose two tracks in the set list.');
 if(from<locked||to<locked)throw Error('The playing track and its prepared handoff stay in place. Reorder the tracks after them.');
 const next=[...ids];next.splice(from,1);next.splice(to,0,source);return next;
}
