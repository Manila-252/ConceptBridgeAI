// src/components/Timeline.tsx
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getProfessions, Profession } from '../lib/api'

export default function Timeline() {
    const [professions, setProfessions] = useState<Profession[]>([])
    const [selectedId, setSelectedId] = useState<number | null>(null)
    const [error, setError] = useState<string | null>(null)
    const navigate = useNavigate()

    useEffect(() => {
        getProfessions()
            .then(setProfessions)
            .catch(err => setError(err.message))
    }, [])

    const selectedProfession = professions.find(p => p.id === selectedId)

    const handleContinue = () => {
        if (selectedId !== null) {
            navigate(`/deeper-insight?profession_id=${selectedId}`)
        }
    }

    return (
        <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-6">
            <h2 className="text-4xl font-bold mb-6">🎯 Choose Your Profession</h2>
            {error && <p className="text-red-500 mb-4">{error}</p>}

            <select
                className="mb-4 px-4 py-2 text-black rounded shadow"
                value={selectedId ?? ''}
                onChange={e => setSelectedId(Number(e.target.value))}
            >
                <option value="" disabled>Select a profession</option>
                {professions.map(p => (
                    <option key={p.id} value={p.id}>
                        {p.name}
                    </option>
                ))}
            </select>

            {selectedProfession && (
                <div className="bg-white bg-opacity-10 p-6 rounded-lg shadow-md mb-4 max-w-lg w-full text-center">
                    <h3 className="text-2xl font-semibold mb-2">{selectedProfession.name}</h3>
                    <p>{selectedProfession.description}</p>
                </div>
            )}

            {selectedId !== null && (
                <button
                    onClick={handleContinue}
                    className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded text-white transition"
                >
                    Continue
                </button>
            )}
        </div>
    )
}
