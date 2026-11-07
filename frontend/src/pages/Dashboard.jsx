import { ArrowRight, ClipboardList, Clock3, FileCheck2, FilePlus2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { useEffect } from 'react'
import { loadHistory } from '../features/investigationSlice'
import StatusBadge from '../components/StatusBadge'

export default function Dashboard() {
  const { history } = useSelector(s=>s.investigation); const dispatch = useDispatch(); useEffect(()=>{dispatch(loadHistory())},[dispatch])
  const count = status => history.filter(x=>x.status===status).length
  const metrics = [[ClipboardList,'Total investigations',history.length,'all'],[Clock3,'Drafts',count('Draft'),'draft'],[FileCheck2,'Under review',count('Pending Review'),'review'],[FileCheck2,'Completed',count('Closed') + count('Approved'),'complete']]
  return <div className="page dashboard"><section className="hero"><div><span className="eyebrow teal">QUALITY INVESTIGATION HUB</span><h2>Move from deviation to an evidence-led decision.</h2><p>AI supports extraction and investigation. Qualified people assess evidence and own every final decision.</p></div><Link to="/new" className="btn primary"><FilePlus2 size={17}/> Start an investigation</Link></section><section className="metric-grid">{metrics.map(([Icon,label,value,kind])=><article className={`metric ${kind}`} key={label}><Icon size={21}/><div><span>{label}</span><strong>{value}</strong></div></article>)}</section><section className="panel recent"><div className="section-title"><div><span className="step">RECENT</span><h2>Recent investigations</h2><p>Continue reviewing saved RCA records.</p></div><Link to="/history" className="text-link">View all <ArrowRight size={15}/></Link></div>{history.length ? <table><thead><tr><th>Investigation</th><th>Product / batch</th><th>Department</th><th>Status</th><th>Updated</th></tr></thead><tbody>{history.slice(0,5).map(item=><tr key={item.id}><td><Link to={`/history/${item.id}`}>{item.investigation_number}<small>{item.title}</small></Link></td><td>{item.product_name || '—'}<small>{item.batch_number || 'No batch'}</small></td><td>{item.department || '—'}</td><td><StatusBadge status={item.status}/></td><td>{new Date(item.updated_at).toLocaleDateString()}</td></tr>)}</tbody></table> : <div className="empty-state">No saved investigations. Start with an incident report.</div>}</section></div>
}
