import React, { useState, useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router'

const QueryResponse = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const query = location.state?.query || ''
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [displayedAnswer, setDisplayedAnswer] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [followUpQuery, setFollowUpQuery] = useState('')
  const answerRef = useRef(null)

  // Redirect if no query
  useEffect(() => {
    if (!query) {
      navigate('/')
    }
  }, [query, navigate])

  // Fetch answer from backend
  useEffect(() => {
    if (!query) return

    const fetchAnswer = async () => {
      setLoading(true)
      setError(null)
      setDisplayedAnswer('')
      setIsTyping(false)

      try {
        const response = await fetch('http://localhost:8000/ask', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query }),
        })

        if (!response.ok) {
          throw new Error(`Server error: ${response.status}`)
        }

        const data = await response.json()
        setAnswer(data.answer || 'No answer was generated.')
        setSources(data.sources || [])
      } catch (err) {
        setError(err.message || 'Failed to get a response. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchAnswer()
  }, [query])

  // Typing animation
  useEffect(() => {
    if (!answer || loading) return

    setIsTyping(true)
    let index = 0
    const speed = 12 // ms per character

    const interval = setInterval(() => {
      setDisplayedAnswer(answer.slice(0, index + 1))
      index++
      if (index >= answer.length) {
        clearInterval(interval)
        setIsTyping(false)
      }
    }, speed)

    return () => clearInterval(interval)
  }, [answer, loading])

  // Auto-scroll as answer types
  useEffect(() => {
    if (answerRef.current) {
      answerRef.current.scrollTop = answerRef.current.scrollHeight
    }
  }, [displayedAnswer])

  const handleFollowUp = (e) => {
    e.preventDefault()
    if (!followUpQuery.trim()) return
    navigate('/response', { state: { query: followUpQuery.trim() }, replace: true })
    setFollowUpQuery('')
    // Force re-fetch by resetting state
    setAnswer('')
    setSources([])
    setLoading(true)
  }

  const handleNewSearch = () => {
    navigate('/')
  }

  // Format answer text with basic markdown-like rendering
  const formatAnswer = (text) => {
    if (!text) return null

    const lines = text.split('\n')
    return lines.map((line, i) => {
      // Headers
      if (line.startsWith('### ')) {
        return <h3 key={i} className="text-lg font-semibold text-gray-900 mt-5 mb-2">{line.replace('### ', '')}</h3>
      }
      if (line.startsWith('## ')) {
        return <h2 key={i} className="text-xl font-bold text-gray-900 mt-6 mb-3">{line.replace('## ', '')}</h2>
      }
      if (line.startsWith('# ')) {
        return <h1 key={i} className="text-2xl font-bold text-gray-900 mt-6 mb-3">{line.replace('# ', '')}</h1>
      }
      // Bullet points
      if (line.startsWith('- ') || line.startsWith('* ')) {
        return (
          <div key={i} className="flex items-start gap-2 my-1 ml-2">
            <span className="text-[#7b9cce] mt-1.5 text-xs">●</span>
            <span className="text-gray-700 leading-relaxed">{line.slice(2)}</span>
          </div>
        )
      }
      // Numbered lists
      if (/^\d+\.\s/.test(line)) {
        const num = line.match(/^(\d+)\./)[1]
        const content = line.replace(/^\d+\.\s/, '')
        return (
          <div key={i} className="flex items-start gap-3 my-1.5 ml-2">
            <span className="bg-[#7b9cce]/10 text-[#7b9cce] text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5">{num}</span>
            <span className="text-gray-700 leading-relaxed">{content}</span>
          </div>
        )
      }
      // Bold text inline
      if (line.includes('**')) {
        const parts = line.split(/\*\*(.*?)\*\*/g)
        return (
          <p key={i} className="text-gray-700 leading-relaxed my-1">
            {parts.map((part, j) => j % 2 === 1 ? <strong key={j} className="text-gray-900 font-semibold">{part}</strong> : part)}
          </p>
        )
      }
      // Empty lines
      if (line.trim() === '') {
        return <div key={i} className="h-3" />
      }
      // Regular paragraph
      return <p key={i} className="text-gray-700 leading-relaxed my-1">{line}</p>
    })
  }

  return (
    <div className="min-h-screen flex flex-col font-sans text-gray-900 bg-white">
      {/* Header */}
      <header className="flex justify-between items-center p-4 border-b border-gray-100">
        <button onClick={handleNewSearch} className="flex items-center gap-2 group">
          <div className="bg-[#1a56db] p-1.5 rounded-lg group-hover:scale-105 transition-transform">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect width="18" height="18" x="3" y="3" rx="2"/>
              <path d="M7 9h.01"/><path d="M17 9h.01"/><path d="M9 15h6"/>
            </svg>
          </div>
          <span className="font-bold text-xl tracking-tight">AI Dashboard</span>
        </button>
        <div className="flex items-center gap-3">
          <button
            onClick={handleNewSearch}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-900 bg-gray-50 hover:bg-gray-100 px-4 py-2 rounded-full text-sm font-medium transition-all"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
            </svg>
            Home
          </button>
          <button className="p-2 rounded-full bg-gray-50 hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-900">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col w-full max-w-4xl mx-auto px-4 py-8">
        {/* Query Display */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-[#7b9cce]/10 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7b9cce" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </div>
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Your Query</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-gray-900 leading-snug">{query}</h1>
        </div>

        {/* Divider */}
        <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent mb-8" />

        {/* Answer Section */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="bg-[#1a56db]/10 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1a56db" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
              </svg>
            </div>
            <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">AI Response</span>
            {isTyping && (
              <span className="flex items-center gap-1 text-xs text-[#7b9cce] font-medium">
                <span className="w-1.5 h-1.5 bg-[#7b9cce] rounded-full animate-pulse" />
                Generating...
              </span>
            )}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="bg-gray-50/50 border border-gray-100 rounded-2xl p-8">
              <div className="flex flex-col items-center justify-center gap-4">
                {/* Animated spinner */}
                <div className="relative w-12 h-12">
                  <div className="absolute inset-0 border-2 border-gray-200 rounded-full" />
                  <div
                    className="absolute inset-0 border-2 border-transparent border-t-[#7b9cce] rounded-full animate-spin"
                  />
                </div>
                <div className="text-center">
                  <p className="text-gray-700 font-medium text-sm">Analyzing your query...</p>
                  <p className="text-gray-400 text-xs mt-1">Our AI agent is researching and formulating a response</p>
                </div>
                {/* Animated progress dots */}
                <div className="flex items-center gap-4 mt-2">
                  {[{text: 'Searching knowledge base', anim: 'animate-dot-pulse-0'}, {text: 'Analyzing context', anim: 'animate-dot-pulse-1'}, {text: 'Generating answer', anim: 'animate-dot-pulse-2'}].map((step, i) => (
                    <div key={i} className="flex items-center gap-1.5">
                      <div
                        className={`w-1.5 h-1.5 rounded-full bg-[#7b9cce] ${step.anim}`}
                      />
                      <span className="text-xs text-gray-400">{step.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="bg-red-50 border border-red-100 rounded-2xl p-6">
              <div className="flex items-start gap-3">
                <div className="bg-red-100 p-2 rounded-lg shrink-0 mt-0.5">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
                </div>
                <div>
                  <h3 className="text-red-800 font-semibold text-sm mb-1">Something went wrong</h3>
                  <p className="text-red-600 text-sm mb-3">{error}</p>
                  <button
                    onClick={() => window.location.reload()}
                    className="text-red-700 hover:text-red-900 text-sm font-medium underline underline-offset-2 transition-colors"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Answer Content */}
          {!loading && !error && (
            <div
              ref={answerRef}
              className="bg-gray-50/50 border border-gray-100 rounded-2xl p-6 md:p-8 max-h-[60vh] overflow-y-auto scroll-smooth"
            >
              <div className="prose prose-gray max-w-none">
                {formatAnswer(displayedAnswer)}
                {isTyping && (
                  <span className="inline-block w-0.5 h-5 bg-[#7b9cce] ml-0.5 align-middle animate-blink" />
                )}
              </div>
            </div>
          )}
        </div>

        {/* Sources Section */}
        {!loading && !error && sources.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="bg-green-50 p-2 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
              </div>
              <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">Sources</span>
              <span className="bg-gray-100 text-gray-500 text-xs font-medium px-2 py-0.5 rounded-full">{sources.length}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sources.map((source, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-xl hover:shadow-sm hover:border-gray-200 transition-all cursor-pointer group"
                >
                  <div className="bg-gray-50 group-hover:bg-[#7b9cce]/10 p-2 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 group-hover:text-[#7b9cce] transition-colors"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-700 truncate">{source}</p>
                    <p className="text-xs text-gray-400">Referenced document</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Follow-up Search */}
        {!loading && !error && (
          <div className="mt-auto pt-4">
            <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-200 to-transparent mb-6" />
            <form onSubmit={handleFollowUp}>
              <div className="w-full flex items-center bg-white border border-gray-200 rounded-full px-2 py-2 shadow-sm focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300 transition-all">
                <div className="pl-4 pr-2 text-[#7b9cce]">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
                  </svg>
                </div>
                <input
                  type="text"
                  value={followUpQuery}
                  onChange={(e) => setFollowUpQuery(e.target.value)}
                  placeholder="Ask a follow-up question..."
                  className="flex-1 outline-none text-sm text-gray-700 bg-transparent placeholder-gray-400 min-w-0"
                />
                <button
                  type="submit"
                  className="flex items-center gap-1.5 bg-[#7b9cce] hover:bg-[#6888bb] text-white px-5 py-2 rounded-full text-sm font-medium transition-colors disabled:opacity-50"
                  disabled={!followUpQuery.trim()}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m5 12 7-7 7 7"/><path d="M12 19V5"/></svg>
                  Ask
                </button>
              </div>
            </form>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center p-6 text-xs text-gray-400 mt-auto pb-8 border-t border-gray-50">
        AI responses may not always be accurate. Please verify important information.
      </footer>
    </div>
  )
}

export default QueryResponse
