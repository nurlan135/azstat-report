"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, CheckCircle, AlertTriangle, Clock } from "lucide-react"

interface StatisticsCardsProps {
  totalReports: number
  validReports: number
  errorsCount: number
  pendingReports: number
}

export function StatisticsCards({
  totalReports,
  validReports,
  errorsCount,
  pendingReports,
}: StatisticsCardsProps) {
  const cards = [
    {
      title: "Total Reports",
      value: totalReports,
      icon: FileText,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
    },
    {
      title: "Valid Reports",
      value: validReports,
      icon: CheckCircle,
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      title: "Errors Found",
      value: errorsCount,
      icon: AlertTriangle,
      color: "text-red-600",
      bgColor: "bg-red-50",
    },
    {
      title: "Pending Review",
      value: pendingReports,
      icon: Clock,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              {card.title}
            </CardTitle>
            <div className={`rounded-lg p-2 ${card.bgColor}`}>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900">{card.value}</div>
            <p className="text-xs text-gray-500 mt-1">
              {card.title.toLowerCase()} in the system
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
