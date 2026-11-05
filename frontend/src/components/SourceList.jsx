export default function SourceList({ sources }) {
  if (!Array.isArray(sources) || sources.length === 0) return null;
  return (
    <details className="sources-panel">
      <summary>Nguồn tham khảo ({sources.length})</summary>
      <ul className="sources">
        {sources.map((source, i) => (
          <li key={`${source.source_id || 'source'}-${i}`}>
            <strong>{source.source_title || 'Tài liệu chưa có tiêu đề'}</strong>
            {source.section && <span> — {source.section}</span>}
            {source.url && <span> (<a href={source.url} target="_blank" rel="noopener noreferrer">Xem nguồn</a>)</span>}
            {source.excerpt && <blockquote>{source.excerpt}</blockquote>}
          </li>
        ))}
      </ul>
    </details>
  );
}
