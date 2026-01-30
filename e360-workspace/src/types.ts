export type SignalType = 'priority' | 'opportunity' | 'risk' | 'info';

export type DomainType = 'revenue' | 'solutions' | 'partners' | 'delivery' | 'strategy';

export interface Signal {
  id: string;
  type: SignalType;
  title: string;
  description: string;
  domain: DomainType;
  source?: string;
  timestamp: string;
  actionable?: boolean;
}

export interface KnowledgeItem {
  id: string;
  title: string;
  category: string;
  domain: DomainType;
  lastUpdated: string;
  excerpt: string;
}

export interface AssistantMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface DomainMetric {
  label: string;
  value: string;
  trend?: 'up' | 'down' | 'neutral';
  description?: string;
}

export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  view: string;
}
