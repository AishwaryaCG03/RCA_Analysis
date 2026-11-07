import { CheckCircle2, FileWarning, Plus, Trash2 } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { addCapa, removeCapa, removeCause, updateCapa, updateCause, updateEvidence } from '../features/investigationSlice'
import StatusBadge from './StatusBadge'

export function RootCauseCards({ items = [] }) {
  const dispatch = useDispatch()
  return <section className="panel"><div className="section-title"><div><span className="step">03</span><h2>Potential root causes</h2><p>AI-generated hypotheses require evidence and human confirmation.</p></div></div>{!items.length ? <div className="empty-state">No root-cause hypotheses yet.</div> : <div className="card-stack">{items.map(item => <article className="analysis-card" key={item.id}><div className="card-heading"><div><span className="category">{item.category}</span><h3>{item.description}</h3></div><button className="icon-btn danger" title="Remove suggestion" onClick={() => dispatch(removeCause(item.id))}><Trash2 size={16}/></button></div><p>{item.explanation}</p><div className="card-meta"><span><b>Evidence:</b> {item.evidence_strength}</span><StatusBadge status={item.status}/></div>{item.supporting_evidence?.length > 0 && <div className="source-box">{item.supporting_evidence.map((s,i) => <div key={i}>“{s.excerpt || 'Source reference supplied'}”</div>)}</div>}{item.missing_evidence?.length > 0 && <div className="missing-list">{item.missing_evidence.map(x => <span key={x}><FileWarning size={14}/>{x}</span>)}</div>}<div className="inline-edit"><label>Status<select value={item.status} onChange={e => dispatch(updateCause({id:item.id,patch:{status:e.target.value}}))}><option>Suggested</option><option>Under Investigation</option><option>Evidence Supported</option><option>Rejected</option></select></label></div></article>)}</div>}</section>
}

export function EvidenceChecklist({ items = [] }) {
  const dispatch = useDispatch()
  return <section className="panel"><div className="section-title"><div><span className="step">04</span><h2>Evidence still required</h2><p>These records may help investigate a hypothesis; they are not proof.</p></div></div><div className="evidence-list">{items.map(item => <article className="evidence-item" key={item.id}><div className="evidence-icon"><FileWarning size={20}/></div><div><h3>{item.evidence_required}</h3><p>{item.reason}</p><small>Suggested record: {item.suggested_record}</small></div><div className="evidence-controls"><StatusBadge status={item.priority}/><select value={item.status} onChange={e => dispatch(updateEvidence({id:item.id,patch:{status:e.target.value}}))}><option>Pending</option><option>Received</option><option>Reviewed</option><option>Not Applicable</option></select></div></article>)}{!items.length && <div className="empty-state">No further evidence suggestions yet.</div>}</div></section>
}

export function CapaCards({ items = [] }) {
  const dispatch = useDispatch()
  return <section className="panel">
    <div className="section-title"><div><span className="step">05</span><h2>CAPA recommendations</h2><p>Recommendations are editable decision support—not a guarantee of compliance.</p></div><button className="btn secondary" onClick={() => dispatch(addCapa())}><Plus size={16}/> Add action</button></div>
    <div className="capa-list">{items.map(item => <article className="capa-card" key={item.id}>
      <div className="capa-top"><span className={`action-type ${item.action_type.toLowerCase().replaceAll(' ','-')}`}>{item.action_type}</span><span className="capa-id">{item.id}</span><button className="icon-btn danger" onClick={() => dispatch(removeCapa(item.id))}><Trash2 size={16}/></button></div>
      <textarea value={item.recommended_action} placeholder="Recommended action" onChange={e => dispatch(updateCapa({ id:item.id, patch:{ recommended_action:e.target.value } }))}/><p>{item.reason}</p>
      <div className="capa-fields">
        <label>Priority<select value={item.priority} onChange={e => dispatch(updateCapa({ id:item.id, patch:{ priority:e.target.value } }))}><option>High</option><option>Medium</option><option>Low</option></select></label>
        <label>Department<input value={item.responsible_department || ''} onChange={e => dispatch(updateCapa({ id:item.id, patch:{ responsible_department:e.target.value || null } }))}/></label>
        <label>Target date<input type="date" value={item.target_completion_date || ''} onChange={e => dispatch(updateCapa({ id:item.id, patch:{ target_completion_date:e.target.value || null } }))}/></label>
        <label>Status<select value={item.status} onChange={e => dispatch(updateCapa({ id:item.id, patch:{ status:e.target.value } }))}><option>Proposed</option><option>In Progress</option><option>Completed</option><option>Rejected</option></select></label>
      </div>
    </article>)}{!items.length && <div className="empty-state">No CAPA recommendations yet.</div>}</div>
  </section>
}

export function ReviewCheck({ analysis }) { return <div className="review-check"><CheckCircle2 size={19}/><span>{analysis.root_causes.filter(c => c.status === 'Confirmed by Investigator').length} root cause(s) confirmed by the investigator</span></div> }
