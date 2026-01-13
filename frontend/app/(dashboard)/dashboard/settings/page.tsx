"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Settings, Search, Filter, Download, Zap, Radio, Gauge, Shield, Wifi, FileText } from "lucide-react"

interface Setting {
  id: number
  brand: string
  equipmentType: string
  model: string | null
  category: string
  name: string
  value: string
  unit: string | null
  country: string
  sourceDoc: string | null
  pageNumber: number | null
  notes: string | null
}

interface FiltersData {
  brands: string[]
  categories: string[]
  equipmentTypes: string[]
}

const CATEGORY_ICONS: Record<string, any> = {
  TENSION: Zap,
  FREQUENCE: Radio,
  PUISSANCE: Gauge,
  RESEAU: Wifi,
  PROTECTION: Shield,
  COMMUNICATION: Wifi,
  INJECTION: Gauge,
}

const CATEGORY_COLORS: Record<string, string> = {
  TENSION: "bg-yellow-100 text-yellow-800 border-yellow-200",
  FREQUENCE: "bg-blue-100 text-blue-800 border-blue-200",
  PUISSANCE: "bg-green-100 text-green-800 border-green-200",
  RESEAU: "bg-purple-100 text-purple-800 border-purple-200",
  PROTECTION: "bg-red-100 text-red-800 border-red-200",
  COMMUNICATION: "bg-cyan-100 text-cyan-800 border-cyan-200",
  INJECTION: "bg-orange-100 text-orange-800 border-orange-200",
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Setting[]>([])
  const [filters, setFilters] = useState<FiltersData>({ brands: [], categories: [], equipmentTypes: [] })
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [selectedBrand, setSelectedBrand] = useState<string>("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [selectedEquipmentType, setSelectedEquipmentType] = useState<string>("")

  useEffect(() => {
    fetchSettings()
  }, [selectedBrand, selectedCategory, selectedEquipmentType])

  const fetchSettings = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedBrand) params.append("brand", selectedBrand)
      if (selectedCategory) params.append("category", selectedCategory)
      if (selectedEquipmentType) params.append("equipmentType", selectedEquipmentType)
      if (search) params.append("search", search)

      const res = await fetch(`/api/settings?${params.toString()}`)
      if (res.ok) {
        const data = await res.json()
        setSettings(data.settings)
        setFilters(data.filters)
      }
    } catch (error) {
      console.error("Erreur chargement settings:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    fetchSettings()
  }

  const handleExport = () => {
    const csv = [
      ["Marque", "Type", "Modèle", "Catégorie", "Paramètre", "Valeur", "Unité", "Source", "Notes"].join(";"),
      ...settings.map(s => [
        s.brand,
        s.equipmentType,
        s.model || "",
        s.category,
        s.name,
        s.value,
        s.unit || "",
        s.sourceDoc || "",
        s.notes || ""
      ].join(";"))
    ].join("\n")

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = `reglages_france_${new Date().toISOString().split("T")[0]}.csv`
    link.click()
  }

  // Grouper les paramètres par catégorie
  const settingsByCategory = settings.reduce((acc, setting) => {
    if (!acc[setting.category]) {
      acc[setting.category] = []
    }
    acc[setting.category].push(setting)
    return acc
  }, {} as Record<string, Setting[]>)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Settings className="h-8 w-8" />
            Réglages France
          </h1>
          <p className="text-muted-foreground mt-2">
            Paramètres techniques spécifiques à la France métropolitaine
          </p>
        </div>
        <Button onClick={handleExport} variant="outline" className="gap-2">
          <Download className="h-4 w-4" />
          Exporter CSV
        </Button>
      </div>

      {/* Filtres */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtres
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Marque</label>
              <select
                className="w-full border rounded-md p-2"
                value={selectedBrand}
                onChange={(e) => setSelectedBrand(e.target.value)}
              >
                <option value="">Toutes les marques</option>
                {filters.brands.map(brand => (
                  <option key={brand} value={brand}>{brand}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Catégorie</label>
              <select
                className="w-full border rounded-md p-2"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <option value="">Toutes les catégories</option>
                {filters.categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Type d'équipement</label>
              <select
                className="w-full border rounded-md p-2"
                value={selectedEquipmentType}
                onChange={(e) => setSelectedEquipmentType(e.target.value)}
              >
                <option value="">Tous les types</option>
                {filters.equipmentTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Recherche</label>
              <div className="flex gap-2">
                <Input
                  placeholder="Rechercher un paramètre..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSearch()}
                />
                <Button onClick={handleSearch} size="icon">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Résultats */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Chargement des réglages...</p>
        </div>
      ) : settings.length === 0 ? (
        <Card className="py-12">
          <CardContent className="text-center">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">Aucun réglage trouvé</h3>
            <p className="text-muted-foreground mt-2">
              Les réglages France seront extraits automatiquement lors de l'import des documentations.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* Statistiques */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{settings.length}</div>
                <p className="text-sm text-muted-foreground">Paramètres total</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{filters.brands.length}</div>
                <p className="text-sm text-muted-foreground">Marques</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{Object.keys(settingsByCategory).length}</div>
                <p className="text-sm text-muted-foreground">Catégories</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="pt-6">
                <div className="text-2xl font-bold">{filters.equipmentTypes.length}</div>
                <p className="text-sm text-muted-foreground">Types d'équipement</p>
              </CardContent>
            </Card>
          </div>

          {/* Paramètres par catégorie */}
          {Object.entries(settingsByCategory).map(([category, categorySettings]) => {
            const IconComponent = CATEGORY_ICONS[category] || Settings
            const colorClass = CATEGORY_COLORS[category] || "bg-gray-100 text-gray-800 border-gray-200"

            return (
              <Card key={category}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-3">
                    <span className={`p-2 rounded-lg border ${colorClass}`}>
                      <IconComponent className="h-5 w-5" />
                    </span>
                    {category}
                    <span className="text-sm font-normal text-muted-foreground">
                      ({categorySettings.length} paramètres)
                    </span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2 px-3 font-medium">Marque</th>
                          <th className="text-left py-2 px-3 font-medium">Modèle</th>
                          <th className="text-left py-2 px-3 font-medium">Paramètre</th>
                          <th className="text-left py-2 px-3 font-medium">Valeur</th>
                          <th className="text-left py-2 px-3 font-medium">Source</th>
                          <th className="text-left py-2 px-3 font-medium">Notes</th>
                        </tr>
                      </thead>
                      <tbody>
                        {categorySettings.map((setting) => (
                          <tr key={setting.id} className="border-b hover:bg-muted/50">
                            <td className="py-2 px-3 font-medium">{setting.brand}</td>
                            <td className="py-2 px-3 text-muted-foreground">
                              {setting.model || "-"}
                            </td>
                            <td className="py-2 px-3">{setting.name}</td>
                            <td className="py-2 px-3">
                              <span className="font-mono bg-muted px-2 py-1 rounded">
                                {setting.value}
                                {setting.unit && <span className="text-muted-foreground ml-1">{setting.unit}</span>}
                              </span>
                            </td>
                            <td className="py-2 px-3 text-muted-foreground text-xs">
                              {setting.sourceDoc || "-"}
                              {setting.pageNumber && ` (p.${setting.pageNumber})`}
                            </td>
                            <td className="py-2 px-3 text-muted-foreground text-xs max-w-xs truncate">
                              {setting.notes || "-"}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
