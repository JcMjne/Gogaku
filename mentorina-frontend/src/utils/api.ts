import { PageItem, VocabularyUpdatePayload } from '@/types';

export async function getPage(token: string, learningLanguageIdx: number): Promise<PageItem> {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get_page`, {
    method: 'POST',
    headers: {
      "Authorization": `Bearer ${token}`,
      'Content-Type': 'application/json' },
    body: JSON.stringify({ learning_language_idx: learningLanguageIdx })
  });
  if (!res.ok) throw new Error('Failed to generate pages');
  return await res.json();
}

export async function updateVocabulary(payload: VocabularyUpdatePayload) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/update_vocabulary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to update vocabulary');
}
