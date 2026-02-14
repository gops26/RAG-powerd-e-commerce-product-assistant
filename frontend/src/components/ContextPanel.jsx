import ContextCard from "./ContextCard";

function ContextPanel({ context }) {
  return (
    <aside className="context-panel">
      <h2 className="context-title">Retrieved Context</h2>
      {context.length === 0 ? (
        <p className="context-placeholder">
          Ask a question to see retrieved context here.
        </p>
      ) : (
        <div className="context-list">
          {context.map((chunk, i) => (
            <ContextCard key={i} chunk={chunk} />
          ))}
        </div>
      )}
    </aside>
  );
}

export default ContextPanel;
