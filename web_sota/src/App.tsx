import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import { Tools } from '@/pages/tools';
import { Status } from '@/pages/status';
import { Transcode } from '@/pages/transcode';
import { Help } from '@/pages/help';
import { Apps } from '@/pages/apps';
import { Settings } from '@/pages/settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tools" element={<Tools />} />
            <Route path="/status" element={<Status />} />
            <Route path="/transcode" element={<Transcode />} />
            <Route path="/help" element={<Help />} />
            <Route path="/apps" element={<Apps />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AppLayout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
