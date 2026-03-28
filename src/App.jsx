import { useEffect, useMemo, useRef, useState } from 'react';
import { BookOpenCheck, Mic, MicOff, SendHorizontal, Upload, Volume2, VolumeX, BrainCircuit, FileText } from 'lucide-react';
import { createQuiz, getTtsAudio, queryAssistant, transcribeAudio, uploadPdf } from './lib/api.js';

const MODEL_OPTIONS = {
  reasoning: [
    { label: 'GPT OSS 120B', value: 'gpt-oss-120b' },
    { label: 'GPT OSS 20B', value: 'gpt-oss-20b' },
    { label: 'Qwen 3 32B', value: 'qwen/qwen3-32b' },
  ],
  tool: [
    { label: 'GPT OSS 120B', value: 'gpt-oss-120b' },
    { label: 'GPT OSS 20B', value: 'gpt-oss-20b' },
    { label: 'Llama 4 Scout', value: 'meta-llama/llama-4-scout-17b-16e-instruct' },
    { label: 'Qwen 3 32B', value: 'qwen/qwen3-32b' },
  ],
  text: [
    { label: 'GPT OSS 120B', value: 'gpt-oss-120b' },
    { label: 'GPT OSS 20B', value: 'gpt-oss-20b' },
    { label: 'Llama 4 Scout', value: 'meta-llama/llama-4-scout-17b-16e-instruct' },
    { label: 'Llama 3.3 70B', value: 'llama-3.3-70b-versatile' },
  ],
  vision: [
    { label: 'Llama 4 Scout', value: 'meta-llama/llama-4-scout-17b-16e-instruct' },
  ],
  multilingual: [
    { label: 'GPT OSS 120B', value: 'gpt-oss-120b' },
    { label: 'GPT OSS 20B', value: 'gpt-oss-20b' },
    { label: 'Llama 4 Scout', value: 'meta-llama/llama-4-scout-17b-16e-instruct' },
    { label: 'Llama 3.3 70B', value: 'llama-3.3-70b-versatile' },
  ],
  stt: [
    { label: 'Whisper Large v3', value: 'whisper-large-v3' },
    { label: 'Whisper Large v3 Turbo', value: 'whisper-large-v3-turbo' },
  ],
  tts: [
    { label: 'Orpheus English', value: 'playai-tts' },
    { label: 'Orpheus Arabic Saudi', value: 'playai-tts-arabic' },
  ],
  ttsVoice: [
    { label: 'Arista PlayAI', value: 'Arista-PlayAI' },
    { label: 'Atlas PlayAI', value: 'Atlas-PlayAI' },
    { label: 'Celeste PlayAI', value: 'Celeste-PlayAI' },
  ],
};

const DEFAULT_MODEL_ROUTING = {
  reasoning_model: MODEL_OPTIONS.reasoning[0].value,
  tool_model: MODEL_OPTIONS.tool[0].value,
  text_model: MODEL_OPTIONS.text[2].value,
  vision_model: MODEL_OPTIONS.vision[0].value,
  multilingual_model: MODEL_OPTIONS.multilingual[2].value,
  stt_model: MODEL_OPTIONS.stt[1].value,
  tts_model: MODEL_OPTIONS.tts[0].value,
  tts_voice: MODEL_OPTIONS.ttsVoice[0].value,
};

const DEFAULT_VOICE_MODE = 'fast-browser';
const DEFAULT_VOICE_RESPONSE_MODE = 'fast-browser-tts';

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

