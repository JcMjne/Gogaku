// pages/system-settings.tsx
"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function SystemSettings() {
  const [nativeLanguage, setNativeLanguage] = useState("");
  const [geminiApiKey, setGeminiApiKey] = useState("");
  const [message, setMessage] = useState("");

  const handleSave = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found in localStorage.");
      setMessage("Authentication required.");
      return;
    }
    console.log("Token found, sending request...");
    try {
      console.log("Sending request to save settings...");
      const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_URL}/system-settings`,
        { native_language: nativeLanguage, gemini_api_key: geminiApiKey },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      console.log("Response from server:", response.data);
      setMessage("Settings saved successfully");
    } catch (err) {
      console.error("Error occurred during API request:", err);
      setMessage("token: " + token);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen space-y-4">
      <h1 className="text-2xl font-bold">System Settings</h1>
      <input
        type="text"
        placeholder="Native Language"
        value={nativeLanguage}
        onChange={(e) => setNativeLanguage(e.target.value)}
        className="border p-2 rounded w-80"
      />
      <input
        type="text"
        placeholder="Gemini API Key"
        value={geminiApiKey}
        onChange={(e) => setGeminiApiKey(e.target.value)}
        className="border p-2 rounded w-80"
      />
      <button
        onClick={handleSave}
        className="bg-purple-600 text-white py-2 px-4 rounded hover:bg-purple-700"
      >
        Save Settings
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}
