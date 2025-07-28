import React, { forwardRef } from "react";
import { clsx } from "clsx";
import { Eye, EyeOff } from "lucide-react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    { label, error, icon, fullWidth = true, className, type, ...props },
    ref
  ) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const inputType = type === "password" && showPassword ? "text" : type;

    return (
      <div className={clsx("space-y-2", fullWidth && "w-full")}>
        {label && (
          <label className="block text-sm font-medium text-gray-700">
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="h-5 w-5 text-gray-400">{icon}</div>
            </div>
          )}
          <input
            ref={ref}
            type={inputType}
            className={clsx(
              "block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 placeholder-gray-500 transition-colors focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500",
              icon && "pl-10",
              type === "password" && "pr-10",
              error && "border-red-300 focus:border-red-500 focus:ring-red-500",
              className
            )}
            {...props}
          />
          {type === "password" && (
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              )}
            </button>
          )}
        </div>
        {error && (
          <p className="text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
