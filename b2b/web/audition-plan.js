// Revalidate model-selected cues without replacing the set's order or commentary.
export async function planAudition(current, ids, tempo, bars, validate) {
 const selected=current?.tempo===tempo && current.transitions?.find(e=>
  e.from===ids[0] && e.to===ids[1] && e.astraReason);
 const checked=await validate({ids,tempo,bars:selected?selected.bars:bars,fixed:true,
  ...(selected?{previous:[selected]}:{})});
 if(checked.order?.length!==2 || checked.order.some((id,i)=>id!==ids[i]) || checked.transitions?.length!==1)
  throw Error('This pair needs grid / cue review or a closer set tempo before a matched transition.');
 const edge=checked.transitions[0];
 if(selected){
  if(['from','to','bars','entry','exit','duration'].some(key=>edge[key]!==selected[key]))
   throw Error('Astra’s selected handoff changed. Preview a new set plan before auditioning.');
  return {plan:current,edge:selected};
 }
 return {plan:checked,edge};
}
