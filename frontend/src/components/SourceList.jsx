export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <ul className="sources">
      {sources.map((s, i) => (
        <li key={i}>
          <strong>{s.source_title || s.source_id || "Nguồn"}</strong>
          {s.section && <span> — {s.section}</span>}
          {s.url && (
            <span>
              {" "}
              (
              <a href={s.url} target="_blank" rel="noreferrer">
                nguồn
              </a>
              )
            </span>
          )}
          {s.excerpt && <blockquote>{s.excerpt}</blockquote>}
        </li>
      ))}
    </ul>
  );
}
