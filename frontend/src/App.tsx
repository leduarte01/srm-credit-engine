import { useState } from 'react';

import { AppLayout } from './components/AppLayout';
import { AssignorsPage } from './pages/AssignorsPage';
import { DashboardPage } from './pages/DashboardPage';
import { ExchangeRatesPage } from './pages/ExchangeRatesPage';

export type AppPage = 'dashboard' | 'assignors' | 'exchange-rates';

export default function App() {
  const [page, setPage] = useState<AppPage>('dashboard');

  return (
    <AppLayout currentPage={page} onNavigate={setPage}>
      {page === 'dashboard' && <DashboardPage />}
      {page === 'assignors' && <AssignorsPage />}
      {page === 'exchange-rates' && <ExchangeRatesPage />}
    </AppLayout>
  );
}
