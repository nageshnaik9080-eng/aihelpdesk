import client from './client';

export async function getDbOverview() {
  const { data } = await client.get('/admin/db');
  return data;
}
