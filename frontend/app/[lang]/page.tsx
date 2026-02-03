"use client"

import { UploadForm } from "@/components/dashboard/upload-form"
import { en, az } from "@/app/dictionaries/en"

const dictionaries = {
  en,
  az,
}

type DictionaryType = typeof en | typeof az

export default function HomePage({
  params: { lang },
}: {
  params: { lang: string }
}) {
  const t = (dictionaries[lang as keyof typeof dictionaries] || en) as any

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">{t.upload.title}</h1>
        <p className="text-gray-500 mt-1">
          {t.upload.description}
        </p>
      </div>
      <UploadForm t={t} />
    </div>
  )
}

