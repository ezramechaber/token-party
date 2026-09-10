
const photo=document.querySelector('#photo');
let split=50, beforeName='V1';
function updateSplit(value){split=Math.max(0,Math.min(100,value));photo.style.setProperty('--split',split+'%');photo.setAttribute('aria-valuenow',String(Math.round(split)));photo.setAttribute('aria-valuetext',Math.round(split)+' percent '+beforeName+', '+Math.round(100-split)+' percent V2');}
function moveDivider(event){const rect=photo.getBoundingClientRect();updateSplit((event.clientX-rect.left)/rect.width*100);}
photo.addEventListener('pointerdown',event=>{if(event.button!==0)return;photo.focus({preventScroll:true});photo.setPointerCapture(event.pointerId);moveDivider(event);});
photo.addEventListener('pointermove',event=>{if(photo.hasPointerCapture(event.pointerId))moveDivider(event);});
photo.addEventListener('pointerup',event=>{if(photo.hasPointerCapture(event.pointerId)){moveDivider(event);photo.releasePointerCapture(event.pointerId);}});
photo.addEventListener('keydown',event=>{const step=event.shiftKey?10:2;const values={ArrowLeft:split-step,ArrowDown:split-step,ArrowRight:split+step,ArrowUp:split+step,Home:0,End:100};if(event.key in values){event.preventDefault();updateSplit(values[event.key]);}});
document.querySelectorAll('[data-pair]').forEach(button=>button.addEventListener('click',()=>{const original=button.dataset.pair==='original';document.querySelectorAll('[data-pair]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));document.querySelector('#before').src=original?'/media/original.jpg':'/media/v1.jpg';document.querySelector('#before').alt=original?'Original RAW rendering':'First Lightroom edit';beforeName=original?'Original':'V1';document.querySelector('#leftTag').textContent=beforeName;updateSplit(split);}));
