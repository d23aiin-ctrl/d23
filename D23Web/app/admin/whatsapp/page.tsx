import UltimateAdminDashboard from "@/components/admin/UltimateAdminDashboard";
import ProtectedRoute from "@/components/admin/ProtectedRoute";

export default function WhatsappAdminPage() {
  return (
    <ProtectedRoute>
      <UltimateAdminDashboard />
    </ProtectedRoute>
  );
}
