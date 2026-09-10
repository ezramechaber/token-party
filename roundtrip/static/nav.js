// Keep the selected photo when moving between the story and gallery.
'use strict';
const galleryLink=document.querySelector('.site-nav a[href="/gallery"]');
try {
  const remembered=sessionStorage.getItem('roundtrip-photo');
  if(remembered)galleryLink.href='/gallery?photo='+encodeURIComponent(remembered);
} catch { /* Navigation also works when storage is disabled. */ }
addEventListener('pagehide',()=>{
  const photoId=new URL(location.href).searchParams.get('photo');
  if(photoId)try{sessionStorage.setItem('roundtrip-photo',photoId);}catch{}
});
