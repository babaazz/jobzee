import { useTranslations } from "next-intl";

export default function HomePage() {
  const t = useTranslations("Index");

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-6">
            {t("title")}
          </h1>
          <p className="text-xl text-gray-600 mb-8">{t("description")}</p>
          <div className="space-x-4">
            <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
              {t("getStarted")}
            </button>
            <button className="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors">
              {t("learnMore")}
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
