import { getDb } from '@/db';
const photo=(id:string,title:string,url:string)=>({id,title,editable:false,credit:'Sample photograph from Unsplash',source:'https://unsplash.com/s/photos/portrait-man',revisions:[{id:id+'-original',label:'Original',summary:'Sample photo. No Lightroom revisions have been made.',url}]});
export const samples=[
  photo('sample-one','Outdoor portrait','https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=max&w=1000&q=85'),
  photo('sample-two','Natural light portrait','https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=max&w=1000&q=85'),
  photo('sample-three','Business portrait','https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=max&w=1000&q=85'),
];
export async function gallery(){
  const {results}=await getDb().prepare('SELECT id,photo_id,label,summary,created FROM gallery_revisions ORDER BY created').all();
  return [...(results.length?[{id:'portrait',title:'Lightroom portrait study',editable:true,credit:'Original photograph and recoverable Lightroom edits',source:'',revisions:results.map(r=>({...r,url:'/api/media/'+r.id}))}]:[]),...samples];
}
export async function validRevision(photoId:string,revisionId:string){
  if(samples.some(p=>p.id===photoId&&p.revisions.some(r=>r.id===revisionId)))return true;
  return !!await getDb().prepare('SELECT 1 FROM gallery_revisions WHERE photo_id=? AND id=?').bind(photoId,revisionId).first();
}
