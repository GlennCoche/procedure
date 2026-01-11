"use client"

import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { apiGet } from "@/lib/api"
import { useState } from "react"
import { Lightbulb, Search } from "lucide-react"

interface Tip {
  id: number
  title: string
  content: string
  category: string
  tags: string[]
}

export default function TipsPage() {
  const [search, setSearch] = useState("")

  const { data: tips, isLoading } = useQuery<Tip[]>({
    queryKey: ["tips", search],
    queryFn: async () => {
      const url = search ? `/tips?search=${encodeURIComponent(search)}` : "/tips"
      return apiGet<Tip[]>(url)
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tips & Astuces</h1>
        <p className="text-muted-foreground mt-2">
          Conseils techniques et informations pratiques
        </p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Rechercher..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {isLoading && <div>Chargement...</div>}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {tips?.map((tip) => (
          <Card key={tip.id}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5" />
                {tip.title}
              </CardTitle>
              {tip.category && (
                <CardDescription>{tip.category}</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              <p className="text-sm whitespace-pre-line">{tip.content}</p>
              {tip.tags && tip.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {tip.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs bg-secondary rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {tips?.length === 0 && !isLoading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Aucun tip trouvé</p>
        </div>
      )}
    </div>
  )
}
