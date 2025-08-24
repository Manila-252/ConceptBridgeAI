// import { assess, predict } from '../lib/api'

type Step = 1 | 2 | 3

// export default function Wizard() {
//     const [step, setStep] = useState<Step>(1)
//     const [prompt, setPrompt] = useState('Explain overfitting with a classroom analogy.')
//     const [simulation, setSimulation] = useState('')
//     const [answer, setAnswer] = useState('Overfitting is when the model memorizes training data.')
//     const [result, setResult] = useState<any>(null)
//     const [loading, setLoading] = useState(false)

//     function next() { setStep(s => (s < 3 ? (s + 1) as Step : s)) }
//     function back() { setStep(s => (s > 1 ? (s - 1) as Step : s)) }

//     async function genSimulation() {
//         setLoading(true)
//         const res = await predict(prompt)
//         setSimulation(res.simulation || JSON.stringify(res, null, 2))
//         addToTimeline({ type: 'scenario', detail: simulation, ts: Date.now() })
//         setLoading(false)
//     }

//     async function score() {
//         setLoading(true)
//         const res = await assess(answer)
//         setResult(res)
//         addToTimeline({ type: 'assessment', detail: JSON.stringify(res), ts: Date.now() })
//         setLoading(false)
//     }

//     return (
//         <section className="card">
//             <h2>⚡ 3-Step Wizard</h2>

//             {step === 1 && (
//                 <div>
//                     <label>Concept prompt</label>
//                     <textarea className="input" rows={3} value={prompt} onChange={e => setPrompt(e.target.value)} />
//                     <button className="btn" onClick={async () => { await genSimulation(); next(); }}>Next → Generate</button>
//                 </div>
//             )}

//             {step === 2 && (
//                 <div>
//                     <h3>Scenario</h3>
//                     <pre className="pre">{simulation}</pre>
//                     <button className="btn" onClick={back}>← Back</button>
//                     <button className="btn" onClick={next}>Next</button>
//                 </div>
//             )}

//             {step === 3 && (
//                 <div>
//                     <label>Your answer</label>
//                     <textarea className="input" rows={3} value={answer} onChange={e => setAnswer(e.target.value)} />
//                     <button className="btn" onClick={back}>← Back</button>
//                     <button className="btn" onClick={score}>Submit & Score</button>
//                     {result && <pre className="pre">{JSON.stringify(result, null, 2)}</pre>}
//                 </div>
//             )}
//         </section>
//     )
// }

// type TimelineItem = { type: 'scenario' | 'assessment'; detail: string; ts: number }
// function addToTimeline(item: TimelineItem) {
//     try {
//         const k = 'cb.timeline'
//         const existing = JSON.parse(localStorage.getItem(k) || '[]')
//         existing.unshift(item)
//         localStorage.setItem(k, JSON.stringify(existing.slice(0, 30)))
//     } catch { }
// }
