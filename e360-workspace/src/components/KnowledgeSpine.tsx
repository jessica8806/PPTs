import { Search, FileText, ChevronRight, Clock, Database } from 'lucide-react';
import { useState } from 'react';
import { knowledgeItems } from '../data/mockData';
import type { KnowledgeItem, DomainType } from '../types';

interface KnowledgeSpineProps {
  filterDomain?: DomainType;
}

const domainBadgeClass = {
  revenue: 'domain-badge-revenue',
  solutions: 'domain-badge-solutions',
  partners: 'domain-badge-partners',
  delivery: 'domain-badge-delivery',
  strategy: 'domain-badge-strategy',
};

export function KnowledgeSpine({ filterDomain }: KnowledgeSpineProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [...new Set(knowledgeItems.map((item) => item.category))];

  const filteredItems = knowledgeItems.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.excerpt.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDomain = !filterDomain || item.domain === filterDomain;
    const matchesCategory = !selectedCategory || item.category === selectedCategory;
    return matchesSearch && matchesDomain && matchesCategory;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Knowledge Spine</h2>
          <p className="text-slate-500 text-sm mt-1">
            The single source of truth for e360 positioning, offerings, and insights
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Database className="w-5 h-5 text-slate-400" />
          <span className="text-sm text-slate-500">{knowledgeItems.length} items</span>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-slate-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-e360-accent focus:border-transparent"
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              !selectedCategory
                ? 'bg-e360-primary text-white'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            All
          </button>
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category === selectedCategory ? null : category)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-e360-primary text-white'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {category}
            </button>
          ))}
        </div>
      </div>

      {/* Knowledge Items */}
      <div className="grid gap-4">
        {filteredItems.map((item) => (
          <KnowledgeCard key={item.id} item={item} />
        ))}
      </div>

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No knowledge items match your search</p>
        </div>
      )}
    </div>
  );
}

function KnowledgeCard({ item }: { item: KnowledgeItem }) {
  const badgeClass = domainBadgeClass[item.domain];

  return (
    <div className="card p-5 hover:shadow-md transition-shadow cursor-pointer group">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              {item.category}
            </span>
            <span className={`domain-badge ${badgeClass} capitalize`}>{item.domain}</span>
          </div>
          <h3 className="font-semibold text-slate-900 group-hover:text-e360-accent transition-colors">
            {item.title}
          </h3>
          <p className="text-slate-600 text-sm mt-2 leading-relaxed">{item.excerpt}</p>
          <div className="flex items-center gap-1 mt-3 text-xs text-slate-400">
            <Clock className="w-3.5 h-3.5" />
            <span>Updated {item.lastUpdated}</span>
          </div>
        </div>
        <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-e360-accent transition-colors flex-shrink-0" />
      </div>
    </div>
  );
}
