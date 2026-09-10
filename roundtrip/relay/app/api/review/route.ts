import { supportedEdit, scopeMessage } from '@/lib/edit-policy';
import { getDb } from '@/db';
import { authorized, body, json, snapshot } from '@/lib/inbox';
export async function GET(req:Request) {
  if(!await authorized(req,'REVIEW_KEY'))return json({error:'Open the review link supplied by your photographer.'},401);
  return json(await snapshot());
}
export async function POST(req:Request) {
  if(!await authorized(req,'REVIEW_KEY'))return json({error:'This review link is not valid.'},401);
  try {
    const data=await body(req), db=getDb();
    if(typeof data.id!=='string'||!/^[a-zA-Z0-9_-]{8,64}$/.test(data.id)||typeof data.base_revision!=='string'||typeof data.feedback!=='string')throw new Error('Invalid request.');
    const feedback=data.feedback.trim();if(feedback.length<3||feedback.length>2000)throw new Error('Describe the change in 3–2000 characters.');
    if(!supportedEdit(feedback))return json({error:scopeMessage},422);
    const existing=await db.prepare('SELECT * FROM requests WHERE id=?').bind(data.id).first();
    if(existing){if(existing.base_revision!==data.base_revision||existing.feedback!==feedback)throw new Error('This request identifier was already used.');return json(existing);}
    const studio=await db.prepare('SELECT * FROM studio WHERE id=1').first();
    if(!studio)throw new Error('The photographer has not connected this inbox yet.');
    if(!studio.accepting||Date.now()-Number(studio.heartbeat)>20000)return json({error:'The photographer’s Mac is busy, paused, or offline. Try again when it is ready.'},409);
    if(studio.revision!==data.base_revision)return json({error:'A new version is available. Review it before sending more feedback.'},409);
    const timestamp=Date.now();
    // One active request is enforced by a database index even under concurrent submissions.
    try { await db.prepare("INSERT INTO requests(id,base_revision,base_label,feedback,status,message,created,updated) SELECT ?,?,?,?,'requested','Waiting for the photographer’s Mac.',?,? WHERE EXISTS (SELECT 1 FROM studio WHERE id=1 AND revision=?)")
      .bind(data.id,data.base_revision,studio.label,feedback,timestamp,timestamp,data.base_revision).run(); }
    catch {return json({error:'A revision is already waiting or in progress. Wait for it to finish.'},409);}
    const saved=await db.prepare('SELECT * FROM requests WHERE id=?').bind(data.id).first();
    if(!saved)return json({error:'The current version changed. Refresh before submitting.'},409);
    return json(saved,202);
  }catch(error){return json({error:error instanceof Error?error.message:'Could not save feedback.'},400);}
}
