import { useTranslations } from "next-intl";
import { Header } from "../../components/layout/Header";
import { Footer } from "../../components/layout/Footer";
import { HeroSection } from "../../components/landing/HeroSection";
import { FeatureSection } from "../../components/landing/FeatureSection";

export default function HomePage() {
  const t = useTranslations("Index");

  return (
    <>
      <Header />
      <main className="pt-16">
        <HeroSection />
        <div id="features">
          <FeatureSection />
        </div>
      </main>
      <Footer />
    </>
  );
}
