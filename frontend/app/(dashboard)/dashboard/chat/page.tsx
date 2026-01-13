"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { sendChatMessageStream, sendChatDualMode, selectDualResponse, ChatSettings, DualResponse } from "@/lib/ai"
import { 
  Mic, Send, ThumbsUp, ThumbsDown, Trash2, RotateCcw, MessageSquare, 
  Settings2, Zap, GitCompare, Check
} from "lucide-react"

interface Message {
  id?: number
  role: "user" | "assistant"
  content: string
  timestamp: Date
  rating?: "positive" | "negative" | null
  dualResponses?: DualResponse[]
  selectedResponse?: string
}

const DEFAULT_SETTINGS: ChatSettings = {
  concise: false,
  dualResponse: false,
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const [settings, setSettings] = useState<ChatSettings>(DEFAULT_SETTINGS)
  const [showSettings, setShowSettings] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const currentMessageIdRef = useRef<number | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Charger les settings depuis localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('chat-settings')
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings))
      } catch {
        // Ignore
      }
    }
  }, [])

  // Sauvegarder les settings
  const updateSettings = (newSettings: ChatSettings) => {
    setSettings(newSettings)
    localStorage.setItem('chat-settings', JSON.stringify(newSettings))
  }

  // Charger l'historique au montage
  const loadHistory = useCallback(async () => {
    try {
      setIsLoadingHistory(true)
      const response = await fetch('/api/chat/history', { credentials: 'include' })
      if (response.ok) {
        const data = await response.json()
        if (data.messages && data.messages.length > 0) {
          const loadedMessages: Message[] = []
          for (const msg of data.messages) {
            loadedMessages.push({
              id: msg.id,
              role: "user",
              content: msg.message,
              timestamp: new Date(msg.createdAt),
            })
            if (msg.response) {
              loadedMessages.push({
                id: msg.id,
                role: "assistant",
                content: msg.response,
                timestamp: new Date(msg.createdAt),
                rating: msg.rating,
              })
            }
          }
          setMessages(loadedMessages)
          setHistoryLoaded(true)
        }
      }
    } catch (error) {
      console.error('Erreur chargement historique:', error)
    } finally {
      setIsLoadingHistory(false)
    }
  }, [])

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  // Envoyer un feedback
  const sendFeedback = async (messageId: number, rating: "positive" | "negative") => {
    try {
      const response = await fetch('/api/chat/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ messageId, rating }),
      })
      
      if (response.ok) {
        setMessages(prev => prev.map(msg => 
          msg.id === messageId && msg.role === "assistant"
            ? { ...msg, rating }
            : msg
        ))
      }
    } catch (error) {
      console.error('Erreur envoi feedback:', error)
    }
  }

  // Sélectionner une réponse en mode dual
  const handleSelectResponse = async (messageIdx: number, response: DualResponse) => {
    const msg = messages[messageIdx]
    if (!msg.id) return

    try {
      await selectDualResponse(msg.id, response.content, response.id)
      
      setMessages(prev => {
        const newMessages = [...prev]
        newMessages[messageIdx] = {
          ...newMessages[messageIdx],
          content: response.content,
          selectedResponse: response.id,
          dualResponses: undefined,
        }
        return newMessages
      })
    } catch (error) {
      console.error('Erreur sélection réponse:', error)
    }
  }

  // Effacer l'historique
  const clearHistory = async () => {
    if (!confirm('Êtes-vous sûr de vouloir effacer tout l\'historique ?')) return
    
    try {
      const response = await fetch('/api/chat/history', { 
        method: 'DELETE',
        credentials: 'include'
      })
      if (response.ok) {
        setMessages([])
        setHistoryLoaded(false)
      }
    } catch (error) {
      console.error('Erreur suppression historique:', error)
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = input
    setInput("")
    setIsLoading(true)

    try {
      // Mode dual: 2 réponses alternatives
      if (settings.dualResponse) {
        const result = await sendChatDualMode(currentInput, undefined, settings)
        
        setMessages((prev) => [
          ...prev,
          {
            id: result.messageId,
            role: "assistant",
            content: "",
            timestamp: new Date(),
            dualResponses: result.responses,
          }
        ])
      } else {
        // Mode standard: streaming
        let assistantMessage: Message = {
          role: "assistant",
          content: "",
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])

        const returnedMessageId = await sendChatMessageStream(
          currentInput, 
          undefined, 
          (chunk, msgId) => {
            if (msgId && !currentMessageIdRef.current) {
              currentMessageIdRef.current = msgId
            }
            if (!chunk) return
            
            setMessages((prev) => {
              const newMessages = [...prev]
              const lastIndex = newMessages.length - 1
              newMessages[lastIndex] = {
                ...newMessages[lastIndex],
                content: newMessages[lastIndex].content + chunk,
                id: currentMessageIdRef.current || undefined,
              }
              return newMessages
            })
          },
          settings
        )
        
        if (returnedMessageId || currentMessageIdRef.current) {
          setMessages((prev) => {
            const newMessages = [...prev]
            newMessages[newMessages.length - 1].id = returnedMessageId || currentMessageIdRef.current!
            return newMessages
          })
        }
      }
    } catch (error) {
      console.error('Erreur chat:', error)
      setMessages((prev) => {
        const newMessages = [...prev]
        if (newMessages[newMessages.length - 1]?.role === "assistant") {
          newMessages[newMessages.length - 1].content = "Erreur lors de la communication avec l'IA."
        }
        return newMessages
      })
    } finally {
      setIsLoading(false)
      currentMessageIdRef.current = null
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chat IA Expert</h1>
          <p className="text-muted-foreground mt-1">
            Assistant maintenance photovoltaïque
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={showSettings ? "default" : "outline"}
            size="sm"
            onClick={() => setShowSettings(!showSettings)}
          >
            <Settings2 className="h-4 w-4 mr-2" />
            Réglages
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={loadHistory}
            disabled={isLoadingHistory}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Actualiser
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={clearHistory}
            disabled={messages.length === 0}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Effacer
          </Button>
        </div>
      </div>

      {/* Panneau de réglages */}
      {showSettings && (
        <Card className="bg-muted/50">
          <CardContent className="p-4">
            <h3 className="font-semibold mb-3">Réglages de l'IA</h3>
            <div className="flex flex-wrap gap-4">
              <Button
                variant={settings.concise ? "default" : "outline"}
                size="sm"
                onClick={() => updateSettings({ ...settings, concise: !settings.concise })}
                className="flex items-center gap-2"
              >
                <Zap className="h-4 w-4" />
                Mode Concis
                {settings.concise && <Check className="h-3 w-3 ml-1" />}
              </Button>
              <Button
                variant={settings.dualResponse ? "default" : "outline"}
                size="sm"
                onClick={() => updateSettings({ ...settings, dualResponse: !settings.dualResponse })}
                className="flex items-center gap-2"
              >
                <GitCompare className="h-4 w-4" />
                Double Réponse
                {settings.dualResponse && <Check className="h-3 w-3 ml-1" />}
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              <strong>Mode Concis:</strong> Réponses courtes, précises, avec questions ciblées.
              <br />
              <strong>Double Réponse:</strong> 2 propositions pour choisir la meilleure (entraîne l'IA).
            </p>
          </CardContent>
        </Card>
      )}

      {/* Indicateur historique */}
      {historyLoaded && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
          <MessageSquare className="h-4 w-4" />
          Conversation restaurée - {messages.filter(m => m.role === "user").length} échanges
        </div>
      )}

      {/* Zone de chat */}
      <Card className="h-[550px] flex flex-col">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {isLoadingHistory && (
            <div className="text-center text-muted-foreground py-12">
              <div className="flex justify-center gap-1 mb-2">
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-75" />
                <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-150" />
              </div>
              <p>Chargement de l'historique...</p>
            </div>
          )}

          {!isLoadingHistory && messages.length === 0 && (
            <div className="text-center text-muted-foreground py-12">
              <p className="text-lg">💬 Commencez une conversation</p>
              <p className="text-sm mt-2">
                Posez vos questions sur les procédures, équipements ou maintenance
              </p>
              {settings.dualResponse && (
                <p className="text-xs mt-4 text-blue-600">
                  Mode double réponse activé - Vous pourrez choisir la meilleure réponse
                </p>
              )}
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className="flex flex-col gap-2 max-w-[85%]">
                {/* Mode dual: afficher les 2 réponses */}
                {message.dualResponses && message.dualResponses.length > 0 ? (
                  <div className="space-y-3">
                    <p className="text-sm text-muted-foreground font-medium">
                      Choisissez la réponse la plus appropriée :
                    </p>
                    {message.dualResponses.map((resp) => (
                      <div
                        key={resp.id}
                        className="bg-muted rounded-lg p-4 border-2 border-transparent hover:border-primary cursor-pointer transition-colors"
                        onClick={() => handleSelectResponse(idx, resp)}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-semibold text-primary">{resp.label}</span>
                          <Button size="sm" variant="outline">
                            <Check className="h-3 w-3 mr-1" />
                            Choisir
                          </Button>
                        </div>
                        <p className="whitespace-pre-wrap text-sm">{resp.content}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <>
                    <div
                      className={`rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.selectedResponse && (
                        <p className="text-xs mt-2 opacity-60">
                          ✓ Réponse {message.selectedResponse} sélectionnée
                        </p>
                      )}
                    </div>
                    
                    {/* Boutons de feedback */}
                    {message.role === "assistant" && message.content && !isLoading && !message.dualResponses && (
                      <div className="flex items-center gap-1 ml-2">
                        <span className="text-xs text-muted-foreground mr-2">Utile ?</span>
                        <Button
                          variant={message.rating === "positive" ? "default" : "ghost"}
                          size="sm"
                          className="h-6 px-2"
                          onClick={() => message.id && sendFeedback(message.id, "positive")}
                          disabled={!message.id}
                        >
                          <ThumbsUp className={`h-3 w-3 ${message.rating === "positive" ? "text-green-400" : ""}`} />
                        </Button>
                        <Button
                          variant={message.rating === "negative" ? "default" : "ghost"}
                          size="sm"
                          className="h-6 px-2"
                          onClick={() => message.id && sendFeedback(message.id, "negative")}
                          disabled={!message.id}
                        >
                          <ThumbsDown className={`h-3 w-3 ${message.rating === "negative" ? "text-red-400" : ""}`} />
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg p-4">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-75" />
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce delay-150" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </CardContent>

        {/* Zone de saisie */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={settings.concise ? "Question courte..." : "Tapez votre message..."}
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              size="icon"
            >
              <Send className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              disabled
              title="Reconnaissance vocale (bientôt)"
            >
              <Mic className="h-4 w-4" />
            </Button>
          </div>
          {(settings.concise || settings.dualResponse) && (
            <div className="flex gap-2 mt-2 text-xs text-muted-foreground">
              {settings.concise && <span className="bg-primary/10 px-2 py-1 rounded">⚡ Mode concis</span>}
              {settings.dualResponse && <span className="bg-primary/10 px-2 py-1 rounded">🔀 Double réponse</span>}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
