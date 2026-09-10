import { getDb,mediaBucket } from '@/db';
import { authorized,json } from '@/lib/inbox';
export async function GET(req:Request,{params}:{params:Promise<{id:string}>}){
 if(!await authorized(req,'REVIEW_KEY'))return json({error:'A review link is required.'},401);
 const {id}=await params;const r=await getDb().prepare('SELECT object_key FROM gallery_revisions WHERE id=?').bind(id).first();
 if(!r)return json({error:'Photo not found.'},404);const object=await mediaBucket().get(String(r.object_key));
 if(!object)return json({error:'Photo not found.'},404);
 return new Response(object.body,{headers:{'Content-Type':'image/jpeg','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
}
