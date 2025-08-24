// src/pages/DeeperInsight.tsx
import { useSearchParams } from 'react-router-dom'

export default function DeeperInsight() {
    const [params] = useSearchParams()
    const professionId = params.get('profession_id')

    return (
        <div className="min-h-screen bg-gray-800 text-white p-8">
            <h1 className="text-3xl font-bold mb-4">🔍 Insights for Profession #{professionId}</h1>
            {/* Add deeper quiz inputs or second-layer API stuff here */}
        </div>
    )
}
