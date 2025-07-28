import React from "react";
import { clsx } from "clsx";
import { CheckCircle, XCircle, Info, AlertTriangle, X } from "lucide-react";

interface AlertProps {
  type: "success" | "error" | "info" | "warning";
  title?: string;
  message: string;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({
  type,
  title,
  message,
  onClose,
  className,
}) => {
  const icons = {
    success: CheckCircle,
    error: XCircle,
    info: Info,
    warning: AlertTriangle,
  };

  const styles = {
    success: "bg-green-50 border-green-200 text-green-800",
    error: "bg-red-50 border-red-200 text-red-800",
    info: "bg-blue-50 border-blue-200 text-blue-800",
    warning: "bg-yellow-50 border-yellow-200 text-yellow-800",
  };

  const Icon = icons[type];

  return (
    <div
      className={clsx("rounded-lg border p-4", styles[type], className)}
      role="alert"
    >
      <div className="flex items-start">
        <Icon className="h-5 w-5 flex-shrink-0 mt-0.5" />
        <div className="ml-3 flex-1">
          {title && <h3 className="text-sm font-medium mb-1">{title}</h3>}
          <p className="text-sm">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 flex-shrink-0 h-5 w-5 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-green-50 focus:ring-green-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};
