import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { HomeView } from './views/HomeView';
import { DomainView } from './views/DomainView';
import { KnowledgeView } from './views/KnowledgeView';
import type { DomainType } from './types';
import { Settings, Bell } from 'lucide-react';

function App() {
  const [activeView, setActiveView] = useState('home');

  const handleNavigate = (view: string) => {
    setActiveView(view);
  };

  const renderView = () => {
    switch (activeView) {
      case 'home':
        return <HomeView onNavigate={handleNavigate} />;
      case 'revenue':
      case 'solutions':
      case 'partners':
      case 'delivery':
      case 'strategy':
        return <DomainView domain={activeView as DomainType} />;
      case 'knowledge':
        return <KnowledgeView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <HomeView onNavigate={handleNavigate} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar activeView={activeView} onNavigate={handleNavigate} />

      {/* Main Content */}
      <div className="ml-64">
        {/* Top Bar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <nav className="text-sm text-slate-500">
              <span className="text-slate-900 font-medium capitalize">{activeView}</span>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <button className="relative p-2 text-slate-500 hover:text-slate-700 transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-e360-accent rounded-full" />
            </button>
            <div className="w-px h-6 bg-slate-200" />
            <button className="p-2 text-slate-500 hover:text-slate-700 transition-colors">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8">
          {renderView()}
        </main>
      </div>
    </div>
  );
}

function SettingsView() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold text-slate-900">Settings</h1>
        <p className="text-slate-500 mt-1">Configure your workspace preferences</p>
      </div>

      <div className="max-w-2xl space-y-6">
        <div className="card p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Notifications</h2>
          <div className="space-y-4">
            {[
              { label: 'Priority signals', description: 'Get notified about high-priority items', enabled: true },
              { label: 'Risk alerts', description: 'Immediate alerts for risk signals', enabled: true },
              { label: 'Weekly digest', description: 'Summary of key signals every Monday', enabled: false },
            ].map((setting, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-slate-900">{setting.label}</p>
                  <p className="text-sm text-slate-500">{setting.description}</p>
                </div>
                <button
                  className={`w-11 h-6 rounded-full transition-colors ${
                    setting.enabled ? 'bg-e360-primary' : 'bg-slate-200'
                  }`}
                >
                  <div
                    className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
                      setting.enabled ? 'translate-x-5' : 'translate-x-0.5'
                    }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Connected Systems</h2>
          <div className="space-y-3">
            {[
              { name: 'Salesforce', status: 'Connected', connected: true },
              { name: 'Slack', status: 'Connected', connected: true },
              { name: 'SharePoint', status: 'Pending', connected: false },
              { name: 'Jira', status: 'Not connected', connected: false },
            ].map((system, index) => (
              <div key={index} className="flex items-center justify-between py-2">
                <span className="font-medium text-slate-700">{system.name}</span>
                <span
                  className={`text-sm ${
                    system.connected ? 'text-emerald-600' : 'text-slate-500'
                  }`}
                >
                  {system.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
