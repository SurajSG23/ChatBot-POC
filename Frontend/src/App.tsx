import { useState } from "react";
import axios from "axios";
import "./App.scss";
import Chatbot from "./components/Chatbot";

const App = () => {
  const [file, setFile] = useState<File | null>(null);
  const [chunks, setChunks] = useState<string[]>([]);
  const [source, setSource] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleUpload = async (e: React.FormEvent) => {
    setIsLoading(true);
    e.preventDefault();
    if (!file || !source.trim()) return;

    const formData = new FormData();
    formData.append("source", source);
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/upload/",
        formData,
        {
          withCredentials: true,
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setChunks(response.data);
      setSource("");
      setFile(null);
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container">
    
      <main>
        <form onSubmit={handleUpload} className="upload-container">
          <div className="topic-container">
            <label htmlFor="topic">
              <h2 className="label-heading">Topic :</h2>
            </label>
            <select
              id="model-selection"
              onChange={(e) => {
                setSource(e.target.value);
              }}
            >
              <option value="" hidden>
                Select Project &#11167;
              </option>
              <option value="project-one">Project-1</option>
              <option value="project-two">Project-2</option>
              <option value="project-three">Project-3</option>
            </select>
          </div>

          {source.trim().length > 0 && (
            <>
              <input
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                required
              />
              <button type="submit" disabled={isLoading}>
                {isLoading ? "Loading..." : "Upload"}
              </button>
            </>
          )}
        </form>

        <section className="chunks-container">
          {chunks.map((chunk, index) => (
            <div className="chunk" key={index}>
              <h3>Chunk {index + 1}:</h3>
              <p className="chunk-data">{chunk}</p>
            </div>
          ))}
        </section>
      </main>

      <Chatbot />
    </div>
  );
};

export default App;
