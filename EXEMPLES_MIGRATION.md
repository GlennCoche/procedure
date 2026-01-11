# 💻 Exemples Concrets de Migration - Next.js Full-Stack

Ce document montre **exactement** comment migrer votre code actuel vers Next.js Full-Stack.

---

## 📋 Table des Matières

1. [Migration de l'Authentification](#1-authentification)
2. [Migration des Procédures](#2-procédures)
3. [Migration du Chat IA](#3-chat-ia)
4. [Migration de la Vision IA](#4-vision-ia)
5. [Migration des Exécutions](#5-exécutions)
6. [Mise à Jour du Frontend](#6-frontend)

---

## 1. Authentification

### Avant (FastAPI)

**Backend : `backend/app/api/auth.py`**
```python
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "user": user}
```

**Frontend : `frontend/lib/api.ts`**
```typescript
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Après (Next.js Full-Stack)

**API Route : `frontend/app/api/auth/login/route.ts`**
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { comparePassword, createToken } from '@/lib/auth'
import { cookies } from 'next/headers'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()
    
    // Trouver l'utilisateur
    const user = await db.user.findUnique({
      where: { email }
    })
    
    if (!user) {
      return NextResponse.json(
        { error: 'Email ou mot de passe incorrect' },
        { status: 401 }
      )
    }
    
    // Vérifier le mot de passe
    const isValid = await comparePassword(password, user.passwordHash)
    if (!isValid) {
      return NextResponse.json(
        { error: 'Email ou mot de passe incorrect' },
        { status: 401 }
      )
    }
    
    // Créer le token
    const token = createToken({ id: user.id, role: user.role })
    
    // Stocker dans un cookie HTTP-only (plus sécurisé que localStorage)
    cookies().set('auth-token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7 // 7 jours
    })
    
    return NextResponse.json({
      user: {
        id: user.id,
        email: user.email,
        role: user.role
      }
    })
  } catch (error) {
    console.error('Erreur login:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}
```

**Helper : `frontend/lib/auth.ts`**
```typescript
import { cookies } from 'next/headers'
import { db } from './db'
import bcrypt from 'bcryptjs'
import jwt from 'jsonwebtoken'

const SECRET = process.env.JWT_SECRET || 'change-me-in-production'

export async function getCurrentUser() {
  try {
    const cookieStore = cookies()
    const token = cookieStore.get('auth-token')?.value
    
    if (!token) return null
    
    const decoded = jwt.verify(token, SECRET) as { id: number; role: string }
    
    const user = await db.user.findUnique({
      where: { id: decoded.id },
      select: { id: true, email: true, role: true }
    })
    
    return user
  } catch {
    return null
  }
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function comparePassword(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export function createToken(user: { id: number; role: string }): string {
  return jwt.sign(
    { id: user.id, role: user.role },
    SECRET,
    { expiresIn: '7d' }
  )
}
```

**Frontend : Plus besoin de `lib/api.ts` !**
```typescript
// Avant
const response = await apiClient.post('/auth/login', { email, password })

// Après
const response = await fetch('/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})
const data = await response.json()
```

---

## 2. Procédures

### Avant (FastAPI)

**Backend : `backend/app/api/procedures.py`**
```python
@router.get("/", response_model=List[ProcedureSchema])
async def get_procedures(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Procedure).filter(Procedure.is_active == 1)
    procedures = query.offset(skip).limit(limit).all()
    return procedures

@router.post("/", response_model=ProcedureSchema)
async def create_procedure(
    procedure_data: ProcedureCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    procedure = Procedure(
        title=procedure_data.title,
        description=procedure_data.description,
        tags=procedure_data.tags,
        created_by=current_user.id
    )
    db.add(procedure)
    db.commit()
    return procedure
```

### Après (Next.js Full-Stack)

**API Route : `frontend/app/api/procedures/route.ts`**
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

// GET /api/procedures
export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user) {
      return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
    }

    // Récupérer les paramètres de query
    const { searchParams } = new URL(request.url)
    const skip = parseInt(searchParams.get('skip') || '0')
    const limit = parseInt(searchParams.get('limit') || '100')
    const category = searchParams.get('category')

    // Construire la requête
    const where: any = { isActive: true }
    if (category) {
      where.category = category
    }

    const procedures = await db.procedure.findMany({
      where,
      skip,
      take: limit,
      include: {
        steps: {
          orderBy: { order: 'asc' }
        },
        createdBy: {
          select: { email: true }
        }
      }
    })

    return NextResponse.json(procedures)
  } catch (error) {
    console.error('Erreur GET /api/procedures:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}

// POST /api/procedures
export async function POST(request: NextRequest) {
  try {
    const user = await getCurrentUser()
    if (!user || user.role !== 'admin') {
      return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
    }

    const body = await request.json()

    // Créer la procédure avec Prisma
    const procedure = await db.procedure.create({
      data: {
        title: body.title,
        description: body.description,
        category: body.category,
        tags: body.tags || [],
        isActive: true,
        createdById: user.id,
        steps: {
          create: body.steps?.map((step: any, index: number) => ({
            title: step.title,
            description: step.description,
            instructions: step.instructions,
            order: index + 1,
            photos: step.photos || [],
            files: step.files || [],
            validationType: step.validationType || 'manual'
          })) || []
        }
      },
      include: {
        steps: {
          orderBy: { order: 'asc' }
        },
        createdBy: {
          select: { email: true }
        }
      }
    })

    return NextResponse.json(procedure, { status: 201 })
  } catch (error) {
    console.error('Erreur POST /api/procedures:', error)
    return NextResponse.json(
      { error: 'Erreur serveur' },
      { status: 500 }
    )
  }
}
```

**Route dynamique : `frontend/app/api/procedures/[id]/route.ts`**
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

// GET /api/procedures/:id
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  const procedure = await db.procedure.findUnique({
    where: { id: parseInt(params.id) },
    include: {
      steps: { orderBy: { order: 'asc' } },
      createdBy: { select: { email: true } }
    }
  })

  if (!procedure) {
    return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
  }

  return NextResponse.json(procedure)
}

// PUT /api/procedures/:id
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await getCurrentUser()
  if (!user || user.role !== 'admin') {
    return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
  }

  const body = await request.json()

  // Supprimer les anciennes étapes
  await db.step.deleteMany({
    where: { procedureId: parseInt(params.id) }
  })

  const procedure = await db.procedure.update({
    where: { id: parseInt(params.id) },
    data: {
      title: body.title,
      description: body.description,
      category: body.category,
      tags: body.tags || [],
      steps: {
        create: body.steps?.map((step: any, index: number) => ({
          title: step.title,
          description: step.description,
          instructions: step.instructions,
          order: index + 1,
          photos: step.photos || [],
          files: step.files || [],
          validationType: step.validationType || 'manual'
        })) || []
      }
    },
    include: {
      steps: { orderBy: { order: 'asc' } }
    }
  })

  return NextResponse.json(procedure)
}

// DELETE /api/procedures/:id
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await getCurrentUser()
  if (!user || user.role !== 'admin') {
    return NextResponse.json({ error: 'Accès refusé' }, { status: 403 })
  }

  await db.procedure.delete({
    where: { id: parseInt(params.id) }
  })

  return NextResponse.json({ success: true })
}
```

---

## 3. Chat IA

### Avant (FastAPI)

**Backend : `backend/app/api/chat.py`**
```python
@router.post("/stream")
async def chat_stream(
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Appeler OpenAI
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[...],
        stream=True
    )
    
    async def generate():
        async for chunk in stream:
            yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Frontend : `frontend/lib/ai.ts`**
```typescript
export async function sendChatMessageStream(
  message: string,
  context: ChatContext | undefined,
  onChunk: (chunk: string) => void
): Promise<void> {
  const token = localStorage.getItem("token")
  const response = await fetch(`${apiClient.defaults.baseURL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message, context }),
  })
  // ... parsing SSE
}
```

### Après (Next.js Full-Stack)

**API Route : `frontend/app/api/chat/route.ts`**
```typescript
import { NextRequest } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
})

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return new Response('Non authentifié', { status: 401 })
  }

  const { message, context } = await request.json()

  // Récupérer l'historique
  const history = await db.chatMessage.findMany({
    where: { userId: user.id },
    orderBy: { createdAt: 'desc' },
    take: 10
  })

  // Construire les messages pour OpenAI
  const messages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
    {
      role: 'system',
      content: 'Tu es un assistant technique spécialisé en maintenance photovoltaïque.'
    },
    ...history.reverse().map(msg => ({
      role: 'user' as const,
      content: msg.message
    })),
    ...history
      .filter(msg => msg.response)
      .map(msg => ({
        role: 'assistant' as const,
        content: msg.response!
      })),
    { role: 'user', content: message }
  ]

  // Sauvegarder le message utilisateur
  const chatMessage = await db.chatMessage.create({
    data: {
      userId: user.id,
      message
    }
  })

  // Appeler OpenAI avec streaming
  const completion = await openai.chat.completions.create({
    model: 'gpt-4o-mini',
    messages,
    stream: true
  })

  // Créer un stream de réponse
  const stream = new ReadableStream({
    async start(controller) {
      let fullResponse = ''
      
      try {
        for await (const chunk of completion) {
          const content = chunk.choices[0]?.delta?.content || ''
          if (content) {
            fullResponse += content
            // Envoyer le chunk au client
            controller.enqueue(
              new TextEncoder().encode(
                `data: ${JSON.stringify({ content })}\n\n`
              )
            )
          }
        }

        // Marquer la fin
        controller.enqueue(new TextEncoder().encode('data: [DONE]\n\n'))

        // Sauvegarder la réponse complète
        await db.chatMessage.update({
          where: { id: chatMessage.id },
          data: { response: fullResponse }
        })

        controller.close()
      } catch (error) {
        console.error('Erreur streaming:', error)
        controller.error(error)
      }
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  })
}
```

**Frontend : Plus besoin de `lib/api.ts` !**
```typescript
// frontend/app/(dashboard)/chat/page.tsx
'use client'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')

  const sendMessage = async () => {
    const userMessage: Message = {
      role: 'user',
      content: input
    }
    setMessages(prev => [...prev, userMessage])
    setInput('')

    // Appel direct à l'API route
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input })
    })

    if (!response.body) return

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let assistantMessage = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') continue
          
          try {
            const parsed = JSON.parse(data)
            if (parsed.content) {
              assistantMessage += parsed.content
              setMessages(prev => {
                const last = prev[prev.length - 1]
                if (last?.role === 'assistant') {
                  return [...prev.slice(0, -1), { ...last, content: assistantMessage }]
                }
                return [...prev, { role: 'assistant', content: assistantMessage }]
              })
            }
          } catch (e) {
            // Ignore
          }
        }
      }
    }
  }

  return (
    <div>
      {/* UI du chat */}
    </div>
  )
}
```

---

## 4. Vision IA

### Avant (FastAPI)

**Backend : `backend/app/api/vision.py`**
```python
@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Lire l'image
    image_data = await file.read()
    
    # Appeler OpenAI Vision
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyse cette image..."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_data).decode()}"}}
            ]
        }]
    )
    
    return {"analysis": response.choices[0].message.content}
```

### Après (Next.js Full-Stack)

**API Route : `frontend/app/api/vision/route.ts`**
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { getCurrentUser } from '@/lib/auth'
import OpenAI from 'openai'

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
})

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  try {
    const formData = await request.formData()
    const file = formData.get('image') as File

    if (!file) {
      return NextResponse.json(
        { error: 'Image requise' },
        { status: 400 }
      )
    }

    // Convertir en base64
    const arrayBuffer = await file.arrayBuffer()
    const buffer = Buffer.from(arrayBuffer)
    const base64 = buffer.toString('base64')

    // Appeler OpenAI Vision
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: 'Identifie cet équipement photovoltaïque et suggère des procédures de maintenance appropriées. Décris l\'état de l\'équipement et les actions recommandées.'
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:${file.type};base64,${base64}`
              }
            }
          ]
        }
      ],
      max_tokens: 500
    })

    const analysis = response.choices[0]?.message?.content || ''

    // (Optionnel) Rechercher des procédures similaires dans la DB
    const suggestedProcedures = await db.procedure.findMany({
      where: {
        isActive: true,
        // Recherche par mots-clés dans l'analyse
        OR: [
          { title: { contains: 'panneau', mode: 'insensitive' } },
          { tags: { has: 'maintenance' } }
        ]
      },
      take: 5
    })

    return NextResponse.json({
      analysis,
      suggestedProcedures: suggestedProcedures.map(p => ({
        id: p.id,
        title: p.title,
        description: p.description
      }))
    })
  } catch (error) {
    console.error('Erreur vision:', error)
    return NextResponse.json(
      { error: 'Erreur lors de l\'analyse' },
      { status: 500 }
    )
  }
}
```

**Frontend : Plus besoin de `lib/api.ts` !**
```typescript
// frontend/app/(dashboard)/camera/page.tsx
const handleImageUpload = async (file: File) => {
  const formData = new FormData()
  formData.append('image', file)

  const response = await fetch('/api/vision', {
    method: 'POST',
    body: formData
  })

  const data = await response.json()
  setAnalysis(data.analysis)
  setSuggestedProcedures(data.suggestedProcedures)
}
```

---

## 5. Exécutions

### Avant (FastAPI)

**Backend : `backend/app/api/executions.py`**
```python
@router.post("/", response_model=ExecutionResponse)
async def create_execution(
    execution_data: ExecutionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    execution = Execution(
        procedure_id=execution_data.procedure_id,
        user_id=current_user.id,
        status="in_progress"
    )
    db.add(execution)
    db.commit()
    return execution
```

### Après (Next.js Full-Stack)

**API Route : `frontend/app/api/executions/route.ts`**
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function POST(request: NextRequest) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  const { procedureId } = await request.json()

  const execution = await db.execution.create({
    data: {
      procedureId: parseInt(procedureId),
      userId: user.id,
      status: 'in_progress',
      currentStep: 0
    },
    include: {
      procedure: {
        include: {
          steps: { orderBy: { order: 'asc' } }
        }
      }
    }
  })

  return NextResponse.json(execution, { status: 201 })
}
```

**Route dynamique : `frontend/app/api/executions/[id]/route.ts`**
```typescript
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { getCurrentUser } from '@/lib/auth'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  const execution = await db.execution.findUnique({
    where: { id: parseInt(params.id) },
    include: {
      procedure: {
        include: {
          steps: { orderBy: { order: 'asc' } }
        }
      },
      stepExecutions: {
        include: {
          step: true
        }
      }
    }
  })

  if (!execution || execution.userId !== user.id) {
    return NextResponse.json({ error: 'Non trouvé' }, { status: 404 })
  }

  return NextResponse.json(execution)
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await getCurrentUser()
  if (!user) {
    return NextResponse.json({ error: 'Non authentifié' }, { status: 401 })
  }

  const body = await request.json()

  // Mettre à jour l'exécution de l'étape
  const stepExecution = await db.stepExecution.upsert({
    where: {
      executionId_stepId: {
        executionId: parseInt(params.id),
        stepId: body.stepId
      }
    },
    update: {
      status: body.status,
      photos: body.photos || [],
      comments: body.comments,
      completedAt: body.status === 'completed' ? new Date() : null
    },
    create: {
      executionId: parseInt(params.id),
      stepId: body.stepId,
      status: body.status,
      photos: body.photos || [],
      comments: body.comments,
      completedAt: body.status === 'completed' ? new Date() : null
    }
  })

  // Mettre à jour l'exécution principale
  const execution = await db.execution.update({
    where: { id: parseInt(params.id) },
    data: {
      currentStep: body.stepId,
      status: body.status === 'completed' ? 'completed' : 'in_progress',
      completedAt: body.status === 'completed' ? new Date() : undefined
    },
    include: {
      procedure: {
        include: {
          steps: { orderBy: { order: 'asc' } }
        }
      },
      stepExecutions: true
    }
  })

  return NextResponse.json(execution)
}
```

---

## 6. Frontend

### Mise à Jour des Appels API

**Avant :**
```typescript
// frontend/lib/api.ts
import axios from 'axios'
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api'
})

// Utilisation
const procedures = await apiClient.get('/procedures')
```

**Après :**
```typescript
// Plus besoin de lib/api.ts !

// Utilisation directe
const response = await fetch('/api/procedures')
const procedures = await response.json()

// Ou avec React Query
const { data } = useQuery({
  queryKey: ['procedures'],
  queryFn: async () => {
    const res = await fetch('/api/procedures')
    if (!res.ok) throw new Error('Erreur')
    return res.json()
  }
})
```

### Exemple : Page des Procédures

**Avant :**
```typescript
// frontend/app/(dashboard)/procedures/page.tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api'

export default function ProceduresPage() {
  const { data: procedures } = useQuery({
    queryKey: ['procedures'],
    queryFn: () => apiClient.get('/procedures').then(res => res.data)
  })

  return (
    <div>
      {procedures?.map(proc => (
        <div key={proc.id}>{proc.title}</div>
      ))}
    </div>
  )
}
```

**Après :**
```typescript
// frontend/app/(dashboard)/procedures/page.tsx
'use client'

import { useQuery } from '@tanstack/react-query'

export default function ProceduresPage() {
  const { data: procedures, isLoading } = useQuery({
    queryKey: ['procedures'],
    queryFn: async () => {
      const res = await fetch('/api/procedures')
      if (!res.ok) throw new Error('Erreur')
      return res.json()
    }
  })

  if (isLoading) return <div>Chargement...</div>

  return (
    <div>
      {procedures?.map((proc: any) => (
        <div key={proc.id}>{proc.title}</div>
      ))}
    </div>
  )
}
```

---

## 📦 Schéma Prisma Complet

**`frontend/prisma/schema.prisma`**
```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"  // Dev: SQLite, Prod: PostgreSQL
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  passwordHash String @map("password_hash")
  role      String   @default("technician")
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  
  procedures Procedure[] @relation("CreatedBy")
  executions Execution[]
  chatMessages ChatMessage[]
  
  @@map("users")
}

model Procedure {
  id          Int      @id @default(autoincrement())
  title       String
  description String?
  category    String?
  tags        String   // JSON string
  isActive    Boolean  @default(true) @map("is_active")
  createdById Int      @map("created_by")
  createdAt   DateTime @default(now()) @map("created_at")
  updatedAt   DateTime @updatedAt @map("updated_at")
  
  createdBy User        @relation("CreatedBy", fields: [createdById], references: [id])
  steps    Step[]
  executions Execution[]
  
  @@map("procedures")
}

model Step {
  id            Int      @id @default(autoincrement())
  procedureId   Int      @map("procedure_id")
  order         Int
  title         String
  description   String?
  instructions  String?
  photos        String?  // JSON string
  files         String?  // JSON string
  validationType String? @default("manual") @map("validation_type")
  createdAt     DateTime @default(now()) @map("created_at")
  
  procedure Procedure @relation(fields: [procedureId], references: [id], onDelete: Cascade)
  stepExecutions StepExecution[]
  
  @@map("steps")
}

model Execution {
  id          Int      @id @default(autoincrement())
  procedureId Int      @map("procedure_id")
  userId      Int      @map("user_id")
  status      String   @default("in_progress")
  currentStep Int?     @map("current_step")
  startedAt   DateTime @default(now()) @map("started_at")
  completedAt DateTime? @map("completed_at")
  
  procedure Procedure @relation(fields: [procedureId], references: [id])
  user      User     @relation(fields: [userId], references: [id])
  stepExecutions StepExecution[]
  
  @@map("executions")
}

model StepExecution {
  id          Int      @id @default(autoincrement())
  executionId Int      @map("execution_id")
  stepId      Int      @map("step_id")
  status      String   @default("pending")
  photos      String?  // JSON string
  comments    String?
  completedAt DateTime? @map("completed_at")
  
  execution Execution @relation(fields: [executionId], references: [id], onDelete: Cascade)
  step      Step      @relation(fields: [stepId], references: [id])
  
  @@unique([executionId, stepId])
  @@map("step_executions")
}

model Tip {
  id        Int      @id @default(autoincrement())
  title     String
  content   String
  category  String?
  tags      String?  // JSON string
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")
  
  @@map("tips")
}

model ChatMessage {
  id        Int      @id @default(autoincrement())
  userId    Int      @map("user_id")
  message   String
  response  String?
  createdAt DateTime @default(now()) @map("created_at")
  
  user User @relation(fields: [userId], references: [id])
  
  @@map("chat_messages")
}
```

---

## 🎯 Résumé des Changements

| Élément | Avant | Après |
|---------|-------|-------|
| **Backend** | FastAPI (Python) | Next.js API Routes (TypeScript) |
| **Base de données** | SQLAlchemy | Prisma |
| **Appels API** | `axios` vers `localhost:8000` | `fetch` vers `/api/*` |
| **Authentification** | JWT dans localStorage | JWT dans cookie HTTP-only |
| **CORS** | Nécessaire | Pas besoin (même origine) |
| **Déploiement** | 2 services | 1 service (Vercel) |

---

**Voulez-vous que je commence la migration maintenant ?** 🚀
