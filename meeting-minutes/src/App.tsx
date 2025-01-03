import React from "react";
import { BrowserRouter, Routes, Route, Router } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import TaskList from "./pages/TaskList";
import TaskDetails from "./pages/TaskDetails";
import UploadAudio from "./pages/UploadAudio";
import { AuthProvider } from "./contexts/AuthContext";
import PrivateRoute from "./components/PrivateRoute";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <>
          <div className="min-h-screen bg-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route
                  path="/"
                  element={<PrivateRoute element={<Dashboard />} />}
                />
                <Route
                  path="/upload"
                  element={<PrivateRoute element={<UploadAudio />} />}
                />
                <Route
                  path="/tasks"
                  element={<PrivateRoute element={<TaskList />} />}
                />
                <Route
                  path="/tasks/:taskId"
                  element={<PrivateRoute element={<TaskDetails />} />}
                />
              </Routes>
            </div>
          </div>
        </>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
