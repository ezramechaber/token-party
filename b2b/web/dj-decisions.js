// Public decision summaries from the selected, validated handoff—not hidden reasoning.
export function nextDecision(plan, edge, {active=false, finished=false, planning=false}={}) {
 if(planning)return {heading:'Astra is planning',title:'Choosing the next records…',reason:'Checking the set’s musical direction and available handoffs.',trackId:null};
 if(finished)return {heading:'Set complete',title:'No more tracks are planned',reason:'There are no more handoffs in this set.',trackId:null};
 const selected=edge||plan?.transitions?.[0];
 if(!selected)return {heading:'Astra’s next move',title:'Give Astra the decks',reason:'Start Astra DJ or preview a plan to see what it wants to play next and why.',trackId:null};
 const model=!!selected.astraReason;
 return {heading:model?'Astra’s next move':'Next move · your order',trackId:selected.to,
  title:active?'Up next':'Planned next',reason:selected.astraReason||selected.reason||'This handoff passed the tempo and phrase checks.',bars:selected.bars};
}
export function requestActions(record, known) {
 if(record.status==='added'||record.status==='accepted')return {match:false,inspect:false,recheck:false,retry:false};
 const pending=['pending','identifying','downloading','analyzing'].includes(record.status);
 return {match:!known&&!pending,inspect:known&&!pending,
  recheck:known&&['review','error','dismissed'].includes(record.status),
  retry:!known&&!pending&&record.provider!=='local'};
}
