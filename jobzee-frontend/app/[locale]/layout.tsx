import { NextIntlClientProvider } from "next-intl";
import { notFound } from "next/navigation";
import { ReactNode } from "react";
import "../../styles/globals.css";

interface Props {
  children: ReactNode;
  params: { locale: string };
}

const locales = ["en", "hi"];

export default async function LocaleLayout({
  children,
  params: { locale },
}: Props) {
  if (!locales.includes(locale)) notFound();

  let messages;
  try {
    messages = (await import(`../../locales/${locale}.json`)).default;
  } catch (error) {
    // Fallback to English if locale file doesn't exist
    messages = (await import(`../../locales/en.json`)).default;
  }

  return (
    <html lang={locale} suppressHydrationWarning>
      <body suppressHydrationWarning>
        <NextIntlClientProvider locale={locale} messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
