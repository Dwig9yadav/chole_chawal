import { useEffect, useMemo, useRef, useState } from 'react';
import { BookOpenCheck, Mic, MicOff, SendHorizontal, Upload, Volume2, BrainCircuit, FileText } from 'lucide-react';
import { createQuiz, getTtsAudio, queryAssistant, uploadPdf } from './lib/api.js';

function WaveBars({ active }) {
  return (
    <div className="wave-bars" aria-hidden="true">
      {Array.from({ length: 9 }).map((_, idx) => (
        <span
          key={idx}
          className={active ? 'wave-bar active' : 'wave-bar'}
          style={{ animationDelay: `${idx * 0.08}s` }}
        />
      ))}
    </div>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div className={isUser ? 'msg-row user' : 'msg-row'}>
      <div className={isUser ? 'msg-avatar user' : 'msg-avatar ai'}>{isUser ? 'You' : 'AI'}</div>
      <div className={isUser ? 'msg-card user' : 'msg-card ai'}>
        <p>{msg.content}</p>
        {msg.sources?.length > 0 && (
          <div className="source-wrap">
            <div className="source-title">Sources</div>
            {msg.sources.map((s, i) => (
              <div key={`${s.source}-${i}`} className="source-item">
                {s.source} (page {s.page || '?'})
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const recognitionRef = useRef(null);
  const chatListRef = useRef(null);
  const dragStateRef = useRef({ active: false, lastY: 0 });
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Welcome to VoxAI. Upload your study PDF, ask questions with text or voice, and use quiz mode to test your understanding.',
    },
  ]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [interimText, setInterimText] = useState('');
  const [quizText, setQuizText] = useState('');
  const [activeTab, setActiveTab] = useState('study');
  const [autoSpeak, setAutoSpeak] = useState(true);
  const [error, setError] = useState('');
  const [stickToBottom, setStickToBottom] = useState(true);
  const chatEndRef = useRef(null);

  const speechSupported = useMemo(
    () => Boolean(window.SpeechRecognition || window.webkitSpeechRecognition),
    []
  );

  useEffect(() => {
    if (!stickToBottom) return;
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, interimText, stickToBottom]);

  function handleChatScroll() {
    const el = chatListRef.current;
    if (!el) return;
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    setStickToBottom(distFromBottom < 120);
  }

  function onChatMouseDown(e) {
    if (e.button !== 0) return;
    const el = chatListRef.current;
    if (!el) return;
    dragStateRef.current = { active: true, lastY: e.clientY };
    el.classList.add('dragging');
  }

  function onChatMouseMove(e) {
    const el = chatListRef.current;
    if (!el || !dragStateRef.current.active) return;
    const deltaY = e.clientY - dragStateRef.current.lastY;
    dragStateRef.current.lastY = e.clientY;
    el.scrollTop -= deltaY;
  }

  function onChatMouseUp() {
    const el = chatListRef.current;
    dragStateRef.current.active = false;
    if (el) el.classList.remove('dragging');
  }

  function pushMessage(message) {
    setMessages((prev) => [...prev, message]);
  }

  async function speakAnswer(text) {
    try {
      const audioBlob = await getTtsAudio(text);
      const url = URL.createObjectURL(audioBlob);
      const audio = new Audio(url);
      audio.onended = () => URL.revokeObjectURL(url);
      await audio.play();
    } catch {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text.slice(0, 700));
        window.speechSynthesis.speak(utterance);
      }
    }
  }

  async function runQuery(rawQuery) {
    const question = rawQuery.trim();
    if (!question || loading) return;

    setError('');
    setQuery('');
    setStickToBottom(true);
    pushMessage({ role: 'user', content: question });
    setLoading(true);

    try {
      const data = await queryAssistant(question);
      const aiMessage = {
        role: 'assistant',
        content: data.answer || 'No answer generated.',
        sources: data.sources || [],
      };
      pushMessage(aiMessage);

      if (autoSpeak && aiMessage.content) {
        await speakAnswer(aiMessage.content);
      }
    } catch (err) {
      setError(err.message || 'Query failed');
    } finally {
      setLoading(false);
    }
  }

  async function onUploadFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError('');
    setUploading(true);
    try {
      const res = await uploadPdf(file);
      pushMessage({
        role: 'assistant',
        content: `Indexed ${res.file}. Chunks: ${res.index?.chunks || 0}. Ask me anything from your notes.`,
      });
    } catch (err) {
      setError(err.message || 'PDF upload failed');
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  }

  async function onGenerateQuiz() {
    const topic = query.trim();
    if (!topic) {
      setError('Enter a topic before generating quiz mode.');
      return;
    }

    setError('');
    setLoading(true);
    try {
      const data = await createQuiz(topic);
      setQuizText(data.quiz || 'No quiz generated.');
      setActiveTab('quiz');
    } catch (err) {
      setError(err.message || 'Quiz generation failed');
    } finally {
      setLoading(false);
    }
  }

  function setupRecognitionIfNeeded() {
    if (recognitionRef.current || !speechSupported) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        const transcript = event.results[i][0]?.transcript || '';
        if (event.results[i].isFinal) finalTranscript += transcript;
        else interim += transcript;
      }
      setInterimText(interim);
      if (finalTranscript.trim()) {
        setInterimText('');
        runQuery(finalTranscript.trim());
      }
    };

    recognition.onend = () => {
      setIsRecording(false);
      setInterimText('');
    };

    recognition.onerror = () => {
      setIsRecording(false);
      setInterimText('');
      setError('Microphone recognition failed.');
    };

    recognitionRef.current = recognition;
  }

  function toggleMic() {
    if (!speechSupported) {
      setError('Browser speech recognition is not supported in this browser.');
      return;
    }
    setupRecognitionIfNeeded();

    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      setInterimText('');
      return;
    }

    setError('');
    setIsRecording(true);
    recognitionRef.current?.start();
  }

  return (
    <div className="app-shell">
      <div className="ambient" />

      <aside className="left-panel">
        <div className="brand-wrap">
          <div className="brand-icon">
            <BrainCircuit size={18} />
          </div>
          <div>
            <h1>VoxAI</h1>
            <p>Voice Study Assistant</p>
          </div>
        </div>

        <label className={uploading ? 'upload-btn disabled' : 'upload-btn'}>
          <Upload size={16} />
          {uploading ? 'Indexing PDF...' : 'Upload Study PDF'}
          <input type="file" accept="application/pdf" onChange={onUploadFile} disabled={uploading} hidden />
        </label>

        <button
          className={autoSpeak ? 'toggle-btn active' : 'toggle-btn'}
          type="button"
          onClick={() => setAutoSpeak((s) => !s)}
        >
          <Volume2 size={15} />
          Auto voice playback: {autoSpeak ? 'On' : 'Off'}
        </button>

        <div className="tab-wrap">
          <button
            type="button"
            className={activeTab === 'study' ? 'tab-btn active' : 'tab-btn'}
            onClick={() => setActiveTab('study')}
          >
            <BookOpenCheck size={15} />
            Study Chat
          </button>
          <button
            type="button"
            className={activeTab === 'quiz' ? 'tab-btn active' : 'tab-btn'}
            onClick={() => setActiveTab('quiz')}
          >
            <FileText size={15} />
            Quiz Mode
          </button>
        </div>

        <div className="hint-card">
          <strong>Demo prompts</strong>
          <p>Explain deadlock from my notes.</p>
          <p>Find best AI courses and summarize.</p>
          <p>Generate quiz on CPU scheduling.</p>
        </div>
      </aside>

      <main className="main-panel">
        <header className="top-bar">
          <div>
            <h2>Real-time Voice + RAG + Agent</h2>
            <p>{loading ? 'Thinking...' : isRecording ? 'Listening...' : 'Ready'}</p>
          </div>
          <WaveBars active={isRecording || loading} />
        </header>

        {activeTab === 'study' ? (
          <section className="chat-pane">
            <div
              className="chat-list"
              ref={chatListRef}
              onScroll={handleChatScroll}
              onMouseDown={onChatMouseDown}
              onMouseMove={onChatMouseMove}
              onMouseUp={onChatMouseUp}
              onMouseLeave={onChatMouseUp}
            >
              {messages.map((msg, idx) => (
                <Message key={`${msg.role}-${idx}`} msg={msg} />
              ))}
              {loading && <div className="thinking">VoxAI is reasoning over your docs and tools...</div>}
              {interimText && <div className="interim">{interimText}</div>}
              <div ref={chatEndRef} />
            </div>

            <div className="composer">
              <button
                type="button"
                className={isRecording ? 'mic-btn active' : 'mic-btn'}
                onClick={toggleMic}
                title="Voice query"
              >
                {isRecording ? <MicOff size={18} /> : <Mic size={18} />}
              </button>

              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask from notes, search web, calculate, or summarize..."
                onKeyDown={(e) => {
                  if (e.key === 'Enter') runQuery(query);
                }}
              />

              <button type="button" className="send-btn" onClick={() => runQuery(query)}>
                <SendHorizontal size={18} />
              </button>
            </div>

            <div className="quiz-inline">
              <button type="button" className="quiz-btn" onClick={onGenerateQuiz}>
                Generate Quiz From Topic
              </button>
            </div>
          </section>
        ) : (
          <section className="quiz-pane">
            <h3>Quiz Mode</h3>
            <p>Type a topic and click "Generate Quiz From Topic" to create voice-ready questions.</p>
            <pre>{quizText || 'No quiz yet.'}</pre>
          </section>
        )}

        {error && <div className="error-banner">{error}</div>}
      </main>
    </div>
  );
}
