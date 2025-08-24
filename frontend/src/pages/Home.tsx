import { useEffect, useState } from 'react'
import { getRoot } from '../lib/api'

export default function Home() {
  const [info, setInfo] = useState<any>(null)
  const [err, setErr] = useState<string>('')

  useEffect(() => {
    getRoot().then(setInfo).catch(e => setErr(String(e)))
  }, [])

  return (
    <section className="card">
      <h1>Welcome 👋</h1>
      <p>Use ConceptBridge AI to turn tough topics into quick scenarios and get feedback fast.</p>
      {err && <div className="error">{err}</div>}
      {info && (
        <pre className="pre">{JSON.stringify(info, null, 2)}</pre>
      )}
      <ol className="steps">
        <li><strong>Create</strong>: Enter a concept to generate a scenario.</li>
        <li><strong>Simulate</strong>: Review the generated scenario.</li>
        <li><strong>Assess</strong>: Submit your answer and get feedback.</li>
      </ol>
    </section>
  )
}
