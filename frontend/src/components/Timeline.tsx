import { useEffect, useState } from 'react';

type Item = { type: 'scenario' | 'assessment'; detail: string; ts: number }

export default function Timeline() {
    const [items, setItems] = useState<Item[]>([])

    useEffect(() => {
        const k = 'cb.timeline'
        try {
            const data = JSON.parse(localStorage.getItem(k) || '[]')
            setItems(data)
        } catch { setItems([]) }
    }, [])

    function clear() {
        localStorage.removeItem('cb.timeline')
        setItems([])
    }

    return (
        <section className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <h2>Timeline</h2>
                <button className="btn" onClick={clear}>Clear</button>
            </div>
            <ul style={{ listStyle: 'none', padding: 0 }}>
                {items.length === 0 && <li>No items yet — try the Wizard</li>}
                {items.map((it, i) => (
                    <li key={i} style={{ marginBottom: 12 }}>
                        <strong>{it.type}</strong> — {new Date(it.ts).toLocaleTimeString()}
                        <pre className="pre">{it.detail}</pre>
                    </li>
                ))}
            </ul>
        </section>
    )
}
