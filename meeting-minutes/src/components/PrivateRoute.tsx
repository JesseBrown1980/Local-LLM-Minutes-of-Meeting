import { Navigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

interface PrivateRouteProps {
  element: React.ReactElement;
}

export default function PrivateRoute({ element }: PrivateRouteProps) {
  const auth = useAuth();

  if (!auth?.user) {
    return <Navigate to="/login" />;
  }

  return element;
}
