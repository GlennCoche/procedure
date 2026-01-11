"use client"

import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { apiGet } from "@/lib/api"
import Link from "next/link"
import { FileText, Play } from "lucide-react"

interface Procedure {
  id: number
  title: string
  description: string
  category: string
  tags: string[]
}

export default function ProceduresPage() {
  const { data: procedures, isLoading } = useQuery<Procedure[]>({
    queryKey: ["procedures"],
    queryFn: async () => {
      return apiGet<Procedure[]>("/procedures")
    },
  })

  if (isLoading) {
    return <div>Chargement...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Procédures de Maintenance</h1>
        <p className="text-muted-foreground mt-2">
          Sélectionnez une procédure à exécuter
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {procedures?.map((procedure) => (
          <Card key={procedure.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                {procedure.title}
              </CardTitle>
              <CardDescription>{procedure.description}</CardDescription>
            </CardHeader>
            <CardContent>
              {procedure.tags && procedure.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {procedure.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs bg-secondary rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
              <Link href={`/dashboard/procedures/${procedure.id}`}>
                <Button className="w-full">
                  <Play className="h-4 w-4 mr-2" />
                  Démarrer
                </Button>
              </Link>
            </CardContent>
          </Card>
        ))}
      </div>

      {procedures?.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Aucune procédure disponible</p>
        </div>
      )}
    </div>
  )
}
