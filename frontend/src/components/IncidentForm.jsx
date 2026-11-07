import { useDispatch, useSelector } from 'react-redux'
import { setTitle, updateIncidentField } from '../features/investigationSlice'

const fields = [
  ['deviation_id', 'Deviation ID'], ['incident_title', 'Incident title'], ['product_name', 'Product name'], ['api_name', 'API name'], ['batch_number', 'Batch number'], ['department', 'Department'], ['equipment_id', 'Equipment ID'], ['process_stage', 'Process stage'], ['manufacturing_date', 'Manufacturing date'], ['incident_date', 'Incident date'], ['expected_parameter', 'Expected parameter / value'], ['actual_parameter', 'Actual observed value'], ['specification_limits', 'Specification limits'], ['immediate_actions', 'Immediate actions taken'], ['reported_impact', 'Reported impact']
]
export default function IncidentForm() {
  const { analysis, title } = useSelector(s => s.investigation.current); const dispatch = useDispatch(); const incident = analysis.incident
  return <section className="panel incident-panel"><div className="section-title"><div><span className="step">01</span><h2>Extracted incident information</h2><p>Review and correct the source-grounded fields before analysing.</p></div><span className="editable-note">All fields editable</span></div>
    <label className="title-input"><span>Investigation title</span><input value={title} onChange={e => dispatch(setTitle(e.target.value))}/></label>
    <div className="form-grid">{fields.map(([key, label]) => <label key={key} className={['incident_title','immediate_actions','reported_impact'].includes(key) ? 'span-2' : ''}><span>{label}<small className={`basis ${incident[key]?.basis || 'unavailable'}`}>{incident[key]?.basis === 'source_fact' ? 'Source fact' : incident[key]?.basis === 'inference' ? 'Inference' : 'Unavailable'}</small></span><input value={incident[key]?.value || ''} placeholder="Not stated" onChange={e => dispatch(updateIncidentField({key, value: e.target.value}))}/>{incident[key]?.source?.excerpt && <em>“{incident[key].source.excerpt}”</em>}</label>)}</div>
    <label className="description"><span>Incident description</span><textarea value={incident.incident_description?.value || ''} placeholder="Not stated" onChange={e => dispatch(updateIncidentField({key: 'incident_description', value: e.target.value}))}/></label>
  </section>
}
