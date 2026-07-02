import { useQuery } from '@tanstack/react-query';
import { getDbOverview } from '../api/admin';

export function useDbOverview() {
  return useQuery({
    queryKey: ['db-overview'],
    queryFn: getDbOverview,
    refetchInterval: 10_000, // auto-refresh so new records show up live
  });
}
