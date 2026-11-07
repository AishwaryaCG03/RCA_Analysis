import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import { api } from '../services/api'

const emptyField = () => ({ value: null, basis: 'unavailable', source: null })
export const blankIncident = () => Object.fromEntries([
  'deviation_id','product_name','api_name','batch_number','manufacturing_date','incident_date','department','equipment_id','process_stage','incident_title','incident_description','expected_parameter','actual_parameter','specification_limits','immediate_actions','reported_impact'
].map(key => [key, emptyField()]).concat([['supporting_evidence', []], ['extraction_notes', []]]))

const blankAnalysis = () => ({ incident: blankIncident(), method: 'five_whys', five_whys: [], fishbone: [], root_causes: [], missing_evidence: [], capa_actions: [], warnings: [] })
const initialState = { current: { id: null, title: 'New root cause investigation', source_type: 'text', source_text: '', status: 'Draft', analysis: blankAnalysis() }, history: [], loading: false, saving: false, error: null, notice: null }

export const extractIncident = createAsyncThunk('investigation/extract', async ({ sourceType, text, subject, file }) => {
  const form = new FormData(); form.append('source_type', sourceType)
  if (sourceType === 'text') form.append('pasted_text', text)
  if (sourceType === 'email') { form.append('email_subject', subject); form.append('email_body', text) }
  if (sourceType === 'pdf') form.append('file', file)
  const result = await api.extract(form)
  return { result, sourceType, sourceText: sourceType === 'email' ? `Subject: ${subject}\n\n${text}` : text }
})

export const runAnalysis = createAsyncThunk('investigation/analyze', async (_, { getState }) => {
  const { current } = getState().investigation
  return api.analyze({ text: current.source_text, method: current.analysis.method, incident: current.analysis.incident })
})
export const saveInvestigation = createAsyncThunk('investigation/save', async (_, { getState }) => {
  const { current } = getState().investigation
  const payload = { title: current.title, status: current.status, source_type: current.source_type, source_text: current.source_text, analysis: current.analysis }
  return current.id ? api.update(current.id, payload) : api.create(payload)
})
export const loadHistory = createAsyncThunk('investigation/history', api.list)
export const loadInvestigation = createAsyncThunk('investigation/load', api.get)
export const submitReview = createAsyncThunk('investigation/review', async ({ action, comments, rootCauseId, role }, { getState }) => {
  const id = getState().investigation.current.id
  return api.review(id, { action, comments, root_cause_id: rootCauseId }, role)
})

const updateById = (items, id, patch) => items.map(item => item.id === id ? { ...item, ...patch } : item)

const slice = createSlice({
  name: 'investigation', initialState,
  reducers: {
    resetInvestigation: state => { state.current = initialState.current; state.error = null; state.notice = null },
    setSource: (state, { payload }) => { state.current.source_type = payload.sourceType; state.current.source_text = payload.text },
    setTitle: (state, { payload }) => { state.current.title = payload },
    setMethod: (state, { payload }) => { state.current.analysis.method = payload },
    updateIncidentField: (state, { payload }) => { state.current.analysis.incident[payload.key] = { value: payload.value || null, basis: payload.value ? 'source_fact' : 'unavailable', source: state.current.analysis.incident[payload.key]?.source || null } },
    updateWhy: (state, { payload }) => { state.current.analysis.five_whys = state.current.analysis.five_whys.map(item => item.level === payload.id ? { ...item, ...payload.patch } : item) },
    updateCause: (state, { payload }) => { state.current.analysis.root_causes = updateById(state.current.analysis.root_causes, payload.id, payload.patch) },
    updateEvidence: (state, { payload }) => { state.current.analysis.missing_evidence = updateById(state.current.analysis.missing_evidence, payload.id, payload.patch) },
    updateCapa: (state, { payload }) => { state.current.analysis.capa_actions = updateById(state.current.analysis.capa_actions, payload.id, payload.patch) },
    removeCause: (state, { payload }) => { state.current.analysis.root_causes = state.current.analysis.root_causes.filter(x => x.id !== payload) },
    removeCapa: (state, { payload }) => { state.current.analysis.capa_actions = state.current.analysis.capa_actions.filter(x => x.id !== payload) },
    addCapa: state => { state.current.analysis.capa_actions.push({ id: `CAPA-MANUAL-${Date.now()}`, action_type: 'Corrective Action', recommended_action: '', reason: '', related_root_cause_ids: [], priority: 'Medium', responsible_department: null, target_completion_date: null, status: 'Proposed' }) },
    clearNotice: state => { state.notice = null; state.error = null },
  },
  extraReducers: builder => builder
    .addCase(extractIncident.pending, state => { state.loading = true; state.error = null })
    .addCase(extractIncident.fulfilled, (state, { payload }) => { state.loading = false; state.current.source_type = payload.sourceType; state.current.source_text = payload.sourceText; state.current.analysis.incident = payload.result.incident; state.current.title = payload.result.incident.incident_title.value || state.current.title; state.notice = 'Incident fields populated from the AI extraction. Please review them.' })
    .addCase(runAnalysis.pending, state => { state.loading = true; state.error = null })
    .addCase(runAnalysis.fulfilled, (state, { payload }) => { state.loading = false; state.current.analysis = payload; state.notice = 'RCA suggestions generated. All hypotheses remain for human review.' })
    .addCase(saveInvestigation.pending, state => { state.saving = true; state.error = null })
    .addCase(saveInvestigation.fulfilled, (state, { payload }) => { state.saving = false; state.current = { ...state.current, ...payload }; state.notice = `Investigation ${payload.investigation_number} saved.` })
    .addCase(loadHistory.fulfilled, (state, { payload }) => { state.history = payload })
    .addCase(loadInvestigation.pending, state => { state.loading = true })
    .addCase(loadInvestigation.fulfilled, (state, { payload }) => { state.loading = false; state.current = payload })
    .addCase(submitReview.fulfilled, (state, { payload }) => { state.current = { ...state.current, ...payload }; state.notice = `Investigation status updated to ${payload.status}.` })
    .addMatcher(action => action.type.endsWith('/rejected'), (state, action) => { state.loading = false; state.saving = false; state.error = action.error.message || 'Something went wrong.' })
})
export const { resetInvestigation, setSource, setTitle, setMethod, updateIncidentField, updateWhy, updateCause, updateEvidence, updateCapa, removeCause, removeCapa, addCapa, clearNotice } = slice.actions
export default slice.reducer
