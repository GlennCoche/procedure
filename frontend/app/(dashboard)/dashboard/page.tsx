"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { FileText, MessageSquare, Lightbulb, Camera } from "lucide-react"

interface User {
  id: number
  email: string
  role: string
}

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await fetch("/api/auth/me", {
          credentials: "include",
        })
        if (response.ok) {
          const data = await response.json()
          setUser(data.user)
        }
      } catch (error) {
        console.error("Erreur récupération user:", error)
      }
    }

    fetchUser()
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Tableau de bord</h1>
        <p className="text-muted-foreground mt-2">
          Bienvenue, {user?.email || "..."}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Procédures
            </CardTitle>
            <CardDescription>
              Accéder aux procédures de maintenance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/procedures">
              <Button className="w-full">Voir les procédures</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Chat IA
            </CardTitle>
            <CardDescription>
              Poser des questions techniques
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/chat">
              <Button className="w-full" variant="outline">Ouvrir le chat</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5" />
              Tips & Astuces
            </CardTitle>
            <CardDescription>
              Conseils et informations techniques
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/tips">
              <Button className="w-full" variant="outline">Voir les tips</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Camera className="h-5 w-5" />
              Reconnaissance
            </CardTitle>
            <CardDescription>
              Identifier un équipement
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/camera">
              <Button className="w-full" variant="outline">Prendre une photo</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
