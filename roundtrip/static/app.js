'use strict';
const $ = selector => document.querySelector(selector);
const terminal = new Set(['completed', 'failed', 'cancelled']);
let selectedPhotoId=new URLSearchParams(location.search).get('photo'), navRender='', draftBase, state, photo, current, beforeId, split = 50, pending = false, requestId, lastRender = '', selectedJobId, lastJobRender = '';
function text(node, value) { node.textContent = value ?? ''; }
function showError(node, message) { text(node, message); node.hidden = !message; }
function currentJob() { return photo?.jobs.find(j => !terminal.has(j.status)); }
function updateSplit(value) {
  split = Math.max(0, Math.min(100, value));
  $('#photo').style.setProperty('--split', `${split}%`);
  $('#photo').setAttribute('aria-valuenow', String(Math.round(split)));
  $('#photo').setAttribute('aria-valuetext', `${Math.round(split)} percent ${$('#leftLabel').textContent}, ${Math.round(100 - split)} percent ${current?.label || 'current'}`);
}
function compare(id) {
  const before = photo.revisions.find(r => r.id === id) || photo.revisions.at(-2) || current;
  beforeId = before.id;
  $('#beforeSelect').value = before.id;
  $('#beforeImage').src = before.url;
  $('#beforeImage').alt = `${before.label}: ${before.summary}`;
  text($('#leftLabel'), before.label);
  updateSplit(split);
}
function renderJob(job) {
  const fingerprint = job ? `${job.id}:${job.status}:${job.events.at(-1)?.id}:${job.error}` : '';
  if (fingerprint === lastJobRender) return;
  lastJobRender = fingerprint;
  $('#activeJob').hidden = !job;
  if (!job) return;
  text($('#jobHeading'), terminal.has(job.status) ? 'Revision result' : 'Revision in progress');
  text($('#jobFeedback'), job.feedback);
  const labels = {queued:'Waiting for Lightroom',running:'Astra is working in Lightroom',verifying:'Checking the exported photo',completed:'New version ready',failed:'Revision needs attention',cancelled:'Revision stopped'};
  text($('#jobStatus'), labels[job.status] || job.status);
  $('#jobDot').className = 'dot' + (terminal.has(job.status) ? (job.status === 'completed' ? '' : ' failed') : ' busy');
  $('#cancelJob').hidden = terminal.has(job.status);
  $('#cancelJob').dataset.job = job.id;
  showError($('#jobError'), job.error);
  $('#reuseFeedback').hidden = !['failed','cancelled'].includes(job.status);
  $('#reuseFeedback').dataset.feedback = job.feedback;
  const events = job.events.slice(-12).reverse();
  const list = $('#eventList');
  list.replaceChildren(...events.map((event, index) => {
    const li = document.createElement('li');
    if (index === 0) li.className = 'last';
    const time = document.createElement('time');
    time.dateTime = new Date(event.created * 1000).toISOString();
    time.textContent = new Date(event.created * 1000).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',hour12:false});
    const content = document.createElement('span');
    content.textContent = event.message;
    li.append(time, content);
    return li;
  }));
}
function render() {
  photo = state.photos.find(p=>p.id===selectedPhotoId)||state.photos[0];
  const globalActive=state.photos.flatMap(p=>p.jobs).find(j=>!terminal.has(j.status));
  text($('#photoTitle'),photo?.title);
  const navKey=state.photos.map(p=>p.id+':'+p.current_revision).join('|')+photo?.id;
  if(navRender!==navKey){navRender=navKey;$('#photoNav').replaceChildren(...state.photos.map(p=>{const b=document.createElement('button');b.type='button';b.setAttribute('aria-pressed',String(p.id===photo.id));const img=document.createElement('img');img.src=p.revisions.find(r=>r.id===p.current_revision).url;img.alt='';const title=document.createElement('span');title.textContent=p.title;b.append(img,title);b.onclick=()=>{if(pending)return;selectedPhotoId=p.id;beforeId=undefined;draftBase=undefined;selectedJobId=undefined;lastRender='';lastJobRender='';$('#feedback').value='';text($('#charCount'),'0 / 2000');showError($('#formError'),'');const u=new URL(location.href);u.searchParams.set('photo',p.id);history.replaceState(null,'',u);render();};return b;}));}
  if (!photo) { showError($('#loadError'), 'No portrait has been imported. See the local setup instructions.'); return; }
  $('#workspace').hidden = false;
  $('#historySection').hidden = false;
  const oldCurrent = current?.id;
  current = photo.revisions.find(r => r.id === photo.current_revision);
  $('#remoteInbox').hidden = !state.remote;
  if(state.remote){
    text($('#remoteStatus'),state.remote.connected?'Connected':'Reconnecting');
    $('#reviewLink').href=state.remote.review_url;
    showError($('#remoteError'),state.remote.error);
  }
  const active = currentJob();
  const job = active || photo.jobs.find(j => j.id === selectedJobId) || photo.jobs[0];
  text($('#connection'), !state.runtime.available ? 'Codex is unavailable' : active ? 'Astra is editing in Lightroom' : 'Astra · Lightroom on this Mac');
  $('#connection').prepend(Object.assign(document.createElement('span'), {className:'dot' + (active ? ' busy' : '')}));
  $('#feedback').disabled = !!globalActive || pending || !!state.remote;
  $('#submit').disabled = !!state.remote || !!globalActive || pending || !state.runtime.available || state.runtime.runs_remaining < 1;
  $('#submit').textContent = state.remote ? 'Use the remote review link above' : globalActive ? 'One Lightroom edit is in progress…' : pending ? 'Submitting…' : 'Revise in Lightroom ↗';
  text($('#baseNote'), globalActive&&globalActive.photo_id!==photo.id?'Lightroom is editing another photo. One edit runs at a time.':`Your feedback applies to ${current.label}.`);
  if (state.runtime.runs_remaining < 1 && !active) text($('#baseNote'), 'This session’s run allowance has been used.');
  renderJob(job);
  const key = photo.revisions.map(r=>r.id).join('|');
  if (lastRender !== key) {
    lastRender = key;
    const select = $('#beforeSelect');
    select.replaceChildren(...photo.revisions.filter(r=>r.id !== current.id||photo.revisions.length===1).map(r=>{
      const option = document.createElement('option'); option.value = r.id; option.textContent = r.label; return option;
    }));
    $('#photo').style.aspectRatio = `${current.width} / ${current.height}`;
    $('#afterImage').src = current.url;
    $('#afterImage').alt = `${current.label}: ${current.summary}`;
    $('#download').href = current.url;
    $('#download').download = `roundtrip-${current.label.toLowerCase()}.jpg`;
    text($('#currentLabel'), current.label); text($('#rightLabel'), current.label);
    text($('#dimensions'), `${current.width} × ${current.height} · JPEG`);
    text($('#nativeVersion'), current.version);
    text($('#summaryHeading'), `${current.label}: current edit`);
    text($('#summary'), current.summary);
    $('#changes').replaceChildren(...current.changes.map(change=>{const li=document.createElement('li');li.textContent=change;return li;}));
    compare(oldCurrent && oldCurrent !== current.id ? oldCurrent : beforeId);
    $('#history').replaceChildren(...photo.revisions.map(revision => {
      const figure=document.createElement('figure');figure.className='revision'+(revision.id===current.id?' current':'');
      const img=document.createElement('img');img.src=revision.url;img.alt=`${revision.label}: ${revision.summary}`;img.width=revision.width;img.height=revision.height;
      const caption=document.createElement('figcaption');
      const head=document.createElement('div');head.className='revision-head';
      const title=document.createElement('strong');title.textContent=revision.label;
      const tag=document.createElement('span');tag.textContent=revision.id===current.id?'Current':'';head.append(title,tag);
      const detail=document.createElement('small');detail.textContent=revision.summary;
      const actions=document.createElement('div');actions.className='revision-actions';
      if(revision.id!==current.id){const compareButton=document.createElement('button');compareButton.type='button';compareButton.textContent='Compare';compareButton.setAttribute('aria-label',`Compare ${revision.label} with ${current.label}`);compareButton.onclick=()=>{compare(revision.id);$('#photo').scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});};actions.append(compareButton);}
      const download=document.createElement('a');download.href=revision.url;download.download=`roundtrip-${revision.label.toLowerCase()}.jpg`;download.textContent='Download';download.setAttribute('aria-label',`Download ${revision.label}`);actions.append(download);
      caption.append(head,detail,actions);figure.append(img,caption);return figure;
    }));
  }
  const past=photo.jobs.filter(j=>terminal.has(j.status)&&j.id!==job?.id);
  $('#pastRequests').hidden=!past.length;
  $('#requestHistory').replaceChildren(...past.map(j=>{
    const section=document.createElement('article');section.className='past-request';
    const title=document.createElement('h3');title.textContent=j.status==='completed'?'Completed revision':j.status==='cancelled'?'Stopped revision':'Revision needs attention';
    const p=document.createElement('p');p.textContent=j.feedback;
    const button=document.createElement('button');button.type='button';button.className='text-button';button.textContent='See activity';button.onclick=()=>{selectedJobId=j.id;render();$('#activeJob').scrollIntoView({block:'start'});};
    section.append(title,p,button);return section;
  }));
}
async function refresh() {
  try {
    const response=await fetch('/api/state',{cache:'no-store'});
    if(!response.ok)throw new Error('The local app could not be reached.');
    state=await response.json();showError($('#loadError'),'');render();return true;
  } catch(error){showError($('#loadError'),error.message);return false;}
}
async function post(url, body) {
  const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-Roundtrip-Token':state.csrf},body:JSON.stringify(body)});
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'The request could not be completed.');
  return result;
}
$('#feedbackForm').addEventListener('submit',async event=>{
  event.preventDefault();if(pending||currentJob())return;
  const feedback=$('#feedback').value.trim();if(feedback.length<3)return;
  requestId ||= crypto.randomUUID();pending=true;showError($('#formError'),'');render();
  try {
    const result=await post('/api/revisions',{photo_id:photo.id,base_revision:draftBase||current.id,feedback,request_id:requestId});
    selectedJobId=result.job_id;draftBase=undefined;$('#feedback').value='';text($('#charCount'),'0 / 2000');requestId=undefined;
  } catch(error){showError($('#formError'),error.message);}
  finally{pending=false;await refresh();}
});
$('#feedback').addEventListener('input',()=>{draftBase ||= current?.id;if(!$('#feedback').value)draftBase=undefined;requestId=undefined;text($('#charCount'),`${$('#feedback').value.length} / 2000`);});
$('#reuseFeedback').addEventListener('click',()=>{if(currentJob())return;$('#feedback').value=$('#reuseFeedback').dataset.feedback;draftBase=current?.id;requestId=undefined;text($('#charCount'),`${$('#feedback').value.length} / 2000`);$('#feedback').focus();});
$('#beforeSelect').addEventListener('change',event=>compare(event.target.value));
$('#cancelJob').addEventListener('click',async()=>{try{await post(`/api/jobs/${$('#cancelJob').dataset.job}/cancel`,{});await refresh();}catch(error){showError($('#jobError'),error.message);}});
const slider=$('#photo');
function move(event){const rect=slider.getBoundingClientRect();updateSplit((event.clientX-rect.left)/rect.width*100);}
slider.addEventListener('pointerdown',event=>{if(event.button!==0)return;slider.focus({preventScroll:true});slider.setPointerCapture(event.pointerId);move(event);});
slider.addEventListener('pointermove',event=>{if(slider.hasPointerCapture(event.pointerId))move(event);});
slider.addEventListener('pointerup',event=>{if(slider.hasPointerCapture(event.pointerId)){move(event);slider.releasePointerCapture(event.pointerId);}});
slider.addEventListener('keydown',event=>{const step=event.shiftKey?10:2;const keys={ArrowLeft:split-step,ArrowDown:split-step,ArrowRight:split+step,ArrowUp:split+step,Home:0,End:100};if(event.key in keys){event.preventDefault();updateSplit(keys[event.key]);}});
async function poll(){await refresh();setTimeout(poll,2000);}poll();

