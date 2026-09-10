import policy from './edit-policy.json';
export const examples = policy.examples;
export const scopeMessage = policy.message;
// Fail closed: every clause must describe an allowed adjustment or preservation.
// This intentionally narrow grammar is a demo boundary, not an AI moderation claim.
export function supportedEdit(feedback: string): boolean {
  const clauses=feedback.toLowerCase().trim().replace(/^(?:please|just for proof of concept)\s+/,'').split(/[.!;]+|,?\s+but\s+|,\s*(?=keep\b)|\s+and\s+(?=crop\b)/).map(s=>s.trim()).filter(Boolean);
  if(!clauses.length||clauses.length>6)return false;
  let edits=0;
  for(const clause of clauses){
    if(policy.actions.some(p=>new RegExp('^(?:'+p+')$').test(clause))){edits++;continue;}
    if(![...policy.preservation,...policy.context].some(p=>new RegExp('^(?:'+p+')$').test(clause)))return false;
  }
  return edits>0&&edits<=3;
}
