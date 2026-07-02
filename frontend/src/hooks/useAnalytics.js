import { useQuery } from '@tanstack/react-query';
import { getAnalytics } from '../api/analytics';
import { listUsers } from '../api/auth';

export function useAnalytics() {
  return useQuery({ queryKey: ['analytics'], queryFn: getAnalytics });
}

export function useUsers() {
  return useQuery({ queryKey: ['users'], queryFn: listUsers });
}
