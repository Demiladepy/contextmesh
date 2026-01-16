'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, FileCode, Layers, Send, Zap } from 'lucide-react';

interface HealthMetric {
  metric: string;
  score: string;
  value: number;
}

interface RefactorItem {
  file: string;
  issue: string;
  severity: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [agent, setAgent] = useState('architect');

  // Structured Data State
  const [healthScores, setHealthScores] = useState<HealthMetric[]>([
    { metric: "Modularity", score: "A-", value: 85 },
    { metric: "Documentation", score: "C+", value: 65 },
    { metric: "Test Coverage", score: "B", value: 78 }
  ]);
  const [refactorQueue, setRefactorQueue] = useState<RefactorItem[]>([
    { file: "AuthService.ts", issue: "High Coupling", severity: "High" },
    { file: "Global Styles", issue: "Unused CSS variables", severity: "Low" }
  ]);

  const analyzeCode = async () => {
    if (!prompt) return;
    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_path: ".",
          prompt: prompt,
          agent_type: agent
        }),
      });

      const data = await res.json();

      if (data.analysis) {
        // Check if response is JSON (for Architect)
        if (agent === 'architect') {
          try {
            // Try to parse JSON from the markdown block if it's wrapped in ```json ... ```
            let jsonStr = data.analysis;
            const jsonMatch = jsonStr.match(/```json\n([\s\S]*?)\n```/);
            if (jsonMatch) {
              jsonStr = jsonMatch[1];
            }

            const parsed = JSON.parse(jsonStr);

            if (parsed.summary) setResponse(parsed.summary);
            if (parsed.health_scores) setHealthScores(parsed.health_scores);
            if (parsed.refactor_suggestions) setRefactorQueue(parsed.refactor_suggestions);

          } catch (e) {
            console.warn("Failed to parse Architect JSON, falling back to raw text", e);
            setResponse(data.analysis);
          }
        } else {
          setResponse(data.analysis);
        }
      } else {
        setResponse('Error: No analysis returned.');
      }
    } catch (error) {
      setResponse(`Error connecting to backend: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: string) => {
    if (score.startsWith('A')) return 'text-emerald-400';
    if (score.startsWith('B')) return 'text-indigo-400';
    return 'text-amber-400';
  };

  const getBarColor = (score: string) => {
    if (score.startsWith('A')) return 'bg-emerald-500';
    if (score.startsWith('B')) return 'bg-indigo-500';
    return 'bg-amber-500';
  };


  // Polling for Events
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await fetch('http://localhost:8000/events');
        const data = await res.json();
        setEvents(data);
      } catch (e) {
        console.error("Failed to fetch events", e);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-indigo-500/30">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="text-indigo-400 w-6 h-6" />
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              ContextMesh
            </h1>
            <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-medium border border-indigo-500/20">
              v0.1.0 Sprint
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Gemini 1.5 Pro Active
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* Sidebar: Architectural Health & Events */}
        <aside className="lg:col-span-3 space-y-6">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 transition-all hover:border-slate-700">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4" /> Codebase Health
            </h2>
            <div className="space-y-4">
              {healthScores.map((item, idx) => (
                <div key={idx}>
                  <div className="flex justify-between text-sm mb-1">
                    <span>{item.metric}</span>
                    <span className={getScoreColor(item.score)}>{item.score}</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${getBarColor(item.score)} rounded-full transition-all duration-1000 ease-out`}
                      style={{ width: `${item.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 transition-all hover:border-slate-700">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <FileCode className="w-4 h-4" /> Refactor Queue
            </h2>
            <ul className="space-y-3">
              {refactorQueue.map((item, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm p-2 hover:bg-slate-800/50 rounded-lg transition-colors cursor-pointer group">
                  <Zap className={`w-4 h-4 mt-1 ${item.severity === 'High' ? 'text-rose-400' : 'text-amber-400'}`} />
                  <div>
                    <span className="block font-medium text-slate-200 group-hover:text-indigo-300 transition-colors">{item.file}</span>
                    <span className="text-xs text-slate-500">{item.issue}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Live Events Feed */}
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800 transition-all hover:border-slate-700">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" /> Live Webhooks
            </h2>
            <ul className="space-y-3 max-h-60 overflow-y-auto custom-scrollbar">
              {events.length === 0 && <li className="text-xs text-slate-600">No events yet...</li>}
              {events.map((evt, idx) => (
                <li key={idx} className="text-sm p-2 bg-slate-950/50 rounded border border-slate-800/50">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>{evt.type}</span>
                    <span>{new Date(evt.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="font-medium text-indigo-300">{evt.details.title}</div>
                  <div className="text-xs text-slate-400">by {evt.details.user}</div>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        {/* Main Interface */}
        <div className="lg:col-span-9 space-y-6">

          {/* Input Area */}
          <div className="p-1 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 shadow-xl focus-within:border-indigo-500/50 transition-colors">
            <div className="bg-slate-950 rounded-xl p-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Check architectural patterns, ask for a refactor plan, or update docs..."
                className="w-full bg-transparent border-none focus:ring-0 text-slate-200 placeholder-slate-600 resize-none h-32 text-lg"
              />
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-500">Select Agent:</span>
                  <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800">
                    {['Architect', 'Refactorer', 'Documentarian'].map((type) => (
                      <button
                        key={type}
                        onClick={() => setAgent(type.toLowerCase())}
                        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${agent === type.toLowerCase()
                          ? 'bg-indigo-600 text-white shadow-lg'
                          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                          }`}
                      >
                        {type}
                      </button>
                    ))}
                  </div>
                </div>
                <button
                  onClick={analyzeCode}
                  disabled={loading || !prompt}
                  className={`flex items-center gap-2 px-6 py-2 rounded-lg font-semibold transition-all ${loading || !prompt
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg hover:shadow-indigo-500/25 active:scale-95'
                    }`}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Thinking...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Analyze
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Response Area */}
          {response && (
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 animate-in fade-in slide-in-from-bottom-4 duration-500">
              <div className="flex items-center gap-2 mb-4 text-indigo-400">
                <Bot className="w-5 h-5" />
                <h3 className="font-semibold">{agent.charAt(0).toUpperCase() + agent.slice(1)}'s Analysis</h3>
              </div>
              <div className="prose prose-invert prose-indigo max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{response}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
