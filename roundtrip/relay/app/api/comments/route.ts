import { getDb } from '@/db';
import { authorized,body,json } from '@/lib/inbox';
import { validRevision } from '@/lib/gallery';
export async function POST(req:Request){
 if(!await authorized(req,'REVIEW_KEY'))return json({error:'A review link is required.'},401);
 try{const d=await body(req);if(![d.id,d.photo_id,d.revision_id,d.text].every(v=>typeof v==='string'))throw Error('Invalid comment.');
 if(!/^[a-zA-Z0-9_-]{8,80}$/.test(d.id)||!d.text.trim()||d.text.length>2000)throw Error('Write a comment of 1–2000 characters.');
 if(!await validRevision(d.photo_id,d.revision_id))throw Error('That photo revision is unavailable.');
 const existing=await getDb().prepare('SELECT * FROM comments WHERE id=?').bind(d.id).first();
 if(existing){if(existing.photo_id!==d.photo_id||existing.revision_id!==d.revision_id||existing.text!==d.text.trim())throw Error('Comment identifier already used.');return json(existing);}
 await getDb().prepare('INSERT INTO comments VALUES(?,?,?,?,?)').bind(d.id,d.photo_id,d.revision_id,d.text.trim(),Date.now()).run();return json({ok:true},201);
 }catch(e){return json({error:e instanceof Error?e.message:'Could not save comment.'},400);}
}
