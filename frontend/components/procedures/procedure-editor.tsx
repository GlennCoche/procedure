"use client"

import { useCallback, useState } from "react"
import {
  ReactFlow,
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Plus, Trash2 } from "lucide-react"

interface Step {
  id: string
  title: string
  description: string
  instructions: string
  order: number
}

interface ProcedureEditorProps {
  onFlowchartChange?: (data: any) => void
  onStepsChange?: (steps: Step[]) => void
  initialNodes?: Node[]
  initialEdges?: Edge[]
  initialSteps?: Step[]
}

export function ProcedureEditor({
  onFlowchartChange,
  onStepsChange,
  initialNodes,
  initialEdges,
  initialSteps,
}: ProcedureEditorProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(
    initialNodes || [
      {
        id: "1",
        type: "input",
        data: { label: "Début" },
        position: { x: 250, y: 0 },
      },
    ]
  )
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges || [])
  const [steps, setSteps] = useState<Step[]>(
    initialSteps || [
      {
        id: "1",
        title: "",
        description: "",
        instructions: "",
        order: 0,
      },
    ]
  )
  const [selectedStepId, setSelectedStepId] = useState<string | null>(null)

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) => addEdge(params, eds))
    },
    [setEdges]
  )

  const addNode = () => {
    const newNodeId = String(nodes.length + 1)
    const newStep: Step = {
      id: newNodeId,
      title: "",
      description: "",
      instructions: "",
      order: steps.length,
    }

    setNodes((nds) => [
      ...nds,
      {
        id: newNodeId,
        data: { label: `Étape ${newNodeId}` },
        position: {
          x: Math.random() * 400,
          y: Math.random() * 400,
        },
      },
    ])

    setSteps((prev) => [...prev, newStep])
    setSelectedStepId(newNodeId)
  }

  const deleteNode = (nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId))
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId))
    setSteps((prev) => prev.filter((step) => step.id !== nodeId))
    if (selectedStepId === nodeId) {
      setSelectedStepId(null)
    }
  }

  const updateStep = (stepId: string, field: keyof Step, value: string) => {
    setSteps((prev) => {
      const updated = prev.map((step) =>
        step.id === stepId ? { ...step, [field]: value } : step
      )
      onStepsChange?.(updated)
      return updated
    })

    // Mettre à jour le label du node
    setNodes((nds) =>
      nds.map((node) =>
        node.id === stepId
          ? { ...node, data: { ...node.data, label: field === "title" ? value || `Étape ${stepId}` : node.data.label } }
          : node
      )
    )
  }

  const selectedStep = steps.find((s) => s.id === selectedStepId)

  // Notifier les changements
  const handleNodesChange = (changes: any) => {
    onNodesChange(changes)
    onFlowchartChange?.({ nodes, edges })
  }

  const handleEdgesChange = (changes: any) => {
    onEdgesChange(changes)
    onFlowchartChange?.({ nodes, edges })
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Éditeur de Procédure</CardTitle>
              <CardDescription>
                Créez le logigramme et configurez les étapes
              </CardDescription>
            </div>
            <Button onClick={addNode} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Ajouter étape
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="h-[500px] border rounded-lg">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={handleNodesChange}
              onEdgesChange={handleEdgesChange}
              onConnect={onConnect}
              onNodeClick={(event, node) => setSelectedStepId(node.id)}
              fitView
            >
              <Controls />
              <MiniMap />
              <Background />
            </ReactFlow>
          </div>
        </CardContent>
      </Card>

      {selectedStep && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Configuration de l'étape {selectedStepId}</CardTitle>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => deleteNode(selectedStepId)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="step-title">Titre *</Label>
              <Input
                id="step-title"
                value={selectedStep.title}
                onChange={(e) => updateStep(selectedStepId, "title", e.target.value)}
                placeholder="Titre de l'étape"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="step-description">Description</Label>
              <Input
                id="step-description"
                value={selectedStep.description}
                onChange={(e) => updateStep(selectedStepId, "description", e.target.value)}
                placeholder="Description courte"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="step-instructions">Instructions</Label>
              <textarea
                id="step-instructions"
                value={selectedStep.instructions}
                onChange={(e) => updateStep(selectedStepId, "instructions", e.target.value)}
                placeholder="Instructions détaillées pour cette étape"
                className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>
          </CardContent>
        </Card>
      )}

      {!selectedStep && (
        <Card>
          <CardContent className="py-8 text-center text-muted-foreground">
            Cliquez sur un nœud dans le logigramme pour configurer une étape
          </CardContent>
        </Card>
      )}
    </div>
  )
}
