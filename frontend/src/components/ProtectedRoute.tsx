import type { ReactNode } from "react";
import RequireAuth from "../auth/RequireAuth.jsx";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  return <RequireAuth>{children}</RequireAuth>;
}
