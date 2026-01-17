import { useState, useRef, useEffect } from 'react';
import { X, Send, Sparkles, Bot, User, Loader2, Maximize2, Minimize2, Trash2, History, Wrench, Brain, Check } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Format markdown for clean, professional look
const formatMarkdown = (text) => {
  if (!text) return '';
  
  let formatted = text
    // Headers with proper spacing
    .replace(/###\s(.+)/g, '<h3 class="text-base font-bold mt-4 mb-2 text-gray-800">$1</h3>')
    .replace(/##\s(.+)/g, '<h2 class="text-lg font-bold mt-5 mb-3 text-gray-900 border-b border-gray-200 pb-2">$2</h2>')
    .replace(/#\s(.+)/g, '<h1 class="text-xl font-bold mt-5 mb-3 text-gray-900">$1</h1>')
    // Bold text (keep inline)
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em class="italic text-gray-700">$1</em>')
    // Numbered lists
    .replace(/^\d+\.\s(.+)$/gm, '<div class="flex gap-2 ml-2 mb-2"><span class="text-blue-600 font-semibold min-w-[20px]">•</span><span>$1</span></div>')
    // Bullet lists
    .replace(/^-\s(.+)$/gm, '<div class="flex gap-2 ml-2 mb-2"><span class="text-blue-600 min-w-[20px]">•</span><span>$1</span></div>')
    // Preserve line breaks but make them smaller
    .replace(/\n\n/g, '<div class="h-3"></div>')
    .replace(/\n/g, '<br/>');
  
  return formatted;
};

export default function AIAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '🇮🇳 Welcome to the Aadhaar Identity Intelligence AI Assistant.\n\nI\'m your AI analyst powered by NVIDIA, designed specifically for government officials managing Aadhaar data at scale.\n\n**I can help you with:**\n\n• 📊 State-level data analysis and comparisons\n• 📈 Understanding IVI and BSI metrics\n• 🎯 Identifying high-risk areas and anomalies\n• 💡 Generating policy recommendations\n• 📉 Explaining trends and forecasts\n• 🔍 District-level insights\n\n**How I work:**\n\nFor complex questions, I\'ll show you my reasoning process, the tools I\'m using, and how I arrive at conclusions. Ask me anything!',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [thinkingSteps, setThinkingSteps] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const abortControllerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, thinkingSteps]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const clearHistory = async () => {
    if (sessionId && window.confirm('Clear conversation history?')) {
      try {
        await fetch(`${API_URL}/api/ai/history/${sessionId}`, { method: 'DELETE' });
        setMessages([{
          role: 'assistant',
          content: '✅ History cleared. How can I help you?',
          timestamp: new Date()
        }]);
        setSessionId(null);
      } catch (error) {
        console.error('Failed to clear history:', error);
      }
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setThinkingSteps([]);
    setIsStreaming(true);

    try {
      abortControllerRef.current = new AbortController();

      // Always stream - let the LLM decide how to respond
      {
        // Stream with Chain-of-Thought
        const response = await fetch(`${API_URL}/api/ai/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: input,
            session_id: sessionId,
            stream: true  // Always stream, LLM decides complexity
          }),
          signal: abortControllerRef.current.signal
        });

        // Extract session ID from headers
        const newSessionId = response.headers.get('X-Session-ID');
        if (newSessionId && !sessionId) {
          setSessionId(newSessionId);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let accumulatedResponse = '';
        const steps = [];

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.substring(6));

                if (data.type === 'thinking') {
                  steps.push({ type: 'thinking', content: data.content });
                  setThinkingSteps([...steps]);
                } else if (data.type === 'tool_call') {
                  steps.push({ type: 'tool_call', tool: data.tool, args: data.args });
                  setThinkingSteps([...steps]);
                } else if (data.type === 'tool_result') {
                  steps.push({ type: 'tool_result', tool: data.tool, result: data.result });
                  setThinkingSteps([...steps]);
                } else if (data.type === 'response') {
                  accumulatedResponse += data.content;
                  // Update the last message in real-time
                  setMessages(prev => {
                    const newMessages = [...prev];
                    if (newMessages[newMessages.length - 1]?.role === 'assistant' && newMessages[newMessages.length - 1]?.isStreaming) {
                      newMessages[newMessages.length - 1].content = accumulatedResponse;
                    } else {
                      newMessages.push({
                        role: 'assistant',
                        content: accumulatedResponse,
                        timestamp: new Date(),
                        isStreaming: true
                      });
                    }
                    return newMessages;
                  });
                } else if (data.type === 'done') {
                  // Finalize message
                  setMessages(prev => {
                    const newMessages = [...prev];
                    if (newMessages[newMessages.length - 1]?.isStreaming) {
                      delete newMessages[newMessages.length - 1].isStreaming;
                    }
                    return newMessages;
                  });
                } else if (data.type === 'error') {
                  throw new Error(data.message);
                }
              } catch (parseError) {
                console.error('Parse error:', parseError);
              }
            }
          }
        }
      }  // End of streaming block
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
        return;
      }

      console.error('AI Chat Error:', error);

      const errorMessage = {
        role: 'assistant',
        content: `❌ I apologize, but I encountered an error: ${error.message}\n\nPlease try again or check if the NVIDIA API key is configured correctly.`,
        timestamp: new Date(),
        isError: true
      };

      setMessages(prev => {
        const newMessages = [...prev];
        if (newMessages[newMessages.length - 1]?.isStreaming) {
          newMessages[newMessages.length - 1] = errorMessage;
        } else {
          newMessages.push(errorMessage);
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      setThinkingSteps([]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickQuestions = [
    'Which state has the highest IVI and why?',
    'What does Biometric Stress Index indicate?',
    'Show me anomalies and explain them',
    'Compare Maharashtra and Uttar Pradesh',
    'What are the top policy recommendations?',
    'Analyze youth enrollment trends',
  ];

  const handleQuickQuestion = (question) => {
    setInput(question);
    inputRef.current?.focus();
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 z-50 group"
        aria-label="Open AI Assistant"
      >
        <div className="relative">
          {/* Glow effect */}
          <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-full blur opacity-75 group-hover:opacity-100 transition duration-300 animate-pulse"></div>
          
          {/* Circular Button */}
          <div className="relative w-16 h-16 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-full shadow-2xl hover:shadow-indigo-500/50 transition-all duration-300 hover:scale-110 flex items-center justify-center">
            <Sparkles className="h-7 w-7 text-white animate-pulse" />
          </div>
          
          {/* Badge */}
          <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
            AI
          </div>
        </div>
      </button>
    );
  }

  return (
    <div className={`fixed z-50 transition-all duration-300 ${
      isFullscreen 
        ? 'inset-0 m-0' 
        : 'bottom-6 right-6 w-[600px] h-[750px] max-w-[95vw] max-h-[90vh]'
    }`}>
      {/* Chat Container - Government-grade design */}
      <div className="h-full bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border-2 border-blue-200">
        {/* Header - Professional government style */}
        <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-700 px-6 py-5 flex items-center justify-between border-b-4 border-blue-800">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Bot className="h-7 w-7 text-white" />
              </div>
              <span className="absolute -bottom-1 -right-1 h-4 w-4 bg-green-400 rounded-full border-2 border-white animate-pulse"></span>
            </div>
            <div>
              <h2 className="text-white font-bold text-lg tracking-wide">Aadhaar Intelligence AI</h2>
              <p className="text-blue-100 text-xs font-medium flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
                Powered by NVIDIA NIM · Meta Llama 3.1 70B
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {sessionId && (
              <button
                onClick={clearHistory}
                className="p-2.5 hover:bg-white/20 rounded-lg transition-colors group"
                title="Clear conversation history"
              >
                <Trash2 className="h-5 w-5 text-white group-hover:text-red-300" />
              </button>
            )}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2.5 hover:bg-white/20 rounded-lg transition-colors"
              aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
            >
              {isFullscreen ? (
                <Minimize2 className="h-5 w-5 text-white" />
              ) : (
                <Maximize2 className="h-5 w-5 text-white" />
              )}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-2.5 hover:bg-white/20 rounded-lg transition-colors"
              aria-label="Close"
            >
              <X className="h-5 w-5 text-white" />
            </button>
          </div>
        </div>

        {/* Messages Area */}
        <div className={`flex-1 overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-gray-50 to-white ${isFullscreen ? 'max-w-5xl mx-auto w-full' : ''}`}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start gap-4 ${
                msg.role === 'user' ? 'flex-row-reverse' : ''
              }`}
            >
              {/* Avatar */}
              <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-blue-600 to-blue-700'
                  : msg.isError
                  ? 'bg-gradient-to-br from-red-600 to-red-700'
                  : 'bg-gradient-to-br from-indigo-600 to-purple-700'
              }`}>
                {msg.role === 'user' ? (
                  <User className="h-5 w-5 text-white" />
                ) : (
                  <Bot className="h-5 w-5 text-white" />
                )}
              </div>
              
              {/* Message Content */}
              <div className={`flex-1 ${msg.role === 'user' ? 'text-right' : ''}`}>
                <div className={`inline-block px-5 py-4 rounded-2xl max-w-full ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg'
                    : msg.isError
                    ? 'bg-red-50 text-red-900 border-2 border-red-300 shadow-md'
                    : 'bg-white text-gray-900 border-2 border-gray-200 shadow-md'
                }`}>
                  <div className={`break-words ${msg.role === 'user' ? 'text-sm leading-relaxed' : 'text-[13px] leading-relaxed'}`}>
                    {msg.role === 'user' ? (
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    ) : (
                      <div 
                        className="space-y-1"
                        dangerouslySetInnerHTML={{ __html: formatMarkdown(msg.content) }} 
                      />
                    )}
                  </div>
                  <div className={`text-xs mt-2 ${
                    msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Chain-of-Thought Display */}
          {isStreaming && thinkingSteps.length > 0 && (
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
                <Brain className="h-5 w-5 text-white animate-pulse" />
              </div>
              <div className="flex-1">
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 border-2 border-amber-300 rounded-2xl p-5 shadow-md">
                  <h4 className="text-xs font-bold text-amber-900 mb-3 flex items-center gap-2">
                    <Brain className="h-4 w-4" />
                    CHAIN OF THOUGHT
                  </h4>
                  <div className="space-y-3">
                    {thinkingSteps.map((step, idx) => (
                      <div key={idx} className="text-xs">
                        {step.type === 'thinking' && (
                          <div className="flex items-start gap-2 text-amber-900">
                            <Loader2 className="h-4 w-4 animate-spin flex-shrink-0 mt-0.5" />
                            <span className="italic">{step.content}</span>
                          </div>
                        )}
                        {step.type === 'tool_call' && (
                          <div className="flex items-start gap-2 text-blue-900 bg-blue-100/50 rounded-lg p-2">
                            <Wrench className="h-4 w-4 flex-shrink-0 mt-0.5" />
                            <div>
                              <span className="font-semibold">Using tool:</span> {step.tool}
                              {step.args && Object.keys(step.args).length > 0 && (
                                <div className="text-xs text-blue-700 mt-1 font-mono">
                                  {JSON.stringify(step.args, null, 2)}
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        {step.type === 'tool_result' && (
                          <div className="flex items-start gap-2 text-green-900 bg-green-100/50 rounded-lg p-2">
                            <Check className="h-4 w-4 flex-shrink-0 mt-0.5" />
                            <div>
                              <span className="font-semibold">Result from {step.tool}:</span>
                              <div className="mt-1 text-xs text-green-800 max-h-20 overflow-y-auto">
                                {step.result}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Loading indicator */}
          {isLoading && thinkingSteps.length === 0 && (
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center shadow-lg">
                <Bot className="h-5 w-5 text-white" />
              </div>
              <div className="bg-white border-2 border-gray-200 rounded-2xl px-5 py-4 shadow-md">
                <div className="flex items-center gap-3 text-gray-700">
                  <Loader2 className="h-5 w-5 animate-spin text-indigo-600" />
                  <span className="text-sm font-medium">Analyzing your question...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Questions - Enhanced */}
        {messages.length === 1 && !isLoading && (
          <div className={`px-6 py-4 border-t-2 border-gray-200 bg-gradient-to-r from-gray-50 to-blue-50 ${isFullscreen ? 'max-w-5xl mx-auto w-full' : ''}`}>
            <p className="text-xs font-bold text-gray-700 mb-3 flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-blue-600" />
              QUICK START QUESTIONS
            </p>
            <div className="grid grid-cols-2 gap-2">
              {quickQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickQuestion(q)}
                  className="text-left text-xs px-4 py-2.5 bg-white border-2 border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-400 hover:shadow-md transition-all font-medium text-gray-700"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Area - Professional style */}
        <div className={`p-5 border-t-2 border-gray-200 bg-white ${isFullscreen ? 'max-w-5xl mx-auto w-full' : ''}`}>
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about Aadhaar data, state analytics, forecasts, anomalies..."
              rows={isFullscreen ? 2 : 1}
              className="flex-1 px-5 py-4 border-2 border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-sm font-medium"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="px-7 py-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-xl hover:from-blue-700 hover:to-indigo-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center gap-2 font-bold shadow-lg hover:shadow-xl disabled:hover:shadow-lg"
            >
              <Send className="h-5 w-5" />
              {isLoading ? 'Analyzing...' : 'Send'}
            </button>
          </div>
          
          {/* Footer info */}
          <div className="mt-3 text-xs text-center text-gray-500">
            <span className="inline-flex items-center gap-1.5">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              Connected to Aadhaar Analytics System · Session {sessionId ? `#${sessionId.substring(0, 8)}` : 'New'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
