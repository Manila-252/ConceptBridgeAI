const API = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export async function getRoot() {
  const r = await fetch(`${API}/`)
  if (!r.ok) throw new Error('API error')
  return r.json()
}

export async function echo(message: string) {
  const r = await fetch(`${API}/echo`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
  return r.json()
}

export async function predict(prompt: string) {
  const r = await fetch(`${API}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  })
  return r.json()
}

export async function assess(answer: string, rubric = 'clarity, correctness, completeness') {
  const r = await fetch(`${API}/assess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answer, rubric })
  })
  return r.json()
}
