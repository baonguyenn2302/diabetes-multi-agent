const ORIGIN_LABELS = {
  chroma: "Tài liệu",
  neo4j: "Đồ thị tri thức (Neo4j)",
};

export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <ul className="sources">
      {sources.map((s, i) => (
        <li key={`${s.origin || "src"}-${s.source_id}-${i}`}>
          {s.origin && (
            <small className={`origin origin-${s.origin}`}>
              [{ORIGIN_LABELS[s.origin] || s.origin}]
            </small>
          )}{" "}
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
