import {
  Home,
  TrendingUp,
  Layers,
  Users,
  Truck,
  Target,
  BookOpen,
  Settings,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  activeView: string;
  onNavigate: (view: string) => void;
}

export function Sidebar({ activeView, onNavigate }: SidebarProps) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'revenue', label: 'Revenue', icon: TrendingUp },
    { id: 'solutions', label: 'Solutions', icon: Layers },
    { id: 'partners', label: 'Partners', icon: Users },
    { id: 'delivery', label: 'Delivery', icon: Truck },
    { id: 'strategy', label: 'Strategy', icon: Target },
  ];

  const secondaryItems = [
    { id: 'knowledge', label: 'Knowledge Spine', icon: BookOpen },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen fixed left-0 top-0">
      {/* Logo */}
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-e360-primary rounded-xl flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-900">e360</h1>
            <p className="text-xs text-slate-500">AI Workspace</p>
          </div>
        </div>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        <p className="px-4 py-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
          Domains
        </p>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`nav-item w-full ${isActive ? 'nav-item-active' : ''}`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}

        <div className="pt-6">
          <p className="px-4 py-2 text-xs font-medium text-slate-400 uppercase tracking-wider">
            Resources
          </p>
          {secondaryItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`nav-item w-full ${isActive ? 'nav-item-active' : ''}`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* User */}
      <div className="p-4 border-t border-slate-200">
        <div className="flex items-center gap-3 px-4 py-3">
          <div className="w-9 h-9 bg-slate-200 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-slate-600">JD</span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-900 truncate">Jessica Davis</p>
            <p className="text-xs text-slate-500 truncate">Chief Executive Officer</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
