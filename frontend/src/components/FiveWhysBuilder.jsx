import { Check, RefreshCw, X } from 'lucide-react'
import { useDispatch } from 'react-redux'
import { updateWhy } from '../features/investigationSlice'

export default function FiveWhysBuilder({ steps, onRegenerate, busy }) {
  const dispatch = useDispatch()
  if (!steps?.length) return <div className="empty-state">Choose <b>Five Whys</b> and run analysis to develop evidence-based questions.</div>
  return <section className="panel"><div className="section-title"><div><span className="step">02A</span><h2>Five Whys analysis</h2><p>Suggested answers are not findings until the investigator confirms them.</p></div><button className="btn secondary" disabled={busy} onClick={onRegenerate}><RefreshCw size={16}/> Regenerate</button></div>
    <div className="why-list">{steps.map((item, i) => <div className="why-row" key={item.level}><div className="why-number">{i + 1}</div><div className="why-body"><label>Why question<input value={item.question} onChange={e => dispatch(updateWhy({id: item.level, patch:{question:e.target.value}}))}/></label><label>Suggested answer<textarea value={item.suggested_answer || ''} onChange={e => dispatch(updateWhy({id: item.level, patch:{suggested_answer:e.target.value}}))}/></label><p className="rationale">{item.rationale}</p><div className="evidence-row">{item.needs_further_investigation ? <span className="status status-under-investigation">Further evidence required</span> : <span className="status status-evidence-supported">Evidence cited</span>}<button onClick={() => dispatch(updateWhy({id:item.level, patch:{investigator_decision:'Confirmed'}}))}><Check size={14}/> Confirm</button><button onClick={() => dispatch(updateWhy({id:item.level, patch:{investigator_decision:'Rejected'}}))}><X size={14}/> Reject</button></div></div></div>)}</div>
  </section>
}
