import client from './client';

export async function getAnalytics() {
  const { data } = await client.get('/analytics');
  return data;
}
