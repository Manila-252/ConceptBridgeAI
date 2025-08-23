import { useState } from 'react'

const API = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export default function App() {
  const [message, setMessage] = useState('')
  const [prompt, setPrompt] = useState('Explain backpropagation like I am 12.')
  const [answer, setAnswer] = useState('Backprop is how neural nets learn by adjusting weights.')
  const [out, setOut] = useState<any>(null)

  async function call(path: string, body?: unknown) {
    const r = await fetch(`${API}${path}`, {
      method: body ? 'POST' : 'GET',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    })
    const j = await r.json()
    setOut(j)
  }

  return (
    <main style={{ fontFamily: 'system-ui', maxWidth: 800, margin: '40px auto', lineHeight: 1.5 }}>
      <h1>ConceptBridge AI (Hackathon)</h1>
      <p>Minimal UI that calls the backend for echo, predict, and assess.</p>

      <section style={{ display: 'grid', gap: 12, marginBlock: 20 }}>
        <div>
          <label>Echo message</label><br/>
          <input value={message} onChange={e => setMessage(e.target.value)} placeholder="Hello team!" style={{ width: '100%', padding: 8 }}/>
          <button onClick={() => call('/echo', { message })} style={{ marginTop: 8 }}>Send /echo</button>
        </div>

        <div>
          <label>Simulation prompt</label><br/>
          <input value={prompt} onChange={e => setPrompt(e.target.value)} style={{ width: '100%', padding: 8 }}/>
          <button onClick={() => call('/predict', { prompt })} style={{ marginTop: 8 }}>Generate /predict</button>
        </div>

        <div>
          <label>Your answer</label><br/>
          <input value={answer} onChange={e => setAnswer(e.target.value)} style={{ width: '100%', padding: 8 }}/>
          <button onClick={() => call('/assess', { answer, rubric: 'clarity, correctness, completeness' })} style={{ marginTop: 8 }}>Score /assess</button>
        </div>
      </section>

      <pre style={{ background: '#f6f6f6', padding: 12, borderRadius: 8, minHeight: 120, overflow: 'auto' }}>
        {out ? JSON.stringify(out, null, 2) : 'Output will appear here...'}
      </pre>
    </main>
  )
}
