// Keep the listener-facing decision short; preserve the complete evidence on demand.
export function requestNote(record) {
 const reason=String(record.reason||'').replace(/^Astra:\s*/,'').trim();
 const technical=String(record.technicalReason||'').trim();
 const review={grid:'The DJ needs to check the beat grid before mixing this track.',
  edge:'The DJ needs to find a suitable transition into this track.',
  key:'The DJ needs to check how the two tracks sound together.',
  energy:'The change in energy needs a listening check.',
  astra:'The DJ needs to listen before deciding whether this fits the set.',
  'queue-changed':'The set changed. This request needs another transition check.'};
 let summary=record.status==='review'&&review[record.reviewKind];
 if(!summary){const first=reason.match(/^.*?[.!?](?=\s|$)/)?.[0]||reason;summary=first.length>240?first.slice(0,237).replace(/\s+\S*$/,'')+'…':first;}
 if(record.status==='added'||record.status==='dismissed')summary='';
 const parts=[];
 if(reason&&reason!==summary&&record.status!=='added'&&record.status!=='dismissed')parts.push(reason);
 if(technical&&technical!==reason&&record.status!=='added'&&record.status!=='dismissed')parts.push('Transition check: '+technical);
 return {summary,details:parts.join('\n\n')};
}
