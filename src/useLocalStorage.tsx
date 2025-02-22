import { useState, useEffect, Dispatch, SetStateAction } from "react";

// Helper function to retrieve stored value from localStorage
function getStorageValue<T>(key: string, defaultValue: T): T {
  const saved = localStorage.getItem(key);
  if (saved) {
    try {
      return JSON.parse(saved) as T;
    } catch (error) {
      console.error("Error parsing localStorage value:", error);
      return defaultValue;
    }
  }
  return defaultValue;
}

// Custom hook to manage localStorage state
export const useLocalStorage = <T,>(
  key: string,
  defaultValue: T
): [T, Dispatch<SetStateAction<T>>] => {
  const [value, setValue] = useState<T>(() => {
    return getStorageValue<T>(key, defaultValue);
  });

  useEffect(() => {
    // Store the value in localStorage whenever it changes
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
};