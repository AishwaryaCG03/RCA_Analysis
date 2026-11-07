import { ArrowLeft, CheckCircle2, RotateCcw, Save, Send, ShieldCheck, XCircle } from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { saveInvestigation, submitReview } from '../features/investigationSlice'
import { ReviewCheck } from '../components/AnalysisCards'
import StatusBadge from '../components/StatusBadge'
import '../review.css'

export default function Review() {
  const { current, saving } = useSelector(s => s.investigation)
  const dispatch = useDispatch()
  const analysis = current.analysis

  async function transition(action, role, rootCauseId) {
    if (!current.id) {
      const saved = await dispatch(saveInvestigation())
      if (!saveInvestigation.fulfilled.match(saved)) return
    }
    await dispatch(submitReview({ action, role, rootCauseId }))
  }

  return <div className="page narrow">
    <div className="review-head"><div><Link to="/workspace" className="back"><ArrowLeft size={16}/> Back to workspace</Link><span className="eyebrow">HUMAN REVIEW</span><h2>Confirm the investigation record.</h2><p>Approval is deliberately separate from AI generation.</p></div><StatusBadge status={current.status}/></div>
    <section className="panel review-panel">
      <ReviewCheck analysis={analysis}/>
      <div className="review-summary"><article><h3>Incident</h3><p>{analysis.incident.incident_description?.value || 'No incident description entered.'}</p><dl><dt>Product</dt><dd>{analysis.incident.product_name?.value || '—'}</dd><dt>Batch</dt><dd>{analysis.incident.batch_number?.value || '—'}</dd><dt>Method</dt><dd>{analysis.method === 'five_whys' ? 'Five Whys' : 'Fishbone'}</dd></dl></article><article><h3>Investigation findings</h3><strong>{analysis.root_causes.length}</strong><span>candidate root cause(s)</span><strong>{analysis.missing_evidence.length}</strong><span>evidence item(s) to collect</span><strong>{analysis.capa_actions.length}</strong><span>editable CAPA action(s)</span></article></div>
      <div className="review-guardrail"><ShieldCheck size={20}/><p><b>Investigator accountability:</b> confirm a root cause only after qualified review of supporting evidence. This tool does not approve quality decisions or establish regulatory compliance.</p></div>
      {analysis.root_causes.length > 0 && <div className="confirmation-list"><h3>Root-cause confirmation</h3>{analysis.root_causes.map(cause => <div className="confirmation-item" key={cause.id}><div><b>{cause.description}</b><small>{cause.evidence_strength} · {cause.status}</small></div>{cause.status === 'Confirmed by Investigator' ? <StatusBadge status={cause.status}/> : <button className="btn secondary" disabled={saving} onClick={() => transition('confirm_root_cause', 'investigator', cause.id)}><CheckCircle2 size={15}/> Confirm root cause</button>}</div>)}</div>}
      <div className="review-actions"><button className="btn secondary" disabled={saving} onClick={() => dispatch(saveInvestigation())}><Save size={16}/> Save as draft</button><button className="btn secondary" disabled={saving} onClick={() => transition('submit')}><Send size={16}/> Submit for review</button><button className="btn success" disabled={saving || !current.id} onClick={() => transition('approve', 'qa_approver')}><CheckCircle2 size={16}/> Approve as QA</button><button className="btn ghost-danger" disabled={saving || !current.id} onClick={() => transition('return')}><RotateCcw size={16}/> Return to investigation</button><button className="btn ghost-danger" disabled={saving || !current.id} onClick={() => transition('reject')}><XCircle size={16}/> Reject</button></div>
    </section>
  </div>
}
