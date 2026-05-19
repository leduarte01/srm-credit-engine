import { useState } from 'react';

import { useI18n } from '../hooks/useI18n';
import type { AppPage } from '../App';
import { HelpModal } from './HelpModal';
import { LanguageToggle } from './LanguageToggle';

interface AppLayoutProps {
  children: React.ReactNode;
  currentPage: AppPage;
  onNavigate: (page: AppPage) => void;
}

function SidebarContent({
  onHelpOpen,
  currentPage,
  onNavigate,
}: {
  onHelpOpen: () => void;
  currentPage: AppPage;
  onNavigate: (page: AppPage) => void;
}) {
  const { t } = useI18n();

  const NAV_ITEMS: { labelKey: Parameters<typeof t>[0]; page: AppPage }[] = [
    { labelKey: 'nav_receivables', page: 'dashboard' },
    { labelKey: 'nav_assignors', page: 'assignors' },
    { labelKey: 'nav_exchange_rates', page: 'exchange-rates' },
  ];

  return (
    <div className="flex h-full w-64 flex-col bg-zinc-900 px-4 py-6 text-zinc-100">
      <div className="mb-8 px-2">
        <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500">SRM</p>
        <p className="mt-1 text-lg font-bold tracking-tight">Credit Engine</p>
      </div>
      <nav className="flex-1">
        <ul className="space-y-1">
          {NAV_ITEMS.map((item) => (
            <li key={item.labelKey}>
              <button
                type="button"
                aria-current={currentPage === item.page ? 'page' : undefined}
                className={
                  currentPage === item.page
                    ? 'flex w-full items-center rounded-lg bg-zinc-700 px-3 py-2 text-sm font-medium text-white'
                    : 'flex w-full items-center rounded-lg px-3 py-2 text-sm font-medium text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100'
                }
                onClick={() => onNavigate(item.page)}
              >
                {t(item.labelKey)}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Bottom controls */}
      <div className="mt-6 flex items-center justify-between border-t border-zinc-800 pt-4">
        <LanguageToggle />
        <button
          type="button"
          onClick={onHelpOpen}
          className="rounded-md px-2 py-1 text-xs font-medium text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100"
        >
          {t('help_btn')}
        </button>
      </div>
    </div>
  );
}

export function AppLayout({ children, currentPage, onNavigate }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-zinc-50 text-zinc-900">
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex lg:flex-shrink-0">
        <SidebarContent
          onHelpOpen={() => setHelpOpen(true)}
          currentPage={currentPage}
          onNavigate={onNavigate}
        />
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
            <SidebarContent
              onHelpOpen={() => {
                setSidebarOpen(false);
                setHelpOpen(true);
              }}
              currentPage={currentPage}
              onNavigate={(p) => {
                setSidebarOpen(false);
                onNavigate(p);
              }}
            />
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
          <span className="flex-1 font-semibold">Credit Engine</span>
          <LanguageToggle />
          <button
            type="button"
            onClick={() => setHelpOpen(true)}
            className="rounded-md px-2 py-1 text-xs font-medium text-zinc-500 hover:bg-zinc-100"
          >
            ?
          </button>
        </header>

        <div className="flex-1 overflow-auto">{children}</div>
      </div>

      <HelpModal open={helpOpen} onClose={() => setHelpOpen(false)} />
    </div>
  );
}
