"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { apiGet, apiPost, apiPut } from "@/lib/api"
import { useState } from "react"
import { Check, ChevronLeft, ChevronRight, Camera } from "lucide-react"

interface Step {
  id: number
  title: string
  description: string
  instructions: string
  order: number
  photos: string[]
}

interface Procedure {
  id: number
  title: string
  description: string
  steps: Step[]
}

export default function ProcedureExecutionPage() {
  const params = useParams()
  const router = useRouter()
  const procedureId = parseInt(params.id as string)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [comments, setComments] = useState("")
  const [executionId, setExecutionId] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: procedure, isLoading } = useQuery<Procedure>({
    queryKey: ["procedure", procedureId],
    queryFn: async () => {
      return apiGet<Procedure>(`/procedures/${procedureId}`)
    },
  })

  const createExecutionMutation = useMutation({
    mutationFn: async () => {
      const data = await apiPost<{ id: number }>("/executions", {
        procedure_id: procedureId,
      })
      return data
    },
    onSuccess: (data) => {
      setExecutionId(data.id)
    },
  })

  const updateStepMutation = useMutation({
    mutationFn: async (status: string) => {
      if (!executionId || !procedure) return
      const currentStep = procedure.steps[currentStepIndex]
      return apiPut(`/executions/${executionId}/step`, {
        step_id: currentStep.id,
        status,
        comments,
        photos: [],
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["execution", executionId] })
    },
  })

  const completeExecutionMutation = useMutation({
    mutationFn: async () => {
      if (!executionId) return
      return apiPut(`/executions/${executionId}/complete`, {})
    },
    onSuccess: () => {
      router.push("/dashboard/procedures")
    },
  })

  if (isLoading) {
    return <div>Chargement...</div>
  }

  if (!procedure) {
    return <div>Procédure non trouvée</div>
  }

  const currentStep = procedure.steps[currentStepIndex]
  const isFirstStep = currentStepIndex === 0
  const isLastStep = currentStepIndex === procedure.steps.length - 1

  const handleStart = () => {
    createExecutionMutation.mutate()
  }

  const handleNext = async () => {
    if (!executionId || !procedure) return
    try {
      await updateStepMutation.mutateAsync("completed")
      if (!isLastStep) {
        setCurrentStepIndex(currentStepIndex + 1)
        setComments("")
      }
    } catch (error) {
      console.error("Erreur lors de la mise à jour de l'étape:", error)
    }
  }

  const handlePrevious = () => {
    if (!isFirstStep) {
      setCurrentStepIndex(currentStepIndex - 1)
      setComments("")
    }
  }

  const handleComplete = async () => {
    if (!executionId || !procedure) return
    try {
      await updateStepMutation.mutateAsync("completed")
      await completeExecutionMutation.mutateAsync()
    } catch (error) {
      console.error("Erreur lors de la finalisation:", error)
    }
  }

  if (!executionId) {
    return (
      <div className="space-y-6">
        <Button onClick={() => router.back()} variant="ghost">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Retour
        </Button>
        <Card>
          <CardHeader>
            <CardTitle>{procedure.title}</CardTitle>
            <CardDescription>{procedure.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="mb-4">
              Cette procédure contient {procedure.steps.length} étape(s).
            </p>
            <Button onClick={handleStart} className="w-full">
              Démarrer la procédure
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button onClick={() => router.back()} variant="ghost">
          <ChevronLeft className="h-4 w-4 mr-2" />
          Retour
        </Button>
        <div className="text-sm text-muted-foreground">
          Étape {currentStepIndex + 1} sur {procedure.steps.length}
        </div>
      </div>

      <div className="w-full bg-secondary rounded-full h-2">
        <div
          className="bg-primary h-2 rounded-full transition-all"
          style={{ width: `${((currentStepIndex + 1) / procedure.steps.length) * 100}%` }}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{currentStep.title}</CardTitle>
          {currentStep.description && (
            <CardDescription>{currentStep.description}</CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {currentStep.instructions && (
            <div className="prose max-w-none">
              <p className="whitespace-pre-line">{currentStep.instructions}</p>
            </div>
          )}

          {currentStep.photos && currentStep.photos.length > 0 && (
            <div className="grid grid-cols-2 gap-4">
              {currentStep.photos.map((photo, idx) => (
                <img
                  key={idx}
                  src={photo}
                  alt={`Étape ${currentStepIndex + 1} - Photo ${idx + 1}`}
                  className="rounded-lg"
                />
              ))}
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="comments">Commentaires (optionnel)</Label>
            <Input
              id="comments"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Ajoutez vos commentaires..."
            />
          </div>

          <div className="flex gap-2">
            {!isFirstStep && (
              <Button onClick={handlePrevious} variant="outline">
                <ChevronLeft className="h-4 w-4 mr-2" />
                Précédent
              </Button>
            )}
            <div className="flex-1" />
            {isLastStep ? (
              <Button onClick={handleComplete}>
                <Check className="h-4 w-4 mr-2" />
                Terminer
              </Button>
            ) : (
              <Button onClick={handleNext}>
                Suivant
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
