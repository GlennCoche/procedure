export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp?: Date
}

export interface ChatContext {
  procedureId?: number
  stepId?: number
  executionId?: number
}

export async function sendChatMessage(
  _message: string,
  _context?: ChatContext
): Promise<string> {
  // Note: Cette fonction n'est plus utilisée car on utilise le streaming
  // Gardée pour compatibilité
  throw new Error("Utilisez sendChatMessageStream à la place")
}

export async function sendChatMessageStream(
  message: string,
  context: ChatContext | undefined,
  onChunk: (chunk: string, messageId?: number) => void
): Promise<number | undefined> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // Inclure les cookies
    body: JSON.stringify({ message, context }),
  })

  if (!response.ok) {
    throw new Error(`Erreur HTTP: ${response.status}`)
  }

  if (!response.body) {
    throw new Error("No response body")
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let messageId: number | undefined

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value)
    const lines = chunk.split("\n")

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6)
        if (data === "[DONE]") continue
        try {
          const parsed = JSON.parse(data)
          // Capturer l'ID du message pour le feedback
          if (parsed.messageId) {
            messageId = parsed.messageId
            onChunk("", messageId)
          }
          if (parsed.content) {
            onChunk(parsed.content, messageId)
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }

  return messageId
}