function Message({ msg, onToggleSpeak, isSpeaking }) {
  const isUser = msg.role === 'user';
  return (
    <div className={isUser ? 'msg-row user' : 'msg-row'}>
      <div className={isUser ? 'msg-avatar user' : 'msg-avatar ai'}>{isUser ? 'You' : 'AI'}</div>
      <div className={isUser ? 'msg-card user' : 'msg-card ai'}>
        <p>{msg.content}</p>
        {!isUser && (
          <button
            type="button"
            onClick={() => onToggleSpeak(msg)}
            className={isSpeaking ? 'msg-audio-btn active' : 'msg-audio-btn'}
            title={isSpeaking ? 'Stop playback' : 'Play this answer'}
          >
            {isSpeaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
            {isSpeaking ? 'Stop voice' : 'Play voice'}
          </button>
        )}
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
  const mediaRecorderRef = useRef(null);
  const micChunksRef = useRef([]);
  const micStreamRef = useRef(null);
  const chatListRef = useRef(null);
  const dragStateRef = useRef({ active: false, lastY: 0 });
  const activeAudioRef = useRef({ audio: null, url: null, utterance: null, cached: false });
  const ttsCacheRef = useRef(new Map());
  const [messages, setMessages] = useState([
    {
      id: Date.now(),
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
  const [speakingMessageId, setSpeakingMessageId] = useState(null);
  const [voiceMode, setVoiceMode] = useState(() => localStorage.getItem('voxai_voice_mode') || DEFAULT_VOICE_MODE);
  const [voiceResponseMode, setVoiceResponseMode] = useState(
    () => localStorage.getItem('voxai_voice_response_mode') || DEFAULT_VOICE_RESPONSE_MODE
  );
  const [modelRouting, setModelRouting] = useState(() => {
    try {
      const saved = localStorage.getItem('voxai_model_routing');
      return saved ? { ...DEFAULT_MODEL_ROUTING, ...JSON.parse(saved) } : DEFAULT_MODEL_ROUTING;
    } catch {
      return DEFAULT_MODEL_ROUTING;
    }
  });
  const [error, setError] = useState('');
  const [stickToBottom, setStickToBottom] = useState(true);
  const chatEndRef = useRef(null);
  function stopCurrentSpeech() {
    const active = activeAudioRef.current;
    if (active.audio) {
      active.audio.pause();
      active.audio.currentTime = 0;
      active.audio.onended = null;
      active.audio.onerror = null;
    }
    if (active.url && !active.cached) URL.revokeObjectURL(active.url);
    if (active.utterance) {
      window.speechSynthesis?.cancel();
    }
    activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
    setSpeakingMessageId(null);
  }

  useEffect(() => {
    return () => stopCurrentSpeech();
  }, []);

  useEffect(() => {
    return () => {
      try { recognitionRef.current?.stop(); } catch {}
      try {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop();
        }
      } catch {}
      micStreamRef.current?.getTracks().forEach((track) => track.stop());
      ttsCacheRef.current.forEach((url) => {
        try { URL.revokeObjectURL(url); } catch {}
      });
      ttsCacheRef.current.clear();
    };
  }, []);

  useEffect(() => {
    localStorage.setItem('voxai_model_routing', JSON.stringify(modelRouting));
  }, [modelRouting]);

  useEffect(() => {
    localStorage.setItem('voxai_voice_mode', voiceMode);
  }, [voiceMode]);

  useEffect(() => {
    localStorage.setItem('voxai_voice_response_mode', voiceResponseMode);
  }, [voiceResponseMode]);

  const browserSpeechSupported = useMemo(
    () => typeof window !== 'undefined' && Boolean(window.SpeechRecognition || window.webkitSpeechRecognition),
    []
  );

  const recorderSupported = useMemo(
    () => typeof window !== 'undefined' && !!window.MediaRecorder,
    []
  );

  const speechSupported = browserSpeechSupported || recorderSupported;

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
    setMessages((prev) => [...prev, { id: message.id || Date.now() + Math.random(), ...message }]);
  }

  function getTtsCacheKey(text) {
    return `${modelRouting.tts_model}|${modelRouting.tts_voice}|${text.slice(0, 700)}`;
  }

  async function warmTtsForMessage(text) {
    const clean = (text || '').trim();
    if (!clean || voiceResponseMode !== 'natural-groq-tts') return;

    const key = getTtsCacheKey(clean);
    if (ttsCacheRef.current.has(key)) return;

    try {
      const audioBlob = await getTtsAudio(clean, {
        model: modelRouting.tts_model,
        voice: modelRouting.tts_voice,
      });
      const url = URL.createObjectURL(audioBlob);
      ttsCacheRef.current.set(key, url);

      while (ttsCacheRef.current.size > 8) {
        const oldestKey = ttsCacheRef.current.keys().next().value;
        const oldestUrl = ttsCacheRef.current.get(oldestKey);
        try { URL.revokeObjectURL(oldestUrl); } catch {}
        ttsCacheRef.current.delete(oldestKey);
      }
    } catch {
      // Silent: prefetch best-effort only.
    }
  }

  async function speakAnswer(text, messageId) {
    stopCurrentSpeech();
    setSpeakingMessageId(messageId);

    const clean = (text || '').trim();
    if (!clean) {
      setSpeakingMessageId(null);
      return;
    }

    if (voiceResponseMode === 'fast-browser-tts' && 'speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(clean.slice(0, 700));
      activeAudioRef.current = { audio: null, url: null, utterance, cached: false };
      utterance.onend = () => {
        activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
        setSpeakingMessageId(null);
      };
      utterance.onerror = () => {
        activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
        setSpeakingMessageId(null);
      };
      window.speechSynthesis.speak(utterance);
      return;
    }

    try {
      const key = getTtsCacheKey(clean);
      let url = ttsCacheRef.current.get(key);
      let cached = true;

      if (!url) {
        const audioBlob = await getTtsAudio(clean, {
          model: modelRouting.tts_model,
          voice: modelRouting.tts_voice,
        });
        url = URL.createObjectURL(audioBlob);
        cached = false;
      }

      const audio = new Audio(url);
      activeAudioRef.current = { audio, url, utterance: null, cached };
      audio.onended = () => {
        if (activeAudioRef.current.url && !activeAudioRef.current.cached) URL.revokeObjectURL(activeAudioRef.current.url);
        activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
        setSpeakingMessageId(null);
      };
      audio.onerror = () => {
        if (activeAudioRef.current.url && !activeAudioRef.current.cached) URL.revokeObjectURL(activeAudioRef.current.url);
        activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
        setSpeakingMessageId(null);
      };
      await audio.play();
    } catch {
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(clean.slice(0, 700));
        activeAudioRef.current = { audio: null, url: null, utterance, cached: false };
        utterance.onend = () => {
          activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
          setSpeakingMessageId(null);
        };
        utterance.onerror = () => {
          activeAudioRef.current = { audio: null, url: null, utterance: null, cached: false };
          setSpeakingMessageId(null);
        };
        window.speechSynthesis.speak(utterance);
      } else {
        setSpeakingMessageId(null);
      }
    }
  }

  async function onToggleSpeak(msg) {
    if (!msg?.content || msg.role !== 'assistant') return;
    if (speakingMessageId === msg.id) {
      stopCurrentSpeech();
      return;
    }
    await speakAnswer(msg.content, msg.id);
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
      const data = await queryAssistant(question, modelRouting);
      const aiMessage = {
        role: 'assistant',
        content: data.answer || 'No answer generated.',
        sources: data.sources || [],
      };
      pushMessage(aiMessage);
      warmTtsForMessage(aiMessage.content);
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
      const data = await createQuiz(topic, modelRouting);
      setQuizText(data.quiz || 'No quiz generated.');
      setActiveTab('quiz');
    } catch (err) {
      setError(err.message || 'Quiz generation failed');
    } finally {
      setLoading(false);
    }
  }

  async function startRecording() {
    if (!recorderSupported) {
      setError('Audio recording is not supported in this browser.');
      return;
    }

    setError('');
    setInterimText('Listening...');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      micStreamRef.current = stream;
      micChunksRef.current = [];

      const mimeCandidates = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'];
      const mimeType = mimeCandidates.find((t) => MediaRecorder.isTypeSupported(t)) || undefined;
      const recorderOptions = mimeType ? { mimeType, audioBitsPerSecond: 24000 } : { audioBitsPerSecond: 24000 };
      const recorder = new MediaRecorder(stream, recorderOptions);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data?.size > 0) micChunksRef.current.push(event.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(micChunksRef.current, { type: recorder.mimeType || 'audio/webm' });
        if (blob.size < 1200) {
          setInterimText('');
          setError('No voice captured. Please allow microphone access and speak a bit longer.');
          micStreamRef.current?.getTracks().forEach((track) => track.stop());
          micStreamRef.current = null;
          mediaRecorderRef.current = null;
          micChunksRef.current = [];
          setIsRecording(false);
          return;
        }
        const ext = recorder.mimeType?.includes('mp4') ? 'mp4' : 'webm';
        const file = new File([blob], `voice.${ext}`, { type: blob.type || 'audio/webm' });
        setInterimText('Transcribing...');
        try {
          const res = await transcribeAudio(file, { model: modelRouting.stt_model });
          const text = (res.text || '').trim();
          setInterimText('');
          if (text) {
            runQuery(text);
          } else {
            setError('No speech detected. Please try again.');
          }
        } catch (err) {
          setInterimText('');
          setError(err.message || 'Speech transcription failed.');
        } finally {
          micStreamRef.current?.getTracks().forEach((track) => track.stop());
          micStreamRef.current = null;
          mediaRecorderRef.current = null;
          micChunksRef.current = [];
          setIsRecording(false);
        }
      };

      recorder.start(200);
      setIsRecording(true);
    } catch (err) {
      setInterimText('');
      setError(err.message || 'Microphone access failed.');
      setIsRecording(false);
    }
  }

  function stopRecording() {
    const recorder = mediaRecorderRef.current;
    if (!recorder) return;
    if (recorder.state !== 'inactive') recorder.stop();
    setIsRecording(false);
  }

  function startBrowserRecognition() {
    if (!browserSpeechSupported) {
      setError('Fast voice mode is not supported in this browser.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    let gotFinalTranscript = false;
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
      setInterimText(interim || 'Listening...');
      if (finalTranscript.trim()) {
        gotFinalTranscript = true;
        setInterimText('');
        runQuery(finalTranscript.trim());
      }
    };

    recognition.onerror = () => {
      setInterimText('');
      setIsRecording(false);
      setError('Fast voice recognition failed. Switch to Accurate mode if this continues.');
    };

    recognition.onend = () => {
      // If recognition ends without final transcript, show a helpful hint.
      if (!gotFinalTranscript) {
        setError('No speech detected. Try speaking closer to the mic or switch to Accurate mode.');
      }
      setIsRecording(false);
      setInterimText('');
    };

    recognitionRef.current = recognition;

    setError('');
    setInterimText('Listening...');
    setIsRecording(true);
    try {
      recognition.start();
    } catch {
      setIsRecording(false);
      setInterimText('');
      // Automatic fallback: browser mode failed, try backend mode.
      setVoiceMode('accurate-groq');
      startRecording();
    }
  }

  function stopBrowserRecognition() {
    try {
      recognitionRef.current?.stop();
    } catch {}
    setIsRecording(false);
    setInterimText('');
  }

  function toggleMic() {
    if (isRecording) {
      if (voiceMode === 'fast-browser') stopBrowserRecognition();
      else stopRecording();
      return;
    }

    if (!speechSupported) {
      setError('Voice input is not supported in this browser.');
      return;
    }

    if (voiceMode === 'fast-browser') {
      if (!browserSpeechSupported) {
        setVoiceMode('accurate-groq');
        startRecording();
        return;
      }
      startBrowserRecognition();
    } else {
      startRecording();
    }
  }

  function updateRouting(key, value) {
    setModelRouting((prev) => ({ ...prev, [key]: value }));
  }

  function ModelSelect({ label, value, options, onChange }) {
    return (
      <label className="model-select-wrap">
        <span>{label}</span>
        <select value={value} onChange={(e) => onChange(e.target.value)} className="model-select">
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
      </label>
    );
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

        <div className="toggle-btn" style={{ cursor: 'default', pointerEvents: 'none', opacity: 0.95 }}>
          <Volume2 size={15} />
          Tap Play voice on any AI message
        </div>

        <label className="voice-mode-wrap">
          <span>Voice latency mode</span>
          <select
            className="voice-mode-select"
            value={voiceMode}
            onChange={(e) => {
              if (isRecording) {
                if (voiceMode === 'fast-browser') stopBrowserRecognition();
                else stopRecording();
              }
              setVoiceMode(e.target.value);
            }}
          >
            <option value="fast-browser">Fast (browser STT)</option>
            <option value="accurate-groq">Accurate (Groq STT model)</option>
          </select>
        </label>

        <label className="voice-mode-wrap">
          <span>Voice response mode</span>
          <select
            className="voice-mode-select"
            value={voiceResponseMode}
            onChange={(e) => setVoiceResponseMode(e.target.value)}
          >
            <option value="fast-browser-tts">Fast (instant browser TTS)</option>
            <option value="natural-groq-tts">Natural (Groq TTS, cached)</option>
          </select>
        </label>

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

        <div className="model-section">
          <strong>Model Routing</strong>
          <ModelSelect
            label="Reasoning"
            value={modelRouting.reasoning_model}
            options={MODEL_OPTIONS.reasoning}
            onChange={(v) => updateRouting('reasoning_model', v)}
          />
          <ModelSelect
            label="Function/Tool"
            value={modelRouting.tool_model}
            options={MODEL_OPTIONS.tool}
            onChange={(v) => updateRouting('tool_model', v)}
          />
          <ModelSelect
            label="Text to Text"
            value={modelRouting.text_model}
            options={MODEL_OPTIONS.text}
            onChange={(v) => updateRouting('text_model', v)}
          />
          <ModelSelect
            label="Vision"
            value={modelRouting.vision_model}
            options={MODEL_OPTIONS.vision}
            onChange={(v) => updateRouting('vision_model', v)}
          />
          <ModelSelect
            label="Multilingual"
            value={modelRouting.multilingual_model}
            options={MODEL_OPTIONS.multilingual}
            onChange={(v) => updateRouting('multilingual_model', v)}
          />
          <ModelSelect
            label="Speech to Text"
            value={modelRouting.stt_model}
            options={MODEL_OPTIONS.stt}
            onChange={(v) => updateRouting('stt_model', v)}
          />
          <ModelSelect
            label="Text to Speech"
            value={modelRouting.tts_model}
            options={MODEL_OPTIONS.tts}
            onChange={(v) => updateRouting('tts_model', v)}
          />
          <ModelSelect
            label="TTS Voice"
            value={modelRouting.tts_voice}
            options={MODEL_OPTIONS.ttsVoice}
            onChange={(v) => updateRouting('tts_voice', v)}
          />
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
                <Message key={msg.id || `${msg.role}-${idx}`} msg={msg} onToggleSpeak={onToggleSpeak} isSpeaking={speakingMessageId === msg.id} />
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
