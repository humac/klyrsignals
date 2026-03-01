'use client';

import { ProtectedRoute } from '@/components/ProtectedRoute';
import DashboardContent from './dashboard-content';

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
