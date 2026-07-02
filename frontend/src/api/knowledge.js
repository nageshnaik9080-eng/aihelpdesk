import client from './client';

export async function listArticles() {
  const { data } = await client.get('/kb/articles');
  return data;
}

export async function getArticle(id) {
  const { data } = await client.get(`/kb/articles/${id}`);
  return data;
}

export async function searchKB(q, topK = 5) {
  const { data } = await client.get('/kb/search', {
    params: { q, top_k: topK },
  });
  return data;
}

export async function createArticle(input) {
  const { data } = await client.post('/kb/articles', input);
  return data;
}

export async function updateArticle(id, input) {
  const { data } = await client.put(`/kb/articles/${id}`, input);
  return data;
}

export async function deleteArticle(id) {
  await client.delete(`/kb/articles/${id}`);
}
