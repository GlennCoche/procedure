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

export interface ChatSettings {
  concise: boolean      // Réponses courtes et précises
  dualResponse: boolean // Mode 2 réponses alternatives
}

export interface DualResponse {
  id: string
  content: string
  label: string
}

export interface DualResponseResult {
  messageId: number
  dualMode: true
  responses: DualResponse[]
}

export async function sendChatMessage(
  _message: string,
  _context?: ChatContext
): Promise<string> {
  throw new Error("Utilisez sendChatMessageStream à la place")
}

export async function sendChatMessageStream(
  message: string,
  context: ChatContext | undefined,
  onChunk: (chunk: string, messageId?: number) => void,
  settings?: ChatSettings
): Promise<number | undefined> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message, context, settings }),
  })

  if (!response.ok) {
    throw new Error(`Erreur HTTP: ${response.status}`)
  }

  // Mode dual: réponse JSON simple
  if (settings?.dualResponse) {
    const data = await response.json()
    return data.messageId
  }

  // Mode standard: streaming
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

export async function sendChatDualMode(
  message: string,
  context: ChatContext | undefined,
  settings: ChatSettings
): Promise<DualResponseResult> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ message, context, settings: { ...settings, dualResponse: true } }),
  })

  if (!response.ok) {
    throw new Error(`Erreur HTTP: ${response.status}`)
  }

  return response.json()
}

export async function selectDualResponse(
  messageId: number,
  selectedResponse: string,
  selectedId: string
): Promise<void> {
  const response = await fetch("/api/chat", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ messageId, selectedResponse, selectedId }),
  })

  if (!response.ok) {
    throw new Error(`Erreur HTTP: ${response.status}`)
  }
}
