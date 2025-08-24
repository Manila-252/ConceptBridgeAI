
// Two-step flow: Profession → Learn Studio (Topic/Subtopic/Custom) → AI explanation



import React, { useEffect, useMemo, useState } from "react";

// ====== Config ======
const API_BASE: string = (import.meta as any).env?.VITE_API_BASE || "http://localhost:8000/api/v1";

// ====== Types aligned with backend schemas ======
export type DifficultyLevel = "beginner" | "intermediate" | "advanced";

export interface Profession {
  id: number;
  name: string;
  description?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface Topic {
  id: number;
  name: string;
  description?: string | null;
  icon?: string | null;     // e.g., "🚀"
  color?: string | null;    // hex like "#3B82F6"
  created_at: string;
  updated_at?: string | null;
}

export interface Subtopic {
  id: number;
  topic_id: number;
  name: string;
  description?: string | null;
  difficulty_level: DifficultyLevel;
  estimated_time_minutes?: number | null;
  prerequisites?: string | null; // JSON string of prerequisite subtopic IDs
  created_at: string;
  updated_at?: string | null;
}

export interface QuickAnalogyResponse {
  concept: string;
  profession_context: string;
  analogy_title: string;
  explanation: string;
  practical_examples: string[];
  key_connections: string[];
  next_steps: string[];
  generation_time: number;
  tokens_allocated?: number | null;
  response_length?: "short" | "medium" | "long" | null;
}

// ====== Lightweight API client ======
async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${text ? `: ${text}` : ""}`);
  }
  return res.json();
}

const getHealth = () => api<{ status: string; api_version?: string }>(`/health`);
const listProfessions = () => api<Profession[]>(`/professions/`);
const listTopics = () => api<Topic[]>(`/topics/`);

async function listSubtopicsByTopic(topicId: number): Promise<Subtopic[]> {
  // Try /topics/{id}/subtopics first; fall back to /subtopics?topic_id=
  try {
    return await api<Subtopic[]>(`/topics/${topicId}/subtopics`);
  } catch {
    return await api<Subtopic[]>(`/subtopics?topic_id=${topicId}`);
  }
}

async function quickExplain(
  profession: string,
  concept: string,
  options?: {
    context?: string;
    creativity_level?: number;  // 1-5
    max_tokens?: number;        // 300-3000 per schema (safe default 1200)
    response_length?: "short" | "medium" | "long";
  }
): Promise<QuickAnalogyResponse> {
  const body = {
    profession,
    concept,
    context: options?.context ?? null,
    creativity_level: options?.creativity_level ?? 3,
    max_tokens: options?.max_tokens ?? 1200,
    response_length: options?.response_length ?? "medium",
  };
  return api<QuickAnalogyResponse>(`/analogies/quick-explain`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ====== Small UI primitives ======
const Pill: React.FC<{ children: React.ReactNode; className?: string; title?: string }> = ({ children, className = "", title }) => (
  <span title={title} className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${className}`}>
    {children}
  </span>
);

const Card: React.FC<{ children: React.ReactNode; className?: string }>= ({ children, className = "" }) => (
  <div className={`rounded-2xl shadow-sm border border-gray-200 bg-white ${className}`}>{children}</div>
);

const SectionTitle: React.FC<{ children: React.ReactNode }>= ({ children }) => (
  <h2 className="text-lg font-semibold text-gray-800 mb-3">{children}</h2>
);

const Spinner: React.FC = () => (
  <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-transparent" />
);

function difficultyClasses(level: DifficultyLevel) {
  switch (level) {
    case "beginner":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "intermediate":
      return "bg-blue-50 text-blue-700 border-blue-200";
    case "advanced":
      return "bg-violet-50 text-violet-700 border-violet-200";
  }
}

function colorStyle(hex?: string | null) {
  if (!hex) return {} as React.CSSProperties;
  return { borderColor: hex, boxShadow: `0 0 0 3px ${hex}22` } as React.CSSProperties;
}

