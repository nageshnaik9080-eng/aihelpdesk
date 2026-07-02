import client from './client';

export async function listNotifications() {
  const { data } = await client.get('/notifications');
  return data;
}

export async function markNotificationRead(id) {
  await client.post(`/notifications/${id}/read`);
}
