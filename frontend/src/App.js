import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Globe, ChevronDown, ChevronUp, Download, Loader2, Filter, Info, ExternalLink } from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [url, setUrl] = useState('');
  const [options, setOptions] = useState({
    max_pages: 30,
    max_depth: 2,
    mode: 'domain',
    include_subdomains: false,
    language: ''
  });
  const [jobId, setJobId] = useState(null);
  const [jobData, setJobData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minScore: 0,
    ngram: 0,
    search: '',
    source: ''
  });
  const [selectedKeyword, setSelectedKeyword] = useState(null);

  useEffect(() => {
    let interval;
    if (jobId && jobData?.status !== 'completed' && jobData?.status !== 'failed') {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE}/results/${jobId}`);
          setJobData(res.data);
        } catch (err) {
          console.error("Error fetching job status", err);
        }
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [jobId, jobData?.status]);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setJobId(null);
    setJobData(null);
    setSelectedKeyword(null);
    try {
      const res = await axios.post(`${API_BASE}/analyze`, {
        url,
        ...options,
        language: options.language || null
      });
      setJobId(res.data.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start analysis");
      setLoading(false);
    }
  };

  const filteredKeywords = (jobData?.keywords || []).filter(k => {
    const matchesScore = k.score >= filters.minScore;
    const matchesNgram = filters.ngram === 0 || k.phrase.split(' ').length === filters.ngram;
    const matchesSearch = k.phrase.toLowerCase().includes(filters.search.toLowerCase());
    const matchesSource = !filters.source || (k.source_mix[filters.source] > 0);
    return matchesScore && matchesNgram && matchesSearch && matchesSource;
  });

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Search className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-gray-900">SEO Keyword Extractor</h1>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span className="flex items-center"><Globe className="w-4 h-4 mr-1" /> Built with FastAPI & React</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Input Section */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">Website URL</label>
                <input
                  type="url"
                  required
                  placeholder="https://example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <div className="md:w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Pages</label>
                <input
                  type="number"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  value={options.max_pages}
                  onChange={(e) => setOptions({...options, max_pages: parseInt(e.target.value)})}
                />
              </div>
              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={loading && jobData?.status !== 'completed' && jobData?.status !== 'failed'}
                  className="w-full md:w-auto bg-indigo-600 text-white px-8 py-2 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 transition flex items-center justify-center"
                >
                  {loading && jobData?.status !== 'completed' && jobData?.status !== 'failed' ? (
                    <><Loader2 className="w-5 h-5 mr-2 animate-spin" /> Analyzing...</>
                  ) : 'Start Analysis'}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Crawl Mode</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none text-sm"
                  value={options.mode}
                  onChange={(e) => setOptions({...options, mode: e.target.value})}
                >
                  <option value="domain">Full Domain</option>
                  <option value="single">Single Page</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Depth</label>
                <input
                  type="number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none text-sm"
                  value={options.max_depth}
                  onChange={(e) => setOptions({...options, max_depth: parseInt(e.target.value)})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg outline-none text-sm"
                  value={options.language}
                  onChange={(e) => setOptions({...options, language: e.target.value})}
                >
                  <option value="">Auto-detect</option>
                  <option value="en">English</option>
                  <option value="bg">Bulgarian</option>
                </select>
              </div>
              <div className="flex items-center pt-6">
                <input
                  type="checkbox"
                  id="subdomains"
                  className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  checked={options.include_subdomains}
                  onChange={(e) => setOptions({...options, include_subdomains: e.target.checked})}
                />
                <label htmlFor="subdomains" className="ml-2 text-sm text-gray-700">Include subdomains</label>
              </div>
            </div>
          </form>
          {error && <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm border border-red-100">{error}</div>}
        </section>

        {/* Status / Results Section */}
        {jobData && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h2 className="text-xl font-bold">Results for {jobData.url}</h2>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                  jobData.status === 'completed' ? 'bg-green-100 text-green-700' :
                  jobData.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                }`}>
                  {jobData.status}
                </span>
              </div>
              {jobData.status === 'completed' && (
                <a
                  href={`${API_BASE}/results/${jobId}/export.csv`}
                  className="flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-800 transition"
                >
                  <Download className="w-4 h-4 mr-1" /> Export CSV
                </a>
              )}
            </div>

            {jobData.status === 'failed' && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
                <strong>Error:</strong> {jobData.error}
              </div>
            )}

            {(jobData.status === 'crawling' || jobData.status === 'analyzing') && (
              <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-gray-200 shadow-sm">
                <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mb-4" />
                <p className="text-gray-600 font-medium">Processing your request...</p>
                <p className="text-sm text-gray-400">This might take a few minutes depending on the site size.</p>
              </div>
            )}

            {jobData.status === 'completed' && (
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Filters Sidebar */}
                <div className="lg:col-span-1 space-y-6">
                  <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-4">
                    <h3 className="font-bold flex items-center"><Filter className="w-4 h-4 mr-2" /> Filters</h3>
                    
                    <div>
                      <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Search Keywords</label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        placeholder="Filter by phrase..."
                        value={filters.search}
                        onChange={(e) => setFilters({...filters, search: e.target.value})}
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Min Score: {filters.minScore}</label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                        value={filters.minScore}
                        onChange={(e) => setFilters({...filters, minScore: parseInt(e.target.value)})}
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Phrase Length</label>
                      <div className="flex flex-wrap gap-2">
                        {[0, 1, 2, 3, 4].map(n => (
                          <button
                            key={n}
                            onClick={() => setFilters({...filters, ngram: n})}
                            className={`px-3 py-1 rounded-md text-xs font-medium border transition ${
                              filters.ngram === n ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-600 border-gray-300 hover:border-indigo-400'
                            }`}
                          >
                            {n === 0 ? 'All' : `${n}-gram`}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-gray-500 uppercase mb-2">Source Zone</label>
                      <select
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm outline-none"
                        value={filters.source}
                        onChange={(e) => setFilters({...filters, source: e.target.value})}
                      >
                        <option value="">Anywhere</option>
                        <option value="title">Title</option>
                        <option value="h1">H1 Tag</option>
                        <option value="h2">H2/H3 Tags</option>
                        <option value="body">Body Text</option>
                        <option value="anchor">Anchor Text</option>
                      </select>
                    </div>
                  </div>

                  {selectedKeyword && (
                    <div className="bg-indigo-50 p-6 rounded-xl border border-indigo-100 shadow-sm animate-in fade-in slide-in-from-bottom-4 duration-300">
                      <div className="flex justify-between items-start mb-4">
                        <h3 className="font-bold text-indigo-900 text-lg leading-tight">{selectedKeyword.phrase}</h3>
                        <button onClick={() => setSelectedKeyword(null)} className="text-indigo-400 hover:text-indigo-600">×</button>
                      </div>
                      <div className="space-y-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-indigo-600">Intent:</span>
                          <span className="font-semibold text-indigo-900 capitalize">{selectedKeyword.intent}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-indigo-600">Top Page:</span>
                          <a href={selectedKeyword.top_page} target="_blank" rel="noreferrer" className="text-indigo-900 truncate ml-4 hover:underline flex items-center">
                            Visit <ExternalLink className="w-3 h-3 ml-1" />
                          </a>
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-indigo-600 uppercase">Zone Distribution</span>
                          <div className="mt-2 space-y-1">
                            {Object.entries(selectedKeyword.source_mix).map(([zone, count]) => (
                              <div key={zone} className="flex items-center justify-between text-xs">
                                <span className="text-indigo-800 capitalize">{zone.replace('_', ' ')}</span>
                                <span className="font-bold text-indigo-900">{count}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Table */}
                <div className="lg:col-span-3">
                  <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                          <th className="px-6 py-4">Keyword</th>
                          <th className="px-6 py-4">Score</th>
                          <th className="px-6 py-4">Vol (Occur)</th>
                          <th className="px-6 py-4">Pages</th>
                          <th className="px-6 py-4 text-right">Intent</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {filteredKeywords.map((kw, idx) => (
                          <tr
                            key={idx}
                            className={`hover:bg-indigo-50/30 cursor-pointer transition ${selectedKeyword?.phrase === kw.phrase ? 'bg-indigo-50' : ''}`}
                            onClick={() => setSelectedKeyword(kw)}
                          >
                            <td className="px-6 py-4 font-medium text-gray-900">{kw.phrase}</td>
                            <td className="px-6 py-4">
                              <div className="flex items-center">
                                <span className="mr-2 font-semibold">{kw.score}</span>
                                <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${kw.score}%` }}></div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-gray-600">{kw.occurrences}</td>
                            <td className="px-6 py-4 text-gray-600">{kw.pages_count}</td>
                            <td className="px-6 py-4 text-right">
                              <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${
                                kw.intent === 'commercial' ? 'bg-orange-100 text-orange-700' :
                                kw.intent === 'navigational' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-600'
                              }`}>
                                {kw.intent}
                              </span>
                            </td>
                          </tr>
                        ))}
                        {filteredKeywords.length === 0 && (
                          <tr>
                            <td colSpan="5" className="px-6 py-12 text-center text-gray-500">No keywords found matching the filters.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
