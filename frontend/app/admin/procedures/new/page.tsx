"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ProcedureEditor } from "@/components/procedures/procedure-editor"
import { apiPost } from "@/lib/api"
import { ArrowLeft } from "lucide-react"

export default function NewProcedurePage() {
  const router = useRouter()
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [category, setCategory] = useState("")
  const [isSaving, setIsSaving] = useState(false)
  const [flowchartData, setFlowchartData] = useState<any>(null)
  const [steps, setSteps] = useState<any[]>([])

  const handleSave = async () => {
    if (!title.trim()) {
      alert("Le titre est requis")
      return
    }

    setIsSaving(true)
    try {
      await apiPost("/procedures", {
        title,
        description,
        category,
        flowchart_data: flowchartData,
        steps: steps.map((step, idx) => ({
          ...step,
          order: idx,
        })),
      })
      router.push("/admin/procedures")
    } catch (error) {
      console.error("Erreur lors de la sauvegarde:", error)
      alert("Erreur lors de la sauvegarde")
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Retour
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Nouvelle Procédure</h1>
          <p className="text-muted-foreground mt-2">
            Créez une nouvelle procédure de maintenance
          </p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Informations</CardTitle>
              <CardDescription>Détails de la procédure</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Titre *</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Ex: Maintenance onduleur"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Description de la procédure"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Catégorie</Label>
                <Input
                  id="category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="Ex: Maintenance préventive"
                />
              </div>
              <Button onClick={handleSave} disabled={isSaving} className="w-full">
                {isSaving ? "Sauvegarde..." : "Sauvegarder"}
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2">
          <ProcedureEditor
            onFlowchartChange={setFlowchartData}
            onStepsChange={setSteps}
          />
        </div>
      </div>
    </div>
  )
}
