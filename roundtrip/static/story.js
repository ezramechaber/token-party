
const photo=document.querySelector('#photo');
let split=50, beforeName='V1', afterName='V2';
function updateSplit(value){split=Math.max(0,Math.min(100,value));photo.style.setProperty('--split',split+'%');photo.setAttribute('aria-valuenow',String(Math.round(split)));photo.setAttribute('aria-valuetext',Math.round(split)+' percent '+beforeName+', '+Math.round(100-split)+' percent '+afterName);}
function moveDivider(event){const rect=photo.getBoundingClientRect();updateSplit((event.clientX-rect.left)/rect.width*100);}
photo.addEventListener('pointerdown',event=>{if(event.button!==0)return;photo.focus({preventScroll:true});photo.setPointerCapture(event.pointerId);moveDivider(event);});
photo.addEventListener('pointermove',event=>{if(photo.hasPointerCapture(event.pointerId))moveDivider(event);});
photo.addEventListener('pointerup',event=>{if(photo.hasPointerCapture(event.pointerId)){moveDivider(event);photo.releasePointerCapture(event.pointerId);}});
photo.addEventListener('keydown',event=>{const step=event.shiftKey?10:2;const values={ArrowLeft:split-step,ArrowDown:split-step,ArrowRight:split+step,ArrowUp:split+step,Home:0,End:100};if(event.key in values){event.preventDefault();updateSplit(values[event.key]);}});
document.querySelectorAll('[data-pair]').forEach(button=>button.addEventListener('click',()=>{const original=button.dataset.pair==='original';document.querySelectorAll('[data-pair]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelector('#before').src=original?'/media/original.jpg':'/media/v1.jpg';document.querySelector('#before').alt=original?'Original RAW rendering':'First Lightroom edit';beforeName=original?'Original':'V1';document.querySelector('#leftTag').textContent=beforeName;updateSplit(split);}));

// Feature only a completed edit whose unedited starting export still exists.
// Without a prepared hero, the original reference study remains the homepage.
async function featureCompletedRawEdit(){
  try {
    const response=await fetch('/api/state',{cache:'no-store'});
    if(!response.ok)return;
    const state=await response.json();
    const seated=state.photos.find(p=>p.id==='gallery-one');
    if(!seated)return;
    const job=seated.jobs.find(j=>j.status==='completed'&&seated.revisions.some(r=>r.id===j.base_revision&&r.label==='Unedited RAW'));
    if(!job)return;
    const base=seated.revisions.find(r=>r.id===job.base_revision);
    const result=seated.revisions.find(r=>r.id===job.revision_id);
    if(!base||!result)return;
    // Keep the original experiment, its recipe attribution, and its recording together.
    const earlier=document.createElement('details');earlier.className='earlier-study';
    const heading=document.createElement('summary');heading.textContent='First experiment: matching a Fujifilm reference';earlier.append(heading);
    const originalNotes=document.querySelector('.notes');
    earlier.append(originalNotes,...document.querySelectorAll('.evolution,.strip,.details,.recording'));
    document.querySelector('.workspace').after(earlier);
    const notes=document.createElement('aside');notes.className='notes hero-feedback';
    const title=document.createElement('h2');title.textContent='The edit request';
    const quote=document.createElement('blockquote');quote.textContent=job.feedback;
    const changesTitle=document.createElement('h2');changesTitle.textContent='What changed';
    const changes=document.createElement('ul');
    for(const change of result.changes){const item=document.createElement('li');item.textContent=change;changes.append(item);}
    const link=document.createElement('a');link.href='/gallery?photo='+encodeURIComponent(seated.id);link.textContent='Open this photo and its revisions';
    notes.append(title,quote,changesTitle,changes,link);document.querySelector('.workspace').append(notes);
    document.querySelector('.intro>p').textContent='Imagine sending a portrait gallery and getting a request for color correction and a tighter crop. Astra makes those changes in Lightroom, exports a new version, and returns it for review. You can inspect or undo the adjustments.';
    document.querySelector('.demo-scope').textContent='This edit started with an unedited RAW. The feedback below went through the local gallery queue, and the finished export returned to the same photo.';
    document.querySelector('.tabs').hidden=true;
    const download=document.querySelector('.toolbar>a');download.href=result.url;download.textContent='Download the edit';
    const before=document.querySelector('#before');before.src=base.url;before.alt='Unedited seated portrait, with its original framing';
    const after=document.querySelector('.after');after.src=result.url;after.alt=result.summary;
    beforeName='Unedited RAW';afterName='Edited';
    document.querySelector('#leftTag').textContent=beforeName;
    document.querySelector('.right-tag').textContent=afterName;
    photo.style.aspectRatio=result.width+'/'+result.height;
    document.querySelector('#sliderHint').textContent='Drag across the photo to compare the original framing and finished crop. Arrow keys also work.';
    updateSplit(50);
  } catch { /* The original study remains available if the local queue is offline. */ }
}
featureCompletedRawEdit();
