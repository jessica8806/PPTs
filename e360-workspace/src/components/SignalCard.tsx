import { AlertTriangle, TrendingUp, AlertCircle, Info, ArrowRight } from 'lucide-react';
import type { Signal } from '../types';

interface SignalCardProps {
  signal: Signal;
  compact?: boolean;
}

const signalConfig = {
  priority: {
    icon: AlertTriangle,
    bgClass: 'signal-card-priority',
    iconColor: 'text-amber-600',
    label: 'Priority',
  },
  opportunity: {
    icon: TrendingUp,
    bgClass: 'signal-card-opportunity',
    iconColor: 'text-emerald-600',
    label: 'Opportunity',
  },
  risk: {
    icon: AlertCircle,
    bgClass: 'signal-card-risk',
    iconColor: 'text-red-600',
    label: 'Risk',
  },
  info: {
    icon: Info,
    bgClass: 'signal-card-info',
    iconColor: 'text-blue-600',
    label: 'Update',
  },
};

const domainBadgeClass = {
  revenue: 'domain-badge-revenue',
  solutions: 'domain-badge-solutions',
  partners: 'domain-badge-partners',
  delivery: 'domain-badge-delivery',
  strategy: 'domain-badge-strategy',
};

export function SignalCard({ signal, compact = false }: SignalCardProps) {
  const config = signalConfig[signal.type];
  const Icon = config.icon;
  const badgeClass = domainBadgeClass[signal.domain];

  if (compact) {
    return (
      <div className={`signal-card ${config.bgClass} hover:shadow-md transition-shadow cursor-pointer`}>
        <div className="flex items-start gap-3">
          <Icon className={`w-5 h-5 ${config.iconColor} mt-0.5 flex-shrink-0`} />
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-slate-900 text-sm">{signal.title}</h3>
            <p className="text-slate-600 text-sm mt-1 line-clamp-2">{signal.description}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-slate-400">{signal.timestamp}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`signal-card ${config.bgClass} hover:shadow-md transition-shadow cursor-pointer group`}>
      <div className="flex items-start gap-4">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-white/80 flex-shrink-0`}>
          <Icon className={`w-5 h-5 ${config.iconColor}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={`domain-badge ${badgeClass} capitalize`}>{signal.domain}</span>
            <span className="text-xs text-slate-400">{config.label}</span>
          </div>
          <h3 className="font-semibold text-slate-900">{signal.title}</h3>
          <p className="text-slate-600 text-sm mt-1 leading-relaxed">{signal.description}</p>
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-3">
              {signal.source && (
                <span className="text-xs text-slate-500">Source: {signal.source}</span>
              )}
              <span className="text-xs text-slate-400">{signal.timestamp}</span>
            </div>
            {signal.actionable && (
              <button className="flex items-center gap-1 text-sm text-e360-accent font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                <span>Review</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
