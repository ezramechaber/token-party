import { getDb } from '@/db';
import { authorized, body, json, finished } from '@/lib/inbox';
export async function POST(req:Request) {
  if(!await authorized(req,'WORKER_KEY'))return json({error:'Worker authentication required.'},401);
  try {
    const data=await body(req), db=getDb(), p=data.photo;
    if(!p||![p.id,p.revision,p.label,p.title].every(v=>typeof v==='string'&&v.length>0&&v.length<120))throw new Error('Invalid photo state.');
    const now=Date.now();
    await db.prepare('INSERT INTO studio VALUES(1,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET photo_id=excluded.photo_id,revision=excluded.revision,label=excluded.label,title=excluded.title,heartbeat=excluded.heartbeat,accepting=excluded.accepting').bind(p.id,p.revision,p.label,p.title,now,data.accepting?1:0).run();
    if(data.update){const u=data.update;
      if(typeof u.id!=='string'||!['requested','running','verifying',...finished].includes(u.status)||typeof u.message!=='string'||u.message.length>500)throw new Error('Invalid status update.');
      await db.prepare("UPDATE requests SET status=?,message=?,result_label=?,updated=? WHERE id=? AND status NOT IN ('completed','failed','cancelled','stale')")
        .bind(u.status,u.message,typeof u.result_label==='string'?u.result_label.slice(0,40):null,now,u.id).run();
    }
    const request=await db.prepare("SELECT * FROM requests WHERE status IN ('requested','running','verifying') ORDER BY created LIMIT 1").first();
    return json({request});
  }catch(error){return json({error:error instanceof Error?error.message:'Sync failed.'},400);}
}
