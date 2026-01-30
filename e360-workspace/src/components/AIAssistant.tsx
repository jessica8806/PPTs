import { useState } from 'react';
import { Send, Sparkles, User } from 'lucide-react';
import type { AssistantMessage, DomainType } from '../types';
import { domainDescriptions } from '../data/mockData';

interface AIAssistantProps {
  domain?: DomainType | 'home';
  expanded?: boolean;
}

const sampleConversations: Record<string, AssistantMessage[]> = {
  revenue: [
    {
      id: '1',
      role: 'user',
      content: 'What should I know before the National Insurance meeting tomorrow?',
      timestamp: '10:30 AM',
    },
    {
      id: '2',
      role: 'assistant',
      content: `Here's what matters for National Insurance Corp:

**Current Engagement**
Cloud optimization project in final phase. Delivered 23% cost reduction, exceeding the 15% target.

**Opportunity**
Their CTO mentioned AI governance concerns in last QBR. Our AI Governance Framework aligns well—they're in financial services with strict regulatory requirements.

**Key Stakeholders**
- Sarah Chen (CTO) - Technical decision maker, values data-driven insights
- Michael Torres (CFO) - Budget authority, focused on ROI
- Jennifer Walsh (VP Data) - Day-to-day champion, very engaged

**Suggested Approach**
Lead with the successful optimization results, then introduce AI governance as a natural next step given their compliance needs.`,
      timestamp: '10:31 AM',
    },
  ],
  solutions: [
    {
      id: '1',
      role: 'user',
      content: 'How did we scope the data mesh project for First Regional Bank?',
      timestamp: '2:15 PM',
    },
    {
      id: '2',
      role: 'assistant',
      content: `Here's the First Regional Bank data mesh scoping approach:

**Phase 1: Foundation (8 weeks)**
- Domain identification workshop
- Data product definition for 3 priority domains
- Self-serve infrastructure setup on GCP

**Phase 2: Implementation (12 weeks)**
- Customer domain data products
- Transaction domain data products
- Governance and catalog implementation

**Key Scope Decisions**
- Started with customer and transaction domains (highest value)
- Used GCP Dataplex for mesh governance
- Built internal data marketplace for discovery

**What Worked**
- Dedicated domain owners from business side
- Iterative approach—started small, proved value

**Watch Out For**
Similar projects often underestimate change management. Budget 20% of effort for training and adoption.`,
      timestamp: '2:16 PM',
    },
  ],
  partners: [
    {
      id: '1',
      role: 'user',
      content: "What are Google Cloud's priorities this quarter that align with our clients?",
      timestamp: '9:00 AM',
    },
    {
      id: '2',
      role: 'assistant',
      content: `Google Cloud Q1 priorities with e360 client alignment:

**Priority 1: Data Cloud & BigQuery**
GCP pushing unified analytics heavily.
- **Aligned clients:** Midwest Manufacturing (data warehouse modernization), Healthcare Partners Inc. (analytics platform)

**Priority 2: Generative AI / Vertex AI**
Focus on enterprise AI adoption with governance.
- **Aligned clients:** National Insurance Corp (AI governance), First Regional Bank (ML ops)

**Priority 3: Industry Solutions**
Healthcare and financial services getting dedicated resources.
- **Opportunity:** Position joint solutions for regulated industries

**Co-sell Opportunities**
GCP has MDF available for healthcare data platform deals. Two current prospects qualify.

**Recommendation**
Schedule sync with our GCP partner manager to discuss co-sell on the healthcare prospects.`,
      timestamp: '9:01 AM',
    },
  ],
  delivery: [
    {
      id: '1',
      role: 'user',
      content: "What's the status on the Enterprise Retail migration project?",
      timestamp: '4:00 PM',
    },
    {
      id: '2',
      role: 'assistant',
      content: `Enterprise Retail Cloud Migration Status:

**Overall Health:** At Risk

**Timeline**
- Original: 16 weeks
- Current projection: 19 weeks (+3 weeks)
- Root cause: Legacy system complexity higher than assessed

**Budget**
- On track (92% of budget consumed at 85% completion)

**Key Issues**
1. Data migration scripts require rework for edge cases
2. Client stakeholder availability limited
3. Integration testing revealing undocumented dependencies

**Team**
- 6 engineers assigned
- Morale: Good, but overtime increasing

**Recommended Actions**
1. Escalation call with client sponsor to discuss timeline
2. Bring in additional data engineer for 4 weeks
3. Daily standups instead of twice weekly

**Similar Past Project**
Regional Bank migration had similar complexity. Adding dedicated integration testing resource helped.`,
      timestamp: '4:01 PM',
    },
  ],
  strategy: [
    {
      id: '1',
      role: 'user',
      content: 'What market signals should inform our Q2 planning?',
      timestamp: '11:00 AM',
    },
    {
      id: '2',
      role: 'assistant',
      content: `Key market signals for Q2 planning:

**AI Governance Demand**
- Enterprise AI adoption accelerating
- Regulatory pressure increasing (EU AI Act, US guidelines)
- **Our position:** Strong—AI Governance Framework differentiates us

**Cloud Spending Patterns**
- Optimization focus continues
- Multi-cloud becoming standard
- **Opportunity:** FinOps and cloud cost management services

**Talent Market**
- AI/ML engineers still scarce
- Cloud architects in high demand
- **Action:** Accelerate internal certification programs

**Competitive Landscape**
- Major competitor acquired by PE (potential disruption)
- Boutique AI firms emerging
- **Differentiation:** Our vendor-neutral, governance-first approach

**Vertical Opportunities**
- Healthcare: Data platform modernization
- Financial services: AI governance and compliance
- Manufacturing: Cloud-first transformation

**Recommended Q2 Focus**
Double down on AI governance positioning. Build 2-3 reference cases.`,
      timestamp: '11:01 AM',
    },
  ],
  home: [
    {
      id: '1',
      role: 'user',
      content: 'What should I focus on this week?',
      timestamp: '8:00 AM',
    },
    {
      id: '2',
      role: 'assistant',
      content: `Here are the signals that deserve your attention this week:

**1. Revenue: Q1 Pipeline Alignment**
Three enterprise deals ($2.4M) need executive involvement before month-end. Sales and Solutions teams need to sync on scope for two of them.

**2. Partners: Google Cloud Co-Sell**
GCP is prioritizing data modernization in financial services. Two current clients match their target profile—this is time-sensitive MDF opportunity.

**3. Delivery: Capacity Planning**
Cloud engineering at 94% utilization with three projects starting in 6 weeks. Decision needed on contractor augmentation or timeline adjustment.

**Cross-Practice Opportunity**
Security and Cloud practices can joint-deliver on three active proposals. Worth a quick alignment call between practice leads.

**Recommendation**
Start with the pipeline review—highest near-term revenue impact. I can prep deal summaries for each.`,
      timestamp: '8:01 AM',
    },
  ],
};

