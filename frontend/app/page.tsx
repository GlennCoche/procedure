import { redirect } from "next/navigation"

export default function Home() {
  // Rediriger vers la page de démarrage au lieu de login
  redirect("/startup")
}
