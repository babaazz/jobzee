"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";
import Link from "next/link";
import { motion } from "framer-motion";
import { Mail, Lock, Eye, EyeOff } from "lucide-react";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import { Alert } from "../ui/Alert";
import { loginSchema, type LoginFormData } from "../../lib/validation";
import { useAuthStore } from "../../lib/auth-store";
import { authAPI } from "../../lib/auth-api";

export const LoginForm: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const locale = useLocale();
  const { login, setLoading } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setError(null);
      setLoading(true);

      const response = await authAPI.login({
        email: data.email,
        password: data.password,
      });

      login(response.accessToken, response.refreshToken, {
        ...response.user,
        role: response.user.role as "candidate" | "hr" | "admin",
      });

      router.push(`/${locale}/dashboard`);
    } catch (err: any) {
      setError(err.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.form
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3 }}
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6"
    >
      {error && (
        <Alert type="error" message={error} onClose={() => setError(null)} />
      )}

      <Input
        label="Email Address"
        type="email"
        placeholder="Enter your email"
        icon={<Mail />}
        error={errors.email?.message}
        {...register("email")}
      />

      <Input
        label="Password"
        type="password"
        placeholder="Enter your password"
        icon={<Lock />}
        error={errors.password?.message}
        {...register("password")}
      />

      <div className="flex items-center justify-between">
        <label className="flex items-center">
          <input
            type="checkbox"
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            {...register("rememberMe")}
          />
          <span className="ml-2 text-sm text-gray-600">Remember me</span>
        </label>
        <Link
          href="/auth/forgot-password"
          className="text-sm text-blue-600 hover:text-blue-500 transition-colors"
        >
          Forgot password?
        </Link>
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        disabled={isSubmitting}
        className="w-full"
      >
        {isSubmitting ? "Signing in..." : "Sign In"}
      </Button>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Don't have an account?{" "}
          <Link
            href="/auth/register"
            className="text-blue-600 hover:text-blue-500 font-medium transition-colors"
          >
            Sign up
          </Link>
        </p>
      </div>
    </motion.form>
  );
};
