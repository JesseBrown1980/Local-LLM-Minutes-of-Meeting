import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Header() {
  const auth = useAuth();

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">
          Meeting Minutes App
        </Link>
        <div className="flex gap-4">
          <Link
            to="/tasks"
            className="px-4 py-2 rounded-md bg-[#ffd5fe] hover:bg-[#aaaeda]"
          >
            <i className="bi bi-journal-text"></i> History
          </Link>
          <button
            onClick={() => auth?.logout()}
            className="px-4 py-2 rounded-md bg-[#ffd5fe] hover:bg-[#aaaeda]"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
