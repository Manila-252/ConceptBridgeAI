import { useState } from 'react'
// import { assess } from '../lib/api'

// export default function Assessment() {
//   const [answer, setAnswer] = useState('Backprop updates weights to reduce error.')
//   const [res, setRes] = useState<any>(null)
//   const [loading, setLoading] = useState(false)

//   async function onAssess() {
//     setLoading(true)
//     const out = await assess(answer)
//     setRes(out)
//     setLoading(false)
//   }

//   return (
//     <section className="card">
//       <h2>Assessment</h2>
//       <label>Your answer</label>
//       <textarea value={answer} onChange={e => setAnswer(e.target.value)} className="input" rows={4} />
//       <button onClick={onAssess} disabled={loading} className="btn">{loading ? 'Scoring...' : 'Score'}</button>
//       {res && <pre className="pre">{JSON.stringify(res, null, 2)}</pre>}
//     </section>
//   )
// }
