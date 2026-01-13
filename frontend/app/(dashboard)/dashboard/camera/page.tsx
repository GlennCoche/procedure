"use client"

import { useState, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Camera, Upload, Loader2 } from "lucide-react"
import { apiPost } from "@/lib/api"

export default function CameraPage() {
  const [image, setImage] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      })
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (error) {
      console.error("Erreur d'accès à la caméra:", error)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop())
      setStream(null)
      if (videoRef.current) {
        videoRef.current.srcObject = null
      }
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext("2d")?.drawImage(video, 0, 0)
      const imageData = canvas.toDataURL("image/jpeg")
      setImage(imageData)
      stopCamera()
    }
  }

  const analyzeImage = async () => {
    if (!image) return

    setIsAnalyzing(true)
    setResult(null)

    try {
      // Convertir base64 en blob
      const response = await fetch(image)
      const blob = await response.blob()

      const formData = new FormData()
      formData.append("file", blob, "image.jpg")

      const apiResponse = await fetch("/api/vision", {
        method: "POST",
        credentials: "include",
        body: formData,
      })

      if (!apiResponse.ok) {
        throw new Error(`Erreur HTTP: ${apiResponse.status}`)
      }

      const data = await apiResponse.json()
      setResult(data)
    } catch (error) {
      console.error("Erreur d'analyse:", error)
      setResult({
        success: false,
        error: "Erreur lors de l'analyse de l'image",
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Reconnaissance d'Équipement</h1>
        <p className="text-muted-foreground mt-2">
          Prenez une photo ou uploadez une image pour identifier l'équipement
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Capture</CardTitle>
            <CardDescription>
              Utilisez votre caméra ou uploadez une photo
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {!stream && !image && (
              <div className="space-y-2">
                <Button onClick={startCamera} className="w-full">
                  <Camera className="h-4 w-4 mr-2" />
                  Ouvrir la caméra
                </Button>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                  className="w-full"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Uploader une photo
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
              </div>
            )}

            {stream && (
              <div className="space-y-2">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  className="w-full rounded-lg"
                />
                <div className="flex gap-2">
                  <Button onClick={capturePhoto} className="flex-1">
                    Capturer
                  </Button>
                  <Button onClick={stopCamera} variant="outline">
                    Annuler
                  </Button>
                </div>
              </div>
            )}

            {image && !stream && (
              <div className="space-y-2">
                <img src={image} alt="Captured" className="w-full rounded-lg" />
                <div className="flex gap-2">
                  <Button onClick={analyzeImage} disabled={isAnalyzing} className="flex-1">
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Analyse...
                      </>
                    ) : (
                      "Analyser"
                    )}
                  </Button>
                  <Button
                    onClick={() => {
                      setImage(null)
                      setResult(null)
                    }}
                    variant="outline"
                  >
                    Nouvelle photo
                  </Button>
                </div>
              </div>
            )}

            <canvas ref={canvasRef} className="hidden" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Résultat</CardTitle>
            <CardDescription>Identification de l'équipement</CardDescription>
          </CardHeader>
          <CardContent>
            {!result && !isAnalyzing && (
              <p className="text-muted-foreground text-sm">
                Prenez ou uploadez une photo pour commencer l'analyse
              </p>
            )}

            {isAnalyzing && (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            )}

            {result && result.success && result.data && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">Type d'équipement</h3>
                  <p>{result.data.equipment_type}</p>
                </div>
                {result.data.brand_model && (
                  <div>
                    <h3 className="font-semibold mb-2">Marque/Modèle</h3>
                    <p>{result.data.brand_model}</p>
                  </div>
                )}
                {result.data.condition && (
                  <div>
                    <h3 className="font-semibold mb-2">État</h3>
                    <p>{result.data.condition}</p>
                  </div>
                )}
                {result.data.maintenance_suggestions &&
                  result.data.maintenance_suggestions.length > 0 && (
                    <div>
                      <h3 className="font-semibold mb-2">Suggestions</h3>
                      <ul className="list-disc list-inside space-y-1">
                        {result.data.maintenance_suggestions.map(
                          (suggestion: string, idx: number) => (
                            <li key={idx} className="text-sm">
                              {suggestion}
                            </li>
                          )
                        )}
                      </ul>
                    </div>
                  )}
              </div>
            )}

            {result && !result.success && (
              <div className="text-destructive">
                <p>Erreur: {result.error || "Erreur inconnue"}</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
