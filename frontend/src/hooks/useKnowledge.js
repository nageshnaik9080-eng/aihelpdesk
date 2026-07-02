import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createArticle,
  deleteArticle,
  getArticle,
  listArticles,
  searchKB,
  updateArticle,
} from '../api/knowledge';

const ARTICLES_KEY = ['articles'];

export function useArticles() {
  return useQuery({ queryKey: ARTICLES_KEY, queryFn: listArticles });
}

export function useArticle(id) {
  return useQuery({
    queryKey: ['article', id],
    queryFn: () => getArticle(id),
    enabled: id != null,
  });
}

export function useSearchKB(query, topK = 5) {
  const q = query.trim();
  return useQuery({
    queryKey: ['kb-search', q, topK],
    queryFn: () => searchKB(q, topK),
    enabled: q.length > 0,
  });
}

export function useCreateArticle() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (input) => createArticle(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ARTICLES_KEY }),
  });
}

export function useUpdateArticle() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (args) => updateArticle(args.id, args.input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ARTICLES_KEY }),
  });
}

export function useDeleteArticle() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => deleteArticle(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ARTICLES_KEY }),
  });
}
