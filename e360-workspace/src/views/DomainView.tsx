import { useState } from 'react';
import { SignalCard } from '../components/SignalCard';
import { AIAssistant } from '../components/AIAssistant';
import { KnowledgeSpine } from '../components/KnowledgeSpine';
import type { DomainType, Signal } from '../types';
import {
  domainDescriptions,
  revenueSignals,
  solutionsSignals,
  partnersSignals,
  deliverySignals,
  strategySignals,
} from '../data/mockData';
import { MessageSquare, FileText, Lightbulb, Clock } from 'lucide-react';

interface DomainViewProps {
  domain: DomainType;
}

const domainSignals: Record<DomainType, Signal[]> = {
  revenue: revenueSignals,
  solutions: solutionsSignals,
  partners: partnersSignals,
  delivery: deliverySignals,
  strategy: strategySignals,
};

const domainColors: Record<DomainType, string> = {
  revenue: 'bg-emerald-500',
  solutions: 'bg-blue-500',
  partners: 'bg-purple-500',
  delivery: 'bg-orange-500',
  strategy: 'bg-slate-500',
};

export function DomainView({ domain }: DomainViewProps) {
  const [activeTab, setActiveTab] = useState<'signals' | 'assistant' | 'knowledge'>('signals');
  const config = domainDescriptions[domain];
  const signals = domainSignals[domain];
  const colorClass = domainColors[domain];

  const tabs = [
    { id: 'signals', label: 'Current Signals', icon: Lightbulb },
    { id: 'assistant', label: 'Assistant', icon: MessageSquare },
    { id: 'knowledge', label: 'Knowledge', icon: FileText },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className={`w-3 h-3 rounded-full ${colorClass}`} />
          <span className="text-sm font-medium text-slate-500 uppercase tracking-wider">
            {domain} Domain
          </span>
        </div>
        <h1 className="text-3xl font-semibold text-slate-900">{config.title}</h1>
        <p className="text-slate-500 mt-1">{config.description}</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-xl w-fit">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Content */}
      <div className="min-h-[600px]">
        {activeTab === 'signals' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-slate-900">Active Signals</h2>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Clock className="w-4 h-4" />
                  <span>Updated 2 hours ago</span>
                </div>
              </div>

              <div className="space-y-4">
                {signals.map((signal) => (
                  <SignalCard key={signal.id} signal={signal} />
                ))}
              </div>

              {signals.length === 0 && (
                <div className="card p-12 text-center">
                  <Lightbulb className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-500">No active signals in this domain</p>
                </div>
              )}
            </div>

            <div className="lg:col-span-1">
              <QuickStats domain={domain} />
            </div>
          </div>
        )}

        {activeTab === 'assistant' && (
          <div className="max-w-4xl">
            <AIAssistant domain={domain} expanded />
          </div>
        )}

        {activeTab === 'knowledge' && <KnowledgeSpine filterDomain={domain} />}
      </div>
    </div>
  );
}

function QuickStats({ domain }: { domain: DomainType }) {
  const stats: Record<DomainType, { label: string; value: string }[]> = {
    revenue: [
      { label: 'Active Opportunities', value: '12' },
      { label: 'Pipeline Value', value: '$8.4M' },
      { label: 'Avg Deal Cycle', value: '94 days' },
      { label: 'Win Rate (Q4)', value: '68%' },
    ],
    solutions: [
      { label: 'Active Architectures', value: '8' },
      { label: 'Reference Cases', value: '24' },
      { label: 'Frameworks', value: '6' },
      { label: 'Playbooks', value: '15' },
    ],
    partners: [
      { label: 'Active Partners', value: '12' },
      { label: 'Co-sell Opportunities', value: '7' },
      { label: 'Certifications', value: '45' },
      { label: 'MDF Available', value: '$85K' },
    ],
    delivery: [
      { label: 'Active Projects', value: '18' },
      { label: 'Team Utilization', value: '94%' },
      { label: 'On-time Delivery', value: '89%' },
      { label: 'CSAT Score', value: '4.7/5' },
    ],
    strategy: [
      { label: 'Market Signals', value: '23' },
      { label: 'Strategic Initiatives', value: '5' },
      { label: 'Competitive Alerts', value: '8' },
      { label: 'Industry Reports', value: '12' },
    ],
  };

  return (
    <div className="card p-5">
      <h3 className="font-semibold text-slate-900 mb-4">Quick Stats</h3>
      <div className="space-y-4">
        {stats[domain].map((stat, index) => (
          <div key={index} className="flex justify-between items-center">
            <span className="text-sm text-slate-600">{stat.label}</span>
            <span className="font-semibold text-slate-900">{stat.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
