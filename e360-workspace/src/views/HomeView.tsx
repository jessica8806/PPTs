import { Calendar, ChevronRight } from 'lucide-react';
import { SignalCard } from '../components/SignalCard';
import { AIAssistant } from '../components/AIAssistant';
import { weeklySignals } from '../data/mockData';

interface HomeViewProps {
  onNavigate: (view: string) => void;
}

export function HomeView({ onNavigate }: HomeViewProps) {
  const today = new Date();
  const formattedDate = today.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-slate-500 text-sm mb-1">
          <Calendar className="w-4 h-4" />
          <span>{formattedDate}</span>
        </div>
        <h1 className="text-3xl font-semibold text-slate-900">Good morning, Jessica</h1>
        <p className="text-slate-500 mt-1">Here's what deserves your attention this week.</p>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Signals Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">What Matters This Week</h2>
            <span className="text-sm text-slate-500">{weeklySignals.length} signals</span>
          </div>

          <div className="space-y-4">
            {weeklySignals.map((signal) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
          </div>

          {/* Quick Navigation */}
          <div className="pt-4">
            <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-4">
              Jump to Domain
            </h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { id: 'revenue', label: 'Revenue', color: 'bg-emerald-500' },
                { id: 'solutions', label: 'Solutions', color: 'bg-blue-500' },
                { id: 'partners', label: 'Partners', color: 'bg-purple-500' },
                { id: 'delivery', label: 'Delivery', color: 'bg-orange-500' },
              ].map((domain) => (
                <button
                  key={domain.id}
                  onClick={() => onNavigate(domain.id)}
                  className="card p-4 flex items-center justify-between hover:shadow-md transition-all group"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${domain.color}`} />
                    <span className="font-medium text-slate-700">{domain.label}</span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-500 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Assistant Column */}
        <div className="lg:col-span-1">
          <AIAssistant domain="home" expanded />
        </div>
      </div>
    </div>
  );
}
