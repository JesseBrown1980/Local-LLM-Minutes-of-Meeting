import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import Header from "../components/Header";
import axios from "axios";

export default function UploadAudio() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const auth = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
        const token = auth?.getToken();
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/tasks/upload`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      navigate(`/tasks/${response.data.task_id}`);
    } catch (error) {
      console.error("Upload failed:", error);
      setError("Failed to upload file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Header />
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-6">Upload Audio File</h2>
        {error && (
          <div className="mb-4 p-4 text-red-700 bg-red-100 rounded-md">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Upload File (MP4, MP3, WAV)
            </label>
            <input
              type="file"
              accept=".mp4,.mp3,.wav"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm"
              disabled={loading}
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-2 bg-[#90eca7] rounded-md hover:bg-opacity-90 disabled:opacity-50"
            disabled={loading || !file}
          >
            {loading ? (
              <span>Uploading...</span>
            ) : (
              <>
                <i className="bi bi-stopwatch-fill"></i> Generate
              </>
            )}
          </button>
        </form>
      </div>
    </>
  );
}