// ====== Step 1: Profession Select ======
const ProfessionStep: React.FC<{
  onContinue: (profession: Profession) => void;
}> = ({ onContinue }) => {
  const [health, setHealth] = useState<string>("checking");
  const [items, setItems] = useState<Profession[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Profession | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const h = await getHealth();
        setHealth(h.status || "unknown");
      } catch {
        setHealth("unhealthy");
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const data = await listProfessions();
        setItems(data);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🧠</span>
          <h1 className="text-xl font-bold tracking-tight">ConceptBridgeAI</h1>
        </div>
        {health === "checking" ? (
          <div className="flex items-center gap-2 text-gray-500">
            <Spinner /><span className="text-sm">Checking API…</span>
          </div>
        ) : health === "healthy" ? (
          <Pill className="bg-emerald-50 text-emerald-700 border-emerald-200">API Healthy</Pill>
        ) : (
          <Pill className="bg-rose-50 text-rose-700 border-rose-200">API Unhealthy</Pill>
        )}
      </div>

      <Card className="p-6">
        <SectionTitle>🎯 Choose your profession</SectionTitle>

        {/* Dropdown */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700">Profession:</label>
          <select
            className="mt-1 w-full rounded-xl border-gray-300 focus:ring-blue-500 focus:border-blue-500"
            value={selected?.id ?? ""}
            onChange={(e) => {
              const id = Number(e.target.value);
              const found = items.find((p) => p.id === id) || null;
              setSelected(found);
            }}
          >
            <option value="" disabled>Select…</option>
            {items.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        {/* Or grid list */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {loading ? (
            <div className="col-span-2 flex items-center gap-2 text-gray-500">
              <Spinner /><span>Loading…</span>
            </div>
          ) : items.map((p) => {
              const active = selected?.id === p.id;
              return (
                <button
                  type="button"
                  key={p.id}
                  onClick={() => setSelected(p)}
                  className={`text-left rounded-2xl border p-4 hover:shadow-sm transition ${active ? "border-blue-500 ring-2 ring-blue-500/20 bg-blue-50" : "border-gray-200 bg-white"}`}
                >
                  <div className="font-medium text-gray-900">{p.name}</div>
                  {p.description && <div className="text-sm text-gray-600 mt-1 line-clamp-2">{p.description}</div>}
                </button>
              );
            })}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            disabled={!selected}
            onClick={() => selected && onContinue(selected)}
            className={`inline-flex items-center rounded-xl px-4 py-2 text-white font-medium ${selected ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-400 cursor-not-allowed"}`}
          >
            Continue →
          </button>
        </div>
      </Card>
    </div>
  );
};

// ====== Step 2: Learn Studio (Topic → Subtopic/Custom → Generate) ======
const LearnStudio: React.FC<{ profession: Profession; onBack: () => void }> = ({ profession, onBack }) => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [subtopics, setSubtopics] = useState<Subtopic[]>([]);
  const [loading, setLoading] = useState({ topics: true, subs: false, gen: false });
  const [error, setError] = useState<string | null>(null);

  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [selectedSubtopic, setSelectedSubtopic] = useState<Subtopic | null>(null);

  const [customConcept, setCustomConcept] = useState("");
  const [customContext, setCustomContext] = useState("");
  const [creativity, setCreativity] = useState(3);
  const [responseLength, setResponseLength] = useState<"short" | "medium" | "long">("medium");

  const [result, setResult] = useState<QuickAnalogyResponse | null>(null);

  // load topics
  useEffect(() => {
    (async () => {
      setLoading((s) => ({ ...s, topics: true }));
      try {
        const data = await listTopics();
        setTopics(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading((s) => ({ ...s, topics: false }));
      }
    })();
  }, []);

  // load subtopics when topic changes
  useEffect(() => {
    (async () => {
      setSubtopics([]);
      setSelectedSubtopic(null);
      setResult(null);
      if (!selectedTopic) return;
      setLoading((s) => ({ ...s, subs: true }));
      try {
        const subs = await listSubtopicsByTopic(selectedTopic.id);
        setSubtopics(subs);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading((s) => ({ ...s, subs: false }));
      }
    })();
  }, [selectedTopic?.id]);

  const readyToGenerate = useMemo(() => {
    return !!profession && (customConcept.trim().length > 0 || !!selectedSubtopic?.name);
  }, [profession, customConcept, selectedSubtopic]);

  async function handleGenerate() {
    if (!readyToGenerate) return;
    const concept = customConcept.trim() || selectedSubtopic?.name || "";
    setLoading((s) => ({ ...s, gen: true }));
    setError(null);
    setResult(null);
    try {
      const data = await quickExplain(profession.name, concept, {
        context: customContext || undefined,
        creativity_level: creativity,
        response_length: responseLength,
        max_tokens: responseLength === "short" ? 600 : responseLength === "medium" ? 1200 : 2000,
      });
      setResult(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading((s) => ({ ...s, gen: false }));
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <button onClick={onBack} className="rounded-xl border px-3 py-1.5 text-sm hover:bg-gray-50">← Back</button>
          <h1 className="text-xl font-bold tracking-tight">Learn Studio</h1>
        </div>
        <Pill className="bg-gray-50 text-gray-700 border-gray-200">Profession: {profession.name}</Pill>
      </div>

      {error && (
        <Card className="p-4 mb-4">
          <div className="text-rose-700 text-sm">{String(error)}</div>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left column: Topic & Subtopic */}
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-4">
            <SectionTitle>Pick a topic</SectionTitle>
            {loading.topics ? (
              <div className="flex items-center gap-2 text-gray-500"><Spinner /><span>Loading topics…</span></div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {topics.map((t) => {
                  const active = selectedTopic?.id === t.id;
                  return (
                    <button
                      key={t.id}
                      onClick={() => setSelectedTopic(t)}
                      className={`rounded-2xl border p-3 text-center hover:shadow-sm transition ${active ? "bg-white ring-2 ring-offset-2 ring-blue-500" : "bg-white"}`}
                      style={colorStyle(t.color)}
                    >
                      <div className="text-2xl">{t.icon || "📚"}</div>
                      <div className="mt-1 text-sm font-medium text-gray-900">{t.name}</div>
                      {t.description && <div className="mt-1 text-xs text-gray-600 line-clamp-2">{t.description}</div>}
                    </button>
                  );
                })}
              </div>
            )}
          </Card>

          <Card className="p-4">
            <SectionTitle>Choose a subtopic (or type your own concept)</SectionTitle>

            {/* Custom concept */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700">Custom concept (optional)</label>
              <input
                value={customConcept}
                onChange={(e) => setCustomConcept(e.target.value)}
                placeholder="e.g., Recursion, Binary Trees, Kepler orbits…"
                className="mt-1 w-full rounded-xl border-gray-300 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="mt-1 text-xs text-gray-500">Leave empty and select a subtopic below if you prefer curated options.</p>
            </div>

            {!selectedTopic ? (
              <div className="text-sm text-gray-500">Pick a topic to see available subtopics.</div>
            ) : loading.subs ? (
              <div className="flex items-center gap-2 text-gray-500"><Spinner /><span>Loading subtopics…</span></div>
            ) : subtopics.length === 0 ? (
              <div className="text-sm text-gray-500">No subtopics found for this topic.</div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {subtopics.map((s) => {
                  const active = selectedSubtopic?.id === s.id;
                  return (
                    <button
                      key={s.id}
                      onClick={() => setSelectedSubtopic(s)}
                      className={`text-left rounded-2xl border p-4 hover:shadow-sm transition ${active ? "border-blue-500 ring-2 ring-blue-500/20 bg-blue-50" : "border-gray-200 bg-white"}`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="font-medium text-gray-900">{s.name}</div>
                        <Pill className={difficultyClasses(s.difficulty_level)} title={`Difficulty: ${s.difficulty_level}`}>
                          {s.difficulty_level}
                        </Pill>
                      </div>
                      {s.description && <div className="text-sm text-gray-600 mt-1 line-clamp-2">{s.description}</div>}
                      <div className="mt-2 flex items-center gap-3 text-xs text-gray-500">
                        {typeof s.estimated_time_minutes === "number" && <span>⏱️ {s.estimated_time_minutes} min</span>}
                        {s.prerequisites && <span title="Prerequisites listed">✔️ prereqs</span>}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </Card>
        </div>

        {/* Right column: Options & Generate */}
        <div className="space-y-4">
          <Card className="p-4">
            <SectionTitle>Personalize & generate</SectionTitle>
            <div>
              <label className="block text-sm font-medium text-gray-700">Additional context (optional)</label>
              <textarea
                value={customContext}
                onChange={(e) => setCustomContext(e.target.value)}
                rows={4}
                placeholder="Tell the AI what to emphasize (e.g., 'use analogies for kids; show one code example')."
                className="mt-1 w-full rounded-xl border-gray-300 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">Creativity</label>
              <input
                type="range"
                min={1}
                max={5}
                value={creativity}
                onChange={(e) => setCreativity(Number(e.target.value))}
                className="w-full"
              />
              <div className="text-xs text-gray-500 mt-1">{creativity} / 5</div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">Response length</label>
              <select
                value={responseLength}
                onChange={(e) => setResponseLength(e.target.value as any)}
                className="mt-1 w-full rounded-xl border-gray-300 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long</option>
              </select>
            </div>

            <button
              onClick={handleGenerate}
              disabled={!readyToGenerate || loading.gen}
              className={`mt-4 w-full inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2 text-white font-medium transition ${readyToGenerate && !loading.gen ? "bg-blue-600 hover:bg-blue-700" : "bg-gray-400 cursor-not-allowed"}`}
            >
              {loading.gen ? <Spinner /> : "Generate explanation"}
            </button>
          </Card>

          {result && (
            <Card className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-sm text-gray-500">Concept</div>
                  <h3 className="text-lg font-semibold text-gray-900">{result.concept}</h3>
                  <div className="mt-1 text-sm text-gray-600">Profession context: {result.profession_context}</div>
                </div>
                <Pill className="bg-gray-50 text-gray-700 border-gray-200">{result.generation_time.toFixed(2)}s</Pill>
              </div>

              <div className="mt-4">
                <div className="text-sm text-gray-500">Analogy</div>
                <div className="text-base font-medium text-gray-900">{result.analogy_title}</div>
                <div className="prose prose-sm max-w-none mt-2">
                  {result.explanation.split(/\n+/).map((para, idx) => (
                    <p key={idx} className="text-gray-800">{para}</p>
                  ))}
                </div>
              </div>

              {(result.practical_examples?.length || 0) > 0 && (
                <div className="mt-4">
                  <div className="text-sm font-medium text-gray-700">Practical examples</div>
                  <ul className="list-disc pl-5 text-gray-800 mt-1 space-y-1">
                    {result.practical_examples.map((ex, i) => (<li key={i}>{ex}</li>))}
                  </ul>
                </div>
              )}

              {(result.key_connections?.length || 0) > 0 && (
                <div className="mt-4">
                  <div className="text-sm font-medium text-gray-700">Key connections</div>
                  <ul className="list-disc pl-5 text-gray-800 mt-1 space-y-1">
                    {result.key_connections.map((k, i) => (<li key={i}>{k}</li>))}
                  </ul>
                </div>
              )}

              {(result.next_steps?.length || 0) > 0 && (
                <div className="mt-4">
                  <div className="text-sm font-medium text-gray-700">Next steps</div>
                  <ul className="list-disc pl-5 text-gray-800 mt-1 space-y-1">
                    {result.next_steps.map((n, i) => (<li key={i}>{n}</li>))}
                  </ul>
                </div>
              )}
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

// ====== Top-level wrapper to switch steps ======
const ConceptBridgeApp: React.FC = () => {
  const [selectedProfession, setSelectedProfession] = useState<Profession | null>(null);

  return (
    <div className="min-h-screen bg-gray-50">
      {!selectedProfession ? (
        <ProfessionStep onContinue={setSelectedProfession} />
      ) : (
        <LearnStudio profession={selectedProfession} onBack={() => setSelectedProfession(null)} />
      )}
      <footer className="max-w-6xl mx-auto px-4 py-8 text-center text-xs text-gray-500">
        Backend: <code>{API_BASE}</code>
      </footer>
    </div>
  );
};

export default ConceptBridgeApp;
