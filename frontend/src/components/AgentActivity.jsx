const AGENT_LABEL = {
  coordinator: 'Coordinator',
  risk_assessment_agent: 'Risk Assessment Agent',
  medical_knowledge_agent: 'Medical Knowledge Agent',
  medical_advisor_agent: 'Medical Advisor Agent',
};

export default function AgentActivity({ events = [] }) {
  if (!Array.isArray(events) || events.length === 0) return null;
  return (
    <details className="trace-panel" open>
      <summary>Hoạt động Agent ({events.length} sự kiện)</summary>
      <ol className="trace-events">
        {events.map((event, index) => (
          <li key={`${event.task_id || 'event'}-${index}`}>
            <div className="trace-event-heading">
              <strong>{AGENT_LABEL[event.agent] || event.agent || 'Unknown agent'}</strong>
              <span className={`status-tag status-${event.status || 'unknown'}`}>{event.status || 'unknown'}</span>
            </div>
            {event.message && <p>{event.message}</p>}
          </li>
        ))}
      </ol>
    </details>
  );
}
