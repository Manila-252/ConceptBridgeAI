import { useState } from 'react'
import { predict } from '../lib/api'

export default function CreateScenario() {
  const [prompt, setPrompt] = useState('Explain backpropagation like I am 12.')
  const [out, setOut] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string>('')

  async function onGenerate() {
    setLoading(true); setErr('')
    try {
      const res = await predict(prompt)
      setOut(res)
    } catch (e:any) {
      setErr(String(e.message || e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="card">
      <h2>Create Scenario</h2>
      <label>Concept prompt</label>
      <textarea value={prompt} onChange={e => setPrompt(e.target.value)} className="input" rows={4} />
      <button onClick={onGenerate} disabled={loading} className="btn">
        {loading ? 'Generating...' : 'Generate'}
      </button>
      {err && <div className="error">{err}</div>}
      {out && (
        <pre className="pre">{JSON.stringify(out, null, 2)}</pre>
      )}
    </section>
  )
}
