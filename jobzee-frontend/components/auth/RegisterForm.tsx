"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { User, Mail, Lock, Building, UserCheck } from "lucide-react";
import { Input } from "../ui/Input";
import { Button } from "../ui/Button";
import { Alert } from "../ui/Alert";
import { registerSchema, type RegisterFormData } from "../../lib/validation";
import { useAuthStore } from "../../lib/auth-store";
import { authAPI } from "../../lib/auth-api";

export const RegisterForm: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { login, setLoading } = useAuthStore();

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const password = watch("password");

  const getPasswordStrength = (password: string) => {
    if (!password) return { score: 0, label: "", color: "" };

    let score = 0;
    if (password.length >= 8) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    const labels = ["Very Weak", "Weak", "Fair", "Good", "Strong"];
    const colors = [
      "bg-red-500",
      "bg-orange-500",
      "bg-yellow-500",
      "bg-blue-500",
      "bg-green-500",
    ];

    return {
      score: Math.min(score, 5),
      label: labels[Math.min(score - 1, 4)],
      color: colors[Math.min(score - 1, 4)],
    };
  };

  const passwordStrength = getPasswordStrength(password);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setError(null);
      setLoading(true);

      const response = await authAPI.register({
        email: data.email,
        password: data.password,
        firstName: data.firstName,
        lastName: data.lastName,
        role: data.role,
      });

      login(response.accessToken, response.refreshToken, {
        ...response.user,
        role: response.user.role as "candidate" | "hr" | "admin",
      });

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed. Please try again.");
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="First Name"
          type="text"
          placeholder="Enter your first name"
          icon={<User />}
          error={errors.firstName?.message}
          {...register("firstName")}
        />
        <Input
          label="Last Name"
          type="text"
          placeholder="Enter your last name"
          icon={<User />}
          error={errors.lastName?.message}
          {...register("lastName")}
        />
      </div>

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
        placeholder="Create a strong password"
        icon={<Lock />}
        error={errors.password?.message}
        {...register("password")}
      />

      {password && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Password strength:</span>
            <span
              className={`font-medium ${passwordStrength.color.replace(
                "bg-",
                "text-"
              )}`}
            >
              {passwordStrength.label}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${passwordStrength.color}`}
              style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
            />
          </div>
        </div>
      )}

      <Input
        label="Confirm Password"
        type="password"
        placeholder="Confirm your password"
        icon={<Lock />}
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />

      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700">
          I am a:
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
            <input
              type="radio"
              value="candidate"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              {...register("role")}
            />
            <div className="ml-3 flex items-center">
              <UserCheck className="h-5 w-5 text-blue-600 mr-2" />
              <div>
                <div className="text-sm font-medium text-gray-900">
                  Job Seeker
                </div>
                <div className="text-xs text-gray-500">
                  Looking for opportunities
                </div>
              </div>
            </div>
          </label>
          <label className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
            <input
              type="radio"
              value="hr"
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              {...register("role")}
            />
            <div className="ml-3 flex items-center">
              <Building className="h-5 w-5 text-green-600 mr-2" />
              <div>
                <div className="text-sm font-medium text-gray-900">
                  HR Professional
                </div>
                <div className="text-xs text-gray-500">Hiring talent</div>
              </div>
            </div>
          </label>
        </div>
        {errors.role && (
          <p className="text-sm text-red-600">{errors.role.message}</p>
        )}
      </div>

      <div className="space-y-3">
        <label className="flex items-start">
          <input
            type="checkbox"
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mt-1"
            {...register("acceptTerms")}
          />
          <span className="ml-3 text-sm text-gray-600">
            I agree to the{" "}
            <Link
              href="/terms"
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link
              href="/privacy"
              className="text-blue-600 hover:text-blue-500 font-medium"
            >
              Privacy Policy
            </Link>
          </span>
        </label>
        {errors.acceptTerms && (
          <p className="text-sm text-red-600">{errors.acceptTerms.message}</p>
        )}
      </div>

      <Button
        type="submit"
        variant="primary"
        size="lg"
        fullWidth
        disabled={isSubmitting}
      >
        {isSubmitting ? "Creating account..." : "Create Account"}
      </Button>

      <div className="text-center">
        <p className="text-sm text-gray-600">
          Already have an account?{" "}
          <Link
            href="/auth/login"
            className="text-blue-600 hover:text-blue-500 font-medium transition-colors"
          >
            Sign in
          </Link>
        </p>
      </div>
    </motion.form>
  );
};
