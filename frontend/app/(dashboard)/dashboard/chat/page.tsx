"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { sendChatMessageStream } from "@/lib/ai"
import { Mic, Send, ThumbsUp, ThumbsDown, Trash2, RotateCcw, MessageSquare } from "lucide-react"

interface Message {
  id?: number
  role: "user" | "assistant"
  content: string
  timestamp: Date
  rating?: "positive" | "negative" | null
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const [isListening, setIsListening] = useState(false)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const currentMessageIdRef = useRef<number | null>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Charger l'historique au montage du composant
  const loadHistory = useCallback(async () => {
    try {
      setIsLoadingHistory(true)
      const response = await fetch('/api/chat/history')
      if (response.ok) {
        const data = await response.json()
        if (data.messages && data.messages.length > 0) {
          const loadedMessages: Message[] = []
          for (const msg of data.messages) {
            // Message utilisateur
            loadedMessages.push({
              id: msg.id,
              role: "user",
              content: msg.message,
              timestamp: new Date(msg.createdAt),
            })
            // Réponse IA si disponible
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

  // Envoyer un feedback (like/dislike)
  const sendFeedback = async (messageId: number, rating: "positive" | "negative") => {
    try {
      const response = await fetch('/api/chat/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messageId, rating }),
      })
      
      if (response.ok) {
        // Mettre à jour l'état local
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

  // Effacer l'historique
  const clearHistory = async () => {
    if (!confirm('Êtes-vous sûr de vouloir effacer tout l\'historique ?')) return
    
    try {
      const response = await fetch('/api/chat/history', { method: 'DELETE' })
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
    setInput("")
    setIsLoading(true)

    let assistantMessage: Message = {
      role: "assistant",
      content: "",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, assistantMessage])

    try {
      const returnedMessageId = await sendChatMessageStream(input, undefined, (chunk, msgId) => {
        // Capturer l'ID du message pour le feedback
        if (msgId && !currentMessageIdRef.current) {
          currentMessageIdRef.current = msgId
        }
        
        // Ne pas ajouter de chunk vide (juste pour l'ID)
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
      })
      
      // Mettre à jour l'ID du dernier message avec l'ID retourné
      const finalMessageId = returnedMessageId || currentMessageIdRef.current
      if (finalMessageId) {
        setMessages((prev) => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1].id = finalMessageId
          return newMessages
        })
      }
    } catch (error) {
      setMessages((prev) => {
        const newMessages = [...prev]
        newMessages[newMessages.length - 1] = {
          ...assistantMessage,
          content: "Erreur lors de la communication avec l'IA.",
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
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Chat IA</h1>
          <p className="text-muted-foreground mt-2">
            Posez vos questions techniques sur la maintenance
          </p>
        </div>
        <div className="flex gap-2">
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

      {historyLoaded && (
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 flex items-center gap-2 text-sm text-blue-700 dark:text-blue-300">
          <MessageSquare className="h-4 w-4" />
          Conversation restaurée - {messages.filter(m => m.role === "user").length} échanges
        </div>
      )}

      <Card className="h-[600px] flex flex-col">
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
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
              <p>Commencez une conversation avec l'IA</p>
              <p className="text-sm mt-2">
                Posez des questions sur les procédures, les équipements, ou la maintenance
              </p>
            </div>
          )}

          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div className="flex flex-col gap-1 max-w-[80%]">
                <div
                  className={`rounded-lg p-4 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
                
                {/* Boutons de feedback pour les réponses IA */}
                {message.role === "assistant" && message.content && !isLoading && (
                  <div className="flex items-center gap-1 ml-2">
                    <span className="text-xs text-muted-foreground mr-2">
                      Cette réponse vous a-t-elle aidé ?
                    </span>
                    <Button
                      variant={message.rating === "positive" ? "default" : "ghost"}
                      size="sm"
                      className="h-7 px-2"
                      onClick={() => message.id && sendFeedback(message.id, "positive")}
                      disabled={!message.id}
                    >
                      <ThumbsUp className={`h-3 w-3 ${message.rating === "positive" ? "text-green-500" : ""}`} />
                    </Button>
                    <Button
                      variant={message.rating === "negative" ? "default" : "ghost"}
                      size="sm"
                      className="h-7 px-2"
                      onClick={() => message.id && sendFeedback(message.id, "negative")}
                      disabled={!message.id}
                    >
                      <ThumbsDown className={`h-3 w-3 ${message.rating === "negative" ? "text-red-500" : ""}`} />
                    </Button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && messages[messages.length - 1]?.content === "" && (
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

        <div className="border-t p-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Tapez votre message..."
              disabled={isLoading}
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
              disabled={isLoading}
              onClick={() => {
                // TODO: Implémenter la reconnaissance vocale
                setIsListening(!isListening)
              }}
            >
              <Mic className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
