// src/lib/api.ts
const API = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export type Profession = {
  id: number
  name: string
  description?: string
  created_at: string
  updated_at?: string
}

export async function getProfessions(): Promise<Profession[]> {
  const res = await fetch(`${API}/api/v1/professions`)
  if (!res.ok) throw new Error('Failed to fetch professions')
  return res.json()
}
