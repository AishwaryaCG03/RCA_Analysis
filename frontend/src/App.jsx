import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NewInvestigation from './pages/NewInvestigation'
import Workspace from './pages/Workspace'
import Review from './pages/Review'
import History from './pages/History'
import Detail from './pages/Detail'
export default function App(){return <Routes><Route element={<Layout/>}><Route path="/" element={<Dashboard/>}/><Route path="/new" element={<NewInvestigation/>}/><Route path="/workspace" element={<Workspace/>}/><Route path="/review" element={<Review/>}/><Route path="/history" element={<History/>}/><Route path="/history/:id" element={<Detail/>}/></Route></Routes>}
