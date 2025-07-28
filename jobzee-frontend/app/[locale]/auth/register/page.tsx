"use client";

import { useTranslations } from "next-intl";
import { AuthLayout } from "../../../../components/auth/AuthLayout";
import { RegisterForm } from "../../../../components/auth/RegisterForm";

export default function RegisterPage() {
  const t = useTranslations("auth");

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Join thousands of professionals finding their dream jobs"
      maxWidth="lg"
    >
      <RegisterForm />
    </AuthLayout>
  );
}
