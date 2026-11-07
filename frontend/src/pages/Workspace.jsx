import { BrainCircuit, Network, Save, Sparkles } from 'lucide-react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { runAnalysis, saveInvestigation, setMethod } from '../features/investigationSlice'
import IncidentForm from '../components/IncidentForm'
import FiveWhysBuilder from '../components/FiveWhysBuilder'
import FishboneDiagram from '../components/FishboneDiagram'
import { CapaCards, EvidenceChecklist, RootCauseCards } from '../components/AnalysisCards'
import Loading from '../components/Loading'

export default function Workspace() {
  const { current, loading, saving } = useSelector(s=>s.investigation); const dispatch=useDispatch(); const a=current.analysis
  async function analyze(){ await dispatch(runAnalysis()) }
  return <div className="page workspace"><section className="workflow-bar"><div className="workflow-copy"><span className="eyebrow teal">AI-ASSISTED WORKFLOW</span><h2>{current.title}</h2><p>{current.source_text ? 'Incident report loaded; review extracted data, then generate cautious investigation suggestions.' : 'Load an incident report to begin.'}</p></div><div className="workflow-actions"><button className="btn secondary" disabled={saving} onClick={()=>dispatch(saveInvestigation())}><Save size={16}/>{saving?'Saving…':'Save draft'}</button><Link className="btn primary" to="/review">Review investigation</Link></div></section><IncidentForm/><section className="panel method-picker"><div><span className="step">02</span><h2>Choose an investigation lens</h2><p>Both methods produce hypotheses—not confirmed causes.</p></div><div className="method-buttons"><button className={a.method==='five_whys'?'method selected':'method'} onClick={()=>dispatch(setMethod('five_whys'))}><BrainCircuit size={22}/><span><b>Five Whys</b><small>Trace a causal chain</small></span></button><button className={a.method==='fishbone'?'method selected':'method'} onClick={()=>dispatch(setMethod('fishbone'))}><Network size={22}/><span><b>Fishbone</b><small>Explore six factor groups</small></span></button></div><button className="btn primary analyze" onClick={analyze} disabled={loading || !current.source_text}><Sparkles size={16}/>{loading?'Running workflow…':'Generate RCA analysis'}</button></section>{loading&&<Loading label="LangGraph is extracting, analysing evidence needs, and creating editable suggestions…"/>}{!loading&&<>{a.method==='five_whys'?<FiveWhysBuilder steps={a.five_whys} busy={loading} onRegenerate={analyze}/>:<FishboneDiagram categories={a.fishbone}/>}<RootCauseCards items={a.root_causes}/><EvidenceChecklist items={a.missing_evidence}/><CapaCards items={a.capa_actions}/></>}</div>
}
