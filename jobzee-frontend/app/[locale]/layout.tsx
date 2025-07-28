import { NextIntlClientProvider } from "next-intl";
import { notFound } from "next/navigation";
import { ReactNode } from "react";

interface Props {
  children: ReactNode;
  params: { locale: string };
}

const locales = [
  "en",
  "hi",
  "es",
  "fr",
  "ml",
  "tr",
  "gu",
  "bn",
  "ar",
  "ru",
  "mr",
  "kn",
];

export default async function LocaleLayout({
  children,
  params: { locale },
}: Props) {
  if (!locales.includes(locale)) notFound();

  let messages;
  try {
    messages = (await import(`../../locales/${locale}.json`)).default;
  } catch (error) {
    notFound();
  }

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
