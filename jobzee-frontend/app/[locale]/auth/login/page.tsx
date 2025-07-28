"use client";

import { useTranslations } from "next-intl";
import { AuthLayout } from "../../../../components/auth/AuthLayout";
import { LoginForm } from "../../../../components/auth/LoginForm";

export default function LoginPage() {
  const t = useTranslations("auth");

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to your account to continue"
    >
      <LoginForm />
    </AuthLayout>
  );
}
