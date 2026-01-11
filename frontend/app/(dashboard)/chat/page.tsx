"use client"

import { useState, useRef, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { sendChatMessageStream } from "@/lib/ai"
import { Mic, Send } from "lucide-react"

interface Message {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
      await sendChatMessageStream(input, undefined, (chunk) => {
        setMessages((prev) => {
          const newMessages = [...prev]
          newMessages[newMessages.length - 1] = {
            ...assistantMessage,
            content: assistantMessage.content + chunk,
          }
          assistantMessage = newMessages[newMessages.length - 1]
          return newMessages
        })
      })
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
      <div>
        <h1 className="text-3xl font-bold">Chat IA</h1>
        <p className="text-muted-foreground mt-2">
          Posez vos questions techniques sur la maintenance
        </p>
      </div>

      <Card className="h-[600px] flex flex-col">
        <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
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
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === "user"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
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
