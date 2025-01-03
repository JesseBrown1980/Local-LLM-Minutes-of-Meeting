import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";

export default function UploadAudio() {
  const [file, setFile] = useState<File | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      navigate(`/tasks/${data.task_id}`);
    } catch (error) {
      console.error("Upload failed:", error);
    }
  };

  return (
    <>
      <Header />
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-6">Upload Audio File</h2>
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
            />
          </div>
          <button
            type="submit"
            className="w-full px-4 py-2 bg-[#90eca7] rounded-md hover:bg-opacity-90"
          >
            <i className="bi bi-stopwatch-fill"></i> Generate
          </button>
        </form>
      </div>
    </>
  );
}
