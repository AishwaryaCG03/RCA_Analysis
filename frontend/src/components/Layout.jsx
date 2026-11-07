import { Activity, ClipboardCheck, FilePlus2, History, LayoutDashboard, ShieldCheck } from 'lucide-react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { clearNotice, resetInvestigation } from '../features/investigationSlice'

const links = [
  ['/', LayoutDashboard, 'Overview'], ['/new', FilePlus2, 'New investigation'], ['/workspace', Activity, 'RCA workspace'], ['/review', ClipboardCheck, 'Review & approval'], ['/history', History, 'Investigation history']
]

export default function Layout() {
  const { error, notice, current } = useSelector(s => s.investigation); const dispatch = useDispatch(); const navigate = useNavigate()
  function startNew() { dispatch(resetInvestigation()); navigate('/new') }
  return <div className="app-shell">
    <aside className="sidebar"><div className="brand"><span className="brand-mark">A</span><span>AIVOA<span className="brand-ai">.ai</span></span></div><div className="side-label">QUALITY INTELLIGENCE</div>
      <nav>{links.map(([to, Icon, label]) => <NavLink key={to} to={to} className={({isActive}) => `nav-link ${isActive ? 'active' : ''}`}><Icon size={18}/>{label}</NavLink>)}</nav>
      <div className="sidebar-footer"><div className="compliance"><ShieldCheck size={17}/><span>Human review required</span></div><button className="new-side" onClick={startNew}><FilePlus2 size={16}/> New RCA</button></div>
    </aside>
    <main className="main-content"><header className="topbar"><div><div className="eyebrow">ROOT CAUSE ANALYSIS</div><h1>{current.id ? current.investigation_number || 'Saved investigation' : 'Investigation workspace'}</h1></div><div className="user-chip"><span className="avatar">QI</span><span>Quality Investigator</span></div></header>
      {notice && <div className="toast success"><span>{notice}</span><button onClick={() => dispatch(clearNotice())}>×</button></div>}
      {error && <div className="toast error"><span>{error}</span><button onClick={() => dispatch(clearNotice())}>×</button></div>}
      <Outlet />
    </main>
  </div>
}
