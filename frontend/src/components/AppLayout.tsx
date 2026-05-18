import { useState } from 'react';

interface AppLayoutProps {
  children: React.ReactNode;
}

const NAV_ITEMS = [
  { label: 'Receivables', href: '#', active: true },
  { label: 'Config', href: '#', active: false, soon: true },
] as const;

function SidebarContent() {
  return (
    <div className="flex h-full w-64 flex-col bg-zinc-900 px-4 py-6 text-zinc-100">
      <div className="mb-8 px-2">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">SRM</p>
        <p className="mt-1 text-lg font-bold tracking-tight">Credit Engine</p>
      </div>
      <nav>
        <ul className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <li key={item.label}>
              <a
                href={item.href}
                aria-current={item.active ? 'page' : undefined}
                className={
                  item.active
                    ? 'flex items-center justify-between rounded-lg bg-zinc-700 px-3 py-2 text-sm font-medium text-white'
                    : 'flex items-center justify-between rounded-lg px-3 py-2 text-sm font-medium text-zinc-400 opacity-50'
                }
                onClick={(e) => e.preventDefault()}
              >
                {item.label}
                {'soon' in item && item.soon && (
                  <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-500">
                    soon
                  </span>
                )}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-zinc-50 text-zinc-900">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div
            aria-hidden="true"
            className="absolute inset-0 bg-black/50"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="absolute inset-y-0 left-0 z-50">
            <SidebarContent />
          </aside>
        </div>
      )}

      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Mobile top bar */}
        <header className="flex items-center gap-4 border-b border-zinc-200 bg-white px-4 py-3 lg:hidden">
          <button
            type="button"
            aria-label="Open navigation menu"
            className="rounded-md p-1 text-zinc-600 hover:bg-zinc-100"
            onClick={() => setSidebarOpen(true)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
              className="h-6 w-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
              />
            </svg>
          </button>
          <span className="font-semibold">Credit Engine</span>
        </header>

        <div className="flex-1 overflow-auto">{children}</div>
      </div>
    </div>
  );
}
