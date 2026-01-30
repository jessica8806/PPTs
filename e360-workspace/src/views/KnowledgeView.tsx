import { KnowledgeSpine } from '../components/KnowledgeSpine';
import { Database, Plus, Upload } from 'lucide-react';

export function KnowledgeView() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-5 h-5 text-slate-500" />
            <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">
              Central Repository
            </span>
          </div>
          <h1 className="text-3xl font-semibold text-slate-900">Knowledge Spine</h1>
          <p className="text-slate-500 mt-1 max-w-2xl">
            The institutional memory of e360. Everything the organization knows—positioning,
            offerings, case studies, and insights—connected and searchable.
          </p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors">
            <Upload className="w-4 h-4" />
            Import
          </button>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-e360-primary text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors">
            <Plus className="w-4 h-4" />
            Add Item
          </button>
        </div>
      </div>

      {/* Categories Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: 'Positioning', count: 4, color: 'bg-slate-500' },
          { label: 'Solutions', count: 8, color: 'bg-blue-500' },
          { label: 'Case Studies', count: 12, color: 'bg-emerald-500' },
          { label: 'Partners', count: 6, color: 'bg-purple-500' },
          { label: 'Verticals', count: 5, color: 'bg-orange-500' },
        ].map((category) => (
          <div
            key={category.label}
            className="card p-4 hover:shadow-md transition-shadow cursor-pointer"
          >
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${category.color}`} />
              <span className="text-sm font-medium text-slate-700">{category.label}</span>
            </div>
            <p className="text-2xl font-semibold text-slate-900">{category.count}</p>
            <p className="text-xs text-slate-500">items</p>
          </div>
        ))}
      </div>

      {/* Main Knowledge Spine */}
      <KnowledgeSpine />
    </div>
  );
}
