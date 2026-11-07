import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { loadInvestigation } from '../features/investigationSlice'
import Loading from '../components/Loading'
import { RootCauseCards, EvidenceChecklist, CapaCards } from '../components/AnalysisCards'
import FishboneDiagram from '../components/FishboneDiagram'
import FiveWhysBuilder from '../components/FiveWhysBuilder'

export default function Detail(){const {id}=useParams(),dispatch=useDispatch(),nav=useNavigate(),{current,loading}=useSelector(s=>s.investigation);useEffect(()=>{dispatch(loadInvestigation(id))},[id,dispatch]);if(loading)return <Loading label="Loading saved investigation…"/>;const a=current.analysis;return <div className="page"><div className="detail-head"><div><Link className="back" to="/history">← Investigation history</Link><span className="eyebrow">{current.investigation_number}</span><h2>{current.title}</h2></div><button className="btn primary" onClick={()=>nav('/workspace')}>Edit in workspace</button></div>{a.method==='fishbone'?<FishboneDiagram categories={a.fishbone}/>:<FiveWhysBuilder steps={a.five_whys} onRegenerate={()=>nav('/workspace')}/>}<RootCauseCards items={a.root_causes}/><EvidenceChecklist items={a.missing_evidence}/><CapaCards items={a.capa_actions}/></div>}
