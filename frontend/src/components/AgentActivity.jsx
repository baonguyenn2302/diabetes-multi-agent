export default function AgentActivity({ trace = [] }) {
  if (!trace || trace.length === 0) return null;
  return (
    <details className="agent-activity">
      <summary>Hoạt động Agent ({trace.length})</summary>
      <ol>
        {trace.map((e, i) => (
          <li key={i}>
            <code>{e.agent}</code> — {e.status}
            {e.message ? `: ${e.message}` : ""}
          </li>
        ))}
      </ol>
    </details>
  );
}
