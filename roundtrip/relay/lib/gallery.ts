import { getDb } from '@/db';

// Media and source filenames stay in private storage, outside the source repository.
export const photoCatalog = [
  { id: 'portrait', title: 'Lightroom portrait study', editable: true },
  { id: 'gallery-one', title: 'Seated portrait', editable: false },
  { id: 'gallery-two', title: 'Portrait by the plants', editable: false },
  { id: 'gallery-three', title: 'Studio portrait', editable: false },
];

export async function gallery() {
  const { results } = await getDb().prepare(
    'SELECT id,photo_id,label,summary,created FROM gallery_revisions ORDER BY created,id'
  ).all();
  return photoCatalog.flatMap(photo => {
    const revisions = results.filter(r => r.photo_id === photo.id)
      .map(r => ({ ...r, url: '/api/media/' + r.id }));
    return revisions.length ? [{ ...photo, source: '',
      credit: 'Photographer’s RAW · exported from Lightroom', revisions }] : [];
  });
}

export async function validRevision(photoId: string, revisionId: string) {
  if (!photoCatalog.some(p => p.id === photoId)) return false;
  return !!await getDb().prepare(
    'SELECT 1 FROM gallery_revisions WHERE photo_id=? AND id=?'
  ).bind(photoId, revisionId).first();
}
