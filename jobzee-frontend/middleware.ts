import createMiddleware from "next-intl/middleware";

export default createMiddleware({
  // A list of all locales that are supported
  locales: [
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
  ],

  // Used when no locale matches
  defaultLocale: "en",
});

export const config = {
  // Match only internationalized pathnames
  matcher: ["/", "/(hi|en|es|fr|ml|tr|gu|bn|ar|ru|mr|kn)/:path*"],
};
