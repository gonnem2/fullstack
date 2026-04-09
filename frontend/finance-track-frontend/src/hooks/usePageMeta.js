import { useEffect } from 'react';

/**
 * Устанавливает title и description страницы.
 * @param {string} title        - Заголовок вкладки
 * @param {string} [description] - Мета-описание (опционально)
 */
export function usePageMeta(title, description) {
  useEffect(() => {
    const suffix = 'FinanceTrack';
    document.title = title ? `${title} | ${suffix}` : suffix;

    if (description) {
      let tag = document.querySelector('meta[name="description"]');
      if (!tag) {
        tag = document.createElement('meta');
        tag.name = 'description';
        document.head.appendChild(tag);
      }
      tag.content = description;
    }
  }, [title, description]);
}
