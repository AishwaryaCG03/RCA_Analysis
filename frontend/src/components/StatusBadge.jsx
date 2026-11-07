export default function StatusBadge({ status = 'Draft' }) {
  const kind = String(status).toLowerCase().replaceAll(' ', '-')
  return <span className={`status status-${kind}`}>{status}</span>
}
