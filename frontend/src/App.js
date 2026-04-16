import { useState, useEffect } from "react";

function App() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [books, setBooks] = useState([]);

  // Load data
  useEffect(() => {
    loadBooks();
    loadHistory();
  }, []);

  const loadBooks = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/books/");
      const data = await res.json();
      setBooks(data);
    } catch (err) {
      console.log("Could not load books");
    }
  };

  const loadHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat/history/");
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.log("History load failed");
    }
  };

  const addBook = async () => {
    if (!title.trim()) return alert("Please enter book title");
    
    try {
      await fetch("http://127.0.0.1:8000/api/upload/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description }),
      });
      alert("✅ Book added successfully!");
      setTitle("");
      setDescription("");
      loadBooks();
    } catch (error) {
      alert("Upload failed");
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/ask/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await res.json();
      setAnswer(data.answer);

      // Save to history
      await fetch("http://127.0.0.1:8000/api/chat/save/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          answer: data.answer,
          sources: data.sources ? data.sources.join(", ") : ""
        }),
      });

      loadHistory();
    } catch (error) {
      setAnswer("Sorry, something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // Suggested Questions
  const suggestedQuestions = [
    "What is the book about?",
    "Summarize the main idea",
    "What genre is this book?",
    "Recommend similar books",
  ];

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-10">
          📚 Book Intelligence Platform
        </h1>

        {/* Add Book - Minimal */}
        <div className="bg-white p-6 rounded-xl shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Add New Book</h2>
          
          <input
            className="w-full border p-3 rounded mb-3"
            placeholder="Book Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          
          <textarea
            className="w-full border p-3 rounded mb-4"
            placeholder="Description (optional)"
            rows="2"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <button onClick={addBook} className="w-full bg-blue-600 text-white py-3 rounded hover:bg-blue-700">
            Add Book
          </button>

          {/* Books Dropdown */}
          {books.length > 0 && (
            <div className="mt-4">
              <label className="block text-sm font-medium mb-1">Added Books ({books.length})</label>
              <select className="w-full border p-3 rounded">
                {books.map(book => (
                  <option key={book.id}>{book.title}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Ask Question Section - Improved */}
        <div className="bg-white p-6 rounded-xl shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Ask Question (RAG)</h2>
          
          <input
            className="w-full border p-3 rounded mb-4"
            placeholder="Ask anything about the books..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          {/* Suggested Questions */}
          <div className="mb-4">
            <p className="text-sm text-gray-500 mb-2">Suggested Questions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => setQuestion(q)}
                  className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-full transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={askQuestion}
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 disabled:bg-gray-400"
          >
            {loading ? "Thinking..." : "Ask"}
          </button>

          {answer && (
            <div className="mt-6 bg-gray-50 border p-5 rounded-lg">
              <p className="font-semibold mb-2">Answer:</p>
              <p className="text-gray-700 leading-relaxed">{answer}</p>
            </div>
          )}
        </div>

        {/* Chat History */}
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-semibold mb-4">Chat History</h2>
          {history.length === 0 ? (
            <p className="text-gray-500 py-8 text-center">No questions asked yet.</p>
          ) : (
            <div className="space-y-6 max-h-[450px] overflow-y-auto">
              {history.map((chat, i) => (
                <div key={i} className="border-l-4 border-green-500 pl-4 bg-gray-50 p-4 rounded-r-lg">
                  <p className="font-medium">Q: {chat.question}</p>
                  <p className="mt-2 text-gray-700">{chat.answer}</p>
                  {chat.sources && <p className="text-xs text-gray-500 mt-2">Sources: {chat.sources}</p>}
                  <p className="text-xs text-gray-400 mt-3">{chat.time}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;