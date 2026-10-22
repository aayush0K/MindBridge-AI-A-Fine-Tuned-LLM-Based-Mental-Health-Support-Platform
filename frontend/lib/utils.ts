import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Ensures a date string from the backend is parsed as UTC if no timezone is specified.
 */
function toUtcDate(dateStr: unknown): Date | null {
  if (!dateStr) return null;
  if (dateStr instanceof Date) {
    return isNaN(dateStr.getTime()) ? null : dateStr;
  }
  
  try {
    const s = String(dateStr).trim();
    if (!s) return null;
    
    // If date string does not have timezone info, append 'Z' so JS parses as UTC
    const isIsoWithoutTz =
      /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2}(\.\d+)?)?$/.test(s);
    const cleanStr = isIsoWithoutTz
      ? s.replace(" ", "T") + "Z"
      : s;

    const d = new Date(cleanStr);
    return isNaN(d.getTime()) ? null : d;
  } catch {
    return null;
  }
}

/**
 * Formats a date string into Indian Standard Time (IST) format: "01 Sep 2026, 03:01:20 pm"
 */
export function formatIndianDateTime(
  dateStr: unknown,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!dateStr) return "";
  try {
    const date = toUtcDate(dateStr);
    if (!date) return String(dateStr);
    return date.toLocaleString("en-IN", {
      timeZone: "Asia/Kolkata",
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
      ...options,
    });
  } catch {
    return String(dateStr || "");
  }
}

/**
 * Formats a date string into Indian Standard Date format: "01 Sep 2026"
 */
export function formatIndianDate(
  dateStr: unknown,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!dateStr) return "";
  try {
    const date = toUtcDate(dateStr);
    if (!date) return String(dateStr);
    return date.toLocaleDateString("en-IN", {
      timeZone: "Asia/Kolkata",
      day: "2-digit",
      month: "short",
      year: "numeric",
      ...options,
    });
  } catch {
    return String(dateStr || "");
  }
}

/**
 * Formats a date string into Indian Standard Time format: "03:01 pm"
 */
export function formatIndianTime(
  dateStr: unknown,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!dateStr) return "";
  try {
    const date = toUtcDate(dateStr);
    if (!date) return String(dateStr);
    return date.toLocaleTimeString("en-IN", {
      timeZone: "Asia/Kolkata",
      hour: "2-digit",
      minute: "2-digit",
      hour12: true,
      ...options,
    });
  } catch {
    return String(dateStr || "");
  }
}
