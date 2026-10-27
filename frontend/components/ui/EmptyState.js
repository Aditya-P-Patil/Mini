export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="empty">
      {Icon && <Icon size={25} aria-hidden="true" />}
      <strong>{title}</strong>
      <p>{description}</p>
      {action}
    </div>
  );
}
