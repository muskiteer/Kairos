"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Bot, User, Send, Activity, TrendingUp, AlertTriangle } from "lucide-react";
import { getApiUrl } from '@/lib/config'


interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  intent?: string;
  confidence?: number;
  data?: any;
  actions_taken?: string[];
  reasoning?: string;
  suggestions?: string[];
}

interface KairosChatProps {
  sessionId?: string;
  onSessionUpdate?: (sessionId: string) => void;
}

export function KairosChat({ sessionId, onSessionUpdate }: KairosChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "🚀 Welcome to Kairos! I'm your AI trading copilot. I can help you execute trades, analyze your portfolio, research market trends, and develop trading strategies. What would you like to do today?",
      timestamp: new Date().toISOString(),
      suggestions: [
        "Show me my portfolio",
        "What's happening in the crypto market?",
        "I want to buy some ETH"
      ]
    }
  ]);
  
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(sessionId);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const startNewSession = async () => {
    try {
      const response = await fetch(getApiUrl('/api/sessions'), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "default" })
      });
      
      if (response.ok) {
        const data = await response.json();
        setCurrentSessionId(data.session_id);
        onSessionUpdate?.(data.session_id);
        
        // Add session start message
        const sessionMessage: ChatMessage = {
          id: `session-${Date.now()}`,
          role: "assistant", 
          content: data.message,
          timestamp: data.timestamp
        };
        setMessages(prev => [...prev, sessionMessage]);
      }
    } catch (error) {
      console.error("Failed to start session:", error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Start session if none exists
      let sessionToUse = currentSessionId;
      if (!sessionToUse) {
        await startNewSession();
        sessionToUse = currentSessionId;
      }

      // const response = await fetch(getApiUrl('/api/portfolio'))
      const response = await fetch(getApiUrl('/api/chat'), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: input,
          user_id: "default",
          session_id: sessionToUse
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        const assistantMessage: ChatMessage = {
          id: `msg-${Date.now()}-assistant`,
          role: "assistant",
          content: data.response,
          timestamp: data.timestamp,
          intent: data.intent,
          confidence: data.confidence,
          data: data.data,
          actions_taken: data.actions_taken,
          reasoning: data.reasoning,
          suggestions: data.suggestions
        };

        setMessages(prev => [...prev, assistantMessage]);
        
        // Update session ID if provided
        if (data.session_id && data.session_id !== currentSessionId) {
          setCurrentSessionId(data.session_id);
          onSessionUpdate?.(data.session_id);
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error("Chat error:", error);
      
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "I apologize, but I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const getIntentColor = (intent?: string) => {
    switch (intent) {
      case "trade_request":
      case "trade_executed":
        return "bg-green-100 text-green-800";
      case "trade_blocked":
        return "bg-red-100 text-red-800";
      case "portfolio_inquiry":
      case "portfolio_analysis":
        return "bg-blue-100 text-blue-800";
      case "market_analysis":
        return "bg-purple-100 text-purple-800";
      case "strategy_discussion":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatActions = (actions?: string[]) => {
    if (!actions || actions.length === 0) return null;
    
    return (
      <div className="flex flex-wrap gap-1 mt-2">
        {actions.map((action, index) => (
          <Badge key={index} variant="outline" className="text-xs">
            <Activity className="w-3 h-3 mr-1" />
            {action.replace(/_/g, " ")}
          </Badge>
        ))}
      </div>
    );
  };

  return (
    <Card className="flex flex-col h-[600px]">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="flex items-center gap-2">
          <Bot className="w-5 h-5" />
          Kairos Trading Copilot
        </CardTitle>
        {currentSessionId && (
          <Badge variant="outline" className="text-xs">
            Session: {currentSessionId.slice(0, 8)}...
          </Badge>
        )}
      </CardHeader>
      
      <CardContent className="flex flex-col flex-1 space-y-4 p-4">
        <ScrollArea ref={scrollAreaRef} className="flex-1 pr-4">
          <div className="space-y-4">
            {messages.map((message) => (
              <div key={message.id} className="space-y-2">
                <div className={`flex gap-3 ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`flex items-start gap-2 max-w-[80%] ${message.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${message.role === "user" ? "bg-blue-500" : "bg-emerald-500"}`}>
                      {message.role === "user" ? (
                        <User className="w-4 h-4 text-white" />
                      ) : (
                        <Bot className="w-4 h-4 text-white" />
                      )}
                    </div>
                    
                    <div className={`rounded-lg p-3 space-y-2 ${message.role === "user" ? "bg-blue-500 text-white" : "bg-gray-100"}`}>
                      <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                      
                      {message.intent && (
                        <div className="flex flex-wrap gap-2">
                          <Badge className={`text-xs ${getIntentColor(message.intent)}`}>
                            {message.intent.replace(/_/g, " ")}
                          </Badge>
                          {message.confidence && (
                            <Badge variant="outline" className="text-xs">
                              {Math.round(message.confidence * 100)}% confidence
                            </Badge>
                          )}
                        </div>
                      )}
                      
                      {formatActions(message.actions_taken)}
                      
                      {message.reasoning && (
                        <details className="mt-2">
                          <summary className="text-xs cursor-pointer opacity-70 hover:opacity-100">
                            View AI Reasoning
                          </summary>
                          <div className="text-xs mt-1 p-2 bg-white/10 rounded border-l-2 border-blue-400">
                            {message.reasoning}
                          </div>
                        </details>
                      )}
                      
                      {message.suggestions && message.suggestions.length > 0 && (
                        <div className="space-y-1">
                          <div className="text-xs opacity-70">Suggestions:</div>
                          <div className="flex flex-wrap gap-1">
                            {message.suggestions.map((suggestion, index) => (
                              <Button
                                key={index}
                                variant="outline"
                                size="sm"
                                className="text-xs h-6 px-2"
                                onClick={() => handleSuggestionClick(suggestion)}
                              >
                                {suggestion}
                              </Button>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="text-xs opacity-50">
                        {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500">
                <Bot className="w-4 h-4" />
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        <Separator />
        
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me about trading, portfolio, or market analysis..."
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={isLoading}
            className="flex-1"
          />
          <Button 
            onClick={sendMessage} 
            disabled={isLoading || !input.trim()}
            size="icon"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        
        <div className="text-xs text-gray-500 text-center">
          💡 Try: "Buy 100 USDC of ETH" • "Show my portfolio" • "Market analysis for Bitcoin"
        </div>
      </CardContent>
    </Card>
  );
}
