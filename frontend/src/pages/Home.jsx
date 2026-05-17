import React, { useState } from 'react'
import { useNavigate } from 'react-router'

const Home = () => {
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const handleSearch = (e) => {
    e?.preventDefault()
    if (!query.trim()) return
    navigate('/response', { state: { query: query.trim() } })
  }

  const handleSuggestion = (text) => {
    navigate('/response', { state: { query: text } })
  }
  return (
    <div className="min-h-screen flex flex-col font-sans text-gray-900 bg-white">
      {/* Header */}
      <header className="flex justify-between items-center p-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="bg-[#1a56db] p-1.5 rounded-lg">
             {/* Robot icon approx */}
             <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect width="18" height="18" x="3" y="3" rx="2"/>
                <path d="M7 9h.01"/><path d="M17 9h.01"/><path d="M9 15h6"/>
             </svg>
          </div>
          <span className="font-bold text-xl tracking-tight">AI Dashboard</span>
        </div>
        <div className="flex items-center gap-4 text-gray-500">
          <button className="hover:text-gray-900 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
          <button className="p-1 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col items-center pt-24 px-4 w-full max-w-5xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-bold mb-4 text-center">How can I help you today?</h1>
        <p className="text-gray-500 text-lg mb-10 text-center">Ask questions, analyze documents, or get instant insights powered by AI.</p>

        {/* Search Bar */}
        <div className="w-full max-w-3xl flex items-center bg-white border border-gray-200 rounded-full px-2 py-2 shadow-sm focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-300 transition-all mb-6">
          <div className="pl-4 pr-2 text-[#7b9cce]">
             <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/></svg>
          </div>
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch(e)}
            placeholder="Ask anything or search your documents..." 
            className="flex-1 outline-none text-base text-gray-700 bg-transparent placeholder-gray-400 min-w-0"
          />
          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1.5 text-gray-500 hover:text-gray-800 px-3 py-2 text-sm font-medium transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
              Upload
            </button>
            <button onClick={handleSearch} className="flex items-center gap-1.5 bg-[#7b9cce] hover:bg-[#6888bb] text-white px-5 py-2.5 rounded-full text-sm font-medium transition-colors disabled:opacity-50" disabled={!query.trim()}>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              Search
            </button>
          </div>
        </div>

        {/* Suggestions */}
        <div className="flex flex-wrap items-center justify-center gap-3 mb-12">
          <span className="text-gray-500 text-sm">Try:</span>
          <button onClick={() => handleSuggestion('Summarize my documents')} className="bg-gray-50 hover:bg-gray-100 border border-gray-100 text-gray-600 px-4 py-1.5 rounded-full text-sm transition-colors">
            Summarize my documents
          </button>
          <button onClick={() => handleSuggestion('Find key insights')} className="bg-gray-50 hover:bg-gray-100 border border-gray-100 text-gray-600 px-4 py-1.5 rounded-full text-sm transition-colors">
            Find key insights
          </button>
          <button onClick={() => handleSuggestion('Compare reports')} className="bg-gray-50 hover:bg-gray-100 border border-gray-100 text-gray-600 px-4 py-1.5 rounded-full text-sm transition-colors">
            Compare reports
          </button>
        </div>

        {/* Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 w-full">
          {/* Card 1 */}
          <div className="flex flex-col items-center text-center p-6 rounded-2xl border border-gray-100 bg-white hover:shadow-sm transition-shadow cursor-pointer">
            <div className="text-gray-400 mb-4 bg-gray-50 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>
            </div>
            <h3 className="font-semibold text-gray-900 text-sm mb-1">Analyze Document</h3>
            <p className="text-gray-500 text-xs">Extract insights from your files</p>
          </div>
          
          {/* Card 2 */}
          <div className="flex flex-col items-center text-center p-6 rounded-2xl border border-gray-100 bg-white hover:shadow-sm transition-shadow cursor-pointer">
            <div className="text-gray-400 mb-4 bg-gray-50 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <h3 className="font-semibold text-gray-900 text-sm mb-1">Start Conversation</h3>
            <p className="text-gray-500 text-xs">Chat with your AI assistant</p>
          </div>

          {/* Card 3 */}
          <div className="flex flex-col items-center text-center p-6 rounded-2xl border border-gray-100 bg-white hover:shadow-sm transition-shadow cursor-pointer">
            <div className="text-gray-400 mb-4 bg-gray-50 p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
            </div>
            <h3 className="font-semibold text-gray-900 text-sm mb-1">Quick Summary</h3>
            <p className="text-gray-500 text-xs">Get instant document summaries</p>
          </div>

          {/* Card 4 */}
          <div className="flex flex-col items-center text-center p-6 rounded-2xl border border-gray-100 bg-white hover:shadow-sm transition-shadow cursor-pointer">
            <div className="text-gray-400 mb-4 bg-gray-50 p-2 rounded-lg">
               <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1.3.5 2.6 1.5 3.5.8.8 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></svg>
            </div>
            <h3 className="font-semibold text-gray-900 text-sm mb-1">Generate Ideas</h3>
            <p className="text-gray-500 text-xs">Brainstorm with AI assistance</p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center p-6 text-xs text-gray-400 mt-auto pb-8 border-t border-gray-50">
        AI responses may not always be accurate. Please verify important information.
      </footer>
    </div>
  )
}

export default Home