function ContextCard({ chunk }) {
  const source = chunk.metadata?.source || "Unknown source";
  const type = chunk.metadata?.type || "";

  return (
    <div className="context-card">
      <div className="context-card-source">
        Source: {source}
        {type && <span className="context-card-type"> | {type}</span>}
      </div>
      <div className="context-card-content">{chunk.page_content}</div>
    </div>
  );
}

export default ContextCard;
