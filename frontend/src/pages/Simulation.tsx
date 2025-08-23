import { useState } from 'react'
import { predict } from '../lib/api'

export default function Simulation() {
  const [prompt, setPrompt] = useState('Illustrate gradient descent on a bowl-shaped loss.')
  const [sim, setSim] = useState<string>('')
  const [loading, setLoading] = useState(false)

  async function run() {
    setLoading(true)
    const res = await predict(prompt)
    setSim(res.simulation || JSON.stringify(res, null, 2))
    setLoading(false)
  }

  return (
    <section className="card">
      <h2>Simulation</h2>
      <label>Prompt</label>
      <input value={prompt} onChange={e => setPrompt(e.target.value)} className="input" />
      <button onClick={run} disabled={loading} className="btn">{loading ? 'Running...' : 'Run'}</button>
      {sim && (
        <pre className="pre">{sim}</pre>
      )}
    </section>
  )
}