// Expose the same gallery actions to an agent without bypassing server checks.
if (document.modelContext?.registerTool) {
  const lifecycle = new AbortController();
  addEventListener('pagehide', () => lifecycle.abort(), {once:true});
  const tools = [
    {
      name:'read_revision_status', title:'Read photo revision status',
      description:'Read the current gallery version and real Astra job status. This does not launch a job or edit Lightroom.',
      inputSchema:{type:'object',properties:{},additionalProperties:false},
      annotations:{readOnlyHint:true,untrustedContentHint:true},
      async execute() {
        if (!await refresh()) throw new Error('The local gallery could not be reached.');
        if (!photo || !current) throw new Error('The gallery is not available.');
        return {photo_id:photo.id,current_revision:current.id,label:current.label,summary:current.summary,jobs:photo.jobs.map(j=>({id:j.id,status:j.status,feedback:j.feedback,error:j.error,revision_id:j.revision_id}))};
      }
    },
    {
      name:'request_lightroom_revision', title:'Request a Lightroom revision',
      description:'Submit photo feedback and start an Astra job that operates Lightroom on this Mac, changes the source photo through recoverable controls, and exports a new local gallery version. Requires explicit user authorization for the photo revision. It returns a queued job ID, not a completed edit.',
      inputSchema:{type:'object',properties:{photo_id:{type:'string'},base_revision:{type:'string'},feedback:{type:'string',minLength:3,maxLength:2000},request_id:{type:'string',minLength:8,maxLength:80}},required:['photo_id','base_revision','feedback','request_id'],additionalProperties:false},
      annotations:{readOnlyHint:false,untrustedContentHint:true},
      async execute(input) {
        if (!input || typeof input.feedback !== 'string' || input.feedback.trim().length < 3 || input.feedback.length > 2000) throw new Error('Provide photo feedback in 3–2000 characters.');
        if (!await refresh()) throw new Error('The local gallery could not be reached.');
        if (input.photo_id !== photo?.id || input.base_revision !== current?.id) throw new Error('Read the latest gallery version before requesting a revision.');
        const result=await post('/api/revisions',input);
        selectedJobId=result.job_id;
        await refresh();
        return {job_id:result.job_id,status:photo.jobs.find(j=>j.id===result.job_id)?.status || 'queued'};
      }
    }
  ];
  for (const tool of tools) {
    try { Promise.resolve(document.modelContext.registerTool(tool,{signal:lifecycle.signal})).catch(()=>{}); }
    catch { /* The visible gallery remains available if WebMCP is unsupported. */ }
  }
}

$('#copyReview').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(state.remote.review_url);text($('#copyReview'),'Copied');setTimeout(()=>text($('#copyReview'),'Copy link'),2000);}catch{text($('#copyReview'),'Open the link to copy it');}});
