import { getDb,mediaBucket } from '@/db';
import { authorized,json } from '@/lib/inbox';
import { photoCatalog } from '@/lib/gallery';
export async function POST(req:Request){
 if(!await authorized(req,'WORKER_KEY'))return json({error:'Photographer credentials required.'},401);
 try{
  const origin=req.headers.get('Origin');if(origin&&origin!==new URL(req.url).origin)throw Error('Origin rejected.');
  if(Number(req.headers.get('Content-Length')||0)>4000000)throw Error('Export too large.');
  const form=await req.formData(),file=form.get('file'),id=form.get('id'),label=form.get('label'),summary=form.get('summary'),created=Number(form.get('created'));
  const photoId=form.get('photo_id')||'portrait';
  if(typeof photoId!=='string'||!photoCatalog.some(p=>p.id===photoId))throw Error('Unknown photo.');
  if(!(file instanceof File)||file.size>3000000||typeof id!=='string'||!/^[a-z0-9-]{2,64}$/.test(id)||typeof label!=='string'||!label.trim()||label.length>30||typeof summary!=='string'||summary.length>500||!Number.isFinite(created))throw Error('Invalid export.');
  const existing=await getDb().prepare('SELECT photo_id FROM gallery_revisions WHERE id=?').bind(id).first();
  if(existing){if(existing.photo_id!==photoId)throw Error('Revision belongs to another photo.');return json({ok:true});}
  const bytes=new Uint8Array(await file.arrayBuffer());if(bytes[0]!==255||bytes[1]!==216||bytes.at(-2)!==255||bytes.at(-1)!==217)throw Error('A complete JPEG is required.');
  const objectKey=photoId+'/'+id+'.jpg';await mediaBucket().put(objectKey,bytes,{httpMetadata:{contentType:'image/jpeg'}});
  await getDb().prepare('INSERT INTO gallery_revisions VALUES(?,?,?,?,?,?)').bind(id,photoId,label,summary,objectKey,created).run();return json({ok:true},201);
 }catch(e){return json({error:e instanceof Error?e.message:'Upload failed.'},400);}
}