export function AIAssistant({ domain = 'home', expanded = false }: AIAssistantProps) {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<AssistantMessage[]>(
    sampleConversations[domain] || sampleConversations.home
  );

  const config = domain && domain !== 'home' ? domainDescriptions[domain as DomainType] : {
    assistantName: 'Executive Assistant',
    assistantDescription: 'I synthesize signals across the organization and help you focus on what matters.',
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const newMessage: AssistantMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages([...messages, newMessage]);
    setInput('');

    // Simulate assistant response
    setTimeout(() => {
      const response: AssistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'I\'m analyzing the relevant context from the knowledge spine. In a production system, this would provide a contextual response based on e360\'s institutional knowledge.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, response]);
    }, 1000);
  };

  return (
    <div className={`card flex flex-col ${expanded ? 'h-full' : 'h-96'}`}>
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 bg-e360-primary rounded-lg flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-900">{config.assistantName}</h3>
            <p className="text-xs text-slate-500">{config.assistantDescription}</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}
          >
            {message.role === 'assistant' && (
              <div className="w-7 h-7 bg-e360-primary rounded-lg flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-3.5 h-3.5 text-white" />
              </div>
            )}
            <div
              className={`max-w-[85%] ${
                message.role === 'user'
                  ? 'bg-e360-primary text-white rounded-2xl rounded-tr-sm px-4 py-2'
                  : 'bg-slate-100 text-slate-900 rounded-2xl rounded-tl-sm px-4 py-3'
              }`}
            >
              {message.role === 'assistant' ? (
                <div className="text-sm whitespace-pre-wrap prose prose-sm prose-slate max-w-none">
                  {message.content.split('\n').map((line, i) => {
                    if (line.startsWith('**') && line.endsWith('**')) {
                      return <p key={i} className="font-semibold mt-3 first:mt-0 mb-1">{line.slice(2, -2)}</p>;
                    }
                    if (line.startsWith('- **')) {
                      const parts = line.slice(2).split('**');
                      return (
                        <p key={i} className="ml-2">
                          <span className="font-medium">{parts[1]}</span>
                          {parts[2]}
                        </p>
                      );
                    }
                    if (line.startsWith('- ')) {
                      return <p key={i} className="ml-2">• {line.slice(2)}</p>;
                    }
                    if (line.match(/^\d+\./)) {
                      return <p key={i} className="ml-2">{line}</p>;
                    }
                    return line ? <p key={i} className="text-slate-600">{line}</p> : null;
                  })}
                </div>
              ) : (
                <p className="text-sm">{message.content}</p>
              )}
              <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-white/60' : 'text-slate-400'}`}>
                {message.timestamp}
              </p>
            </div>
            {message.role === 'user' && (
              <div className="w-7 h-7 bg-slate-200 rounded-lg flex items-center justify-center flex-shrink-0">
                <User className="w-3.5 h-3.5 text-slate-600" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="assistant-input"
          />
          <button
            type="submit"
            className="btn-primary px-4 flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
