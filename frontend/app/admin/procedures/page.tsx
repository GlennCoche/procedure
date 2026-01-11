"use client"

import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { apiGet } from "@/lib/api"
import Link from "next/link"
import { Plus, Edit, Trash2 } from "lucide-react"
import { useSession } from "next-auth/react"
import { redirect } from "next/navigation"

interface Procedure {
  id: number
  title: string
  description: string
  category: string
}

export default function AdminProceduresPage() {
  const { data: session } = useSession()

  // Vérifier que l'utilisateur est admin
  if (session && (session as any).role !== "admin") {
    redirect("/dashboard")
  }

  const { data: procedures, isLoading } = useQuery<Procedure[]>({
    queryKey: ["admin-procedures"],
    queryFn: async () => {
      return apiGet<Procedure[]>("/procedures")
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Gestion des Procédures</h1>
          <p className="text-muted-foreground mt-2">
            Créer et modifier les procédures de maintenance
          </p>
        </div>
        <Link href="/admin/procedures/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle procédure
          </Button>
        </Link>
      </div>

      {isLoading && <div>Chargement...</div>}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {procedures?.map((procedure) => (
          <Card key={procedure.id}>
            <CardHeader>
              <CardTitle>{procedure.title}</CardTitle>
              <CardDescription>{procedure.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Link href={`/admin/procedures/${procedure.id}`} className="flex-1">
                  <Button variant="outline" className="w-full">
                    <Edit className="h-4 w-4 mr-2" />
                    Modifier
                  </Button>
                </Link>
                <Button variant="destructive" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {procedures?.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Aucune procédure</p>
        </div>
      )}
    </div>
  )
}
